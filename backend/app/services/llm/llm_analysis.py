# -*- coding: utf-8 -*-
"""
LLM 分析模块

将企查查采集到的企业数据传给大模型，生成完整的分析结果，包括：
- 企业画像 (company_profile)
- 近期动态 (recent_developments) - 基于已有数据推断
- 需求信号 (demand_signals)
- 风险信号 (risk_signals)
- 组织洞察 (organization_insights)
- 商务判断 (sales_assessment)
- 沟通策略 (communication_strategy)
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .llm_client import (
    BaseLLMClient,
    LLMMessage,
    LLMProvider,
    LLMRequest,
    PoeLLMClient,
    get_llm_client,
    set_llm_client,
)


def _get_or_init_poe_client() -> BaseLLMClient:
    """获取 POE LLM 客户端，如果未初始化则用 POE 初始化"""
    from .llm_client import _default_client

    # 如果已有 client 且是 Poe 类型，直接返回
    if _default_client is not None and isinstance(_default_client, PoeLLMClient):
        return _default_client

    # 创建带代理的 POE client
    client = PoeLLMClient(proxy="http://127.0.0.1:7890")
    set_llm_client(client)
    return client


def _build_analysis_prompt(
    company_name: str,
    verify_data: Dict[str, Any],
    user_company_product: str,
    sales_goal: str,
    target_role: Optional[str],
    extra_context: Optional[str],
) -> str:
    """构建完整分析提示词"""

    # 格式化企业数据
    company_info_parts = []
    if verify_data:
        company_info_parts.append(f"企业名称: {verify_data.get('Name', company_name)}")
        company_info_parts.append(f"英文名称: {verify_data.get('EnglishName', '无')}")
        company_info_parts.append(f"法定代表人: {verify_data.get('OperName', '未知')}")
        company_info_parts.append(f"经营状态: {verify_data.get('Status', '未知')}")
        company_info_parts.append(f"成立日期: {verify_data.get('StartDate', '未知')}")
        company_info_parts.append(f"注册资本: {verify_data.get('RegistCapi', '未知')}")
        company_info_parts.append(f"企业类型: {verify_data.get('EconKind', '未知')}")
        company_info_parts.append(f"纳税人类型: {verify_data.get('TaxpayerType', '未知')}")
        company_info_parts.append(f"参保人数: {verify_data.get('InsuredCount', '0')}")
        company_info_parts.append(f"企业规模标识: {verify_data.get('Scale', '未知')}")
        company_info_parts.append(f"是否小微企业: {'是' if verify_data.get('IsSmall') == '1' else '否'}")

        area = verify_data.get("Area", {})
        if area:
            company_info_parts.append(f"所在地区: {area.get('Province', '')}{area.get('City', '')}{area.get('County', '')}")

        company_info_parts.append(f"详细地址: {verify_data.get('Address', '未知')}")

        industry = verify_data.get("Industry", {})
        if industry:
            company_info_parts.append(f"国标行业: {industry.get('Industry', '未知')}")

        qcc_industry = verify_data.get("QccIndustry", {})
        if qcc_industry:
            company_info_parts.append(f"细分行业: {qcc_industry.get('AName', '')}-{qcc_industry.get('BName', '')}-{qcc_industry.get('CName', '')}-{qcc_industry.get('DName', '')}")

        scope = verify_data.get("Scope", "")
        if scope:
            company_info_parts.append(f"经营范围: {scope}")

        contact = verify_data.get("ContactInfo", {})
        if contact:
            if contact.get("Email"):
                company_info_parts.append(f"邮箱: {contact['Email']}")
            if contact.get("Tel"):
                company_info_parts.append(f"电话: {contact['Tel']}")
    else:
        company_info_parts.append(f"企业名称: {company_name}")
        company_info_parts.append("（仅有企业名称，无详细工商数据）")

    company_info_text = "\n".join(company_info_parts)

    # 销售目标描述
    goal_descriptions = {
        "lead_generation": "判断企业是否值得进入销售线索池",
        "first_touch": "首次触达，需要切入点和话术建议",
        "meeting_prep": "会前准备，需要了解企业近况和组织结构",
        "solution_pitch": "方案推进，需要匹配业务场景",
        "account_planning": "客户经营规划，需要多维度分析",
        "other": "综合分析",
    }
    goal_desc = goal_descriptions.get(sales_goal, "综合分析")

    prompt = f"""你是一个专业的企业背调分析智能体。请根据以下企业工商信息，结合你的知识，生成一份完整的企业背调分析报告。

