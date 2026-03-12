"""
评分规则配置模块

基于 discuss004.md 的评分规则表定义，用于后续规则引擎。
评分框架：总分 100 分，由 4 个一级维度组成。
"""

from __future__ import annotations

from typing import Dict, List, Tuple


# =============================================================================
# 一、ICP 匹配度评分规则（0-35分）
# =============================================================================

ICP_FIT_MAX_SCORE = 35

ICP_FIT_ITEMS = {
    "industry_match": {
        "max": 12,
        "description": "行业匹配：是否属于目标行业或相邻行业",
        "rules": {
            "core_target_industry": 12,      # 明确属于核心目标行业
            "adjacent_industry": 8,          # 属于相邻可拓展行业
            "weak_related_industry": 4,      # 行业关联弱但可能可做
            "not_matched": 0,                # 明显不匹配
        }
    },
    "company_size_match": {
        "max": 8,
        "description": "企业规模匹配：员工规模、组织复杂度是否适配",
        "rules": {
            "ideal": 8,       # 完全符合目标规模带
            "acceptable": 5,  # 略大或略小，但仍可服务
            "weak": 2,        # 偏差明显，但理论可做
            "not_matched": 0, # 明显不适配
        }
    },
    "business_scenario_match": {
        "max": 10,
        "description": "业务场景匹配：是否存在我方产品对应场景",
        "rules": {
            "clear_core_scenario": 10,  # 明确存在核心业务场景
            "partial_scenario": 6,      # 存在部分可切入场景
            "weak_scenario": 3,         # 场景模糊，仅弱相关
            "no_scenario": 0,           # 无明显适配场景
        }
    },
    "company_type_match": {
        "max": 5,
        "description": "企业类型匹配：是否适合当前销售模式",
        "rules": {
            "highly_matched": 5,         # 与我方销售模式高度适配
            "partially_matched": 3,      # 存在一定适配性
            "complex_but_possible": 1,   # 流程复杂或成交门槛高
            "not_matched": 0,            # 基本不适配
        }
    }
}

# 客户匹配等级映射（基于 ICP 匹配度分数）
CUSTOMER_FIT_LEVEL_MAPPING: Dict[str, Tuple[int, int]] = {
    "high": (26, 35),    # 高匹配
    "medium": (15, 25),  # 中匹配
    "low": (0, 14),      # 低匹配
}


# =============================================================================
# 二、需求信号评分规则（0-35分）
# =============================================================================

DEMAND_SIGNAL_MAX_SCORE = 35

DEMAND_SIGNAL_ITEMS = {
    "recency": {
        "max": 10,
        "description": "动态新鲜度：最近 3-6 个月是否有变化",
        "rules": {
            "within_3_months_strong": 10,   # 近 3 个月有强相关动态
            "within_6_months_relevant": 7,  # 近 6 个月有相关动态
            "within_12_months_weak": 4,     # 近 12 个月有较弱动态
            "none": 0,                      # 无有效近期动态
        }
    },
    "signal_strength": {
        "max": 15,
        "description": "信号强度：是否直接指向采购/建设需求",
        "rules": {
            "direct_procurement_or_build_signal": 15,  # 有直接需求信号
            "strong_indirect_signal": 10,              # 有较强间接信号
            "weak_signal": 5,                          # 有弱信号
            "none": 0,                                 # 几乎无信号
        }
    },
    "multi_source_consistency": {
        "max": 10,
        "description": "多信号一致性：是否多个来源互相印证",
        "rules": {
            "three_or_more_sources": 10,   # 3个及以上不同来源互相印证
            "two_sources": 6,              # 2个来源相互支持
            "single_source": 3,            # 仅单一来源
            "no_reliable_chain": 0,        # 没有可靠证据链
        }
    }
}

# 商机等级映射（基于需求信号分数）
OPPORTUNITY_LEVEL_MAPPING: Dict[str, Tuple[int, int]] = {
    "high": (26, 35),    # 高商机
    "medium": (15, 25),  # 中商机
    "low": (0, 14),      # 低商机
}


# =============================================================================
# 三、可触达可行性评分规则（0-15分）
# =============================================================================

ENGAGEMENT_FEASIBILITY_MAX_SCORE = 15

