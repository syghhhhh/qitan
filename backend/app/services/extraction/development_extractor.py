# -*- coding: utf-8 -*-
"""
DevelopmentExtractor - 近期动态抽取器

从处理后的证据中抽取近期事件候选项，包括：
- 融资事件
- 产品发布
- 战略合作
- 人事变动
- 业务拓展
- 荣誉奖项
- 技术突破
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..orchestrator.pipeline_state import CandidateFact, ProcessedEvidence


class DevelopmentExtractor:
    """
    近期动态抽取器

    从处理后的证据中抽取近期事件候选项。

    使用方式：
        extractor = DevelopmentExtractor()
        facts = extractor.extract(processed_evidence_list)

    Attributes:
        event_type_keywords: 事件类型关键词映射
        date_patterns: 日期匹配模式
    """

    # 事件类型关键词映射
    EVENT_TYPE_KEYWORDS = {
        "financing": {
            "keywords": ["融资", "投资", "融资轮", "A轮", "B轮", "C轮", "D轮",
                        "Pre-A", "Pre-A轮", "天使轮", "种子轮", "战略投资",
                        "融资完成", "获得融资", "领投", "跟投", "融资额"],
            "label": "融资事件",
        },
        "product_launch": {
            "keywords": ["发布", "上线", "推出", "发布新", "新产品", "新功能",
                        "全新产品", "正式发布", "产品发布", "版本更新"],
            "label": "产品发布",
        },
        "partnership": {
            "keywords": ["合作", "战略合作", "签约", "达成合作", "建立合作",
                        "战略伙伴", "合作伙伴", "联合", "携手", "签约仪式"],
            "label": "战略合作",
        },
        "personnel": {
            "keywords": ["任命", "入职", "加盟", "高管", "CEO", "CTO", "CFO",
                        "副总裁", "总经理", "人事变动", "新任", "履新", "离职"],
            "label": "人事变动",
        },
        "expansion": {
            "keywords": ["拓展", "扩张", "新设", "开设", "布局", "进入", "开拓",
                        "新业务", "新市场", "海外", "全国布局", "城市扩张"],
            "label": "业务拓展",
        },
        "award": {
            "keywords": ["获奖", "荣誉", "认证", "殊荣", "奖项", "被评为",
                        "荣膺", "入选", "榜单", "百强", "优秀", "领先"],
            "label": "荣誉奖项",
        },
        "tech_breakthrough": {
            "keywords": ["突破", "技术突破", "专利", "自主研发", "核心技术",
                        "创新技术", "首创", "技术领先", "技术专利"],
            "label": "技术突破",
        },
        "ipo": {
            "keywords": ["上市", "IPO", "挂牌", "登陆", "公开上市",
                        "科创板", "创业板", "主板", "港交所", "纳斯达克"],
            "label": "上市事件",
        },
    }

    # 日期匹配模式
    DATE_PATTERNS = [
        # YYYY年MM月DD日 格式
        (r"(\d{4})年(\d{1,2})月(\d{1,2})日", "%Y年%m月%d日"),
        # YYYY-MM-DD 格式
        (r"(\d{4})-(\d{1,2})-(\d{1,2})", "%Y-%m-%d"),
        # YYYY/MM/DD 格式
        (r"(\d{4})/(\d{1,2})/(\d{1,2})", "%Y/%m/%d"),
        # MM月DD日 格式（当年）
        (r"(\d{1,2})月(\d{1,2})日", None),  # 需要特殊处理
        # X天前 格式
        (r"(\d+)天前", "days_ago"),
        # X周前 格式
        (r"(\d+)周前", "weeks_ago"),
        # 昨天
        (r"昨天", "yesterday"),
        # 前天
        (r"前天", "day_before_yesterday"),
        # 近日、近期
        (r"近日|近期", "recent"),
    ]

    # 无效事件过滤关键词
    IRRELEVANT_KEYWORDS = [
        "广告", "推广", "优惠券", "促销", "折扣",
        "招聘", "求职", "简历",  # 招聘相关单独处理
    ]

    # 最大候选数量
    MAX_CANDIDATES = 20

    def __init__(self, days_threshold: int = 365):
        """
        初始化近期动态抽取器

        Args:
            days_threshold: 天数阈值，超过此天数的事件不视为"近期"，默认365天
        """
        self.days_threshold = days_threshold
        self.current_year = datetime.now().year

    def extract(
        self,
        evidence_list: List[ProcessedEvidence],
        company_name: Optional[str] = None,
    ) -> List[CandidateFact]:
        """
        从证据列表中抽取近期动态候选事实

        抽取流程：
        1. 遍历所有证据，优先处理新闻类证据
        2. 从每条证据中抽取事件类型、日期、摘要
        3. 过滤低相关性和过期事件
        4. 按日期排序返回候选事实

        Args:
            evidence_list: 处理后的证据列表
            company_name: 企业名称（用于相关性判断）

        Returns:
            List[CandidateFact]: 候选事实列表
        """
        facts: List[CandidateFact] = []

        if not evidence_list:
            return facts

        # 按来源类型分组，新闻优先
        news_evidence = [e for e in evidence_list if e.source_type == "news"]
        other_evidence = [e for e in evidence_list if e.source_type != "news"]

        # 先处理新闻证据
        for evidence in news_evidence:
            extracted_facts = self._extract_from_evidence(
                evidence, company_name, priority=1.0
            )
            facts.extend(extracted_facts)

        # 再处理其他证据
        for evidence in other_evidence:
            extracted_facts = self._extract_from_evidence(
                evidence, company_name, priority=0.7
            )
            facts.extend(extracted_facts)

        # 去重并排序
        facts = self._deduplicate_and_sort(facts)

        # 限制数量
        return facts[: self.MAX_CANDIDATES]

    def _extract_from_evidence(
        self,
        evidence: ProcessedEvidence,
        company_name: Optional[str],
        priority: float = 1.0,
    ) -> List[CandidateFact]:
        """
        从单条证据中抽取近期动态候选事实

        Args:
            evidence: 处理后的证据
            company_name: 企业名称
            priority: 来源优先级权重

        Returns:
            List[CandidateFact]: 候选事实列表
        """
        facts: List[CandidateFact] = []
        content = evidence.cleaned_content
        title = evidence.title

        # 检查是否为无关内容
        if self._is_irrelevant(content, title):
            return facts

        # 抽取事件类型
        event_types = self._extract_event_types(content + " " + title)

        if not event_types:
            return facts

        # 抽取日期
        event_date = self._extract_date(content, evidence.normalized_date)

        # 检查日期是否在近期范围内
        if event_date and not self._is_recent(event_date):
            return facts

        # 生成摘要
        summary = self._generate_summary(content, title, event_types)

        # 计算置信度
        confidence = self._calculate_confidence(
            event_types, event_date, company_name, content, priority
        )

        # 创建候选事实
        for event_type in event_types:
            fact = CandidateFact(
                fact_id=f"fact_{uuid4().hex[:12]}",
                fact_type="recent_development.event",
                fact_data={
                    "event_type": event_type,
                    "event_type_label": self.EVENT_TYPE_KEYWORDS.get(event_type, {}).get("label", event_type),
                    "date": event_date.isoformat() if event_date else None,
                    "date_text": self._extract_date_text(content),
                    "summary": summary,
                    "title": title,
                    "source_url": evidence.url,
                },
                source_evidence_ids=[evidence.evidence_id],
                confidence=confidence,
            )
            facts.append(fact)

        return facts

    def _extract_event_types(self, text: str) -> List[str]:
        """
        抽取事件类型

        Args:
            text: 文本内容

        Returns:
            List[str]: 事件类型列表
        """
        found_types: List[str] = []

        for event_type, config in self.EVENT_TYPE_KEYWORDS.items():
            keywords = config["keywords"]
            for keyword in keywords:
                if keyword in text:
                    found_types.append(event_type)
                    break

        return list(dict.fromkeys(found_types))  # 去重保序

    def _extract_date(
        self, content: str, normalized_date: Optional[str]
    ) -> Optional[datetime]:
        """
        抽取事件日期

        优先使用已标准化的日期，否则从内容中提取。

        Args:
            content: 文本内容
            normalized_date: 已标准化的日期字符串

        Returns:
            Optional[datetime]: 事件日期
        """
        # 优先使用已标准化的日期
        if normalized_date:
            try:
                return datetime.fromisoformat(normalized_date.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # 从内容中提取日期
        now = datetime.now()

        # 尝试各种日期模式
        for pattern, format_type in self.DATE_PATTERNS:
            match = re.search(pattern, content)
            if match:
                try:
                    if format_type == "%Y年%m月%d日":
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        return datetime(year, month, day)
                    elif format_type == "%Y-%m-%d":
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        return datetime(year, month, day)
                    elif format_type == "%Y/%m/%d":
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        return datetime(year, month, day)
                    elif format_type is None and "月" in pattern:
                        # MM月DD日 格式，使用当年
                        month, day = int(match.group(1)), int(match.group(2))
                        return datetime(self.current_year, month, day)
                    elif format_type == "days_ago":
                        days = int(match.group(1))
                        return now - timedelta(days=days)
                    elif format_type == "weeks_ago":
                        weeks = int(match.group(1))
                        return now - timedelta(weeks=weeks)
                    elif format_type == "yesterday":
                        return now - timedelta(days=1)
                    elif format_type == "day_before_yesterday":
                        return now - timedelta(days=2)
                    elif format_type == "recent":
                        return now - timedelta(days=7)  # 近期默认7天前
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_date_text(self, content: str) -> Optional[str]:
        """
        提取日期原文

        Args:
            content: 文本内容

        Returns:
            Optional[str]: 日期原文
        """
        for pattern, _ in self.DATE_PATTERNS:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        return None

    def _is_recent(self, event_date: datetime) -> bool:
        """
        检查日期是否在近期范围内

        Args:
            event_date: 事件日期

        Returns:
            bool: 是否在近期范围内
        """
        now = datetime.now()
        threshold_date = now - timedelta(days=self.days_threshold)
        return event_date >= threshold_date

    def _is_irrelevant(self, content: str, title: str) -> bool:
        """
        检查内容是否为无关内容

        Args:
            content: 文本内容
            title: 标题

        Returns:
            bool: 是否为无关内容
        """
        text = content + " " + title
        for keyword in self.IRRELEVANT_KEYWORDS:
            if keyword in text:
                return True
        return False

    def _generate_summary(
        self,
        content: str,
        title: str,
        event_types: List[str],
    ) -> str:
        """
        生成事件摘要

        Args:
            content: 文本内容
            title: 标题
            event_types: 事件类型列表

        Returns:
            str: 事件摘要
        """
        # 优先使用标题作为摘要
        if title and len(title) >= 10:
            # 清理标题
            summary = re.sub(r"【[^】]+】", "", title)  # 移除【】标签
            summary = re.sub(r"[|｜].*$", "", summary)  # 移除 | 之后的内容
            summary = summary.strip()
            if len(summary) >= 10:
                return summary[:200]  # 限制长度

        # 从内容中提取摘要
        # 寻找包含事件关键词的句子
        sentences = re.split(r"[。！？\n]", content)
        relevant_sentences = []

        for event_type in event_types:
            keywords = self.EVENT_TYPE_KEYWORDS.get(event_type, {}).get("keywords", [])
            for sentence in sentences:
                if any(kw in sentence for kw in keywords):
                    relevant_sentences.append(sentence.strip())
                    break

        if relevant_sentences:
            summary = relevant_sentences[0]
            return summary[:200] if len(summary) > 200 else summary

        # 兜底：取内容前200字符
        return content[:200] if len(content) > 200 else content

    def _calculate_confidence(
        self,
        event_types: List[str],
        event_date: Optional[datetime],
        company_name: Optional[str],
        content: str,
        priority: float,
    ) -> float:
        """
        计算置信度

        Args:
            event_types: 事件类型列表
            event_date: 事件日期
            company_name: 企业名称
            content: 文本内容
            priority: 来源优先级

        Returns:
            float: 置信度 (0-1)
        """
        confidence = 0.5  # 基础置信度

        # 事件类型加分
        if len(event_types) == 1:
            confidence += 0.1  # 单一类型更可靠
        elif len(event_types) > 3:
            confidence -= 0.1  # 类型过多可能不够精准

        # 日期加分
        if event_date:
            confidence += 0.15

            # 越近的事件置信度越高
            now = datetime.now()
            days_diff = (now - event_date).days
            if days_diff <= 30:
                confidence += 0.1
            elif days_diff <= 90:
                confidence += 0.05

        # 企业名称相关性加分
        if company_name and company_name in content:
            confidence += 0.1

        # 内容长度加分
        if len(content) >= 200:
            confidence += 0.05

        # 应用优先级权重
        confidence = confidence * priority

        # 确保在 0-1 范围内
        return min(max(confidence, 0.0), 1.0)

    def _deduplicate_and_sort(self, facts: List[CandidateFact]) -> List[CandidateFact]:
        """
        去重并按日期排序

        Args:
            facts: 候选事实列表

        Returns:
            List[CandidateFact]: 去重排序后的列表
        """
        # 按摘要去重
        seen_summaries: set = set()
        unique_facts: List[CandidateFact] = []

        for fact in facts:
            summary = fact.fact_data.get("summary", "")
            # 使用摘要前50字符作为去重键
            summary_key = summary[:50] if summary else ""

            if summary_key and summary_key not in seen_summaries:
                seen_summaries.add(summary_key)
                unique_facts.append(fact)
            elif not summary_key:
                unique_facts.append(fact)

        # 按日期降序排序（最近的在前）
        def sort_key(fact: CandidateFact) -> str:
            date_str = fact.fact_data.get("date")
            if date_str:
                return date_str
            return "0000-00-00"  # 无日期的排最后

        unique_facts.sort(key=sort_key, reverse=True)

        return unique_facts


# 模块级单例实例
_default_extractor: Optional[DevelopmentExtractor] = None


def get_development_extractor(days_threshold: int = 365) -> DevelopmentExtractor:
    """
    获取近期动态抽取器单例实例

    Args:
        days_threshold: 天数阈值

    Returns:
        DevelopmentExtractor: 近期动态抽取器实例
    """
    global _default_extractor
    if _default_extractor is None:
        _default_extractor = DevelopmentExtractor(days_threshold=days_threshold)
    return _default_extractor


def extract_developments(
    evidence_list: List[ProcessedEvidence],
    company_name: Optional[str] = None,
) -> List[CandidateFact]:
    """
    便捷函数：从证据列表中抽取近期动态候选事实

    Args:
        evidence_list: 处理后的证据列表
        company_name: 企业名称

    Returns:
        List[CandidateFact]: 候选事实列表
    """
    extractor = get_development_extractor()
    return extractor.extract(evidence_list, company_name)