"""
Prompt 模板模块

包含三个核心 Prompt 模板：
1. extraction - 企业信息抽取
2. analysis - 商务分析
3. communication - 话术生成
"""

from backend.app.prompts.extraction import (
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_USER_TEMPLATE,
    format_raw_documents,
    render_extraction_prompt,
)
from backend.app.prompts.analysis import (
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_TEMPLATE,
    render_analysis_prompt,
)
from backend.app.prompts.communication import (
    COMMUNICATION_SYSTEM_PROMPT,
    COMMUNICATION_USER_TEMPLATE,
    render_communication_prompt,
)

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