## 企业工商数据
{company_info_text}

## 分析需求
- 我方产品/服务: {user_company_product}
- 本次跟进目标: {sales_goal} ({goal_desc})
{f'- 目标联系角色: {target_role}' if target_role else ''}
{f'- 补充背景: {extra_context}' if extra_context else ''}

## 输出要求
请以 JSON 格式输出以下内容，不要输出任何其他文字：

```json
{{
  "company_profile": {{
    "company_name": "完整企业名称",
    "short_name": "企业简称（2-4字）",
    "industry": ["行业标签1", "行业标签2"],
    "company_type": "企业类型（如民营企业/国有企业/外商投资等）",
    "founded_year": 成立年份数字,
    "headquarters": "总部所在城市",
    "business_scope": ["主营业务1", "主营业务2"],
    "main_products_or_services": ["产品或服务1", "产品或服务2"],
    "estimated_size": "员工规模估计（如50人以下/50-100人/100-500人/500-1000人/1000人以上）",
    "region_coverage": ["业务覆盖区域"],
    "official_website": "官网地址或null",
    "profile_summary": "一段100-200字的企业画像摘要"
  }},
  "recent_developments": [
    {{
      "date": "YYYY-MM",
      "type": "news/financing/hiring/expansion/new_product/partnership/digital_transformation/other",
      "title": "动态标题",
      "summary": "动态摘要",
      "source": "信息来源",
      "confidence": 0.5到1.0的置信度
    }}
  ],
  "demand_signals": [
    {{
      "signal_type": "recruitment_signal/expansion_signal/digitalization_signal/growth_signal/management_signal/other",
      "signal": "观察到的客观信号",
      "evidence": "支撑该信号的证据",
      "inference": "基于事实得出的商务推断",
      "strength": "high/medium/low"
    }}
  ],
  "risk_signals": [
    {{
      "risk_type": "legal/compliance/financial/reputation/procurement_complexity/organization_instability/low_budget_probability/other",
      "risk": "风险简述",
      "description": "风险详细说明",
      "impact": "对商务合作的影响",
      "level": "high/medium/low"
    }}
  ],
  "organization_insights": {{
    "possible_target_departments": ["可能的目标部门1", "部门2"],
    "recommended_target_roles": [
      {{
        "role": "角色名称",
        "department": "所属部门",
        "reason": "推荐理由",
        "priority": 1到10的优先级数字
      }}
    ],
    "possible_decision_chain": ["决策环节1", "环节2"]
  }},
  "sales_assessment": {{
    "customer_fit_level": "high/medium/low",
    "opportunity_level": "high/medium/low",
    "follow_up_priority": "P1/P2/P3/discard",
    "core_opportunity_scenarios": ["核心机会场景1", "场景2"],
    "main_obstacles": ["主要障碍1", "障碍2"],
    "assessment_summary": "100-200字的商务判断总结",
    "should_follow_up": true或false
  }},
  "communication_strategy": {{
    "recommended_entry_points": ["推荐切入点1", "切入点2"],
    "avoid_points": ["应避免的点1"],
    "opening_message": "一句话破冰建议（30-50字）",
    "phone_script": "电话话术（100-200字，包含自我介绍、切入话题、价值说明）",
    "wechat_message": "微信话术（50-100字，简洁有价值感）",
    "email_message": "邮件话术（150-250字，正式、有数据支撑）",
    "next_step_suggestion": "下一步行动建议"
  }}
}}
```

