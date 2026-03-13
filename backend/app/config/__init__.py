# -*- coding: utf-8 -*-
"""
配置模块

包含评分规则配置、运行模式配置等。
"""

from __future__ import annotations

from .run_mode import (
    ModuleConfig,
    ModuleStatus,
    PipelineModuleConfig,
    RunModeConfig,
    get_run_mode_config,
    set_run_mode_config,
)

__all__ = [
    # run_mode
    "ModuleConfig",
    "ModuleStatus",
    "PipelineModuleConfig",
    "RunModeConfig",
    "get_run_mode_config",
    "set_run_mode_config",
]