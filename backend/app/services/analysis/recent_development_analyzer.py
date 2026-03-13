# -*- coding: utf-8 -*-
"""
RecentDevelopmentAnalyzer - 近期动态分析器

对近期动态候选项进行筛选、去重、排序和统一结构化，生成 recent_developments 输出。

主要功能：
1. 筛选 recent_development 类型的候选事实
2. 事件类型映射与标准化
3. 基于相似度的去重
4. 按日期和重要性排序
5. 生成结构化 RecentDevelopment 列表
"""

from __future__ import annotations

from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from ...schemas import RecentDevelopment, RecentDevelopmentTypeEnum
from ..orchestrator.pipeline_state import AnalysisResult, CandidateFact


class RecentDevelopmentAnalyzer:
    """
    近期动态分析器

    对近期动态候选项进行筛选、去重、排序和统一结构化。

    使用方式：
        analyzer = RecentDevelopmentAnalyzer()
        result = analyzer.analyze(candidate_facts)

    Attributes:
        event_type_mapping: extractor 事件类型到 RecentDevelopmentTypeEnum 的映射
        max_developments: 最大返回数量
        similarity_threshold: 相似度阈值（用于去重）
    """

    # extractor 事件类型到 RecentDevelopmentTypeEnum 的映射
    EVENT_TYPE_MAPPING = {
        "financing": RecentDevelopmentTypeEnum.FINANCING,
        "product_launch": RecentDevelopmentTypeEnum.NEW_PRODUCT,
        "partnership": RecentDevelopmentTypeEnum.PARTNERSHIP,
        "personnel": RecentDevelopmentTypeEnum.MANAGEMENT_CHANGE,
        "expansion": RecentDevelopmentTypeEnum.EXPANSION,
        "award": RecentDevelopmentTypeEnum.NEWS,  # 荣誉奖项归类为新闻
        "tech_breakthrough": RecentDevelopmentTypeEnum.NEWS,  # 技术突破归类为新闻
        "ipo": RecentDevelopmentTypeEnum.NEWS,  # 上市事件归类为新闻
        "hiring": RecentDevelopmentTypeEnum.HIRING,
        "bidding": RecentDevelopmentTypeEnum.BIDDING,
        "digital_transformation": RecentDevelopmentTypeEnum.DIGITAL_TRANSFORMATION,
        "compliance": RecentDevelopmentTypeEnum.COMPLIANCE,
    }

    # 事件类型重要性权重（用于排序）
    EVENT_TYPE_WEIGHTS = {
        RecentDevelopmentTypeEnum.FINANCING: 1.0,
        RecentDevelopmentTypeEnum.NEW_PRODUCT: 0.9,
        RecentDevelopmentTypeEnum.PARTNERSHIP: 0.85,
        RecentDevelopmentTypeEnum.MANAGEMENT_CHANGE: 0.8,
        RecentDevelopmentTypeEnum.EXPANSION: 0.75,
        RecentDevelopmentTypeEnum.DIGITAL_TRANSFORMATION: 0.7,
        RecentDevelopmentTypeEnum.BIDDING: 0.65,
        RecentDevelopmentTypeEnum.HIRING: 0.5,
        RecentDevelopmentTypeEnum.COMPLIANCE: 0.6,
        RecentDevelopmentTypeEnum.NEWS: 0.55,
        RecentDevelopmentTypeEnum.OTHER: 0.3,
    }

    # 默认配置
    DEFAULT_MAX_DEVELOPMENTS = 15
    DEFAULT_SIMILARITY_THRESHOLD = 0.75

    def __init__(
        self,
        max_developments: int = DEFAULT_MAX_DEVELOPMENTS,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        """
        初始化近期动态分析器

        Args:
            max_developments: 最大返回数量
            similarity_threshold: 相似度阈值（0-1），超过此阈值视为重复
        """
        self.max_developments = max_developments
        self.similarity_threshold = similarity_threshold

    def analyze(
        self,
        candidate_facts: List[CandidateFact],
        source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> AnalysisResult:
        """
        分析近期动态候选事实，生成统一的近期动态列表

        分析流程：
        1. 筛选 recent_development 类型的候选事实
        2. 转换为 DevelopmentItem 中间结构
        3. 去重（基于摘要相似度）
        4. 按日期和重要性排序
        5. 生成结构化 RecentDevelopment 列表

        Args:
            candidate_facts: 候选事实列表
            source_evidence_map: 证据来源映射（用于获取来源信息）

        Returns:
            AnalysisResult: 包含 RecentDevelopment 列表的分析结果
        """
        # 筛选近期动态相关候选事实
        development_facts = [
            f for f in candidate_facts
            if f.fact_type.startswith("recent_development.")
        ]

        if not development_facts:
            return self._create_empty_result()

        # 转换为中间结构
        items = [self._convert_to_item(fact) for fact in development_facts]

        # 去重
        unique_items = self._deduplicate(items)

        # 排序
        sorted_items = self._sort_items(unique_items)

        # 限制数量
        final_items = sorted_items[:self.max_developments]

        # 生成 RecentDevelopment 列表
        developments = []
        source_fact_ids: List[str] = []
        total_confidence = 0.0

        for item in final_items:
            development = self._create_development(item, source_evidence_map)
            developments.append(development)
            source_fact_ids.append(item.fact_id)
            total_confidence += item.confidence

        # 计算平均置信度
        avg_confidence = total_confidence / len(final_items) if final_items else 0.0

        return AnalysisResult(
            result_type="recent_developments",
            result_data={"developments": [d.model_dump() for d in developments]},
            source_fact_ids=source_fact_ids,
            confidence=avg_confidence,
        )

    def _convert_to_item(self, fact: CandidateFact) -> DevelopmentItem:
        """
        将候选事实转换为中间结构

        Args:
            fact: 候选事实

        Returns:
            DevelopmentItem: 中间结构
        """
        fact_data = fact.fact_data

        # 获取事件类型
        event_type_str = fact_data.get("event_type", "other")
        event_type = self.EVENT_TYPE_MAPPING.get(
            event_type_str, RecentDevelopmentTypeEnum.OTHER
        )

        # 获取日期
        date_str = fact_data.get("date")
        date_obj = None
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        return DevelopmentItem(
            fact_id=fact.fact_id,
            event_type=event_type,
            event_type_label=fact_data.get("event_type_label", event_type_str),
            date=date_obj,
            date_text=fact_data.get("date_text"),
            title=fact_data.get("title", ""),
            summary=fact_data.get("summary", ""),
            source_url=fact_data.get("source_url", ""),
            confidence=fact.confidence,
            source_evidence_ids=fact.source_evidence_ids,
        )

    def _deduplicate(self, items: List[DevelopmentItem]) -> List[DevelopmentItem]:
        """
        基于摘要相似度去重

        Args:
            items: 开发项列表

        Returns:
            List[DevelopmentItem]: 去重后的列表
        """
        if not items:
            return []

        unique_items: List[DevelopmentItem] = []

        for item in items:
            is_duplicate = False

            for existing in unique_items:
                # 检查是否为相似事件
                if self._is_similar(item, existing):
                    is_duplicate = True
                    # 保留置信度更高的
                    if item.confidence > existing.confidence:
                        # 替换为置信度更高的
                        unique_items.remove(existing)
                        unique_items.append(item)
                    break

            if not is_duplicate:
                unique_items.append(item)

        return unique_items

    def _is_similar(
        self,
        item1: DevelopmentItem,
        item2: DevelopmentItem,
    ) -> bool:
        """
        判断两个事件是否相似

        Args:
            item1: 第一个事件
            item2: 第二个事件

        Returns:
            bool: 是否相似
        """
        # 相同事件类型
        if item1.event_type != item2.event_type:
            return False

        # 日期相近（7天内）
        if item1.date and item2.date:
            days_diff = abs((item1.date - item2.date).days)
            if days_diff > 7:
                return False

        # 标题相似度
        title_similarity = self._calculate_similarity(item1.title, item2.title)
        if title_similarity > self.similarity_threshold:
            return True

        # 摘要相似度
        summary_similarity = self._calculate_similarity(item1.summary, item2.summary)
        if summary_similarity > self.similarity_threshold:
            return True

        return False

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        Args:
            text1: 第一个文本
            text2: 第二个文本

        Returns:
            float: 相似度 (0-1)
        """
        if not text1 or not text2:
            return 0.0

        # 使用 SequenceMatcher 计算相似度
        return SequenceMatcher(None, text1, text2).ratio()

    def _sort_items(self, items: List[DevelopmentItem]) -> List[DevelopmentItem]:
        """
        按日期和重要性排序

        排序规则：
        1. 有日期的优先
        2. 日期降序（最近的在前）
        3. 同日期按事件类型权重排序
        4. 同权重按置信度排序

        Args:
            items: 开发项列表

        Returns:
            List[DevelopmentItem]: 排序后的列表
        """
        def sort_key(item: DevelopmentItem) -> tuple:
            # 日期排序：有日期的优先，日期越近越前
            if item.date:
                # 使用负值使日期降序
                date_key = (0, -item.date.timestamp())
            else:
                # 无日期的排最后
                date_key = (1, 0)

            # 事件类型权重
            type_weight = self.EVENT_TYPE_WEIGHTS.get(item.event_type, 0.3)

            # 置信度
            confidence = item.confidence

            return (date_key[0], date_key[1], -type_weight, -confidence)

        return sorted(items, key=sort_key)

    def _create_development(
        self,
        item: DevelopmentItem,
        source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> RecentDevelopment:
        """
        创建 RecentDevelopment 对象

        Args:
            item: 中间结构
            source_evidence_map: 证据来源映射

        Returns:
            RecentDevelopment: 近期动态对象
        """
        # 格式化日期
        if item.date:
            date_str = item.date.strftime("%Y-%m-%d")
        elif item.date_text:
            date_str = item.date_text
        else:
            date_str = "未知日期"

        # 获取来源名称
        source = "公开信息"
        if item.source_url:
            # 从 URL 提取域名作为来源
            try:
                from urllib.parse import urlparse
                parsed = urlparse(item.source_url)
                source = parsed.netloc or "公开信息"
            except Exception:
                pass

        # 如果有证据映射，获取更详细的来源信息
        if source_evidence_map and item.source_evidence_ids:
            for evidence_id in item.source_evidence_ids:
                if evidence_id in source_evidence_map:
                    evidence_info = source_evidence_map[evidence_id]
                    if "title" in evidence_info:
                        source = evidence_info["title"][:50]
                        break

        return RecentDevelopment(
            date=date_str,
            type=item.event_type,
            title=item.title or item.summary[:50] if item.summary else "企业动态",
            summary=item.summary or item.title or "暂无详细信息",
            source=source,
            source_ref_ids=item.source_evidence_ids,
            confidence=item.confidence,
        )

    def _create_empty_result(self) -> AnalysisResult:
        """
        创建空结果

        Returns:
            AnalysisResult: 空的分析结果
        """
        return AnalysisResult(
            result_type="recent_developments",
            result_data={"developments": []},
            source_fact_ids=[],
            confidence=0.0,
        )


class DevelopmentItem:
    """
    近期动态中间结构

    用于分析过程中的中间数据处理。
    """

    def __init__(
        self,
        fact_id: str,
        event_type: RecentDevelopmentTypeEnum,
        event_type_label: str,
        date: Optional[datetime],
        date_text: Optional[str],
        title: str,
        summary: str,
        source_url: str,
        confidence: float,
        source_evidence_ids: List[str],
    ):
        self.fact_id = fact_id
        self.event_type = event_type
        self.event_type_label = event_type_label
        self.date = date
        self.date_text = date_text
        self.title = title
        self.summary = summary
        self.source_url = source_url
        self.confidence = confidence
        self.source_evidence_ids = source_evidence_ids


# 模块级单例实例
_default_analyzer: Optional[RecentDevelopmentAnalyzer] = None


def get_recent_development_analyzer(
    max_developments: int = RecentDevelopmentAnalyzer.DEFAULT_MAX_DEVELOPMENTS,
    similarity_threshold: float = RecentDevelopmentAnalyzer.DEFAULT_SIMILARITY_THRESHOLD,
) -> RecentDevelopmentAnalyzer:
    """
    获取近期动态分析器单例实例

    Args:
        max_developments: 最大返回数量
        similarity_threshold: 相似度阈值

    Returns:
        RecentDevelopmentAnalyzer: 近期动态分析器实例
    """
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = RecentDevelopmentAnalyzer(
            max_developments=max_developments,
            similarity_threshold=similarity_threshold,
        )
    return _default_analyzer


def analyze_recent_developments(
    candidate_facts: List[CandidateFact],
    source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> AnalysisResult:
    """
    便捷函数：分析近期动态候选事实

    Args:
        candidate_facts: 候选事实列表
        source_evidence_map: 证据来源映射

    Returns:
        AnalysisResult: 包含 RecentDevelopment 列表的分析结果
    """
    analyzer = get_recent_development_analyzer()
    return analyzer.analyze(candidate_facts, source_evidence_map)