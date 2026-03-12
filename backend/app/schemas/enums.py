# -*- coding: utf-8 -*-
"""枚举字典 - 用于前端展示映射"""

from typing import Dict, Any

# meta.language
LANGUAGE_LABELS: Dict[str, str] = {
    "zh-CN": "简体中文",
    "en-US": "English (US)",
}

# input.sales_goal
SALES_GOAL_LABELS: Dict[str, Dict[str, str]] = {
    "lead_generation": {
        "label": "线索挖掘",
        "description": "判断企业是否值得进入销售线索池",
    },
    "first_touch": {
        "label": "首次触达",
        "description": "生成初次沟通建议和切入点",
    },
    "meeting_prep": {
        "label": "会前准备",
        "description": "为销售拜访或线上会议提供背景材料",
    },
    "solution_pitch": {
        "label": "方案推进",
        "description": "辅助识别业务场景和价值表达方向",
    },
    "account_planning": {
        "label": "客户经营",
        "description": "针对重点客户做账户规划和角色分析",
    },
    "other": {
        "label": "其他",
        "description": "保留扩展用途",
    },
}

# recent_developments[].type
RECENT_DEVELOPMENT_TYPE_LABELS: Dict[str, Dict[str, str]] = {
    "news": {
        "label": "新闻动态",
        "description": "泛新闻、媒体报道、企业公告",
    },
    "financing": {
        "label": "融资事件",
        "description": "融资、增资、投资并购等资本动作",
    },
    "hiring": {
        "label": "招聘动态",
        "description": "公开招聘、岗位扩张、关键岗位招聘",
    },
    "expansion": {
        "label": "业务扩张",
        "description": "区域扩张、团队扩张、渠道扩张、海外拓展",
    },
    "new_product": {
        "label": "新产品/新方案",
        "description": "发布新产品、新解决方案、新服务能力",
    },
    "bidding": {
        "label": "招投标相关",
        "description": "招标、中标、采购立项、集采等",
    },
    "partnership": {
        "label": "合作伙伴动态",
        "description": "生态合作、战略合作、渠道合作",
    },
    "digital_transformation": {
        "label": "数字化建设",
        "description": "信息化、数字化、系统建设、平台升级",
    },
    "management_change": {
        "label": "管理层变动",
        "description": "高管任命、组织调整、负责人变更",
    },
    "compliance": {
        "label": "合规相关",
        "description": "监管、资质、审计、整改、合规建设",
    },
    "other": {
        "label": "其他",
        "description": "不适合归类到上述类型的动态",
    },
}

# demand_signals[].signal_type
DEMAND_SIGNAL_TYPE_LABELS: Dict[str, Dict[str, str]] = {
    "recruitment_signal": {
        "label": "招聘信号",
        "description": "通过招聘岗位反映企业组织或能力建设方向",
    },
    "expansion_signal": {
        "label": "扩张信号",
        "description": "区域、业务、团队、渠道或市场扩张",
    },
    "digitalization_signal": {
        "label": "数字化信号",
        "description": "信息化系统建设、平台升级、流程数字化",
    },
    "growth_signal": {
        "label": "增长信号",
        "description": "融资、营收增长、业务增长、客户增长",
    },
    "management_signal": {
        "label": "管理升级信号",
        "description": "流程标准化、组织调整、经营管理升级",
    },
    "cost_reduction_signal": {
        "label": "降本增效信号",
        "description": "提效、自动化、成本控制、运营优化",
    },
    "compliance_signal": {
        "label": "合规信号",
        "description": "内控、审计、监管、资质、数据合规",
    },
    "customer_operation_signal": {
        "label": "客户经营信号",
        "description": "客户成功、会员运营、客户生命周期管理",
    },
    "sales_management_signal": {
        "label": "销售管理信号",
        "description": "销售流程、CRM、销售运营、商机管理",
    },
    "data_governance_signal": {
        "label": "数据治理信号",
        "description": "数据平台、数据质量、主数据、BI、治理体系",
    },
    "other": {
        "label": "其他信号",
        "description": "暂不归类",
    },
}

# demand_signals[].strength / risk_signals[].level
STRENGTH_LABELS: Dict[str, Dict[str, str]] = {
    "high": {
        "label": "强",
        "description": "有直接证据支撑，且与采购/建设场景高度相关",
    },
    "medium": {
        "label": "中",
        "description": "有一定证据支撑，但仍需进一步确认",
    },
    "low": {
        "label": "弱",
        "description": "仅为间接信号，推断成分较多",
    },
}

# risk_signals[].risk_type
RISK_TYPE_LABELS: Dict[str, Dict[str, str]] = {
    "legal": {
        "label": "法律风险",
        "description": "诉讼、仲裁、法律争议等",
    },
    "compliance": {
        "label": "合规风险",
        "description": "监管处罚、整改、资质问题、数据合规问题",
    },
    "financial": {
        "label": "财务风险",
        "description": "资金压力、经营异常、偿债压力等",
    },
    "reputation": {
        "label": "舆情风险",
        "description": "负面舆论、品牌形象受损",
    },
    "procurement_complexity": {
        "label": "采购复杂度高",
        "description": "招采流程复杂、审批链长、集采门槛高",
    },
    "organization_instability": {
        "label": "组织不稳定",
        "description": "高管频繁变动、组织频繁调整",
    },
    "low_budget_probability": {
        "label": "预算不足概率高",
        "description": "需求可能存在，但预算条件不明或偏弱",
    },
    "unclear_demand": {
        "label": "需求不清晰",
        "description": "缺少明确场景和强需求信号",
    },
    "long_decision_cycle": {
        "label": "决策周期长",
        "description": "涉及多部门、多层审批或大型采购流程",
    },
    "other": {
        "label": "其他风险",
        "description": "暂不归类",
    },
}

