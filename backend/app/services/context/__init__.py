# -*- coding: utf-8 -*-
"""
上下文模块

负责将 API 请求转换为统一的分析上下文，标准化输入字段。
"""

from __future__ import annotations

from .context_builder import (
    AnalysisContext,
    ContextBuilder,
    build_context,
    get_context_builder,
)

__all__ = [
    "AnalysisContext",
    "ContextBuilder",
    "build_context",
    "get_context_builder",
]