"""
企业信息抽取 Prompt 模板

用途：把原始资料抽取为结构化信息，重点生成：
- company_profile
- recent_developments
- risk_signals
- evidence_references
"""

from __future__ import annotations

# System Prompt
EXTRACTION_SYSTEM_PROMPT = """你是一个企业公开信息抽取助手。你的任务是从用户提供的企业原始材料中，提取"客观事实信息"，并输出为严格的 JSON。

要求：
1. 只根据提供的材料提取，不要臆测没有依据的事实。
2. 信息不足时，使用空字符串、空数组或 null，不要编造。
3. 优先提取客观、可验证、可追溯的信息。
4. 将不同来源整理为 evidence_references，并给每条信息尽量关联 source_ref_ids。
5. recent_developments 只保留相对重要、与商务跟进相关的动态。
6. risk_signals 中仅保留可以从材料中直接看到的风险，或基于材料做出的非常弱推断；不要输出夸张结论。
7. 输出必须是合法 JSON，不要输出任何 JSON 之外的解释。
8. 如果用户材料中存在互相冲突的信息，保留较新来源，或在 summary 中简要体现不确定性。"""

# User Prompt Template
EXTRACTION_USER_TEMPLATE = """请根据以下输入，抽取企业公开信息并输出 JSON。

【目标企业】
{company_name}

【官网】
{company_website}

【原始材料】
{raw_documents}

原始材料可能包含以下内容：
- 官网介绍
- 新闻稿
- 招聘信息
- 公众号文章
- 工商/公开登记信息
- 用户手工补充文本

请输出以下 JSON 结构，不要增加额外字段：

{{
  "company_profile": {{
    "company_name": "",
    "short_name": "",
    "industry": [],
    "company_type": "",
    "founded_year": null,
    "headquarters": "",
    "business_scope": [],
    "main_products_or_services": [],
    "estimated_size": "",
    "region_coverage": [],
    "official_website": "",
    "official_accounts": [],
    "profile_summary": ""
  }},
  "recent_developments": [
    {{
      "date": "",
      "type": "",
      "title": "",
      "summary": "",
      "source": "",
      "source_ref_ids": [],
      "confidence": 0
    }}
  ],
  "risk_signals": [
    {{
      "risk_type": "",
      "risk": "",
      "description": "",
      "impact": "",
      "level": "",
      "source": "",
      "source_ref_ids": [],
      "date": ""
    }}
  ],
  "evidence_references": [
    {{
      "reference_id": "",
      "source": "",
      "title": "",
      "url": "",
      "date": "",
      "excerpt": ""
    }}
  ]
}}"""


def render_extraction_prompt(
    company_name: str,
    company_website: str = "",
    raw_documents: str = "",
) -> tuple[str, str]:
    """
    渲染企业信息抽取 Prompt。

    Args:
        company_name: 目标企业名称
        company_website: 目标企业官网
        raw_documents: 原始材料文本

    Returns:
        (system_prompt, user_prompt) 元组
    """
    user_prompt = EXTRACTION_USER_TEMPLATE.format(
        company_name=company_name,
        company_website=company_website or "未提供",
        raw_documents=raw_documents or "未提供",
    )
    return EXTRACTION_SYSTEM_PROMPT, user_prompt


def format_raw_documents(documents: list[dict]) -> str:
    """
    将原始文档列表格式化为 Prompt 输入格式。

    Args:
        documents: 文档列表，每个文档包含 source, title, url, date, content 字段

    Returns:
        格式化后的文档字符串

    Example:
        >>> docs = [
        ...     {"source": "官网", "title": "公司介绍", "url": "https://xxx.com/about", "date": "2026-03-01", "content": "..."},
        ...     {"source": "招聘信息", "title": "销售运营经理", "url": "https://xxx.com/jobs/123", "date": "2026-01-18", "content": "..."}
        ... ]
        >>> format_raw_documents(docs)
    """
    if not documents:
        return "未提供原始材料"

    formatted_parts = []
    for i, doc in enumerate(documents, 1):
        part = f"""[Doc {i}]
source: {doc.get('source', '未知')}
title: {doc.get('title', '未知')}
url: {doc.get('url', '未知')}
date: {doc.get('date', '未知')}
content: {doc.get('content', '')}"""
        formatted_parts.append(part)

    return "\n\n".join(formatted_parts)