ENGAGEMENT_FEASIBILITY_ITEMS = {
    "target_role_clarity": {
        "max": 5,
        "description": "目标角色清晰度：是否知道找谁",
        "rules": {
            "clear": 5,      # 明确知道优先接触角色
            "inferable": 3,  # 可推断 1-2 个关键角色
            "vague": 1,      # 角色模糊
            "unknown": 0,    # 基本无法判断
        }
    },
    "entry_point_clarity": {
        "max": 5,
        "description": "切入场景清晰度：是否知道聊什么",
        "rules": {
            "clear": 5,      # 有非常明确的业务切入点
            "general": 3,    # 有可讨论的通用场景
            "weak": 1,       # 场景比较泛
            "none": 0,       # 没有清晰切入点
        }
    },
    "decision_path_clarity": {
        "max": 5,
        "description": "组织路径可推断性：是否能大致判断决策链",
        "rules": {
            "clear": 5,      # 可判断主要决策链
            "partial": 3,    # 只能判断部分参与部门
            "weak": 1,       # 组织结构不清晰
            "unknown": 0,    # 完全无法判断
        }
    }
}


# =============================================================================
# 四、风险扣分规则（0-15分）
# =============================================================================

RISK_PENALTY_MAX_SCORE = 15

# 默认扣分规则（按风险等级）
DEFAULT_RISK_PENALTY = {
    "high": 5,
    "medium": 3,
    "low": 1,
}

# 按风险类型加权的扣分规则
WEIGHTED_RISK_PENALTY = {
    # 高影响风险类型：legal, compliance, financial
    "legal": {"high": 5, "medium": 4, "low": 2},
    "compliance": {"high": 5, "medium": 4, "low": 2},
    "financial": {"high": 5, "medium": 4, "low": 2},
    # 中影响风险类型
    "procurement_complexity": {"high": 4, "medium": 3, "low": 1},
    "organization_instability": {"high": 4, "medium": 3, "low": 1},
    "long_decision_cycle": {"high": 4, "medium": 3, "low": 1},
    # 低到中影响风险类型
    "unclear_demand": {"high": 3, "medium": 2, "low": 1},
    "low_budget_probability": {"high": 3, "medium": 2, "low": 1},
    "reputation": {"high": 3, "medium": 2, "low": 1},
    "other": {"high": 3, "medium": 2, "low": 1},
}


# =============================================================================
# 五、总分映射规则
# =============================================================================

FOLLOW_UP_PRIORITY_MAPPING: Dict[str, Tuple[int, int]] = {
    "P1": (75, 100),     # 高优先级：建议尽快跟进
    "P2": (55, 74),      # 中优先级：建议进入跟进池
    "P3": (35, 54),      # 低优先级：建议保留观察
    "discard": (0, 34),  # 放弃：不建议继续投入
}

# 总分解释
TOTAL_SCORE_DESCRIPTIONS = {
    (75, 100): "高匹配且近期窗口明确，值得优先投入",
    (55, 74): "有一定匹配度和商机，适合进入跟进池",
    (35, 54): "信息有限或信号较弱，建议观察或轻触达",
    (0, 34): "不适合当前投入资源",
}


# =============================================================================
# 六、兜底规则
# =============================================================================

# 强制 discard 条件
FORCE_DISCARD_CONDITIONS: List[str] = [
    "customer_fit_level = low 且 opportunity_level = low",
    "存在 high 级 financial/legal/compliance 风险且无明确业务机会",
    "企业类型明显不适配当前产品交付方式",
    "信息极度不足，无法识别行业、规模和场景",
]

# 强制 P1 条件
FORCE_P1_CONDITIONS: List[str] = [
    "customer_fit_level = high 且 opportunity_level = high",
    "近3个月内存在明确数字化/采购/招聘相关强信号，且场景与产品高度匹配",
    "已有多个来源共同证明企业正在进行组织扩张或系统建设",
]

# 降级条件（即使总分高，也建议降级到 P2 或 P3）
DOWNGRADE_CONDITIONS: List[str] = [
    "采购链明显复杂，且当前无法识别关键角色",
    "需求信号较强，但预算/时机不明",
    "企业确有需求，但已高度怀疑被现有成熟系统锁定",
    "风险扣分较高（>=10）",
]


# =============================================================================
# 七、评分配置汇总
# =============================================================================

