# -*- coding: utf-8 -*-
"""
编排层模块

负责分析链路的整体编排和流程控制，串联各模块完成完整分析任务。
"""

from __future__ import annotations

from .pipeline_state import (
    AnalysisResult,
    CandidateFact,
    PipelineStage,
    PipelineState,
    ProcessedEvidence,
    RawEvidence,
    ResolvedCompany,
    RunMode,
    StageError,
    StageWarning,
)

__all__ = [
    "AnalysisResult",
    "CandidateFact",
    "PipelineStage",
    "PipelineState",
    "ProcessedEvidence",
    "RawEvidence",
    "ResolvedCompany",
    "RunMode",
    "StageError",
    "StageWarning",
]