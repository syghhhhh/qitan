# -*- coding: utf-8 -*-
"""
EvidenceCleaner - 证据清洗器

对原始证据执行清洗操作：
- 移除 HTML 标签
- 清理多余空白字符
- 移除无效字符
- 过滤低质量内容
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..orchestrator.pipeline_state import ProcessedEvidence, RawEvidence


class EvidenceCleaner:
    """
    证据清洗器

    对原始证据执行基础清洗操作，提高内容质量。

    使用方式：
        cleaner = EvidenceCleaner()
        cleaned = cleaner.clean(raw_evidence)

    Attributes:
        min_content_length: 最小内容长度
        max_content_length: 最大内容长度
    """

    # 默认配置
    DEFAULT_MIN_CONTENT_LENGTH = 20
    DEFAULT_MAX_CONTENT_LENGTH = 50000

    def __init__(
        self,
        min_content_length: int = DEFAULT_MIN_CONTENT_LENGTH,
        max_content_length: int = DEFAULT_MAX_CONTENT_LENGTH,
    ):
        """
        初始化证据清洗器

        Args:
            min_content_length: 最小有效内容长度，低于此值的内容视为低质量
            max_content_length: 最大内容长度，超出部分将被截断
        """
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length

    def clean(self, evidence: RawEvidence) -> Optional[ProcessedEvidence]:
        """
        清洗单条原始证据

        清洗流程：
        1. 移除 HTML 标签
        2. 清理空白字符
        3. 移除无效字符
        4. 截断过长内容
        5. 质量评估

        Args:
            evidence: 原始证据

        Returns:
            ProcessedEvidence: 清洗后的证据，如内容无效则返回 None
        """
        # 清洗内容
        cleaned_content = self._clean_content(evidence.content)

        # 质量检查
        if not self._is_valid_content(cleaned_content):
            return None

        # 清洗标题
        cleaned_title = self._clean_title(evidence.title)

        # 计算质量评分
        quality_score = self._calculate_quality_score(
            cleaned_content, evidence.source_type
        )

        # 创建处理后证据
        return ProcessedEvidence(
            evidence_id=f"proc_{uuid4().hex[:12]}",
            raw_evidence_id=evidence.evidence_id,
            source_type=evidence.source_type,
            url=evidence.url,
            title=cleaned_title,
            cleaned_content=cleaned_content,
            normalized_date=None,  # 由 normalizer 处理
            quality_score=quality_score,
            relevance_score=0.5,  # 默认值，由 ranker 调整
            metadata={
                **evidence.metadata,
                "cleaned_at": datetime.now().isoformat(),
                "original_content_length": len(evidence.content),
                "cleaned_content_length": len(cleaned_content),
            },
        )

    def clean_batch(
        self, evidence_list: List[RawEvidence]
    ) -> List[ProcessedEvidence]:
        """
        批量清洗证据

        Args:
            evidence_list: 原始证据列表

        Returns:
            List[ProcessedEvidence]: 清洗后的证据列表（过滤掉无效内容）
        """
        results = []
        for evidence in evidence_list:
            processed = self.clean(evidence)
            if processed:
                results.append(processed)
        return results

    def _clean_content(self, content: str) -> str:
        """
        清洗内容

        Args:
            content: 原始内容

        Returns:
            str: 清洗后的内容
        """
        if not content:
            return ""

        # 移除 HTML 标签
        cleaned = re.sub(r"<[^>]+>", " ", content)

        # 移除 HTML 实体
        cleaned = self._decode_html_entities(cleaned)

        # 清理多余空白
        cleaned = re.sub(r"\s+", " ", cleaned)

        # 移除首尾空白
        cleaned = cleaned.strip()

        # 截断过长内容
        if len(cleaned) > self.max_content_length:
            cleaned = cleaned[: self.max_content_length] + "..."

        return cleaned

    def _clean_title(self, title: str) -> str:
        """
        清洗标题

        Args:
            title: 原始标题

        Returns:
            str: 清洗后的标题
        """
        if not title:
            return ""

        # 移除 HTML 标签
        cleaned = re.sub(r"<[^>]+>", " ", title)

        # 清理空白
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # 移除常见的前后缀符号
        cleaned = cleaned.strip("-_|:：")

        return cleaned

    def _decode_html_entities(self, text: str) -> str:
        """
        解码 HTML 实体

        Args:
            text: 包含 HTML 实体的文本

        Returns:
            str: 解码后的文本
        """
        entities = {
            "&nbsp;": " ",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&apos;": "'",
        }

        for entity, char in entities.items():
            text = text.replace(entity, char)

        # 解码数字实体
        text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
        text = re.sub(
            r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text
        )

        return text

    def _is_valid_content(self, content: str) -> bool:
        """
        检查内容是否有效

        Args:
            content: 清洗后的内容

        Returns:
            bool: 内容是否有效
        """
        if not content or len(content) < self.min_content_length:
            return False

        # 检查是否全部为空白或特殊字符
        if re.match(r"^[\s\W]+$", content):
            return False

        return True

    def _calculate_quality_score(
        self, content: str, source_type: str
    ) -> float:
        """
        计算内容质量评分

        评分因素：
        - 内容长度
        - 信息密度（非空白字符比例）
        - 来源类型权重

        Args:
            content: 清洗后的内容
            source_type: 来源类型

        Returns:
            float: 质量评分 (0-1)
        """
        score = 0.5  # 基础分

        # 内容长度加分
        content_length = len(content)
        if content_length >= 500:
            score += 0.15
        elif content_length >= 200:
            score += 0.1
        elif content_length >= 100:
            score += 0.05

        # 信息密度加分（非空白字符比例）
        non_whitespace_ratio = len(content.replace(" ", "")) / content_length
        score += non_whitespace_ratio * 0.15

        # 来源类型权重
        source_weights = {
            "website": 0.1,
            "news": 0.15,
            "user_supplied": 0.1,
        }
        score += source_weights.get(source_type, 0.05)

        # 确保评分在 0-1 范围内
        return min(max(score, 0.0), 1.0)


# 模块级单例实例
_default_cleaner: Optional[EvidenceCleaner] = None


def get_evidence_cleaner(
    min_content_length: int = EvidenceCleaner.DEFAULT_MIN_CONTENT_LENGTH,
    max_content_length: int = EvidenceCleaner.DEFAULT_MAX_CONTENT_LENGTH,
) -> EvidenceCleaner:
    """
    获取证据清洗器单例实例

    Args:
        min_content_length: 最小内容长度
        max_content_length: 最大内容长度

    Returns:
        EvidenceCleaner: 证据清洗器实例
    """
    global _default_cleaner
    if _default_cleaner is None:
        _default_cleaner = EvidenceCleaner(
            min_content_length=min_content_length,
            max_content_length=max_content_length,
        )
    return _default_cleaner


def clean_evidence(evidence: RawEvidence) -> Optional[ProcessedEvidence]:
    """
    便捷函数：清洗单条证据

    Args:
        evidence: 原始证据

    Returns:
        ProcessedEvidence: 清洗后的证据
    """
    cleaner = get_evidence_cleaner()
    return cleaner.clean(evidence)


def clean_evidence_batch(
    evidence_list: List[RawEvidence],
) -> List[ProcessedEvidence]:
    """
    便捷函数：批量清洗证据

    Args:
        evidence_list: 原始证据列表

    Returns:
        List[ProcessedEvidence]: 清洗后的证据列表
    """
    cleaner = get_evidence_cleaner()
    return cleaner.clean_batch(evidence_list)