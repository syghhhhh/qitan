# Prompt 模板设计文档

## 概述

本项目定义了三个核心 Prompt 模板，用于 LLM 调用。模板基于 `discuss003.md` 定义，实现于 `backend/app/prompts/` 目录。

## Prompt 模板列表

| 模板 | 文件 | 用途 |
|------|------|------|
| 企业信息抽取 | `extraction.py` | 从原始资料抽取结构化信息 |
| 商务分析 | `analysis.py` | 分析需求信号、推荐联系人、商务判断 |
| 话术生成 | `communication.py` | 生成微信/电话/邮件话术 |

---

## 1. 企业信息抽取 Prompt

### 用途

从原始资料（官网、新闻、招聘等）中抽取结构化信息，生成：
- `company_profile` - 企业画像
- `recent_developments` - 近期动态
- `risk_signals` - 风险提示
- `evidence_references` - 证据来源

### System Prompt 核心要求

```
你是一个企业公开信息抽取助手。你的任务是从用户提供的企业原始材料中，提取"客观事实信息"，并输出为严格的 JSON。

要求：
1. 只根据提供的材料提取，不要臆测没有依据的事实。
2. 信息不足时，使用空字符串、空数组或 null，不要编造。
3. 优先提取客观、可验证、可追溯的信息。
4. 将不同来源整理为 evidence_references，并给每条信息尽量关联 source_ref_ids。
5. recent_developments 只保留相对重要、与商务跟进相关的动态。
6. risk_signals 中仅保留可以从材料中直接看到的风险，或基于材料做出的非常弱推断。
7. 输出必须是合法 JSON，不要输出任何 JSON 之外的解释。
```

### User Prompt 输入变量

| 变量 | 说明 |
|------|------|
| company_name | 目标企业名称 |
| company_website | 目标企业官网 |
| raw_documents | 原始材料（格式化后的文档列表） |

### 渲染函数

```python
def render_extraction_prompt(
    company_name: str,
    company_website: str = "",
    raw_documents: str = "",
) -> tuple[str, str]:
    """
    渲染企业信息抽取 Prompt。

    Returns:
        (system_prompt, user_prompt) 元组
    """
```

### 辅助函数

```python
def format_raw_documents(documents: list[dict]) -> str:
    """
    将原始文档列表格式化为 Prompt 输入格式。

    Args:
        documents: 文档列表，每个文档包含 source, title, url, date, content 字段
    """
```

---

## 2. 商务分析 Prompt

### 用途

基于企业结构化信息和销售目标，输出：
- `demand_signals` - 需求信号
- `organization_insights` - 组织洞察与推荐联系人
- `sales_assessment` - 商务判断

### System Prompt 核心要求

```
你是一个ToB商务分析助手。你的任务是基于企业基础信息、近期动态、我方产品信息和销售目标，做"潜在商机判断"。

要求：
1. 必须区分"事实"和"推断"。
2. demand_signals 中：
   - signal = 事实信号
   - evidence = 支撑证据
   - inference = 商务推断
3. 不要因为信息少就过度乐观，也不要无依据判定为高商机。
4. recommended_target_roles 必须围绕"谁最可能对该场景负责"来推荐。
5. sales_assessment 必须综合企业匹配度、动态信号、决策难度等因素。
6. 如果证据不足，应降低机会等级，并在 assessment_summary 中明确说明。
7. 输出必须是合法 JSON，不要输出任何多余解释。
```

### User Prompt 输入变量

| 变量 | 说明 |
|------|------|
| user_company_product | 我方产品/服务描述 |
| user_target_customer_profile | 我方理想客户画像 |
| sales_goal | 本次销售目标 |
| target_role | 希望接触角色 |
| extra_context | 额外上下文 |
| company_structured_data | 企业结构化信息（JSON） |

### 渲染函数

```python
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

    Returns:
        (system_prompt, user_prompt) 元组
    """
```

---

## 3. 话术生成 Prompt

### 用途

基于商务分析结果，生成首次触达策略和话术：
- `communication_strategy` - 沟通策略

### System Prompt 核心要求

```
你是一个B2B销售沟通助手。你的任务是根据企业背调结果，生成"自然、克制、可执行"的首次触达策略和话术。

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
11. 输出必须是合法 JSON，不要输出任何多余说明。
```

### User Prompt 输入变量

| 变量 | 说明 |
|------|------|
| user_company_product | 我方产品/服务描述 |
| sales_goal | 本次销售目标 |
| target_role | 目标角色 |
| analysis_data | 企业基础画像与分析结果（JSON） |

### 渲染函数

```python
def render_communication_prompt(
    user_company_product: str,
    sales_goal: str = "",
    target_role: str = "",
    analysis_data: str = "",
) -> tuple[str, str]:
    """
    渲染话术生成 Prompt。

    Returns:
        (system_prompt, user_prompt) 元组
    """
```

---

## 模块导出

```python
# backend/app/prompts/__init__.py

__all__ = [
    # 企业信息抽取
    "EXTRACTION_SYSTEM_PROMPT",
    "EXTRACTION_USER_TEMPLATE",
    "render_extraction_prompt",
    "format_raw_documents",
    # 商务分析
    "ANALYSIS_SYSTEM_PROMPT",
    "ANALYSIS_USER_TEMPLATE",
    "render_analysis_prompt",
    # 话术生成
    "COMMUNICATION_SYSTEM_PROMPT",
    "COMMUNICATION_USER_TEMPLATE",
    "render_communication_prompt",
]
```

---

## 使用示例

```python
from backend.app.prompts import (
    render_extraction_prompt,
    render_analysis_prompt,
    render_communication_prompt,
    format_raw_documents,
)

# 1. 企业信息抽取
documents = [
    {"source": "官网", "title": "公司介绍", "content": "..."},
    {"source": "招聘", "title": "销售经理", "content": "..."},
]
raw_docs = format_raw_documents(documents)
system, user = render_extraction_prompt(
    company_name="某科技有限公司",
    raw_documents=raw_docs
)

# 2. 商务分析
system, user = render_analysis_prompt(
    user_company_product="CRM系统",
    sales_goal="first_touch",
    company_structured_data=extraction_result_json
)

# 3. 话术生成
system, user = render_communication_prompt(
    user_company_product="CRM系统",
    sales_goal="first_touch",
    analysis_data=analysis_result_json
)
```