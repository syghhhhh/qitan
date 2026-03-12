"""
话术生成 Prompt 模板

用途：基于商务分析结果生成：
- communication_strategy

适用于：
- 微信
- 邮件
- 电话开场
- 下一步推进建议
"""

from __future__ import annotations

# System Prompt
COMMUNICATION_SYSTEM_PROMPT = """你是一个B2B销售沟通助手。你的任务是根据企业背调结果，生成"自然、克制、可执行"的首次触达策略和话术。

要求：
1. 语气要专业、简洁，不要夸张，不要像群发广告。
2. 必须围绕企业近期动态、潜在场景和目标角色来写，不要空泛推销。
3. opening_message 应为一句话破冰建议。
4. phone_script 要适合电话开场，控制在简短可说完的长度。
5. wechat_message 要适合企业微信/微信初次触达，不宜过长。
6. email_message 要适合首次商务邮件，结构清楚，避免太硬的销售感。
7. recommended_entry_points 应对应"对方可能在意的问题"。
8. avoid_points 应提示不适合的切入方式。
9. next_step_suggestion 要给出一个明确、轻量的下一步动作建议。
10. 如果证据不足，话术要更保守，避免过强结论。
11. 输出必须是合法 JSON，不要输出任何多余说明。"""

# User Prompt Template
COMMUNICATION_USER_TEMPLATE = """请根据以下信息，输出首次触达沟通策略 JSON。

【我方产品/服务】
{user_company_product}

【本次销售目标】
{sales_goal}

【目标角色】
{target_role}

【企业基础画像与分析结果】
{analysis_data}

请输出以下 JSON 结构，不要增加额外字段：

{{
  "communication_strategy": {{
    "recommended_entry_points": [],
    "avoid_points": [],
    "opening_message": "",
    "phone_script": "",
    "wechat_message": "",
    "email_message": "",
    "next_step_suggestion": ""
  }}
}}"""


def render_communication_prompt(
    user_company_product: str,
    sales_goal: str = "",
    target_role: str = "",
    analysis_data: str = "",
) -> tuple[str, str]:
    """
    渲染话术生成 Prompt。

    Args:
        user_company_product: 我方产品/服务描述
        sales_goal: 本次销售目标
        target_role: 目标角色
        analysis_data: 企业基础画像与分析结果（JSON 字符串）

    Returns:
        (system_prompt, user_prompt) 元组
    """
    user_prompt = COMMUNICATION_USER_TEMPLATE.format(
        user_company_product=user_company_product or "未提供",
        sales_goal=sales_goal or "未提供",
        target_role=target_role or "未指定",
        analysis_data=analysis_data or "未提供",
    )
    return COMMUNICATION_SYSTEM_PROMPT, user_prompt