# -*- coding: utf-8 -*-
"""
编排层模块

负责分析链路的整体编排和流程控制，串联各模块完成完整分析任务。
"""

from __future__ import annotations

# RunMode 从 config 模块导入，保持向后兼容
from ...config.run_mode import RunMode
from .pipeline_state import (
    AnalysisResult,
    CandidateFact,
    PipelineStage,
    PipelineState,
    ProcessedEvidence,
    RawEvidence,
    ResolvedCompany,
    StageError,
    StageWarning,
)
from .analysis_orchestrator import (
    AnalysisOrchestrator,
    AnalysisRequest,
    get_orchestrator,
    reset_orchestrator,
)

__all__ = [
    # run_mode (从 config 模块重新导出，保持向后兼容)
    "RunMode",
    # pipeline_state
    "AnalysisResult",
    "CandidateFact",
    "PipelineStage",
    "PipelineState",
    "ProcessedEvidence",
    "RawEvidence",
    "ResolvedCompany",
    "StageError",
    "StageWarning",
    # analysis_orchestrator
    "AnalysisOrchestrator",
    "AnalysisRequest",
    "get_orchestrator",
    "reset_orchestrator",
]