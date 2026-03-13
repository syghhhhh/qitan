# -*- coding: utf-8 -*-
"""
EvidenceRanker - 证据排序器

对处理后的证据执行排序和评分：
- 相关性评分
- 时效性评分
- 来源权重
- 综合排序
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from ..orchestrator.pipeline_state import ProcessedEvidence


class EvidenceRanker:
    """
    证据排序器

    对处理后证据执行评分和排序，优先保留高质量、高相关性的证据。

    使用方式：
        ranker = EvidenceRanker()
        ranked = ranker.rank(processed_evidence, company_name)

    Attributes:
        recency_weight: 时效性权重
        quality_weight: 质量权重
        relevance_weight: 相关性权重
        source_weights: 来源类型权重
    """

    # 默认权重配置
    DEFAULT_RECENCY_WEIGHT = 0.3
    DEFAULT_QUALITY_WEIGHT = 0.3
    DEFAULT_RELEVANCE_WEIGHT = 0.4

    # 来源类型权重
    DEFAULT_SOURCE_WEIGHTS = {
        "website": 0.9,
        "news": 0.85,
        "jobs": 0.7,
        "risk": 0.8,
        "social": 0.6,
        "patent": 0.75,
        "finance": 0.8,
        "user_supplied": 0.95,
    }

    def __init__(
        self,
        recency_weight: float = DEFAULT_RECENCY_WEIGHT,
        quality_weight: float = DEFAULT_QUALITY_WEIGHT,
        relevance_weight: float = DEFAULT_RELEVANCE_WEIGHT,
        source_weights: Optional[dict] = None,
    ):
        """
        初始化证据排序器

        Args:
            recency_weight: 时效性权重 (0-1)
            quality_weight: 质量权重 (0-1)
            relevance_weight: 相关性权重 (0-1)
            source_weights: 来源类型权重映射
        """
        self.recency_weight = recency_weight
        self.quality_weight = quality_weight
        self.relevance_weight = relevance_weight
        self.source_weights = source_weights or self.DEFAULT_SOURCE_WEIGHTS

    def rank(
        self,
        evidence_list: List[ProcessedEvidence],
        company_name: Optional[str] = None,
    ) -> List[ProcessedEvidence]:
        """
        对证据列表执行评分和排序

        排序流程：
        1. 计算时效性评分
        2. 计算相关性评分
        3. 综合质量、时效、相关性计算总分
        4. 按总分降序排序

        Args:
            evidence_list: 标准化后的证据列表
            company_name: 企业名称，用于相关性计算

        Returns:
            List[ProcessedEvidence]: 排序后的证据列表
        """
        if not evidence_list:
            return []

        # 计算每条证据的综合评分
        scored_evidence = []
        for evidence in evidence_list:
            # 计算各项评分
            recency_score = self._calculate_recency_score(evidence)
            quality_score = evidence.quality_score
            relevance_score = self._calculate_relevance_score(
                evidence, company_name
            )
            source_score = self._get_source_weight(evidence.source_type)

            # 综合评分
            total_score = (
                recency_score * self.recency_weight
                + quality_score * self.quality_weight
                + relevance_score * self.relevance_weight
            ) * source_score

            # 更新证据的相关性评分
            updated_evidence = self._update_relevance_score(
                evidence, relevance_score
            )
            scored_evidence.append((total_score, updated_evidence))

        # 按总分降序排序
        scored_evidence.sort(key=lambda x: x[0], reverse=True)

        return [evidence for _, evidence in scored_evidence]

    def _calculate_recency_score(self, evidence: ProcessedEvidence) -> float:
        """
        计算时效性评分

        基于证据日期，越近的证据得分越高

        Args:
            evidence: 处理后的证据

        Returns:
            float: 时效性评分 (0-1)
        """
        # 尝试从标准化日期获取
        if evidence.normalized_date:
            try:
                evidence_date = datetime.strptime(
                    evidence.normalized_date, "%Y-%m-%d"
                )
                return self._date_to_recency_score(evidence_date)
            except ValueError:
                pass

        # 尝试从元数据获取
        if "publish_date" in evidence.metadata:
            try:
                evidence_date = datetime.strptime(
                    evidence.metadata["publish_date"], "%Y-%m-%d"
                )
                return self._date_to_recency_score(evidence_date)
            except (ValueError, TypeError):
                pass

        # 无法获取日期，使用默认中等评分
        return 0.5

    def _date_to_recency_score(self, evidence_date: datetime) -> float:
        """
        将日期转换为时效性评分

        Args:
            evidence_date: 证据日期

        Returns:
            float: 时效性评分 (0-1)
        """
        now = datetime.now()
        days_diff = (now - evidence_date).days

        # 时间衰减函数
        if days_diff <= 7:
            return 1.0
        elif days_diff <= 30:
            return 0.9 - (days_diff - 7) * 0.01
        elif days_diff <= 90:
            return 0.6 - (days_diff - 30) * 0.005
        elif days_diff <= 365:
            return 0.3 - (days_diff - 90) * 0.001
        else:
            return max(0.1, 0.1 - (days_diff - 365) * 0.0001)

    def _calculate_relevance_score(
        self,
        evidence: ProcessedEvidence,
        company_name: Optional[str],
    ) -> float:
        """
        计算相关性评分

        基于内容与企业名称的相关性

        Args:
            evidence: 处理后的证据
            company_name: 企业名称

        Returns:
            float: 相关性评分 (0-1)
        """
        base_score = evidence.relevance_score

        if not company_name:
            return base_score

        # 检查企业名称在内容中的出现情况
        content = evidence.cleaned_content.lower()
        title = evidence.title.lower()
        company_lower = company_name.lower()

        # 标题包含企业名称
        if company_lower in title:
            base_score = min(1.0, base_score + 0.3)

        # 内容包含企业名称
        if company_lower in content:
            # 计算出现频率
            occurrences = content.count(company_lower)
            frequency_bonus = min(0.2, occurrences * 0.05)
            base_score = min(1.0, base_score + frequency_bonus)

        # 检查企业简称
        if len(company_name) >= 2:
            short_name = company_name[:2].lower()
            if short_name in title or short_name in content:
                base_score = min(1.0, base_score + 0.1)

        return base_score

    def _get_source_weight(self, source_type: str) -> float:
        """
        获取来源类型权重

        Args:
            source_type: 来源类型

        Returns:
            float: 来源权重 (0-1)
        """
        return self.source_weights.get(source_type, 0.7)

    def _update_relevance_score(
        self,
        evidence: ProcessedEvidence,
        relevance_score: float,
    ) -> ProcessedEvidence:
        """
        更新证据的相关性评分

        Args:
            evidence: 原证据
            relevance_score: 新的相关性评分

        Returns:
            ProcessedEvidence: 更新后的证据
        """
        return ProcessedEvidence(
            evidence_id=evidence.evidence_id,
            raw_evidence_id=evidence.raw_evidence_id,
            source_type=evidence.source_type,
            url=evidence.url,
            title=evidence.title,
            cleaned_content=evidence.cleaned_content,
            normalized_date=evidence.normalized_date,
            quality_score=evidence.quality_score,
            relevance_score=relevance_score,
            metadata=evidence.metadata,
        )


# 模块级单例实例
_default_ranker: Optional[EvidenceRanker] = None


def get_evidence_ranker(
    recency_weight: float = EvidenceRanker.DEFAULT_RECENCY_WEIGHT,
    quality_weight: float = EvidenceRanker.DEFAULT_QUALITY_WEIGHT,
    relevance_weight: float = EvidenceRanker.DEFAULT_RELEVANCE_WEIGHT,
) -> EvidenceRanker:
    """
    获取证据排序器单例实例

    Args:
        recency_weight: 时效性权重
        quality_weight: 质量权重
        relevance_weight: 相关性权重

    Returns:
        EvidenceRanker: 证据排序器实例
    """
    global _default_ranker
    if _default_ranker is None:
        _default_ranker = EvidenceRanker(
            recency_weight=recency_weight,
            quality_weight=quality_weight,
            relevance_weight=relevance_weight,
        )
    return _default_ranker


def rank_evidence(
    evidence_list: List[ProcessedEvidence],
    company_name: Optional[str] = None,
) -> List[ProcessedEvidence]:
    """
    便捷函数：对证据排序

    Args:
        evidence_list: 标准化后的证据列表
        company_name: 企业名称

    Returns:
        List[ProcessedEvidence]: 排序后的证据列表
    """
    ranker = get_evidence_ranker()
    return ranker.rank(evidence_list, company_name)