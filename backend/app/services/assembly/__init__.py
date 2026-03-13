# -*- coding: utf-8 -*-
"""
组装模块

负责将分析层输出组装为统一 API 响应结构。
"""

from __future__ import annotations

from .output_assembler import (
    OutputAssembler,
    get_output_assembler,
    assemble_output,
)

__all__ = [
    "OutputAssembler",
    "get_output_assembler",
    "assemble_output",
]