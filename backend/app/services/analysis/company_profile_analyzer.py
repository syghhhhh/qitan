# -*- coding: utf-8 -*-
"""
CompanyProfileAnalyzer - 企业画像分析器

对候选事实进行归并、冲突消解和结果结构化，生成统一 company_profile 输出。

主要功能：
1. 按字段类型分组候选事实
2. 合并相同字段的多个来源值
3. 处理冲突（取置信度最高或来源优先级最高）
4. 生成结构化 CompanyProfile 输出
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...schemas import CompanyProfile
from ..orchestrator.pipeline_state import AnalysisResult, CandidateFact


class CompanyProfileAnalyzer:
    """
    企业画像分析器

    对企业画像候选事实进行归并、冲突消解和结果结构化。

    使用方式：
        analyzer = CompanyProfileAnalyzer()
        result = analyzer.analyze(candidate_facts, resolved_company_name)

    Attributes:
        source_priority: 来源类型优先级配置
        field_conflict_strategies: 字段冲突处理策略
    """

    # 来源类型优先级（数值越大优先级越高）
    SOURCE_PRIORITY = {
        "website": 1.0,
        "news": 0.8,
        "job": 0.7,
        "user_input": 1.0,
        "other": 0.5,
    }

    # 字段冲突处理策略
    # merge: 合并所有值（去重）
    # highest_confidence: 取置信度最高的值
    # highest_priority: 取来源优先级最高的值
    FIELD_CONFLICT_STRATEGIES = {
        "company_name": "highest_confidence",
        "industry": "merge",
        "company_type": "highest_confidence",
        "founded_year": "highest_confidence",
        "headquarters": "highest_confidence",
        "business_scope": "merge",
        "main_products_or_services": "merge",
        "estimated_size": "highest_confidence",
        "official_website": "highest_confidence",
        "region_coverage": "merge",
    }

    # 默认值配置
    DEFAULT_VALUES = {
        "company_type": "民营企业",
        "estimated_size": "100-500人",
    }

    def __init__(self):
        """初始化企业画像分析器"""
        pass

    def analyze(
        self,
        candidate_facts: List[CandidateFact],
        resolved_company_name: Optional[str] = None,
        source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> AnalysisResult:
        """
        分析企业画像候选事实，生成统一的企业画像输出

        分析流程：
        1. 筛选 company_profile 类型的候选事实
        2. 按字段类型分组
        3. 对每个字段执行归并和冲突消解
        4. 组装最终 CompanyProfile

        Args:
            candidate_facts: 候选事实列表
            resolved_company_name: 已确认的企业名称（用于覆盖抽取结果）
            source_evidence_map: 证据来源映射（用于获取来源类型优先级）

        Returns:
            AnalysisResult: 包含 CompanyProfile 的分析结果
        """
        # 筛选企业画像相关候选事实
        profile_facts = [
            f for f in candidate_facts
            if f.fact_type.startswith("company_profile.")
        ]

        # 按字段类型分组
        facts_by_field: Dict[str, List[CandidateFact]] = defaultdict(list)
        for fact in profile_facts:
            # 提取字段名，如 "company_profile.company_name" -> "company_name"
            field_name = fact.fact_type.split(".", 1)[1] if "." in fact.fact_type else fact.fact_type
            facts_by_field[field_name].append(fact)

        # 计算每个字段的来源优先级权重
        field_values: Dict[str, Any] = {}
        source_fact_ids: List[str] = []
        confidence_scores: Dict[str, float] = {}

        for field_name, facts in facts_by_field.items():
            value, confidence, fact_ids = self._resolve_field(
                field_name, facts, source_evidence_map
            )
            if value is not None:
                field_values[field_name] = value
                confidence_scores[field_name] = confidence
                source_fact_ids.extend(fact_ids)

        # 使用已确认的企业名称覆盖
        if resolved_company_name:
            field_values["company_name"] = resolved_company_name
            confidence_scores["company_name"] = 0.95

        # 生成企业简称
        if "company_name" in field_values and "short_name" not in field_values:
            company_name = field_values["company_name"]
            field_values["short_name"] = company_name[:4] if len(company_name) >= 4 else company_name

        # 填充默认值
        for field, default_value in self.DEFAULT_VALUES.items():
            if field not in field_values:
                field_values[field] = default_value
                confidence_scores[field] = 0.3  # 默认值置信度较低

        # 生成企业画像摘要
        field_values["profile_summary"] = self._generate_profile_summary(field_values)

        # 构建 CompanyProfile
        try:
            company_profile = CompanyProfile(
                company_name=field_values.get("company_name", "未知企业"),
                short_name=field_values.get("short_name"),
                industry=field_values.get("industry", []),
                company_type=field_values.get("company_type", self.DEFAULT_VALUES["company_type"]),
                founded_year=field_values.get("founded_year"),
                headquarters=field_values.get("headquarters"),
                business_scope=field_values.get("business_scope", []),
                main_products_or_services=field_values.get("main_products_or_services", []),
                estimated_size=field_values.get("estimated_size", self.DEFAULT_VALUES["estimated_size"]),
                region_coverage=field_values.get("region_coverage", []),
                official_website=field_values.get("official_website"),
                official_accounts=field_values.get("official_accounts", []),
                profile_summary=field_values.get("profile_summary"),
            )
        except Exception as e:
            # 如果构建失败，返回基本结构
            company_profile = CompanyProfile(
                company_name=field_values.get("company_name", resolved_company_name or "未知企业"),
                company_type=self.DEFAULT_VALUES["company_type"],
                estimated_size=self.DEFAULT_VALUES["estimated_size"],
            )

        # 计算整体置信度
        overall_confidence = self._calculate_overall_confidence(
            confidence_scores, len(profile_facts)
        )

        # 返回分析结果
        return AnalysisResult(
            result_type="company_profile",
            result_data=company_profile.model_dump(),
            source_fact_ids=list(set(source_fact_ids)),
            confidence=overall_confidence,
        )

    def _resolve_field(
        self,
        field_name: str,
        facts: List[CandidateFact],
        source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> tuple[Any, float, List[str]]:
        """
        解析单个字段的候选事实

        根据字段冲突策略，对候选事实进行归并或选择。

        Args:
            field_name: 字段名称
            facts: 该字段的候选事实列表
            source_evidence_map: 证据来源映射

        Returns:
            tuple: (解析后的值, 置信度, 使用的候选事实ID列表)
        """
        if not facts:
            return None, 0.0, []

        strategy = self.FIELD_CONFLICT_STRATEGIES.get(field_name, "highest_confidence")

        if strategy == "merge":
            return self._merge_field_values(facts, field_name)
        elif strategy == "highest_confidence":
            return self._select_highest_confidence(facts, source_evidence_map)
        elif strategy == "highest_priority":
            return self._select_highest_priority(facts, source_evidence_map)
        else:
            return self._select_highest_confidence(facts, source_evidence_map)

    def _merge_field_values(
        self,
        facts: List[CandidateFact],
        field_name: str,
    ) -> tuple[Any, float, List[str]]:
        """
        合并多个候选事实的值

        适用于列表类型字段（如 industry, business_scope）。

        Args:
            facts: 候选事实列表
            field_name: 字段名称

        Returns:
            tuple: (合并后的值列表, 平均置信度, 使用的候选事实ID列表)
        """
        merged_values: List[str] = []
        fact_ids: List[str] = []
        total_confidence = 0.0

        for fact in facts:
            fact_data = fact.fact_data

            # 获取值（可能是 value 或 values）
            if "values" in fact_data:
                values = fact_data["values"]
            elif "value" in fact_data:
                values = [fact_data["value"]]
            else:
                continue

            # 添加到合并列表（去重）
            for value in values:
                if value and value not in merged_values:
                    merged_values.append(value)

            fact_ids.append(fact.fact_id)
            total_confidence += fact.confidence

        if not merged_values:
            return None, 0.0, []

        avg_confidence = total_confidence / len(facts) if facts else 0.0
        return merged_values, avg_confidence, fact_ids

    def _select_highest_confidence(
        self,
        facts: List[CandidateFact],
        source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> tuple[Any, float, List[str]]:
        """
        选择置信度最高的候选事实

        适用于单值类型字段（如 company_name, founded_year）。

        Args:
            facts: 候选事实列表
            source_evidence_map: 证据来源映射

        Returns:
            tuple: (选中的值, 置信度, 使用的候选事实ID列表)
        """
        if not facts:
            return None, 0.0, []

        # 按置信度排序
        sorted_facts = sorted(facts, key=lambda f: f.confidence, reverse=True)
        best_fact = sorted_facts[0]

        # 获取值
        fact_data = best_fact.fact_data
        value = fact_data.get("value")

        # 对于有 raw 字段的特殊处理（如 estimated_size）
        if "raw" in fact_data:
            value = fact_data.get("value")  # 使用标准化后的值

        return value, best_fact.confidence, [best_fact.fact_id]

    def _select_highest_priority(
        self,
        facts: List[CandidateFact],
        source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> tuple[Any, float, List[str]]:
        """
        选择来源优先级最高的候选事实

        当置信度相近时，优先选择来源优先级更高的候选事实。

        Args:
            facts: 候选事实列表
            source_evidence_map: 证据来源映射

        Returns:
            tuple: (选中的值, 置信度, 使用的候选事实ID列表)
        """
        if not facts:
            return None, 0.0, []

        if not source_evidence_map:
            # 没有来源映射时，退回到置信度选择
            return self._select_highest_confidence(facts, source_evidence_map)

        # 计算每个候选事实的综合得分（置信度 * 来源优先级）
        best_fact = None
        best_score = 0.0

        for fact in facts:
            # 获取来源类型
            source_type = "other"
            if fact.source_evidence_ids and source_evidence_map:
                for evidence_id in fact.source_evidence_ids:
                    if evidence_id in source_evidence_map:
                        source_type = source_evidence_map[evidence_id].get("source_type", "other")
                        break

            priority = self.SOURCE_PRIORITY.get(source_type, 0.5)
            score = fact.confidence * priority

            if score > best_score:
                best_score = score
                best_fact = fact

        if not best_fact:
            best_fact = facts[0]

        fact_data = best_fact.fact_data
        value = fact_data.get("value")

        return value, best_fact.confidence, [best_fact.fact_id]

    def _generate_profile_summary(self, field_values: Dict[str, Any]) -> str:
        """
        生成企业画像摘要

        根据已有字段信息，生成简要的企业描述。

        Args:
            field_values: 字段值字典

        Returns:
            str: 企业画像摘要
        """
        parts: List[str] = []

        # 公司基本信息
        company_name = field_values.get("company_name", "该企业")
        company_type = field_values.get("company_type", "")
        founded_year = field_values.get("founded_year")
        headquarters = field_values.get("headquarters")

        # 行业信息
        industries = field_values.get("industry", [])
        industry_str = "、".join(industries[:3]) if industries else ""

        # 业务信息
        business_scope = field_values.get("business_scope", [])
        products = field_values.get("main_products_or_services", [])

        # 规模信息
        size = field_values.get("estimated_size", "")

        # 构建摘要
        if industry_str:
            parts.append(f"一家{industry_str}行业的企业")

        if company_type:
            parts[-1] = parts[-1] + f"，属于{company_type}" if parts else f"属于{company_type}的企业"

        if founded_year:
            parts.append(f"成立于{founded_year}年")

        if headquarters:
            parts.append(f"总部位于{headquarters}")

        if size:
            parts.append(f"员工规模约{size}")

        if business_scope:
            business_str = "、".join(business_scope[:3])
            parts.append(f"主营业务包括{business_str}")

        if products:
            product_str = "、".join(products[:3])
            parts.append(f"主要产品/服务有{product_str}")

        if not parts:
            return f"{company_name}是一家企业，公开信息有限。"

        summary = "，".join(parts) + "。"
        return summary

    def _calculate_overall_confidence(
        self,
        confidence_scores: Dict[str, float],
        fact_count: int,
    ) -> float:
        """
        计算整体置信度

        基于各字段置信度和候选事实数量综合评估。

        Args:
            confidence_scores: 各字段的置信度
            fact_count: 候选事实总数

        Returns:
            float: 整体置信度（0-1）
        """
        if not confidence_scores:
            return 0.3  # 无候选事实时的基础置信度

        # 计算字段平均置信度
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)

        # 根据候选事实数量调整
        # 事实越多，置信度越高（但有上限）
        fact_bonus = min(0.1, fact_count * 0.01)

        # 关键字段存在性调整
        key_fields = ["company_name", "industry", "business_scope"]
        key_field_count = sum(1 for f in key_fields if f in confidence_scores)
        key_field_bonus = key_field_count * 0.02

        overall = avg_confidence + fact_bonus + key_field_bonus
        return min(1.0, max(0.0, overall))


# 模块级单例实例
_default_analyzer: Optional[CompanyProfileAnalyzer] = None


def get_company_profile_analyzer() -> CompanyProfileAnalyzer:
    """
    获取企业画像分析器单例实例

    Returns:
        CompanyProfileAnalyzer: 企业画像分析器实例
    """
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = CompanyProfileAnalyzer()
    return _default_analyzer


def analyze_company_profile(
    candidate_facts: List[CandidateFact],
    resolved_company_name: Optional[str] = None,
    source_evidence_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> AnalysisResult:
    """
    便捷函数：分析企业画像候选事实

    Args:
        candidate_facts: 候选事实列表
        resolved_company_name: 已确认的企业名称
        source_evidence_map: 证据来源映射

    Returns:
        AnalysisResult: 包含 CompanyProfile 的分析结果
    """
    analyzer = get_company_profile_analyzer()
    return analyzer.analyze(candidate_facts, resolved_company_name, source_evidence_map)