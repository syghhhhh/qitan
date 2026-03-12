# -*- coding: utf-8 -*-
"""Mock 分析数据生成模块"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from ..schemas import (
    DueDiligenceOutput,
    Meta,
    Input,
    LanguageEnum,
    SalesGoalEnum,
    CompanyProfile,
    RecentDevelopment,
    RecentDevelopmentTypeEnum,
    DemandSignal,
    DemandSignalTypeEnum,
    RiskSignal,
    RiskTypeEnum,
    StrengthEnum,
    OrganizationInsights,
    RecommendedTargetRole,
    SalesAssessment,
    CommunicationStrategy,
    EvidenceReference,
    CustomerFitLevelEnum,
    OpportunityLevelEnum,
    FollowUpPriorityEnum,
)


def _generate_report_id() -> str:
    """生成报告ID"""
    today = datetime.now().strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:6]
    return f"dd_{today}_{short_uuid}"


def _get_tech_company_mock(company_name: str, user_input: Input) -> DueDiligenceOutput:
    """科技类企业 Mock 数据"""
    return DueDiligenceOutput(
        meta=Meta(
            report_id=_generate_report_id(),
            generated_at=datetime.now(),
            language=LanguageEnum.ZH_CN,
            version="mvp_v1",
        ),
        input=user_input,
        company_profile=CompanyProfile(
            company_name=company_name,
            short_name=company_name[:4] if len(company_name) >= 4 else company_name,
            industry=["企业服务", "软件", "数字化"],
            company_type="民营企业",
            founded_year=2018,
            headquarters="上海",
            business_scope=["企业数字化解决方案", "SaaS产品研发"],
            main_products_or_services=["企业协同平台", "数据分析工具"],
            estimated_size="200-500人",
            region_coverage=["华东", "全国"],
            official_website=f"https://www.{company_name[:4].lower()}-tech.com",
            official_accounts=["微信公众号：" + company_name],
            profile_summary="一家面向企业客户提供数字化产品和解决方案的成长型科技公司。",
        ),
        recent_developments=[
            RecentDevelopment(
                date="2026-01-18",
                type=RecentDevelopmentTypeEnum.HIRING,
                title="招聘销售运营经理",
                summary="公开招聘销售运营经理，职责涉及销售流程优化、CRM管理和数据分析。",
                source="招聘信息",
                source_ref_ids=["ref_001"],
                confidence=0.91,
            ),
            RecentDevelopment(
                date="2025-12-20",
                type=RecentDevelopmentTypeEnum.EXPANSION,
                title="拓展华南市场",
                summary="公司宣布进一步拓展华南区域业务布局。",
                source="新闻稿",
                source_ref_ids=["ref_002"],
                confidence=0.84,
            ),
        ],
        demand_signals=[
            DemandSignal(
                signal_type=DemandSignalTypeEnum.SALES_MANAGEMENT_SIGNAL,
                signal="公司正在招聘销售运营相关岗位",
                evidence="招聘职责明确提到销售流程优化、CRM管理和数据分析",
                inference="公司可能正在加强销售管理体系建设，对CRM和销售运营工具存在潜在需求",
                strength=StrengthEnum.HIGH,
                source="招聘信息",
                source_ref_ids=["ref_001"],
                date="2026-01-18",
            ),
            DemandSignal(
                signal_type=DemandSignalTypeEnum.EXPANSION_SIGNAL,
                signal="企业拓展新区域市场",
                evidence="新闻稿提到华南区域业务扩张",
                inference="随着跨区域业务拓展，线索分配、客户跟进和销售协同复杂度上升",
                strength=StrengthEnum.MEDIUM,
                source="新闻稿",
                source_ref_ids=["ref_002"],
                date="2025-12-20",
            ),
        ],
        organization_insights=OrganizationInsights(
            possible_target_departments=["销售部", "销售运营", "信息化部门"],
            recommended_target_roles=[
                RecommendedTargetRole(
                    role="销售负责人",
                    department="销售部",
                    reason="更关注销售流程、团队管理和业绩提升",
                    priority=1,
                ),
                RecommendedTargetRole(
                    role="销售运营负责人",
                    department="销售运营",
                    reason="与CRM落地、数据管理和流程标准化高度相关",
                    priority=2,
                ),
            ],
            possible_decision_chain=["业务负责人提出需求", "销售运营评估方案", "管理层审批预算", "信息化协同落地"],
            key_people_public_info=[],
        ),
        risk_signals=[
            RiskSignal(
                risk_type=RiskTypeEnum.LONG_DECISION_CYCLE,
                risk="可能存在跨部门决策链",
                description="如果CRM涉及销售、运营和IT协同，决策流程可能较长",
                impact="项目推进周期可能拉长，需要多角色沟通",
                level=StrengthEnum.MEDIUM,
                source="模型推断",
                source_ref_ids=[],
                date="2026-03-12",
            ),
        ],
        sales_assessment=SalesAssessment(
            customer_fit_level=CustomerFitLevelEnum.HIGH,
            opportunity_level=OpportunityLevelEnum.HIGH,
            follow_up_priority=FollowUpPriorityEnum.P1,
            core_opportunity_scenarios=[
                "销售流程标准化",
                "CRM管理升级",
                "线索与客户跟进协同",
                "销售数据分析",
            ],
            main_obstacles=[
                "可能已有现有系统",
                "决策涉及多部门",
            ],
            assessment_summary="该企业存在明显销售管理与区域扩张信号，较符合CRM产品的目标客户画像，建议优先跟进。",
            should_follow_up=True,
        ),
        communication_strategy=CommunicationStrategy(
            recommended_entry_points=[
                "销售流程标准化",
                "跨区域团队协同",
                "线索到商机转化效率",
            ],
            avoid_points=[
                "一开始过度强调系统功能",
                "直接推大而全的平台替换",
            ],
            opening_message="注意到贵司近期在拓展区域业务，同时也在招聘销售运营岗位，说明销售体系建设可能正在加速。",
            phone_script="您好，我们关注到贵司近期在销售运营和区域拓展上动作比较明显。很多类似阶段的企业会开始遇到销售流程不统一、客户跟进协同难和数据不透明的问题。我们这边主要帮助企业优化CRM和销售管理流程，想看看是否有机会交流一下你们当前在这块的管理重点。",
            wechat_message="您好，看到贵司近期在拓展区域业务，也在招销售运营相关岗位。很多成长型企业在这个阶段会开始关注销售流程标准化、客户跟进协同和数据分析效率。我们这边在CRM和销售运营管理方面有一些实践，若方便的话想跟您交流下是否有可借鉴的地方。",
            email_message="您好，关注到贵司近期在业务扩张及销售运营建设方面有较多动作。对于成长型企业而言，这通常意味着销售流程标准化、客户管理协同及数据分析能力的重要性提升。我们团队长期服务于类似阶段企业，帮助其优化CRM和销售管理机制。如果您愿意，我可以基于贵司当前发展阶段提供一个简短的交流建议。",
            next_step_suggestion="优先联系销售负责人或销售运营负责人，围绕销售流程标准化与区域拓张协同问题发起首次交流。",
        ),
        evidence_references=[
            EvidenceReference(
                reference_id="ref_001",
                source="招聘信息",
                title="销售运营经理招聘",
                url="https://example.com/job/1",
                date="2026-01-18",
                excerpt="负责销售流程优化、CRM管理、销售数据分析。",
            ),
            EvidenceReference(
                reference_id="ref_002",
                source="新闻稿",
                title=f"{company_name}拓展华南市场",
                url="https://example.com/news/1",
                date="2025-12-20",
                excerpt="公司进一步拓展华南区域业务布局。",
            ),
        ],
    )


def _get_manufacturing_company_mock(company_name: str, user_input: Input) -> DueDiligenceOutput:
    """制造类企业 Mock 数据"""
    return DueDiligenceOutput(
        meta=Meta(
            report_id=_generate_report_id(),
            generated_at=datetime.now(),
            language=LanguageEnum.ZH_CN,
            version="mvp_v1",
        ),
        input=user_input,
        company_profile=CompanyProfile(
            company_name=company_name,
            short_name=company_name[:4] if len(company_name) >= 4 else company_name,
            industry=["制造业", "工业", "生产制造"],
            company_type="民营企业",
            founded_year=2010,
            headquarters="苏州",
            business_scope=["精密零部件制造", "工业设备生产"],
            main_products_or_services=["精密机械配件", "自动化设备"],
            estimated_size="500-1000人",
            region_coverage=["华东", "华南"],
            official_website=f"https://www.{company_name[:4].lower()}-mfg.com",
            official_accounts=["微信公众号：" + company_name],
            profile_summary="一家专注于精密制造的中型工业企业，近年推进数字化转型。",
        ),
        recent_developments=[
            RecentDevelopment(
                date="2026-02-05",
                type=RecentDevelopmentTypeEnum.DIGITAL_TRANSFORMATION,
                title="启动智能制造升级项目",
                summary="公司宣布投资建设智能工厂，引入MES系统和自动化产线。",
                source="新闻稿",
                source_ref_ids=["ref_001"],
                confidence=0.88,
            ),
            RecentDevelopment(
                date="2025-11-15",
                type=RecentDevelopmentTypeEnum.HIRING,
                title="招聘IT部门负责人",
                summary="公开招聘IT部门负责人，负责企业数字化规划和系统建设。",
                source="招聘信息",
                source_ref_ids=["ref_002"],
                confidence=0.85,
            ),
        ],
        demand_signals=[
            DemandSignal(
                signal_type=DemandSignalTypeEnum.DIGITALIZATION_SIGNAL,
                signal="企业正在进行数字化转型",
                evidence="启动智能制造升级项目，引入MES系统和自动化产线",
                inference="制造企业数字化转型阶段，对ERP、MES、供应链管理等系统有明确需求",
                strength=StrengthEnum.HIGH,
                source="新闻稿",
                source_ref_ids=["ref_001"],
                date="2026-02-05",
            ),
            DemandSignal(
                signal_type=DemandSignalTypeEnum.MANAGEMENT_SIGNAL,
                signal="企业在加强信息化管理能力",
                evidence="招聘IT部门负责人，负责企业数字化规划",
                inference="企业正在建立专门的信息化管理团队，可能有多系统整合需求",
                strength=StrengthEnum.MEDIUM,
                source="招聘信息",
                source_ref_ids=["ref_002"],
                date="2025-11-15",
            ),
        ],
        organization_insights=OrganizationInsights(
            possible_target_departments=["信息化部", "生产部", "供应链部门"],
            recommended_target_roles=[
                RecommendedTargetRole(
                    role="IT部门负责人",
                    department="信息化部",
                    reason="主导企业数字化转型和系统建设",
                    priority=1,
                ),
                RecommendedTargetRole(
                    role="生产总监",
                    department="生产部",
                    reason="关注生产效率和质量管理，数字化项目的实际使用者",
                    priority=2,
                ),
            ],
            possible_decision_chain=["IT部门评估方案", "生产部门确认需求", "财务审核预算", "总经理审批"],
            key_people_public_info=[],
        ),
        risk_signals=[
            RiskSignal(
                risk_type=RiskTypeEnum.PROCUREMENT_COMPLEXITY,
                risk="制造业采购流程较复杂",
                description="制造企业通常有较严格的采购审批流程和多部门评审",
                impact="项目周期可能较长，需要准备详细的技术方案和商务条款",
                level=StrengthEnum.MEDIUM,
                source="行业常识",
                source_ref_ids=[],
                date="2026-03-12",
            ),
        ],
        sales_assessment=SalesAssessment(
            customer_fit_level=CustomerFitLevelEnum.HIGH,
            opportunity_level=OpportunityLevelEnum.MEDIUM,
            follow_up_priority=FollowUpPriorityEnum.P2,
            core_opportunity_scenarios=[
                "生产流程数字化",
                "供应链管理优化",
                "质量追溯体系建设",
            ],
            main_obstacles=[
                "可能已有ERP系统",
                "预算审批周期长",
            ],
            assessment_summary="制造企业处于数字化转型关键期，存在明确的系统建设需求，建议关注生产管理和供应链场景。",
            should_follow_up=True,
        ),
        communication_strategy=CommunicationStrategy(
            recommended_entry_points=[
                "智能制造升级经验",
                "生产数据可视化",
                "多系统数据打通",
            ],
            avoid_points=[
                "直接推销产品功能",
                "忽视现有系统情况",
            ],
            opening_message="注意到贵司正在推进智能制造升级，这个阶段通常面临新旧系统整合和生产数据打通的挑战。",
            phone_script="您好，我们了解到贵司正在进行智能制造升级。很多制造企业在数字化过程中，会遇到ERP、MES等系统数据孤岛的问题，影响生产决策效率。我们这边有帮助企业实现生产数据可视化和多系统整合的经验，想看看是否有机会交流一下。",
            wechat_message="您好，关注到贵司智能制造升级的进展。制造企业在数字化转型中，生产数据打通和多系统协同是常见痛点。我们有这方面的实践经验，如果您方便的话，可以交流一下当前遇到的管理挑战。",
            email_message="您好，关注到贵司正在推进智能制造升级项目。在制造企业数字化转型过程中，我们观察到生产数据可视化、多系统整合和供应链协同是常见的核心挑战。我们团队有服务于多家制造企业的实践经验，如果您愿意，我可以基于贵司当前的项目阶段分享一些可借鉴的经验。",
            next_step_suggestion="优先联系IT部门负责人或生产总监，围绕智能制造实施过程中的痛点发起交流。",
        ),
        evidence_references=[
            EvidenceReference(
                reference_id="ref_001",
                source="新闻稿",
                title=f"{company_name}启动智能制造升级项目",
                url="https://example.com/news/2",
                date="2026-02-05",
                excerpt="公司投资建设智能工厂，引入MES系统和自动化产线。",
            ),
            EvidenceReference(
                reference_id="ref_002",
                source="招聘信息",
                title="IT部门负责人招聘",
                url="https://example.com/job/2",
                date="2025-11-15",
                excerpt="负责企业数字化规划和系统建设。",
            ),
        ],
    )


def _get_education_company_mock(company_name: str, user_input: Input) -> DueDiligenceOutput:
    """教育类企业 Mock 数据"""
    return DueDiligenceOutput(
        meta=Meta(
            report_id=_generate_report_id(),
            generated_at=datetime.now(),
            language=LanguageEnum.ZH_CN,
            version="mvp_v1",
        ),
        input=user_input,
        company_profile=CompanyProfile(
            company_name=company_name,
            short_name=company_name[:4] if len(company_name) >= 4 else company_name,
            industry=["教育", "培训", "在线教育"],
            company_type="民营企业",
            founded_year=2015,
            headquarters="北京",
            business_scope=["在线教育", "职业培训", "企业内训"],
            main_products_or_services=["在线课程平台", "企业培训解决方案"],
            estimated_size="100-300人",
            region_coverage=["全国"],
            official_website=f"https://www.{company_name[:4].lower()}-edu.com",
            official_accounts=["微信公众号：" + company_name],
            profile_summary="一家专注于职业培训和企业内训的在线教育公司。",
        ),
        recent_developments=[
            RecentDevelopment(
                date="2026-01-20",
                type=RecentDevelopmentTypeEnum.PARTNERSHIP,
                title="与多家企业达成培训合作",
                summary="公司宣布与多家大型企业签订年度培训服务协议。",
                source="新闻稿",
                source_ref_ids=["ref_001"],
                confidence=0.92,
            ),
            RecentDevelopment(
                date="2025-10-08",
                type=RecentDevelopmentTypeEnum.FINANCING,
                title="完成B轮融资",
                summary="公司完成B轮融资，金额数千万元，将用于产品研发和市场拓展。",
                source="新闻稿",
                source_ref_ids=["ref_002"],
                confidence=0.95,
            ),
        ],
        demand_signals=[
            DemandSignal(
                signal_type=DemandSignalTypeEnum.GROWTH_SIGNAL,
                signal="企业业务快速扩张",
                evidence="完成B轮融资，与多家大型企业签订培训合作协议",
                inference="企业处于快速成长期，可能需要加强客户管理和服务交付能力",
                strength=StrengthEnum.HIGH,
                source="新闻稿",
                source_ref_ids=["ref_001", "ref_002"],
                date="2026-01-20",
            ),
            DemandSignal(
                signal_type=DemandSignalTypeEnum.CUSTOMER_OPERATION_SIGNAL,
                signal="企业客户数量快速增长",
                evidence="与多家大型企业签订年度培训服务协议",
                inference="客户规模扩大后，客户服务和续约管理压力增大",
                strength=StrengthEnum.MEDIUM,
                source="新闻稿",
                source_ref_ids=["ref_001"],
                date="2026-01-20",
            ),
        ],
        organization_insights=OrganizationInsights(
            possible_target_departments=["客户成功部", "销售部", "产品部"],
            recommended_target_roles=[
                RecommendedTargetRole(
                    role="客户成功负责人",
                    department="客户成功部",
                    reason="管理企业客户的服务交付和续约",
                    priority=1,
                ),
                RecommendedTargetRole(
                    role="销售负责人",
                    department="销售部",
                    reason="负责企业客户拓展和签约",
                    priority=2,
                ),
            ],
            possible_decision_chain=["销售挖掘线索", "客户成功评估服务能力", "产品确认交付方案", "管理层审批"],
            key_people_public_info=[],
        ),
        risk_signals=[
            RiskSignal(
                risk_type=RiskTypeEnum.ORGANIZATION_INSTABILITY,
                risk="快速扩张可能带来管理挑战",
                description="融资后快速扩张期，团队和管理体系可能不稳定",
                impact="合作过程中可能遇到对接人变动或流程调整",
                level=StrengthEnum.LOW,
                source="模型推断",
                source_ref_ids=[],
                date="2026-03-12",
            ),
        ],
        sales_assessment=SalesAssessment(
            customer_fit_level=CustomerFitLevelEnum.MEDIUM,
            opportunity_level=OpportunityLevelEnum.HIGH,
            follow_up_priority=FollowUpPriorityEnum.P2,
            core_opportunity_scenarios=[
                "客户服务管理",
                "销售流程优化",
                "培训交付管理",
            ],
            main_obstacles=[
                "可能已有内部系统",
                "预算分配不确定",
            ],
            assessment_summary="教育企业处于快速成长期，客户管理和服务交付需求明确，建议关注客户成功场景。",
            should_follow_up=True,
        ),
        communication_strategy=CommunicationStrategy(
            recommended_entry_points=[
                "企业客户服务管理",
                "培训交付效率提升",
                "客户续约率管理",
            ],
            avoid_points=[
                "忽视教育行业特点",
                "过度强调技术能力",
            ],
            opening_message="关注到贵司近期融资并签约多家企业客户，这个阶段客户服务管理压力通常会显著增加。",
            phone_script="您好，我们关注到贵司最近发展势头很好，签了多家企业客户。在线教育企业在客户规模扩大后，通常会面临客户服务交付和续约管理的挑战。我们这边有帮助企业优化客户管理和销售流程的经验，想看看是否有机会交流一下。",
            wechat_message="您好，关注到贵司近期的业务进展。在线教育企业在客户规模快速扩张阶段，客户服务交付和续约管理是常见的挑战。我们在这方面有一些实践经验，如果方便的话可以交流一下当前的管理重点。",
            email_message="您好，关注到贵司近期完成融资并签约多家企业客户。在线教育企业在快速成长阶段，客户服务管理、培训交付效率和客户续约率管理是常见的核心挑战。我们团队有服务于多家教育企业的实践经验，如果您愿意，我可以基于贵司当前的发展阶段分享一些可借鉴的经验。",
            next_step_suggestion="优先联系客户成功负责人或销售负责人，围绕客户服务管理和续约场景发起交流。",
        ),
        evidence_references=[
            EvidenceReference(
                reference_id="ref_001",
                source="新闻稿",
                title=f"{company_name}与多家企业达成培训合作",
                url="https://example.com/news/3",
                date="2026-01-20",
                excerpt="公司与多家大型企业签订年度培训服务协议。",
            ),
            EvidenceReference(
                reference_id="ref_002",
                source="新闻稿",
                title=f"{company_name}完成B轮融资",
                url="https://example.com/news/4",
                date="2025-10-08",
                excerpt="公司完成B轮融资，金额数千万元。",
            ),
        ],
    )


def _get_default_mock(company_name: str, user_input: Input) -> DueDiligenceOutput:
    """默认 Mock 数据"""
    return DueDiligenceOutput(
        meta=Meta(
            report_id=_generate_report_id(),
            generated_at=datetime.now(),
            language=LanguageEnum.ZH_CN,
            version="mvp_v1",
        ),
        input=user_input,
        company_profile=CompanyProfile(
            company_name=company_name,
            short_name=company_name[:4] if len(company_name) >= 4 else company_name,
            industry=["综合"],
            company_type="民营企业",
            founded_year=2016,
            headquarters="上海",
            business_scope=["综合业务"],
            main_products_or_services=["产品服务"],
            estimated_size="100-500人",
            region_coverage=["华东"],
            official_website=f"https://www.{company_name[:4].lower()}.com",
            official_accounts=["微信公众号：" + company_name],
            profile_summary="一家综合性企业，业务涉及多个领域。",
        ),
        recent_developments=[
            RecentDevelopment(
                date="2026-02-01",
                type=RecentDevelopmentTypeEnum.NEWS,
                title="公司发展动态",
                summary="公司近期保持稳定发展态势。",
                source="公开信息",
                source_ref_ids=["ref_001"],
                confidence=0.7,
            ),
        ],
        demand_signals=[
            DemandSignal(
                signal_type=DemandSignalTypeEnum.OTHER,
                signal="企业信息待进一步调研",
                evidence="公开信息有限",
                inference="需要更多信息来判断企业需求",
                strength=StrengthEnum.LOW,
                source="公开信息",
                source_ref_ids=["ref_001"],
                date="2026-02-01",
            ),
        ],
        organization_insights=OrganizationInsights(
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
        ),
        risk_signals=[
            RiskSignal(
                risk_type=RiskTypeEnum.UNCLEAR_DEMAND,
                risk="企业需求不明确",
                description="公开信息有限，难以判断具体需求场景",
                impact="需要更多调研才能确定合作可能性",
                level=StrengthEnum.MEDIUM,
                source="模型推断",
                source_ref_ids=[],
                date="2026-03-12",
            ),
        ],
        sales_assessment=SalesAssessment(
            customer_fit_level=CustomerFitLevelEnum.MEDIUM,
            opportunity_level=OpportunityLevelEnum.LOW,
            follow_up_priority=FollowUpPriorityEnum.P3,
            core_opportunity_scenarios=[
                "待进一步了解",
            ],
            main_obstacles=[
                "信息不足",
                "需求不明确",
            ],
            assessment_summary="公开信息有限，建议进一步调研后再确定跟进策略。",
            should_follow_up=False,
        ),
        communication_strategy=CommunicationStrategy(
            recommended_entry_points=[
                "了解企业现状",
                "探索合作机会",
            ],
            avoid_points=[
                "盲目推销产品",
            ],
            opening_message="我们对贵司的了解还不够充分，希望能进一步交流。",
            phone_script="您好，我们希望了解更多关于贵司业务发展的信息，看看是否有合作的机会。",
            wechat_message="您好，我们希望进一步了解贵司的业务情况，如果有方便的时间可以交流一下。",
            email_message="您好，我们希望进一步了解贵司的业务发展方向和当前的管理重点，以便评估可能的合作机会。",
            next_step_suggestion="建议先通过公开渠道或人脉进一步了解企业情况。",
        ),
        evidence_references=[
            EvidenceReference(
                reference_id="ref_001",
                source="公开信息",
                title="公司基本信息",
                url="",
                date="2026-02-01",
                excerpt="公司公开信息。",
            ),
        ],
    )


def get_mock_analysis(
    company_name: str,
    user_company_product: str,
    company_website: Optional[str] = None,
    user_target_customer_profile: Optional[str] = None,
    sales_goal: SalesGoalEnum = SalesGoalEnum.FIRST_TOUCH,
    target_role: Optional[str] = None,
    extra_context: Optional[str] = None,
) -> DueDiligenceOutput:
    """
    获取 Mock 分析数据

    根据企业名称关键词返回不同类型的 Mock 数据：
    - 包含"科技"、"软件"、"信息"等关键词：科技类企业
    - 包含"制造"、"机械"、"工业"等关键词：制造类企业
    - 包含"教育"、"培训"、"学校"等关键词：教育类企业
    - 其他：默认 Mock 数据

    Args:
        company_name: 目标企业名称
        user_company_product: 我方产品/服务描述
        company_website: 目标企业官网
        user_target_customer_profile: 我方理想客户画像
        sales_goal: 本次跟进目标
        target_role: 用户希望接触的角色
        extra_context: 用户补充背景

    Returns:
        DueDiligenceOutput: 完整的背调输出数据
    """
    # 构建用户输入
    user_input = Input(
        company_name=company_name,
        company_website=company_website,
        user_company_product=user_company_product,
        user_target_customer_profile=user_target_customer_profile,
        sales_goal=sales_goal,
        target_role=target_role,
        extra_context=extra_context,
    )

    # 根据企业名称关键词判断企业类型
    name_lower = company_name.lower()

    # 科技类企业关键词
    tech_keywords = ["科技", "软件", "信息", "网络", "互联网", "数字", "智能", "技术"]
    if any(keyword in name_lower for keyword in tech_keywords):
        return _get_tech_company_mock(company_name, user_input)

    # 制造类企业关键词
    manufacturing_keywords = ["制造", "机械", "工业", "设备", "材料", "电子", "汽车", "装备"]
    if any(keyword in name_lower for keyword in manufacturing_keywords):
        return _get_manufacturing_company_mock(company_name, user_input)

    # 教育类企业关键词
    education_keywords = ["教育", "培训", "学校", "学院", "学堂", "学习", "知识"]
    if any(keyword in name_lower for keyword in education_keywords):
        return _get_education_company_mock(company_name, user_input)

    # 默认返回通用 Mock 数据
    return _get_default_mock(company_name, user_input)