注意事项：
1. 基于已有的工商数据进行合理推断，但不要编造不存在的事实
2. 如果信息不足，在对应字段明确标注"信息有限"，不要胡编
3. 经营范围中的关键词可以帮助推断可能的需求信号
4. 根据企业规模、行业和经营范围推断适合的联系角色
5. 话术要具体、有针对性，引用企业的真实信息
6. 所有分析要围绕"我方产品: {user_company_product}"展开
7. 风险信号要保守，没有证据不要写
8. 近期动态如果没有真实新闻数据，可以根据企查查的经营状态和成立时间等信息给出基础判断，但要标注低置信度"""

    return prompt


def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """解析 LLM 返回的 JSON 文本"""
    import re

    # 尝试直接解析
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 代码块
    json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(json_block_pattern, response_text)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # 尝试查找 JSON 对象
    json_object_pattern = r"\{[\s\S]*\}"
    matches = re.findall(json_object_pattern, response_text)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    raise ValueError(f"无法从 LLM 响应中解析 JSON: {response_text[:500]}")


def run_llm_analysis(
    company_name: str,
    verify_data: Dict[str, Any],
    user_company_product: str,
    sales_goal: str,
    target_role: Optional[str] = None,
    extra_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    调用大模型执行企业背调分析

    Args:
        company_name: 企业名称
        verify_data: 企查查核验数据
        user_company_product: 我方产品/服务
        sales_goal: 销售目标
        target_role: 目标角色
        extra_context: 补充背景

    Returns:
        包含各分析模块结果的字典
    """
    # 获取 LLM 客户端
    client = _get_or_init_poe_client()

    # 构建提示词
    prompt = _build_analysis_prompt(
        company_name=company_name,
        verify_data=verify_data,
        user_company_product=user_company_product,
        sales_goal=sales_goal,
        target_role=target_role,
        extra_context=extra_context,
    )

    # 构建请求
    request = LLMRequest(
        messages=[
            LLMMessage(
                role="system",
                content="你是一个专业的企业背调分析智能体，擅长从企业工商信息中提取商业洞察。你的输出必须是严格的 JSON 格式。",
            ),
            LLMMessage(role="user", content=prompt),
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    # 调用 LLM（最多重试 2 次）
    last_error = None
    for attempt in range(3):
        response = client.complete(request)

        if not response.is_success:
            last_error = f"LLM 调用失败 (第{attempt+1}次): {response.error_message}"
            print(f"[LLM分析] {last_error}")
            continue

        try:
            parsed = _parse_llm_response(response.content)

            # 将解析结果转换为 PipelineState 需要的格式
            results = {}

            # company_profile
            if "company_profile" in parsed:
                results["company_profile"] = parsed["company_profile"]

            # recent_developments
            if "recent_developments" in parsed:
                results["recent_developments"] = {
                    "developments": parsed["recent_developments"]
                }

            # demand_signals
            if "demand_signals" in parsed:
                results["demand_signals"] = {
                    "signals": parsed["demand_signals"]
                }

            # risk_signals
            if "risk_signals" in parsed:
                results["risk_signals"] = {
                    "signals": parsed["risk_signals"]
                }

            # organization_insights
            if "organization_insights" in parsed:
                results["organization_insights"] = parsed["organization_insights"]

            # sales_assessment
            if "sales_assessment" in parsed:
                results["sales_assessment"] = parsed["sales_assessment"]

            # communication_strategy
            if "communication_strategy" in parsed:
                results["communication_strategy"] = parsed["communication_strategy"]

            print(f"[LLM分析] 成功解析分析结果，包含 {len(results)} 个模块")
            return results

        except Exception as e:
            last_error = f"解析 LLM 响应失败 (第{attempt+1}次): {e}"
            print(f"[LLM分析] {last_error}")
            continue

    raise ValueError(f"LLM 分析失败，已重试 3 次: {last_error}")
