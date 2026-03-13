# -*- coding: utf-8 -*-
"""
预处理模块

负责对原始证据执行清洗、去重、标准化与排序。

处理流程：
1. clean: 清洗原始内容（移除 HTML、空白、无效字符）
2. dedupe: 去除重复证据（URL、标题、内容）
3. normalize: 标准化证据格式（日期、URL）
4. rank: 评分排序（质量、时效、相关性）

使用方式：
    from backend.app.services.preprocessing import preprocess_evidence

    processed = preprocess_evidence(raw_evidence_list, company_name="某公司")
"""

from __future__ import annotations

from typing import List, Optional

from ..orchestrator.pipeline_state import ProcessedEvidence, RawEvidence
from .evidence_cleaner import (
    EvidenceCleaner,
    clean_evidence,
    clean_evidence_batch,
    get_evidence_cleaner,
)
from .evidence_deduplicator import (
    EvidenceDeduplicator,
    deduplicate_evidence,
    get_evidence_deduplicator,
)
from .evidence_normalizer import (
    EvidenceNormalizer,
    get_evidence_normalizer,
    normalize_evidence,
    normalize_evidence_batch,
)
from .evidence_ranker import (
    EvidenceRanker,
    get_evidence_ranker,
    rank_evidence,
)


class PreprocessingPipeline:
    """
    预处理管道

    串联清洗、去重、标准化、排序四个阶段，提供统一入口。

    使用方式：
        pipeline = PreprocessingPipeline()
        result = pipeline.process(raw_evidence_list, company_name="某公司")
    """

    def __init__(
        self,
        cleaner: Optional[EvidenceCleaner] = None,
        deduplicator: Optional[EvidenceDeduplicator] = None,
        normalizer: Optional[EvidenceNormalizer] = None,
        ranker: Optional[EvidenceRanker] = None,
    ):
        """
        初始化预处理管道

        Args:
            cleaner: 证据清洗器实例
            deduplicator: 证据去重器实例
            normalizer: 证据标准化器实例
            ranker: 证据排序器实例
        """
        self.cleaner = cleaner or get_evidence_cleaner()
        self.deduplicator = deduplicator or get_evidence_deduplicator()
        self.normalizer = normalizer or get_evidence_normalizer()
        self.ranker = ranker or get_evidence_ranker()

    def process(
        self,
        raw_evidence_list: List[RawEvidence],
        company_name: Optional[str] = None,
    ) -> List[ProcessedEvidence]:
        """
        执行完整预处理流程

        流程顺序：clean -> dedupe -> normalize -> rank

        Args:
            raw_evidence_list: 原始证据列表
            company_name: 企业名称，用于相关性评分

        Returns:
            List[ProcessedEvidence]: 处理后的证据列表
        """
        if not raw_evidence_list:
            return []

        # 1. 清洗
        cleaned = self.cleaner.clean_batch(raw_evidence_list)
        if not cleaned:
            return []

        # 2. 去重
        deduplicated = self.deduplicator.deduplicate(cleaned)
        if not deduplicated:
            return []

        # 3. 标准化
        normalized = self.normalizer.normalize_batch(deduplicated)

        # 4. 排序
        ranked = self.ranker.rank(normalized, company_name)

        return ranked


# 模块级单例实例
_default_pipeline: Optional[PreprocessingPipeline] = None


def get_preprocessing_pipeline() -> PreprocessingPipeline:
    """
    获取预处理管道单例实例

    Returns:
        PreprocessingPipeline: 预处理管道实例
    """
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = PreprocessingPipeline()
    return _default_pipeline


def preprocess_evidence(
    raw_evidence_list: List[RawEvidence],
    company_name: Optional[str] = None,
) -> List[ProcessedEvidence]:
    """
    便捷函数：执行完整预处理流程

    Args:
        raw_evidence_list: 原始证据列表
        company_name: 企业名称

    Returns:
        List[ProcessedEvidence]: 处理后的证据列表
    """
    pipeline = get_preprocessing_pipeline()
    return pipeline.process(raw_evidence_list, company_name)


# 导出所有公共接口
__all__ = [
    # 模块
    "EvidenceCleaner",
    "EvidenceDeduplicator",
    "EvidenceNormalizer",
    "EvidenceRanker",
    "PreprocessingPipeline",
    # 单例获取函数
    "get_evidence_cleaner",
    "get_evidence_deduplicator",
    "get_evidence_normalizer",
    "get_evidence_ranker",
    "get_preprocessing_pipeline",
    # 便捷函数
    "clean_evidence",
    "clean_evidence_batch",
    "deduplicate_evidence",
    "normalize_evidence",
    "normalize_evidence_batch",
    "rank_evidence",
    "preprocess_evidence",
]