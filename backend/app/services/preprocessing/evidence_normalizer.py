# -*- coding: utf-8 -*-
"""
EvidenceNormalizer - 证据标准化器

对处理后的证据执行标准化操作：
- 日期标准化
- URL 标准化
- 来源类型标准化
- 内容格式标准化
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

from ..orchestrator.pipeline_state import ProcessedEvidence


class EvidenceNormalizer:
    """
    证据标准化器

    对处理后证据执行标准化，确保数据格式统一，便于后续处理。

    使用方式：
        normalizer = EvidenceNormalizer()
        normalized = normalizer.normalize(processed_evidence)

    Attributes:
        date_patterns: 日期匹配模式列表
        default_date_format: 默认日期格式
    """

    # 常见日期格式模式
    DATE_PATTERNS = [
        # ISO 格式
        (r"(\d{4}-\d{2}-\d{2})", "%Y-%m-%d"),
        (r"(\d{4}/\d{2}/\d{2})", "%Y/%m/%d"),
        # 中文格式
        (r"(\d{4}年\d{1,2}月\d{1,2}日)", None),  # 需要特殊处理
        # 常见格式
        (r"(\d{4}\.\d{2}\.\d{2})", "%Y.%m.%d"),
        (r"(\d{2}-\d{2}-\d{4})", "%m-%d-%Y"),
        (r"(\d{2}/\d{2}/\d{4})", "%m/%d/%Y"),
    ]

    DEFAULT_DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self,
        date_patterns: Optional[List[tuple]] = None,
        default_date_format: str = DEFAULT_DATE_FORMAT,
    ):
        """
        初始化证据标准化器

        Args:
            date_patterns: 自定义日期匹配模式
            default_date_format: 默认日期格式
        """
        self.date_patterns = date_patterns or self.DATE_PATTERNS
        self.default_date_format = default_date_format

    def normalize(self, evidence: ProcessedEvidence) -> ProcessedEvidence:
        """
        标准化单条证据

        标准化流程：
        1. 标准化 URL
        2. 提取并标准化日期
        3. 标准化内容格式

        Args:
            evidence: 处理后的证据

        Returns:
            ProcessedEvidence: 标准化后的证据
        """
        # 标准化 URL
        normalized_url = self._normalize_url(evidence.url)

        # 提取并标准化日期
        normalized_date = self._extract_and_normalize_date(
            evidence.cleaned_content, evidence.metadata
        )

        # 更新元数据
        updated_metadata = {
            **evidence.metadata,
            "normalized_at": datetime.now().isoformat(),
            "url_normalized": normalized_url != evidence.url if evidence.url else False,
        }

        # 创建标准化后的证据
        return ProcessedEvidence(
            evidence_id=evidence.evidence_id,
            raw_evidence_id=evidence.raw_evidence_id,
            source_type=evidence.source_type,
            url=normalized_url,
            title=evidence.title,
            cleaned_content=evidence.cleaned_content,
            normalized_date=normalized_date,
            quality_score=evidence.quality_score,
            relevance_score=evidence.relevance_score,
            metadata=updated_metadata,
        )

    def normalize_batch(
        self, evidence_list: List[ProcessedEvidence]
    ) -> List[ProcessedEvidence]:
        """
        批量标准化证据

        Args:
            evidence_list: 处理后的证据列表

        Returns:
            List[ProcessedEvidence]: 标准化后的证据列表
        """
        return [self.normalize(evidence) for evidence in evidence_list]

    def _normalize_url(self, url: Optional[str]) -> Optional[str]:
        """
        标准化 URL

        Args:
            url: 原始 URL

        Returns:
            Optional[str]: 标准化后的 URL
        """
        if not url:
            return None

        url = url.strip()

        # 添加默认协议
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)

            # 确保有协议
            scheme = parsed.scheme or "https"
            netloc = parsed.netloc.lower()
            path = parsed.path

            # 移除 www 前缀（可选）
            # if netloc.startswith("www."):
            #     netloc = netloc[4:]

            # 重构 URL
            normalized = f"{scheme}://{netloc}{path}"

            # 保留查询参数（移除追踪参数）
            if parsed.query:
                clean_params = self._clean_query_params(parsed.query)
                if clean_params:
                    normalized += f"?{clean_params}"

            return normalized

        except Exception:
            return url

    def _clean_query_params(self, query: str) -> str:
        """
        清理 URL 查询参数

        Args:
            query: 原始查询字符串

        Returns:
            str: 清理后的查询字符串
        """
        tracking_params = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "ref",
            "source",
            "fbclid",
            "gclid",
        }

        if not query:
            return ""

        params = []
        for param in query.split("&"):
            if "=" in param:
                key = param.split("=")[0]
                if key.lower() not in tracking_params:
                    params.append(param)

        return "&".join(params)

    def _extract_and_normalize_date(
        self,
        content: str,
        metadata: dict,
    ) -> Optional[str]:
        """
        从内容和元数据中提取并标准化日期

        优先级：
        1. 元数据中的 publish_date
        2. 内容中提取的日期

        Args:
            content: 文本内容
            metadata: 证据元数据

        Returns:
            Optional[str]: 标准化日期 (YYYY-MM-DD 格式)
        """
        # 首先尝试从元数据获取
        if "publish_date" in metadata:
            date_str = metadata["publish_date"]
            normalized = self._normalize_date_string(date_str)
            if normalized:
                return normalized

        # 从内容中提取日期
        extracted_date = self._extract_date_from_content(content)
        if extracted_date:
            return extracted_date

        return None

    def _extract_date_from_content(self, content: str) -> Optional[str]:
        """
        从内容中提取日期

        Args:
            content: 文本内容

        Returns:
            Optional[str]: 标准化日期
        """
        for pattern, date_format in self.date_patterns:
            match = re.search(pattern, content)
            if match:
                date_str = match.group(1)

                # 中文日期特殊处理
                if date_format is None:
                    return self._parse_chinese_date(date_str)

                try:
                    parsed_date = datetime.strptime(date_str, date_format)
                    return parsed_date.strftime(self.default_date_format)
                except ValueError:
                    continue

        return None

    def _normalize_date_string(self, date_str: str) -> Optional[str]:
        """
        标准化日期字符串

        Args:
            date_str: 原始日期字符串

        Returns:
            Optional[str]: 标准化日期
        """
        if not date_str:
            return None

        # 已经是标准格式
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return date_str

        # 中文日期
        if "年" in date_str:
            return self._parse_chinese_date(date_str)

        # 尝试各种格式
        for pattern, date_format in self.date_patterns:
            if date_format:
                try:
                    parsed_date = datetime.strptime(date_str, date_format)
                    return parsed_date.strftime(self.default_date_format)
                except ValueError:
                    continue

        return None

    def _parse_chinese_date(self, date_str: str) -> Optional[str]:
        """
        解析中文日期格式

        Args:
            date_str: 中文日期字符串，如 "2024年3月15日"

        Returns:
            Optional[str]: 标准化日期
        """
        match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"

        return None


# 模块级单例实例
_default_normalizer: Optional[EvidenceNormalizer] = None


def get_evidence_normalizer(
    default_date_format: str = EvidenceNormalizer.DEFAULT_DATE_FORMAT,
) -> EvidenceNormalizer:
    """
    获取证据标准化器单例实例

    Args:
        default_date_format: 默认日期格式

    Returns:
        EvidenceNormalizer: 证据标准化器实例
    """
    global _default_normalizer
    if _default_normalizer is None:
        _default_normalizer = EvidenceNormalizer(
            default_date_format=default_date_format,
        )
    return _default_normalizer


def normalize_evidence(evidence: ProcessedEvidence) -> ProcessedEvidence:
    """
    便捷函数：标准化单条证据

    Args:
        evidence: 处理后的证据

    Returns:
        ProcessedEvidence: 标准化后的证据
    """
    normalizer = get_evidence_normalizer()
    return normalizer.normalize(evidence)


def normalize_evidence_batch(
    evidence_list: List[ProcessedEvidence],
) -> List[ProcessedEvidence]:
    """
    便捷函数：批量标准化证据

    Args:
        evidence_list: 处理后的证据列表

    Returns:
        List[ProcessedEvidence]: 标准化后的证据列表
    """
    normalizer = get_evidence_normalizer()
    return normalizer.normalize_batch(evidence_list)