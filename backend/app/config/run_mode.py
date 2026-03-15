# -*- coding: utf-8 -*-
"""
运行模式配置模块

定义 full_mock、hybrid、full_pipeline 三种运行模式的配置能力。
支持通过环境变量或配置文件切换运行模式，并管理模块降级策略。

运行模式说明：
- full_mock: 全流程 mock，所有模块使用 mock 实现，稳定可靠
- hybrid: 混合模式，部分模块使用真实实现，未实现模块自动降级到 mock
- full_pipeline: 全流程真实，所有模块使用真实实现
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Any, Dict, Optional, Set

from pydantic import BaseModel, Field


class RunMode(str, Enum):
    """运行模式枚举"""

    FULL_MOCK = "full_mock"  # 全流程 mock
    HYBRID = "hybrid"  # 混合模式：部分真实，部分 mock
    FULL_PIPELINE = "full_pipeline"  # 全流程真实


class ModuleStatus(str, Enum):
    """模块实现状态"""

    IMPLEMENTED = "implemented"  # 已实现，可使用真实逻辑
    NOT_IMPLEMENTED = "not_implemented"  # 未实现，需使用 mock
    PARTIAL = "partial"  # 部分实现，可降级使用


class ModuleConfig(BaseModel):
    """单个模块的配置"""

    name: str = Field(..., description="模块名称")
    status: ModuleStatus = Field(default=ModuleStatus.NOT_IMPLEMENTED, description="实现状态")
    allow_mock_fallback: bool = Field(default=True, description="是否允许降级到 mock")
    enabled_sources: Set[str] = Field(default_factory=set, description="启用的数据源")

    def is_available_for_real(self) -> bool:
        """判断模块是否可用于真实链路"""
        return self.status == ModuleStatus.IMPLEMENTED

    def should_use_mock(self) -> bool:
        """判断是否应该使用 mock"""
        if self.status == ModuleStatus.IMPLEMENTED:
            return False
        return self.allow_mock_fallback


class PipelineModuleConfig(BaseModel):
    """流水线各模块配置"""

    # 上下文构建
    context_builder: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="context_builder",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="上下文构建模块",
    )

    # 实体解析
    entity_resolver: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="entity_resolver",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="实体解析模块",
    )

    # 数据采集（通过企查查 API 实现）
    website_collector: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="website_collector",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="官网采集模块（企查查API替代）",
    )

    news_collector: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="news_collector",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="新闻采集模块（LLM推断替代）",
    )

    # 证据预处理（当前版本跳过，由LLM直接处理）
    evidence_cleaner: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="evidence_cleaner",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="证据清洗模块（当前版本跳过）",
    )

    evidence_deduplicator: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="evidence_deduplicator",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="证据去重模块（当前版本跳过）",
    )

    evidence_normalizer: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="evidence_normalizer",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="证据标准化模块（当前版本跳过）",
    )

    evidence_ranker: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="evidence_ranker",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="证据排序模块（当前版本跳过）",
    )

    # 事实抽取（由LLM统一完成）
    company_profile_extractor: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="company_profile_extractor",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="企业画像抽取模块（LLM统一处理）",
    )

    development_extractor: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="development_extractor",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="近期动态抽取模块（LLM统一处理）",
    )

    # 业务分析（由LLM统一完成）
    company_profile_analyzer: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="company_profile_analyzer",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="企业画像分析模块（LLM统一处理）",
    )

    recent_development_analyzer: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="recent_development_analyzer",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="近期动态分析模块（LLM统一处理）",
    )

    # 结果组装
    output_assembler: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="output_assembler",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="输出组装模块",
    )

    output_validator: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="output_validator",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="输出校验模块",
    )

    # Mock 分析器
    mock_analyzer: ModuleConfig = Field(
        default_factory=lambda: ModuleConfig(
            name="mock_analyzer",
            status=ModuleStatus.IMPLEMENTED,
        ),
        description="Mock 分析模块",
    )


class RunModeConfig(BaseModel):
    """
    运行模式配置

    管理整体运行模式、模块配置和降级策略。
    支持通过环境变量 RUN_MODE 切换运行模式。
    """

    # 默认运行模式
    default_run_mode: RunMode = Field(
        default=RunMode.FULL_PIPELINE,
        description="默认运行模式",
    )

    # 各模块配置
    modules: PipelineModuleConfig = Field(
        default_factory=PipelineModuleConfig,
        description="流水线模块配置",
    )

    # 降级配置
    enable_auto_fallback: bool = Field(
        default=True,
        description="是否启用自动降级到 mock",
    )

    fallback_mode: RunMode = Field(
        default=RunMode.FULL_MOCK,
        description="降级时使用的运行模式",
    )

    # 日志配置
    log_mode_switch: bool = Field(
        default=True,
        description="是否记录模式切换日志",
    )

    def get_run_mode(self, request_mode: Optional[RunMode] = None) -> RunMode:
        """
        获取实际运行模式

        根据请求指定的模式和配置的默认模式，返回实际使用的运行模式。

        Args:
            request_mode: 请求指定的运行模式，如果为 None 则使用默认模式

        Returns:
            RunMode: 实际使用的运行模式
        """
        mode = request_mode or self.default_run_mode

        # 检查请求的模式是否可用
        if mode == RunMode.FULL_PIPELINE:
            if not self._check_full_pipeline_available():
                if self.log_mode_switch:
                    print(f"[RunModeConfig] full_pipeline 模式不可用，降级到 hybrid")
                mode = RunMode.HYBRID

        if mode == RunMode.HYBRID:
            if not self._check_hybrid_available():
                if self.log_mode_switch:
                    print(f"[RunModeConfig] hybrid 模式不可用，降级到 full_mock")
                mode = RunMode.FULL_MOCK

        return mode

    def _check_full_pipeline_available(self) -> bool:
        """检查 full_pipeline 模式是否可用"""
        required_modules = [
            self.modules.context_builder,
            self.modules.entity_resolver,
            self.modules.website_collector,
            self.modules.news_collector,
            self.modules.evidence_cleaner,
            self.modules.evidence_deduplicator,
            self.modules.evidence_normalizer,
            self.modules.evidence_ranker,
            self.modules.company_profile_extractor,
            self.modules.development_extractor,
            self.modules.company_profile_analyzer,
            self.modules.recent_development_analyzer,
            self.modules.output_assembler,
            self.modules.output_validator,
        ]

        return all(m.is_available_for_real() for m in required_modules)

    def _check_hybrid_available(self) -> bool:
        """检查 hybrid 模式是否可用"""
        # hybrid 模式至少需要基础模块实现
        required_modules = [
            self.modules.context_builder,
            self.modules.entity_resolver,
            self.modules.output_assembler,
            self.modules.output_validator,
            self.modules.mock_analyzer,
        ]

        return all(m.is_available_for_real() for m in required_modules)

    def should_use_mock_for_module(self, module_name: str) -> bool:
        """
        判断指定模块是否应使用 mock

        Args:
            module_name: 模块名称

        Returns:
            bool: True 表示应使用 mock，False 表示应使用真实实现
        """
        module_config = self._get_module_config(module_name)
        if module_config is None:
            return True  # 未知模块默认使用 mock

        return module_config.should_use_mock()

    def _get_module_config(self, module_name: str) -> Optional[ModuleConfig]:
        """获取指定模块的配置"""
        module_map = {
            "context_builder": self.modules.context_builder,
            "entity_resolver": self.modules.entity_resolver,
            "website_collector": self.modules.website_collector,
            "news_collector": self.modules.news_collector,
            "evidence_cleaner": self.modules.evidence_cleaner,
            "evidence_deduplicator": self.modules.evidence_deduplicator,
            "evidence_normalizer": self.modules.evidence_normalizer,
            "evidence_ranker": self.modules.evidence_ranker,
            "company_profile_extractor": self.modules.company_profile_extractor,
            "development_extractor": self.modules.development_extractor,
            "company_profile_analyzer": self.modules.company_profile_analyzer,
            "recent_development_analyzer": self.modules.recent_development_analyzer,
            "output_assembler": self.modules.output_assembler,
            "output_validator": self.modules.output_validator,
            "mock_analyzer": self.modules.mock_analyzer,
        }
        return module_map.get(module_name)

    def get_module_status_summary(self) -> Dict[str, Any]:
        """
        获取所有模块状态摘要

        Returns:
            Dict: 模块状态摘要
        """
        all_modules = [
            ("context_builder", self.modules.context_builder),
            ("entity_resolver", self.modules.entity_resolver),
            ("website_collector", self.modules.website_collector),
            ("news_collector", self.modules.news_collector),
            ("evidence_cleaner", self.modules.evidence_cleaner),
            ("evidence_deduplicator", self.modules.evidence_deduplicator),
            ("evidence_normalizer", self.modules.evidence_normalizer),
            ("evidence_ranker", self.modules.evidence_ranker),
            ("company_profile_extractor", self.modules.company_profile_extractor),
            ("development_extractor", self.modules.development_extractor),
            ("company_profile_analyzer", self.modules.company_profile_analyzer),
            ("recent_development_analyzer", self.modules.recent_development_analyzer),
            ("output_assembler", self.modules.output_assembler),
            ("output_validator", self.modules.output_validator),
            ("mock_analyzer", self.modules.mock_analyzer),
        ]

        implemented = [name for name, cfg in all_modules if cfg.is_available_for_real()]
        not_implemented = [name for name, cfg in all_modules if cfg.status == ModuleStatus.NOT_IMPLEMENTED]
        partial = [name for name, cfg in all_modules if cfg.status == ModuleStatus.PARTIAL]

        return {
            "total_modules": len(all_modules),
            "implemented_count": len(implemented),
            "not_implemented_count": len(not_implemented),
            "partial_count": len(partial),
            "implemented": implemented,
            "not_implemented": not_implemented,
            "partial": partial,
            "full_pipeline_available": self._check_full_pipeline_available(),
            "hybrid_available": self._check_hybrid_available(),
            "default_run_mode": self.default_run_mode.value,
        }


def _get_run_mode_from_env() -> RunMode:
    """从环境变量获取运行模式"""
    env_mode = os.environ.get("RUN_MODE", "full_pipeline").lower()
    mode_map = {
        "full_mock": RunMode.FULL_MOCK,
        "hybrid": RunMode.HYBRID,
        "full_pipeline": RunMode.FULL_PIPELINE,
    }
    return mode_map.get(env_mode, RunMode.FULL_MOCK)


def get_run_mode_config() -> RunModeConfig:
    """
    获取运行模式配置单例

    Returns:
        RunModeConfig: 运行模式配置实例
    """
    global _run_mode_config
    if _run_mode_config is None:
        default_mode = _get_run_mode_from_env()
        _run_mode_config = RunModeConfig(default_run_mode=default_mode)
    return _run_mode_config


def set_run_mode_config(config: RunModeConfig) -> None:
    """
    设置运行模式配置

    Args:
        config: 运行模式配置实例
    """
    global _run_mode_config
    _run_mode_config = config


# 全局配置实例
_run_mode_config: Optional[RunModeConfig] = None