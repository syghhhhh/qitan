# -*- coding: utf-8 -*-
"""
CompanyProfileExtractor - 企业画像抽取器

从处理后的证据中抽取企业画像候选事实，包括：
- 公司名称、简称
- 行业标签
- 企业类型
- 成立时间
- 总部所在地
- 主营业务
- 主要产品或服务
- 规模估计
- 业务覆盖区域
- 官网地址
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..orchestrator.pipeline_state import CandidateFact, ProcessedEvidence


class CompanyProfileExtractor:
    """
    企业画像抽取器

    从处理后的证据中抽取企业画像相关候选事实。

    使用方式：
        extractor = CompanyProfileExtractor()
        facts = extractor.extract(processed_evidence_list, resolved_company_name)

    Attributes:
        industry_keywords: 行业关键词映射
        company_type_keywords: 企业类型关键词映射
        size_patterns: 规模匹配模式
    """

    # 行业关键词映射
    INDUSTRY_KEYWORDS = {
        "科技": ["科技", "软件", "信息技术", "互联网", "网络", "数字化", "智能", "AI", "人工智能"],
        "金融": ["金融", "投资", "基金", "证券", "银行", "保险", "资产管理"],
        "制造": ["制造", "机械", "工业", "设备", "汽车", "电子", "材料", "装备"],
        "教育": ["教育", "培训", "学校", "学院", "在线教育", "知识付费"],
        "医疗": ["医疗", "医药", "健康", "生物", "医疗器械", "医院"],
        "零售": ["零售", "电商", "消费", "商贸", "超市", "连锁"],
        "物流": ["物流", "供应链", "仓储", "运输", "快递"],
        "房地产": ["房地产", "置业", "物业", "建筑"],
        "能源": ["能源", "电力", "新能源", "石油", "光伏", "风电"],
        "咨询": ["咨询", "管理咨询", "战略咨询", "人力资源"],
    }

    # 企业类型关键词映射
    COMPANY_TYPE_KEYWORDS = {
        "民营企业": ["民营", "私营", "有限公司", "有限责任公司"],
        "国有企业": ["国有", "央企", "国企", "集团"],
        "外资企业": ["外资", "外企", "合资", "跨国"],
        "上市公司": ["上市", "股份公司", "A股", "港股", "纳斯达克"],
        "创业公司": ["创业", "初创", "孵化器"],
    }

    # 规模匹配模式
    SIZE_PATTERNS = [
        (r"(\d+)-(\d+)人", "{0}-{1}人"),
        (r"(\d+)人以上", "{0}人以上"),
        (r"(\d+)人以下", "{0}人以下"),
        (r"(\d+)人左右", "约{0}人"),
        (r"(\d+)-(\d+)", "{0}-{1}人"),  # 纯数字范围
    ]

    # 规模等级映射
    SIZE_LEVELS = {
        "1-50人": "1-50人",
        "50-150人": "50-150人",
        "150-500人": "150-500人",
        "500-1000人": "500-1000人",
        "1000-5000人": "1000-5000人",
        "5000人以上": "5000人以上",
    }

    def __init__(self):
        """初始化企业画像抽取器"""
        pass

    def extract(
        self,
        evidence_list: List[ProcessedEvidence],
        resolved_company_name: Optional[str] = None,
    ) -> List[CandidateFact]:
        """
        从证据列表中抽取企业画像候选事实

        抽取流程：
        1. 遍历所有证据，按来源类型分类
        2. 从官网证据中抽取基础信息
        3. 从新闻证据中补充信息
        4. 合并相同字段的候选事实

        Args:
            evidence_list: 处理后的证据列表
            resolved_company_name: 已确认的企业名称（用于置信度调整）

        Returns:
            List[CandidateFact]: 候选事实列表
        """
        facts: List[CandidateFact] = []

        if not evidence_list:
            return facts

        # 按来源类型分组
        website_evidence = [e for e in evidence_list if e.source_type == "website"]
        news_evidence = [e for e in evidence_list if e.source_type == "news"]
        other_evidence = [e for e in evidence_list if e.source_type not in ["website", "news"]]

        # 优先从官网证据抽取
        for evidence in website_evidence:
            extracted_facts = self._extract_from_evidence(
                evidence, resolved_company_name, priority=1.0
            )
            facts.extend(extracted_facts)

        # 从新闻证据补充
        for evidence in news_evidence:
            extracted_facts = self._extract_from_evidence(
                evidence, resolved_company_name, priority=0.8
            )
            facts.extend(extracted_facts)

        # 从其他证据补充
        for evidence in other_evidence:
            extracted_facts = self._extract_from_evidence(
                evidence, resolved_company_name, priority=0.6
            )
            facts.extend(extracted_facts)

        return facts

    def _extract_from_evidence(
        self,
        evidence: ProcessedEvidence,
        resolved_company_name: Optional[str],
        priority: float = 1.0,
    ) -> List[CandidateFact]:
        """
        从单条证据中抽取企业画像候选事实

        Args:
            evidence: 处理后的证据
            resolved_company_name: 已确认的企业名称
            priority: 来源优先级权重

        Returns:
            List[CandidateFact]: 候选事实列表
        """
        facts: List[CandidateFact] = []
        content = evidence.cleaned_content
        title = evidence.title

        # 抽取公司名称
        name_fact = self._extract_company_name(content, title, evidence, resolved_company_name)
        if name_fact:
            name_fact.confidence = min(1.0, name_fact.confidence * priority)
            facts.append(name_fact)

        # 抽取行业标签
        industry_fact = self._extract_industry(content, evidence)
        if industry_fact:
            industry_fact.confidence = min(1.0, industry_fact.confidence * priority)
            facts.append(industry_fact)

        # 抽取企业类型
        type_fact = self._extract_company_type(content, evidence)
        if type_fact:
            type_fact.confidence = min(1.0, type_fact.confidence * priority)
            facts.append(type_fact)

        # 抽取成立年份
        founded_fact = self._extract_founded_year(content, evidence)
        if founded_fact:
            founded_fact.confidence = min(1.0, founded_fact.confidence * priority)
            facts.append(founded_fact)

        # 抽取总部所在地
        hq_fact = self._extract_headquarters(content, evidence)
        if hq_fact:
            hq_fact.confidence = min(1.0, hq_fact.confidence * priority)
            facts.append(hq_fact)

        # 抽取主营业务
        business_fact = self._extract_business_scope(content, evidence)
        if business_fact:
            business_fact.confidence = min(1.0, business_fact.confidence * priority)
            facts.append(business_fact)

        # 抽取产品或服务
        product_fact = self._extract_products(content, evidence)
        if product_fact:
            product_fact.confidence = min(1.0, product_fact.confidence * priority)
            facts.append(product_fact)

        # 抽取规模
        size_fact = self._extract_size(content, evidence)
        if size_fact:
            size_fact.confidence = min(1.0, size_fact.confidence * priority)
            facts.append(size_fact)

        # 抽取官网地址
        website_fact = self._extract_website(content, evidence)
        if website_fact:
            website_fact.confidence = min(1.0, website_fact.confidence * priority)
            facts.append(website_fact)

        return facts

    def _extract_company_name(
        self,
        content: str,
        title: str,
        evidence: ProcessedEvidence,
        resolved_company_name: Optional[str],
    ) -> Optional[CandidateFact]:
        """
        抽取公司名称

        优先使用已确认的企业名称，否则从内容中提取。
        """
        # 如果已有确认的企业名称，直接使用
        if resolved_company_name:
            return CandidateFact(
                fact_id=f"fact_{uuid4().hex[:12]}",
                fact_type="company_profile.company_name",
                fact_data={"value": resolved_company_name},
                source_evidence_ids=[evidence.evidence_id],
                confidence=0.95,
            )

        # 从标题或内容中提取公司名称
        # 匹配"有限公司"、"股份有限公司"等后缀
        patterns = [
            r"([^\s,，。；;]+?(?:有限公司|股份有限公司|集团|科技|信息|网络|软件|互联网))",
        ]

        for pattern in patterns:
            match = re.search(pattern, title + " " + content)
            if match:
                company_name = match.group(1).strip()
                # 清理常见的前缀
                company_name = re.sub(r"^(关于|公告|新闻|报道)[：:]*", "", company_name)

                return CandidateFact(
                    fact_id=f"fact_{uuid4().hex[:12]}",
                    fact_type="company_profile.company_name",
                    fact_data={"value": company_name},
                    source_evidence_ids=[evidence.evidence_id],
                    confidence=0.7,
                )

        return None

    def _extract_industry(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取行业标签"""
        found_industries: List[str] = []

        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content:
                    found_industries.append(industry)
                    break

        if not found_industries:
            return None

        # 去重
        unique_industries = list(dict.fromkeys(found_industries))

        return CandidateFact(
            fact_id=f"fact_{uuid4().hex[:12]}",
            fact_type="company_profile.industry",
            fact_data={"values": unique_industries},
            source_evidence_ids=[evidence.evidence_id],
            confidence=0.6 if len(unique_industries) == 1 else 0.5,
        )

    def _extract_company_type(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取企业类型"""
        for company_type, keywords in self.COMPANY_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content:
                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.company_type",
                        fact_data={"value": company_type},
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.7,
                    )

        return None

    def _extract_founded_year(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取成立年份"""
        # 匹配"成立于XXXX年"、"创办于XXXX年"等模式
        patterns = [
            r"(?:成立于|创办于|创立于|建立于|成立于)(\d{4})年",
            r"(\d{4})年(?:成立|创办|创立|建立)",
            r"成立于(\d{4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                year = int(match.group(1))
                if 1980 <= year <= datetime.now().year:
                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.founded_year",
                        fact_data={"value": year},
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.8,
                    )

        return None

    def _extract_headquarters(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取总部所在地"""
        # 常见城市列表
        cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都",
            "武汉", "西安", "重庆", "天津", "青岛", "大连", "厦门", "宁波",
            "无锡", "长沙", "郑州", "福州", "济南", "合肥", "石家庄",
        ]

        # 匹配模式
        patterns = [
            r"总部[位位]?于([^\s,，。；;]+)",
            r"总部[在]([^\s,，。；;]+)",
            r"位于([^\s,，。；;]+)(?:市|区)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                location = match.group(1).strip()
                # 检查是否包含有效城市名
                for city in cities:
                    if city in location:
                        return CandidateFact(
                            fact_id=f"fact_{uuid4().hex[:12]}",
                            fact_type="company_profile.headquarters",
                            fact_data={"value": city},
                            source_evidence_ids=[evidence.evidence_id],
                            confidence=0.7,
                        )

        # 直接查找城市名（较低置信度）
        for city in cities:
            if city in content:
                # 检查是否在总部相关上下文中
                context_window = 50
                city_pos = content.find(city)
                context_start = max(0, city_pos - context_window)
                context = content[context_start:city_pos + len(city)]
                if "总部" in context or "位于" in context or "总部位于" in context:
                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.headquarters",
                        fact_data={"value": city},
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.6,
                    )

        return None

    def _extract_business_scope(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取主营业务范围"""
        # 匹配模式
        patterns = [
            r"主营业务[：:](.+?)(?:。|；|;|$)",
            r"经营范围[：:](.+?)(?:。|；|;|$)",
            r"主要业务[：:](.+?)(?:。|；|;|$)",
            r"专注于(.+?)(?:领域|业务|行业)",
            r"从事(.+?)(?:业务|行业|领域)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                business_text = match.group(1).strip()
                # 分割多个业务
                businesses = re.split(r"[,，、和与及]", business_text)
                businesses = [b.strip() for b in businesses if b.strip() and len(b.strip()) > 2]

                if businesses:
                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.business_scope",
                        fact_data={"values": businesses[:5]},  # 最多取5个
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.65,
                    )

        return None

    def _extract_products(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取主要产品或服务"""
        # 匹配模式
        patterns = [
            r"主要产品[：:](.+?)(?:。|；|;|$)",
            r"核心产品[：:](.+?)(?:。|；|;|$)",
            r"产品包括[：:]?(.+?)(?:。|；|;|$)",
            r"提供(.+?)(?:服务|产品|解决方案)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                product_text = match.group(1).strip()
                # 分割多个产品
                products = re.split(r"[,，、和与及]", product_text)
                products = [p.strip() for p in products if p.strip() and len(p.strip()) > 2]

                if products:
                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.main_products_or_services",
                        fact_data={"values": products[:5]},  # 最多取5个
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.6,
                    )

        return None

    def _extract_size(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取员工规模"""
        # 匹配规模模式
        for pattern, _ in self.SIZE_PATTERNS:
            match = re.search(pattern, content)
            if match:
                groups = match.groups()

                # 根据匹配结果判断规模
                if len(groups) == 2:
                    min_size = int(groups[0])
                    max_size = int(groups[1])

                    # 映射到标准规模等级
                    size_level = self._map_to_size_level(min_size, max_size)

                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.estimated_size",
                        fact_data={
                            "value": size_level,
                            "raw": f"{min_size}-{max_size}人",
                        },
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.7,
                    )
                elif len(groups) == 1:
                    size = int(groups[0])
                    size_level = self._map_to_size_level(size, size)

                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.estimated_size",
                        fact_data={
                            "value": size_level,
                            "raw": f"{size}人",
                        },
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.65,
                    )

        # 关键词匹配
        size_keywords = {
            "小型": ["小型企业", "小微企业", "创业公司"],
            "中型": ["中型企业", "成长型企业"],
            "大型": ["大型企业", "龙头企业", "行业巨头"],
        }

        for level, keywords in size_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return CandidateFact(
                        fact_id=f"fact_{uuid4().hex[:12]}",
                        fact_type="company_profile.estimated_size",
                        fact_data={"value": f"{level}企业"},
                        source_evidence_ids=[evidence.evidence_id],
                        confidence=0.5,
                    )

        return None

    def _map_to_size_level(self, min_size: int, max_size: int) -> str:
        """将具体人数映射到规模等级"""
        avg_size = (min_size + max_size) / 2

        if avg_size < 50:
            return "1-50人"
        elif avg_size < 150:
            return "50-150人"
        elif avg_size < 500:
            return "150-500人"
        elif avg_size < 1000:
            return "500-1000人"
        elif avg_size < 5000:
            return "1000-5000人"
        else:
            return "5000人以上"

    def _extract_website(
        self,
        content: str,
        evidence: ProcessedEvidence,
    ) -> Optional[CandidateFact]:
        """抽取官网地址"""
        # 如果证据本身有 URL，使用它
        if evidence.url and evidence.source_type == "website":
            return CandidateFact(
                fact_id=f"fact_{uuid4().hex[:12]}",
                fact_type="company_profile.official_website",
                fact_data={"value": evidence.url},
                source_evidence_ids=[evidence.evidence_id],
                confidence=0.9,
            )

        # 从内容中提取 URL
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        match = re.search(url_pattern, content)
        if match:
            url = match.group(0)
            # 清理 URL 结尾的标点
            url = re.sub(r'[.,;:!?)\]}>]+$', '', url)

            return CandidateFact(
                fact_id=f"fact_{uuid4().hex[:12]}",
                fact_type="company_profile.official_website",
                fact_data={"value": url},
                source_evidence_ids=[evidence.evidence_id],
                confidence=0.6,
            )

        return None


# 模块级单例实例
_default_extractor: Optional[CompanyProfileExtractor] = None


def get_company_profile_extractor() -> CompanyProfileExtractor:
    """
    获取企业画像抽取器单例实例

    Returns:
        CompanyProfileExtractor: 企业画像抽取器实例
    """
    global _default_extractor
    if _default_extractor is None:
        _default_extractor = CompanyProfileExtractor()
    return _default_extractor


def extract_company_profile(
    evidence_list: List[ProcessedEvidence],
    resolved_company_name: Optional[str] = None,
) -> List[CandidateFact]:
    """
    便捷函数：从证据列表中抽取企业画像候选事实

    Args:
        evidence_list: 处理后的证据列表
        resolved_company_name: 已确认的企业名称

    Returns:
        List[CandidateFact]: 候选事实列表
    """
    extractor = get_company_profile_extractor()
    return extractor.extract(evidence_list, resolved_company_name)