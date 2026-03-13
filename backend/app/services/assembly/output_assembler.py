# -*- coding: utf-8 -*-
"""
OutputAssembler - 输出组装器

将 analysis 层输出组装为统一 API 响应结构 (DueDiligenceOutput)，
兼容 full_mock、hybrid 和 partial result 场景。

主要功能：
1. 从 PipelineState 获取分析结果
2. 将 company_profile 和 recent_developments 正确组装到响应中
3. 处理部分结果缺失的情况
4. 生成报告元数据
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...schemas import (
    DueDiligenceOutput,
    Input,
    Meta,
    LanguageEnum,
    CompanyProfile,
    RecentDevelopment,
    DemandSignal,
    OrganizationInsights,
    RecommendedTargetRole,
    RiskSignal,
    SalesAssessment,
    CommunicationStrategy,
    EvidenceReference,
    CustomerFitLevelEnum,
    OpportunityLevelEnum,
    FollowUpPriorityEnum,
)
from ..orchestrator.pipeline_state import PipelineState, AnalysisResult


class OutputAssembler:
    """
    输出组装器

    将分析链路各阶段的结果组装为最终的 DueDiligenceOutput。

    使用方式：
        assembler = OutputAssembler()
        output = assembler.assemble(state, user_input)

    Attributes:
        version: 输出版本号
        language: 输出语言
    """

    # 默认配置
    DEFAULT_VERSION = "mvp_v1"
    DEFAULT_LANGUAGE = LanguageEnum.ZH_CN

    # 默认企业画像（用于部分结果缺失时的降级）
    DEFAULT_COMPANY_PROFILE = {
        "company_name": "未知企业",
        "short_name": "未知",
        "industry": ["综合"],
        "company_type": "民营企业",
        "estimated_size": "100-500人",
        "profile_summary": "公开信息有限，企业画像待完善。",
    }

    # 默认商务判断
    DEFAULT_SALES_ASSESSMENT = {
        "customer_fit_level": CustomerFitLevelEnum.MEDIUM,
        "opportunity_level": OpportunityLevelEnum.LOW,
        "follow_up_priority": FollowUpPriorityEnum.P3,
        "core_opportunity_scenarios": ["待进一步了解"],
        "main_obstacles": ["信息不足"],
        "assessment_summary": "公开信息有限，建议进一步调研后再确定跟进策略。",
        "should_follow_up": False,
    }

    # 默认沟通策略
    DEFAULT_COMMUNICATION_STRATEGY = {
        "recommended_entry_points": ["了解企业现状", "探索合作机会"],
        "avoid_points": ["盲目推销产品"],
        "opening_message": "我们对贵司的了解还不够充分，希望能进一步交流。",
        "phone_script": "您好，我们希望了解更多关于贵司业务发展的信息，看看是否有合作的机会。",
        "wechat_message": "您好，我们希望进一步了解贵司的业务情况，如果有方便的时间可以交流一下。",
        "email_message": "您好，我们希望进一步了解贵司的业务发展方向和当前的管理重点，以便评估可能的合作机会。",
        "next_step_suggestion": "建议先通过公开渠道或人脉进一步了解企业情况。",
    }

    # 默认组织洞察
    DEFAULT_ORGANIZATION_INSIGHTS = {
        "possible_target_departments": ["综合管理部"],
        "recommended_target_roles": [
            {
                "role": "业务负责人",
                "department": "业务部门",
                "reason": "主导业务决策",
                "priority": 1,
            }
        ],
        "possible_decision_chain": ["业务评估", "管理层审批"],
        "key_people_public_info": [],
    }

    def __init__(
        self,
        version: str = DEFAULT_VERSION,
        language: LanguageEnum = DEFAULT_LANGUAGE,
    ):
        """
        初始化输出组装器

        Args:
            version: 输出版本号
            language: 输出语言
        """
        self.version = version
        self.language = language

    def assemble(
        self,
        state: PipelineState,
        user_input: Input,
    ) -> DueDiligenceOutput:
        """
        组装最终输出

        从 PipelineState 中提取分析结果，组装为 DueDiligenceOutput。

        组装流程：
        1. 生成报告元数据
        2. 提取并转换 company_profile
        3. 提取并转换 recent_developments
        4. 构建默认的 demand_signals（v0.0.2 暂未实现）
        5. 构建默认的 organization_insights
        6. 构建默认的 risk_signals（v0.0.2 暂未实现）
        7. 构建默认的 sales_assessment
        8. 构建默认的 communication_strategy
        9. 构建证据引用列表
        10. 组装最终输出

        Args:
            state: 流水线状态，包含分析结果
            user_input: 用户输入数据

        Returns:
            DueDiligenceOutput: 完整的背调输出结果
        """
        # 1. 生成报告元数据
        meta = self._create_meta()

        # 2. 提取并转换 company_profile
        company_profile = self._extract_company_profile(state, user_input)

        # 3. 提取并转换 recent_developments
        recent_developments = self._extract_recent_developments(state)

        # 4. 构建需求信号（v0.0.2 使用默认值）
        demand_signals = self._extract_demand_signals(state)

        # 5. 构建组织洞察
        organization_insights = self._extract_organization_insights(state, user_input)

        # 6. 构建风险信号（v0.0.2 使用默认值）
        risk_signals = self._extract_risk_signals(state)

        # 7. 构建商务判断
        sales_assessment = self._extract_sales_assessment(state, user_input)

        # 8. 构建沟通策略
        communication_strategy = self._extract_communication_strategy(state, user_input)

        # 9. 构建证据引用列表
        evidence_references = self._build_evidence_references(state)

        # 10. 组装最终输出
        return DueDiligenceOutput(
            meta=meta,
            input=user_input,
            company_profile=company_profile,
            recent_developments=recent_developments,
            demand_signals=demand_signals,
            organization_insights=organization_insights,
            risk_signals=risk_signals,
            sales_assessment=sales_assessment,
            communication_strategy=communication_strategy,
            evidence_references=evidence_references,
        )

    def _create_meta(self) -> Meta:
        """
        创建报告元数据

        Returns:
            Meta: 报告元数据
        """
        today = datetime.now().strftime("%Y%m%d")
        short_uuid = uuid.uuid4().hex[:6]
        report_id = f"dd_{today}_{short_uuid}"

        return Meta(
            report_id=report_id,
            generated_at=datetime.now(),
            language=self.language,
            version=self.version,
        )

    def _extract_company_profile(
        self,
        state: PipelineState,
        user_input: Input,
    ) -> CompanyProfile:
        """
        提取并转换企业画像

        从 analysis_results 中获取 company_profile 类型的结果，
        如果不存在则使用默认值。

        Args:
            state: 流水线状态
            user_input: 用户输入

        Returns:
            CompanyProfile: 企业画像
        """
        # 尝试从分析结果中获取
        result = state.get_analysis_result("company_profile")

        if result and result.result_data:
            try:
                return self._dict_to_company_profile(
                    result.result_data,
                    user_input.company_name,
                )
            except Exception:
                pass

        # 使用默认值
        return self._create_default_company_profile(user_input.company_name)

    def _dict_to_company_profile(
        self,
        data: Dict[str, Any],
        fallback_name: str,
    ) -> CompanyProfile:
        """
        将字典转换为 CompanyProfile 对象

        Args:
            data: 企业画像数据字典
            fallback_name: 降级时使用的企业名称

        Returns:
            CompanyProfile: 企业画像对象
        """
        return CompanyProfile(
            company_name=data.get("company_name", fallback_name),
            short_name=data.get("short_name"),
            industry=data.get("industry", []),
            company_type=data.get("company_type", "民营企业"),
            founded_year=data.get("founded_year"),
            headquarters=data.get("headquarters"),
            business_scope=data.get("business_scope", []),
            main_products_or_services=data.get("main_products_or_services", []),
            estimated_size=data.get("estimated_size", "100-500人"),
            region_coverage=data.get("region_coverage", []),
            official_website=data.get("official_website"),
            official_accounts=data.get("official_accounts", []),
            profile_summary=data.get("profile_summary"),
        )

    def _create_default_company_profile(self, company_name: str) -> CompanyProfile:
        """
        创建默认企业画像

        Args:
            company_name: 企业名称

        Returns:
            CompanyProfile: 默认企业画像
        """
        short_name = company_name[:4] if len(company_name) >= 4 else company_name
        return CompanyProfile(
            company_name=company_name,
            short_name=short_name,
            industry=["综合"],
            company_type="民营企业",
            estimated_size="100-500人",
            profile_summary=f"{company_name}是一家企业，公开信息有限。",
        )

    def _extract_recent_developments(
        self,
        state: PipelineState,
    ) -> List[RecentDevelopment]:
        """
        提取并转换近期动态

        从 analysis_results 中获取 recent_developments 类型的结果。

        Args:
            state: 流水线状态

        Returns:
            List[RecentDevelopment]: 近期动态列表
        """
        # 尝试从分析结果中获取
        result = state.get_analysis_result("recent_developments")

        if result and result.result_data:
            developments_data = result.result_data.get("developments", [])
            if developments_data:
                return self._dict_list_to_developments(developments_data)

        return []

    def _dict_list_to_developments(
        self,
        data_list: List[Dict[str, Any]],
    ) -> List[RecentDevelopment]:
        """
        将字典列表转换为 RecentDevelopment 列表

        Args:
            data_list: 近期动态数据列表

        Returns:
            List[RecentDevelopment]: 近期动态列表
        """
        developments = []
        for data in data_list:
            try:
                # 处理 type 字段，可能是枚举值或字符串
                type_value = data.get("type", "other")
                if isinstance(type_value, str):
                    from ...schemas.company import RecentDevelopmentTypeEnum
                    try:
                        type_enum = RecentDevelopmentTypeEnum(type_value)
                    except ValueError:
                        type_enum = RecentDevelopmentTypeEnum.OTHER
                else:
                    type_enum = type_value

                development = RecentDevelopment(
                    date=data.get("date", "未知日期"),
                    type=type_enum,
                    title=data.get("title", "企业动态"),
                    summary=data.get("summary", "暂无详细信息"),
                    source=data.get("source", "公开信息"),
                    source_ref_ids=data.get("source_ref_ids", []),
                    confidence=data.get("confidence", 0.5),
                )
                developments.append(development)
            except Exception:
                continue

        return developments

    def _extract_demand_signals(
        self,
        state: PipelineState,
    ) -> List[DemandSignal]:
        """
        提取需求信号

        v0.0.2 阶段尚未实现需求信号分析器，返回空列表。

        Args:
            state: 流水线状态

        Returns:
            List[DemandSignal]: 需求信号列表
        """
        result = state.get_analysis_result("demand_signals")
        if result and result.result_data:
            signals_data = result.result_data.get("signals", [])
            if signals_data:
                return self._dict_list_to_demand_signals(signals_data)

        return []

    def _dict_list_to_demand_signals(
        self,
        data_list: List[Dict[str, Any]],
    ) -> List[DemandSignal]:
        """
        将字典列表转换为 DemandSignal 列表

        Args:
            data_list: 需求信号数据列表

        Returns:
            List[DemandSignal]: 需求信号列表
        """
        from ...schemas.analysis import DemandSignalTypeEnum, StrengthEnum

        signals = []
        for data in data_list:
            try:
                # 处理枚举值
                signal_type_value = data.get("signal_type", "other")
                if isinstance(signal_type_value, str):
                    try:
                        signal_type = DemandSignalTypeEnum(signal_type_value)
                    except ValueError:
                        signal_type = DemandSignalTypeEnum.OTHER
                else:
                    signal_type = signal_type_value

                strength_value = data.get("strength", "low")
                if isinstance(strength_value, str):
                    try:
                        strength = StrengthEnum(strength_value)
                    except ValueError:
                        strength = StrengthEnum.LOW
                else:
                    strength = strength_value

                signal = DemandSignal(
                    signal_type=signal_type,
                    signal=data.get("signal", ""),
                    evidence=data.get("evidence", ""),
                    inference=data.get("inference", ""),
                    strength=strength,
                    source=data.get("source"),
                    source_ref_ids=data.get("source_ref_ids", []),
                    date=data.get("date"),
                )
                signals.append(signal)
            except Exception:
                continue

        return signals

    def _extract_organization_insights(
        self,
        state: PipelineState,
        user_input: Input,
    ) -> OrganizationInsights:
        """
        提取组织洞察

        v0.0.2 阶段根据企业名称和行业生成默认组织洞察。

        Args:
            state: 流水线状态
            user_input: 用户输入

        Returns:
            OrganizationInsights: 组织洞察
        """
        result = state.get_analysis_result("organization_insights")

        if result and result.result_data:
            return self._dict_to_organization_insights(result.result_data)

        # 使用默认值，但根据企业名称调整
        return self._create_default_organization_insights(user_input.company_name)

    def _dict_to_organization_insights(
        self,
        data: Dict[str, Any],
    ) -> OrganizationInsights:
        """
        将字典转换为 OrganizationInsights 对象

        Args:
            data: 组织洞察数据

        Returns:
            OrganizationInsights: 组织洞察对象
        """
        # 处理推荐角色
        roles_data = data.get("recommended_target_roles", [])
        roles = []
        for role_data in roles_data:
            roles.append(RecommendedTargetRole(
                role=role_data.get("role", ""),
                department=role_data.get("department"),
                reason=role_data.get("reason", ""),
                priority=role_data.get("priority", 1),
            ))

        return OrganizationInsights(
            possible_target_departments=data.get("possible_target_departments", []),
            recommended_target_roles=roles,
            possible_decision_chain=data.get("possible_decision_chain", []),
            key_people_public_info=data.get("key_people_public_info", []),
        )

    def _create_default_organization_insights(
        self,
        company_name: str,
    ) -> OrganizationInsights:
        """
        创建默认组织洞察

        Args:
            company_name: 企业名称

        Returns:
            OrganizationInsights: 默认组织洞察
        """
        return OrganizationInsights(
            possible_target_departments=["综合管理部", "业务部门"],
            recommended_target_roles=[
                RecommendedTargetRole(
                    role="业务负责人",
                    department="业务部门",
                    reason="主导业务决策",
                    priority=1,
                ),
            ],
            possible_decision_chain=["业务评估", "管理层审批"],
            key_people_public_info=[],
        )

    def _extract_risk_signals(
        self,
        state: PipelineState,
    ) -> List[RiskSignal]:
        """
        提取风险信号

        v0.0.2 阶段尚未实现风险信号分析器，返回空列表。

        Args:
            state: 流水线状态

        Returns:
            List[RiskSignal]: 风险信号列表
        """
        result = state.get_analysis_result("risk_signals")
        if result and result.result_data:
            signals_data = result.result_data.get("signals", [])
            if signals_data:
                return self._dict_list_to_risk_signals(signals_data)

        return []

    def _dict_list_to_risk_signals(
        self,
        data_list: List[Dict[str, Any]],
    ) -> List[RiskSignal]:
        """
        将字典列表转换为 RiskSignal 列表

        Args:
            data_list: 风险信号数据列表

        Returns:
            List[RiskSignal]: 风险信号列表
        """
        from ...schemas.analysis import RiskTypeEnum, StrengthEnum

        signals = []
        for data in data_list:
            try:
                # 处理枚举值
                risk_type_value = data.get("risk_type", "other")
                if isinstance(risk_type_value, str):
                    try:
                        risk_type = RiskTypeEnum(risk_type_value)
                    except ValueError:
                        risk_type = RiskTypeEnum.OTHER
                else:
                    risk_type = risk_type_value

                level_value = data.get("level", "low")
                if isinstance(level_value, str):
                    try:
                        level = StrengthEnum(level_value)
                    except ValueError:
                        level = StrengthEnum.LOW
                else:
                    level = level_value

                signal = RiskSignal(
                    risk_type=risk_type,
                    risk=data.get("risk", ""),
                    description=data.get("description", ""),
                    impact=data.get("impact", ""),
                    level=level,
                    source=data.get("source"),
                    source_ref_ids=data.get("source_ref_ids", []),
                    date=data.get("date"),
                )
                signals.append(signal)
            except Exception:
                continue

        return signals

    def _extract_sales_assessment(
        self,
        state: PipelineState,
        user_input: Input,
    ) -> SalesAssessment:
        """
        提取商务判断

        v0.0.2 阶段使用默认值。

        Args:
            state: 流水线状态
            user_input: 用户输入

        Returns:
            SalesAssessment: 商务判断
        """
        result = state.get_analysis_result("sales_assessment")

        if result and result.result_data:
            return self._dict_to_sales_assessment(result.result_data)

        return self._create_default_sales_assessment(user_input.company_name)

    def _dict_to_sales_assessment(
        self,
        data: Dict[str, Any],
    ) -> SalesAssessment:
        """
        将字典转换为 SalesAssessment 对象

        Args:
            data: 商务判断数据

        Returns:
            SalesAssessment: 商务判断对象
        """
        # 处理枚举值
        fit_value = data.get("customer_fit_level", "medium")
        if isinstance(fit_value, str):
            try:
                customer_fit_level = CustomerFitLevelEnum(fit_value)
            except ValueError:
                customer_fit_level = CustomerFitLevelEnum.MEDIUM
        else:
            customer_fit_level = fit_value

        opportunity_value = data.get("opportunity_level", "low")
        if isinstance(opportunity_value, str):
            try:
                opportunity_level = OpportunityLevelEnum(opportunity_value)
            except ValueError:
                opportunity_level = OpportunityLevelEnum.LOW
        else:
            opportunity_level = opportunity_value

        priority_value = data.get("follow_up_priority", "P3")
        if isinstance(priority_value, str):
            try:
                follow_up_priority = FollowUpPriorityEnum(priority_value)
            except ValueError:
                follow_up_priority = FollowUpPriorityEnum.P3
        else:
            follow_up_priority = priority_value

        return SalesAssessment(
            customer_fit_level=customer_fit_level,
            opportunity_level=opportunity_level,
            follow_up_priority=follow_up_priority,
            core_opportunity_scenarios=data.get("core_opportunity_scenarios", []),
            main_obstacles=data.get("main_obstacles", []),
            assessment_summary=data.get("assessment_summary", "暂无评估结论"),
            should_follow_up=data.get("should_follow_up"),
        )

    def _create_default_sales_assessment(
        self,
        company_name: str,
    ) -> SalesAssessment:
        """
        创建默认商务判断

        Args:
            company_name: 企业名称

        Returns:
            SalesAssessment: 默认商务判断
        """
        return SalesAssessment(
            customer_fit_level=CustomerFitLevelEnum.MEDIUM,
            opportunity_level=OpportunityLevelEnum.LOW,
            follow_up_priority=FollowUpPriorityEnum.P3,
            core_opportunity_scenarios=["待进一步了解"],
            main_obstacles=["信息不足"],
            assessment_summary=f"{company_name}公开信息有限，建议进一步调研后再确定跟进策略。",
            should_follow_up=False,
        )

    def _extract_communication_strategy(
        self,
        state: PipelineState,
        user_input: Input,
    ) -> CommunicationStrategy:
        """
        提取沟通策略

        v0.0.2 阶段使用默认值。

        Args:
            state: 流水线状态
            user_input: 用户输入

        Returns:
            CommunicationStrategy: 沟通策略
        """
        result = state.get_analysis_result("communication_strategy")

        if result and result.result_data:
            return self._dict_to_communication_strategy(result.result_data)

        return self._create_default_communication_strategy(user_input.company_name)

    def _dict_to_communication_strategy(
        self,
        data: Dict[str, Any],
    ) -> CommunicationStrategy:
        """
        将字典转换为 CommunicationStrategy 对象

        Args:
            data: 沟通策略数据

        Returns:
            CommunicationStrategy: 沟通策略对象
        """
        return CommunicationStrategy(
            recommended_entry_points=data.get("recommended_entry_points", []),
            avoid_points=data.get("avoid_points", []),
            opening_message=data.get("opening_message", ""),
            phone_script=data.get("phone_script", ""),
            wechat_message=data.get("wechat_message", ""),
            email_message=data.get("email_message", ""),
            next_step_suggestion=data.get("next_step_suggestion", ""),
        )

    def _create_default_communication_strategy(
        self,
        company_name: str,
    ) -> CommunicationStrategy:
        """
        创建默认沟通策略

        Args:
            company_name: 企业名称

        Returns:
            CommunicationStrategy: 默认沟通策略
        """
        return CommunicationStrategy(
            recommended_entry_points=["了解企业现状", "探索合作机会"],
            avoid_points=["盲目推销产品"],
            opening_message=f"我们对{company_name}的了解还不够充分，希望能进一步交流。",
            phone_script=f"您好，我们希望了解更多关于{company_name}业务发展的信息，看看是否有合作的机会。",
            wechat_message=f"您好，我们希望进一步了解{company_name}的业务情况，如果有方便的时间可以交流一下。",
            email_message=f"您好，我们希望进一步了解{company_name}的业务发展方向和当前的管理重点，以便评估可能的合作机会。",
            next_step_suggestion="建议先通过公开渠道或人脉进一步了解企业情况。",
        )

    def _build_evidence_references(
        self,
        state: PipelineState,
    ) -> List[EvidenceReference]:
        """
        构建证据引用列表

        从 PipelineState 的原始证据和处理后证据中构建 EvidenceReference 列表。

        Args:
            state: 流水线状态

        Returns:
            List[EvidenceReference]: 证据引用列表
        """
        references: List[EvidenceReference] = []
        seen_ids: set = set()

        # 从原始证据构建引用
        for evidence in state.raw_evidence:
            if evidence.evidence_id in seen_ids:
                continue
            seen_ids.add(evidence.evidence_id)

            reference = EvidenceReference(
                reference_id=evidence.evidence_id,
                source=evidence.source_type,
                title=evidence.title,
                url=evidence.url,
                date=evidence.normalized_date if hasattr(evidence, 'normalized_date') else None,
                excerpt=evidence.content[:200] if evidence.content else None,
            )
            references.append(reference)

        # 如果没有证据，返回空列表
        return references


# 模块级单例实例
_default_assembler: Optional[OutputAssembler] = None


def get_output_assembler(
    version: str = OutputAssembler.DEFAULT_VERSION,
    language: LanguageEnum = OutputAssembler.DEFAULT_LANGUAGE,
) -> OutputAssembler:
    """
    获取输出组装器单例实例

    Args:
        version: 输出版本号
        language: 输出语言

    Returns:
        OutputAssembler: 输出组装器实例
    """
    global _default_assembler
    if _default_assembler is None:
        _default_assembler = OutputAssembler(version=version, language=language)
    return _default_assembler


def assemble_output(
    state: PipelineState,
    user_input: Input,
) -> DueDiligenceOutput:
    """
    便捷函数：组装最终输出

    Args:
        state: 流水线状态
        user_input: 用户输入

    Returns:
        DueDiligenceOutput: 完整的背调输出结果
    """
    assembler = get_output_assembler()
    return assembler.assemble(state, user_input)