SCORE_CONFIG = {
    "dimensions": {
        "icp_fit_score": {
            "max": ICP_FIT_MAX_SCORE,
            "items": ICP_FIT_ITEMS,
        },
        "demand_signal_score": {
            "max": DEMAND_SIGNAL_MAX_SCORE,
            "items": DEMAND_SIGNAL_ITEMS,
        },
        "engagement_feasibility_score": {
            "max": ENGAGEMENT_FEASIBILITY_MAX_SCORE,
            "items": ENGAGEMENT_FEASIBILITY_ITEMS,
        },
        "risk_penalty_score": {
            "max": RISK_PENALTY_MAX_SCORE,
            "default_penalty": DEFAULT_RISK_PENALTY,
            "weighted_penalty": WEIGHTED_RISK_PENALTY,
        }
    },
    "mapping": {
        "customer_fit_level": CUSTOMER_FIT_LEVEL_MAPPING,
        "opportunity_level": OPPORTUNITY_LEVEL_MAPPING,
        "follow_up_priority": FOLLOW_UP_PRIORITY_MAPPING,
    },
    "override_rules": {
        "force_discard": FORCE_DISCARD_CONDITIONS,
        "force_p1": FORCE_P1_CONDITIONS,
        "downgrade": DOWNGRADE_CONDITIONS,
    }
}


# =============================================================================
# 八、辅助函数
# =============================================================================

def get_risk_penalty(risk_type: str, risk_level: str) -> int:
    """
    获取风险扣分值。

    Args:
        risk_type: 风险类型
        risk_level: 风险等级 (high/medium/low)

    Returns:
        扣分值
    """
    if risk_type in WEIGHTED_RISK_PENALTY:
        return WEIGHTED_RISK_PENALTY[risk_type].get(risk_level, 0)
    return DEFAULT_RISK_PENALTY.get(risk_level, 0)


def calculate_total_risk_penalty(risks: List[Dict[str, str]]) -> int:
    """
    计算总风险扣分（上限 15 分）。

    Args:
        risks: 风险列表，每个元素包含 risk_type 和 level

    Returns:
        总扣分值（不超过 15）
    """
    total_penalty = 0
    for risk in risks:
        risk_type = risk.get("risk_type", "other")
        risk_level = risk.get("level", "low")
        total_penalty += get_risk_penalty(risk_type, risk_level)

    return min(total_penalty, RISK_PENALTY_MAX_SCORE)


def map_score_to_level(score: int, mapping: Dict[str, Tuple[int, int]]) -> str:
    """
    将分数映射到等级。

    Args:
        score: 分数
        mapping: 等级映射字典

    Returns:
        等级字符串
    """
    for level, (min_score, max_score) in mapping.items():
        if min_score <= score <= max_score:
            return level
    return "unknown"


def calculate_total_score(
    icp_fit_score: int,
    demand_signal_score: int,
    engagement_feasibility_score: int,
    risk_penalty_score: int
) -> int:
    """
    计算总分。

    Args:
        icp_fit_score: ICP 匹配度分数 (0-35)
        demand_signal_score: 需求信号分数 (0-35)
        engagement_feasibility_score: 可触达可行性分数 (0-15)
        risk_penalty_score: 风险扣分 (0-15)

    Returns:
        总分 (0-100)
    """
    total = (
        icp_fit_score +
        demand_signal_score +
        engagement_feasibility_score -
        risk_penalty_score
    )
    return max(0, min(100, total))


def get_follow_up_priority(total_score: int) -> str:
    """
    根据总分获取跟进优先级。

    Args:
        total_score: 总分

    Returns:
        跟进优先级 (P1/P2/P3/discard)
    """
    return map_score_to_level(total_score, FOLLOW_UP_PRIORITY_MAPPING)


def get_customer_fit_level(icp_fit_score: int) -> str:
    """
    根据 ICP 匹配度分数获取客户匹配等级。

    Args:
        icp_fit_score: ICP 匹配度分数

    Returns:
        客户匹配等级 (high/medium/low)
    """
    return map_score_to_level(icp_fit_score, CUSTOMER_FIT_LEVEL_MAPPING)


def get_opportunity_level(demand_signal_score: int) -> str:
    """
    根据需求信号分数获取商机等级。

    Args:
        demand_signal_score: 需求信号分数

    Returns:
        商机等级 (high/medium/low)
    """
    return map_score_to_level(demand_signal_score, OPPORTUNITY_LEVEL_MAPPING)