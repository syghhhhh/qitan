"""
商务分析 Prompt 模板

用途：基于输入信息和我方销售目标，输出：
- demand_signals
- organization_insights
- sales_assessment
"""

from __future__ import annotations

# System Prompt
ANALYSIS_SYSTEM_PROMPT = """你是一个ToB商务分析助手。你的任务是基于企业基础信息、近期动态、我方产品信息和销售目标，做"潜在商机判断"。

要求：
1. 必须区分"事实"和"推断"。
2. demand_signals 中：
   - signal = 事实信号
   - evidence = 支撑证据
   - inference = 商务推断
3. 不要因为信息少就过度乐观，也不要无依据判定为高商机。
4. recommended_target_roles 必须围绕"谁最可能对该场景负责"来推荐。
5. sales_assessment 必须综合以下因素：
   - 企业与我方ICP匹配度
   - 近期动态是否构成需求信号
   - 决策难度与推进风险
6. 如果证据不足，应降低机会等级，并在 assessment_summary 中明确说明。
7. 输出必须是合法 JSON，不要输出任何多余解释。"""

# User Prompt Template
ANALYSIS_USER_TEMPLATE = """请基于以下信息，输出企业的商务分析结果 JSON。

【我方产品/服务】
{user_company_product}

【我方理想客户画像】
{user_target_customer_profile}

【本次销售目标】
{sales_goal}

【希望接触角色】
{target_role}

【额外上下文】
{extra_context}

【企业结构化信息】
{company_structured_data}

请输出以下 JSON 结构，不要增加额外字段：

{{
  "demand_signals": [
    {{
      "signal_type": "",
      "signal": "",
      "evidence": "",
      "inference": "",
      "strength": "",
      "source": "",
      "source_ref_ids": [],
      "date": ""
    }}
  ],
  "organization_insights": {{
    "possible_target_departments": [],
    "recommended_target_roles": [
      {{
        "role": "",
        "department": "",
        "reason": "",
        "priority": 1
      }}
    ],
    "possible_decision_chain": [],
    "key_people_public_info": []
  }},
  "sales_assessment": {{
    "customer_fit_level": "",
    "opportunity_level": "",
    "follow_up_priority": "",
    "core_opportunity_scenarios": [],
    "main_obstacles": [],
    "assessment_summary": "",
    "should_follow_up": true
  }}
}}"""


def render_analysis_prompt(
    user_company_product: str,
    user_target_customer_profile: str = "",
    sales_goal: str = "",
    target_role: str = "",
    extra_context: str = "",
    company_structured_data: str = "",
) -> tuple[str, str]:
    """
    渲染商务分析 Prompt。

    Args:
        user_company_product: 我方产品/服务描述
        user_target_customer_profile: 我方理想客户画像
        sales_goal: 本次销售目标
        target_role: 希望接触角色
        extra_context: 额外上下文
        company_structured_data: 企业结构化信息（JSON 字符串）

    Returns:
        (system_prompt, user_prompt) 元组
    """
    user_prompt = ANALYSIS_USER_TEMPLATE.format(
        user_company_product=user_company_product or "未提供",
        user_target_customer_profile=user_target_customer_profile or "未提供",
        sales_goal=sales_goal or "未提供",
        target_role=target_role or "未指定",
        extra_context=extra_context or "无",
        company_structured_data=company_structured_data or "未提供",
    )
    return ANALYSIS_SYSTEM_PROMPT, user_prompt