# -*- coding: utf-8 -*-
"""
大模型适配模块

提供统一的 LLM 客户端接口，支持 Prompt 渲染和结构化生成。

模块组成：
- llm_client: 统一 LLM 客户端接口，支持多种提供商
- prompt_renderer: Prompt 模板渲染器
- structured_generation: 结构化输出生成器
"""

from __future__ import annotations

from .llm_client import (
    BaseLLMClient,
    LLMClientError,
    LLMMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMStatus,
    MockLLMClient,
    PoeLLMClient,
    get_llm_client,
    reset_llm_client,
    set_llm_client,
)
from .prompt_renderer import (
    PromptRenderer,
    PromptTemplate,
    PromptTemplateType,
    get_prompt_renderer,
    render_prompt,
)
from .structured_generation import (
    MockStructuredGenerator,
    OutputFormat,
    StructuredGenerator,
    StructuredOutputConfig,
    StructuredOutputResult,
    generate_structured_output,
    get_structured_generator,
    set_structured_generator,
)

__all__ = [
    # LLM Client
    "BaseLLMClient",
    "LLMClientError",
    "LLMMessage",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "LLMStatus",
    "MockLLMClient",
    "PoeLLMClient",
    "get_llm_client",
    "reset_llm_client",
    "set_llm_client",
    # Prompt Renderer
    "PromptRenderer",
    "PromptTemplate",
    "PromptTemplateType",
    "get_prompt_renderer",
    "render_prompt",
    # Structured Generation
    "MockStructuredGenerator",
    "OutputFormat",
    "StructuredGenerator",
    "StructuredOutputConfig",
    "StructuredOutputResult",
    "generate_structured_output",
    "get_structured_generator",
    "set_structured_generator",
]