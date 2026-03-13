# -*- coding: utf-8 -*-
"""
EvidenceDeduplicator - 证据去重器

对处理后的证据执行去重操作：
- URL 去重
- 标题相似度去重
- 内容相似度去重
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Set

from ..orchestrator.pipeline_state import ProcessedEvidence


class EvidenceDeduplicator:
    """
    证据去重器

    对处理后证据执行去重，避免重复内容进入后续分析阶段。

    使用方式：
        deduplicator = EvidenceDeduplicator()
        unique = deduplicator.deduplicate(processed_evidence)

    Attributes:
        similarity_threshold: 相似度阈值，超过此值视为重复
        enable_url_dedup: 是否启用 URL 去重
        enable_title_dedup: 是否启用标题去重
        enable_content_dedup: 是否启用内容去重
    """

    # 默认配置
    DEFAULT_SIMILARITY_THRESHOLD = 0.85
    DEFAULT_MIN_HASH_LENGTH = 50

    def __init__(
        self,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        enable_url_dedup: bool = True,
        enable_title_dedup: bool = True,
        enable_content_dedup: bool = True,
    ):
        """
        初始化证据去重器

        Args:
            similarity_threshold: 相似度阈值 (0-1)
            enable_url_dedup: 是否启用 URL 去重
            enable_title_dedup: 是否启用标题去重
            enable_content_dedup: 是否启用内容去重
        """
        self.similarity_threshold = similarity_threshold
        self.enable_url_dedup = enable_url_dedup
        self.enable_title_dedup = enable_title_dedup
        self.enable_content_dedup = enable_content_dedup

    def deduplicate(
        self, evidence_list: List[ProcessedEvidence]
    ) -> List[ProcessedEvidence]:
        """
        对证据列表执行去重

        去重顺序：
        1. URL 去重（完全匹配）
        2. 标题去重（相似度匹配）
        3. 内容去重（相似度匹配）

        Args:
            evidence_list: 处理后的证据列表

        Returns:
            List[ProcessedEvidence]: 去重后的证据列表
        """
        if not evidence_list:
            return []

        result: List[ProcessedEvidence] = []
        seen_urls: Set[str] = set()
        seen_titles: List[str] = []
        seen_content_hashes: Set[str] = set()

        for evidence in evidence_list:
            # URL 去重
            if self.enable_url_dedup and evidence.url:
                normalized_url = self._normalize_url(evidence.url)
                if normalized_url in seen_urls:
                    continue
                seen_urls.add(normalized_url)

            # 标题去重
            if self.enable_title_dedup:
                normalized_title = self._normalize_text(evidence.title)
                if self._is_duplicate_text(
                    normalized_title, seen_titles, self.similarity_threshold
                ):
                    continue
                seen_titles.append(normalized_title)

            # 内容去重
            if self.enable_content_dedup:
                content_hash = self._get_content_hash(evidence.cleaned_content)
                if content_hash in seen_content_hashes:
                    continue
                seen_content_hashes.add(content_hash)

            result.append(evidence)

        return result

    def _normalize_url(self, url: str) -> str:
        """
        标准化 URL，用于去重比较

        Args:
            url: 原始 URL

        Returns:
            str: 标准化后的 URL
        """
        if not url:
            return ""

        # 转小写
        normalized = url.lower().strip()

        # 移除协议
        for prefix in ["https://", "http://"]:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :]
                break

        # 移除 www 前缀
        if normalized.startswith("www."):
            normalized = normalized[4:]

        # 移除尾部斜杠
        normalized = normalized.rstrip("/")

        # 移除常见追踪参数
        tracking_params = [
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "ref",
            "source",
        ]
        for param in tracking_params:
            pattern = rf"[?&]{param}=[^&]*"
            normalized = re.sub(pattern, "", normalized)

        return normalized

    def _normalize_text(self, text: str) -> str:
        """
        标准化文本，用于相似度比较

        Args:
            text: 原始文本

        Returns:
            str: 标准化后的文本
        """
        if not text:
            return ""

        # 转小写
        normalized = text.lower().strip()

        # 移除标点符号
        normalized = re.sub(r"[^\w\s]", "", normalized)

        # 移除多余空白
        normalized = re.sub(r"\s+", " ", normalized)

        return normalized

    def _get_content_hash(self, content: str) -> str:
        """
        获取内容的哈希值

        对于短内容使用全文哈希，对于长内容使用分段哈希

        Args:
            content: 文本内容

        Returns:
            str: 内容哈希值
        """
        if not content:
            return ""

        # 标准化内容
        normalized = self._normalize_text(content)

        # 对于长内容，使用前中后三段组合
        if len(normalized) > 500:
            part_size = len(normalized) // 3
            combined = (
                normalized[:part_size]
                + normalized[part_size : 2 * part_size]
                + normalized[2 * part_size :]
            )
        else:
            combined = normalized

        return hashlib.md5(combined.encode("utf-8")).hexdigest()

    def _is_duplicate_text(
        self,
        text: str,
        existing_texts: List[str],
        threshold: float,
    ) -> bool:
        """
        检查文本是否与已有文本重复

        使用简单的字符级相似度计算，适用于短文本（标题）

        Args:
            text: 待检查文本
            existing_texts: 已有文本列表
            threshold: 相似度阈值

        Returns:
            bool: 是否重复
        """
        if not text or not existing_texts:
            return False

        for existing in existing_texts:
            similarity = self._calculate_similarity(text, existing)
            if similarity >= threshold:
                return True

        return False

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        使用简单的字符级 Jaccard 相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            float: 相似度 (0-1)
        """
        if not text1 or not text2:
            return 0.0

        # 转换为字符集合
        set1 = set(text1)
        set2 = set(text2)

        # 计算 Jaccard 相似度
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        return intersection / union


# 模块级单例实例
_default_deduplicator: Optional[EvidenceDeduplicator] = None


def get_evidence_deduplicator(
    similarity_threshold: float = EvidenceDeduplicator.DEFAULT_SIMILARITY_THRESHOLD,
    enable_url_dedup: bool = True,
    enable_title_dedup: bool = True,
    enable_content_dedup: bool = True,
) -> EvidenceDeduplicator:
    """
    获取证据去重器单例实例

    Args:
        similarity_threshold: 相似度阈值
        enable_url_dedup: 是否启用 URL 去重
        enable_title_dedup: 是否启用标题去重
        enable_content_dedup: 是否启用内容去重

    Returns:
        EvidenceDeduplicator: 证据去重器实例
    """
    global _default_deduplicator
    if _default_deduplicator is None:
        _default_deduplicator = EvidenceDeduplicator(
            similarity_threshold=similarity_threshold,
            enable_url_dedup=enable_url_dedup,
            enable_title_dedup=enable_title_dedup,
            enable_content_dedup=enable_content_dedup,
        )
    return _default_deduplicator


def deduplicate_evidence(
    evidence_list: List[ProcessedEvidence],
) -> List[ProcessedEvidence]:
    """
    便捷函数：执行证据去重

    Args:
        evidence_list: 处理后的证据列表

    Returns:
        List[ProcessedEvidence]: 去重后的证据列表
    """
    deduplicator = get_evidence_deduplicator()
    return deduplicator.deduplicate(evidence_list)