# sales_assessment.customer_fit_level
CUSTOMER_FIT_LEVEL_LABELS: Dict[str, Dict[str, str]] = {
    "high": {
        "label": "高匹配",
        "description": "行业、规模、业务模式、场景与我方目标客户高度一致",
    },
    "medium": {
        "label": "中匹配",
        "description": "存在一定适配性，但不是典型目标客户",
    },
    "low": {
        "label": "低匹配",
        "description": "行业、规模、场景或组织形态与我方产品明显不匹配",
    },
}

# sales_assessment.opportunity_level
OPPORTUNITY_LEVEL_LABELS: Dict[str, Dict[str, str]] = {
    "high": {
        "label": "高商机",
        "description": "近期存在明显需求信号，且与我方产品价值场景吻合",
    },
    "medium": {
        "label": "中商机",
        "description": "存在一些需求信号，但仍需进一步确认",
    },
    "low": {
        "label": "低商机",
        "description": "缺少有效需求信号，或当前窗口不明显",
    },
}

# sales_assessment.follow_up_priority
FOLLOW_UP_PRIORITY_LABELS: Dict[str, Dict[str, str]] = {
    "P1": {
        "label": "高优先级",
        "description": "建议尽快跟进，适合分配给销售做重点触达",
    },
    "P2": {
        "label": "中优先级",
        "description": "建议进入跟进池，择机触达",
    },
    "P3": {
        "label": "低优先级",
        "description": "建议保留观察，暂不重点投入",
    },
    "discard": {
        "label": "放弃",
        "description": "当前不建议继续投入销售资源",
    },
}

# organization_insights.recommended_target_roles[].priority
ROLE_PRIORITY_LABELS: Dict[int, str] = {
    1: "最高优先联系角色",
    2: "较高优先联系角色",
    3: "可作为备选切入角色",
    4: "低优先级辅助角色",
    5: "仅在特定场景下考虑",
}

# 企业规模标准化枚举
NORMALIZED_COMPANY_SIZE_LABELS: Dict[str, Dict[str, str]] = {
    "micro": {
        "label": "1-20人",
        "description": "微型团队",
    },
    "small": {
        "label": "21-99人",
        "description": "小型企业",
    },
    "medium": {
        "label": "100-499人",
        "description": "中型企业",
    },
    "large": {
        "label": "500-1999人",
        "description": "大型企业",
    },
    "enterprise": {
        "label": "2000人以上",
        "description": "超大型/集团型企业",
    },
    "unknown": {
        "label": "未知",
        "description": "公开信息不足",
    },
}

# 企业类型标准化枚举
NORMALIZED_COMPANY_TYPE_LABELS: Dict[str, str] = {
    "private": "民营企业",
    "state_owned": "国有企业",
    "foreign_owned": "外资企业",
    "joint_venture": "合资企业",
    "public_listed": "上市公司",
    "subsidiary": "子公司/分公司",
    "government_institution": "政府/事业单位",
    "nonprofit": "非营利组织",
    "other": "其他",
    "unknown": "未知",
}

# 来源类型标准化枚举
EVIDENCE_SOURCE_LABELS: Dict[str, str] = {
    "official_website": "官网",
    "official_wechat": "官方公众号",
    "news_media": "新闻媒体",
    "recruitment_posting": "招聘信息",
    "annual_report": "年报/财报/招股书",
    "registry_record": "工商/登记公开信息",
    "bidding_notice": "招标公告",
    "winning_notice": "中标公告",
    "social_media": "社交媒体",
    "user_input": "用户补充",
    "model_inference": "模型推断",
    "other": "其他",
}


def get_enum_label(enum_type: str, enum_value: str) -> str:
    """
    获取枚举值的中文标签

    Args:
        enum_type: 枚举类型名称
        enum_value: 枚举值

    Returns:
        中文标签，未找到则返回原值
    """
    label_maps: Dict[str, Dict[str, Any]] = {
        "language": LANGUAGE_LABELS,
        "sales_goal": SALES_GOAL_LABELS,
        "recent_development_type": RECENT_DEVELOPMENT_TYPE_LABELS,
        "demand_signal_type": DEMAND_SIGNAL_TYPE_LABELS,
        "strength": STRENGTH_LABELS,
        "risk_type": RISK_TYPE_LABELS,
        "customer_fit_level": CUSTOMER_FIT_LEVEL_LABELS,
        "opportunity_level": OPPORTUNITY_LEVEL_LABELS,
        "follow_up_priority": FOLLOW_UP_PRIORITY_LABELS,
        "normalized_company_size": NORMALIZED_COMPANY_SIZE_LABELS,
        "normalized_company_type": NORMALIZED_COMPANY_TYPE_LABELS,
        "evidence_source": EVIDENCE_SOURCE_LABELS,
    }

    label_map = label_maps.get(enum_type, {})
    value_info = label_map.get(enum_value, {})

    if isinstance(value_info, dict):
        return value_info.get("label", enum_value)
    return value_info if value_info else enum_value