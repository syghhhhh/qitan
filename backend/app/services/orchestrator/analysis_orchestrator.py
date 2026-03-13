# -*- coding: utf-8 -*-
"""
AnalysisOrchestrator - 分析流程主编排器

作为后端分析服务的统一入口，负责：
- 接收 API 层传入的标准请求
- 初始化分析上下文和状态
- 组织各子模块的调用顺序
- 记录中间状态和错误
- 对失败模块进行降级处理
- 最终输出统一结果对象
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from ...schemas import (
    DueDiligenceOutput,
    Input,
    SalesGoalEnum,
)
from .pipeline_state import (
    PipelineStage,
    PipelineState,
    RunMode,
)


class AnalysisRequest(BaseModel):
    """
    分析请求统一封装

    将 API 层的请求参数封装为内部统一格式，
    便于 orchestrator 和下游模块处理。
    """

    company_name: str
    company_website: Optional[str] = None
    user_company_product: str = "CRM系统"
    user_target_customer_profile: Optional[str] = None
    sales_goal: SalesGoalEnum = SalesGoalEnum.FIRST_TOUCH
    target_role: Optional[str] = None
    extra_context: Optional[str] = None
    run_mode: RunMode = RunMode.FULL_MOCK  # 默认使用 full_mock 模式


class AnalysisOrchestrator:
    """
    分析流程主编排器

    负责协调各服务模块完成完整的企业背调分析任务。
    支持 full_mock、hybrid 和 full_pipeline 三种运行模式。

    使用方式：
        orchestrator = AnalysisOrchestrator()
        result = await orchestrator.analyze(request)
    """

    def __init__(self, default_run_mode: RunMode = RunMode.FULL_MOCK):
        """
        初始化编排器

        Args:
            default_run_mode: 默认运行模式，默认为 FULL_MOCK
        """
        self.default_run_mode = default_run_mode

    async def analyze(self, request: AnalysisRequest) -> DueDiligenceOutput:
        """
        执行完整的企业背调分析

        这是编排器的主入口方法，负责：
        1. 初始化 PipelineState
        2. 根据运行模式选择执行路径
        3. 依次调用各阶段模块
        4. 处理错误和降级
        5. 返回最终结果

        Args:
            request: 分析请求对象

        Returns:
            DueDiligenceOutput: 完整的背调输出结果
        """
        # 初始化流水线状态
        state = PipelineState(
            run_mode=request.run_mode,
            request=request.model_dump(),
        )

        try:
            # 根据运行模式选择执行路径
            if request.run_mode == RunMode.FULL_MOCK:
                result = await self._run_full_mock(state, request)
            elif request.run_mode == RunMode.HYBRID:
                result = await self._run_hybrid(state, request)
            else:
                result = await self._run_full_pipeline(state, request)

            # 更新最终状态
            state.update_stage(PipelineStage.COMPLETED)
            state.final_output = result.model_dump()

            return result

        except Exception as e:
            # 记录不可恢复的错误
            state.add_error(
                stage=state.current_stage,
                error_type=type(e).__name__,
                error_message=str(e),
                is_recoverable=False,
            )
            state.update_stage(PipelineStage.FAILED)

            # 尝试降级到 mock 模式
            state.add_error(
                stage=PipelineStage.INIT,
                error_type="FallbackToMock",
                error_message="主流程失败，降级到 mock 模式",
                is_recoverable=True,
                fallback_used=True,
                fallback_description="使用 mock 数据返回结果",
            )

            # 返回 mock 结果作为兜底
            return await self._get_fallback_mock_result(request)

    async def _run_full_mock(
        self, state: PipelineState, request: AnalysisRequest
    ) -> DueDiligenceOutput:
        """
        执行全 Mock 模式分析

        在此模式下，所有分析结果都来自 mock 数据生成器，
        适用于前端联调、演示和测试场景。

        Args:
            state: 流水线状态
            request: 分析请求

        Returns:
            DueDiligenceOutput: Mock 生成的背调结果
        """
        start_time = time.time()
        state.update_stage(PipelineStage.INIT)
        state.set_stage_status("init", "started")

        # 标记使用 mock 路径
        state.debug_info["execution_path"] = "full_mock"

        # 直接调用 mock_analyzer 获取结果
        # 延迟导入避免循环依赖
        from ..mock_analyzer import get_mock_analysis

        state.set_stage_status("init", "completed")
        state.set_stage_timing("init", time.time() - start_time)

        # 构建 Input 对象
        user_input = Input(
            company_name=request.company_name,
            company_website=request.company_website,
            user_company_product=request.user_company_product,
            user_target_customer_profile=request.user_target_customer_profile,
            sales_goal=request.sales_goal,
            target_role=request.target_role,
            extra_context=request.extra_context,
        )

        # 获取 mock 结果
        result = get_mock_analysis(
            company_name=request.company_name,
            user_company_product=request.user_company_product,
            company_website=request.company_website,
            user_target_customer_profile=request.user_target_customer_profile,
            sales_goal=request.sales_goal,
            target_role=request.target_role,
            extra_context=request.extra_context,
        )

        # 更新统计信息
        state.stage_timings["total"] = time.time() - start_time

        return result

    async def _run_hybrid(
        self, state: PipelineState, request: AnalysisRequest
    ) -> DueDiligenceOutput:
        """
        执行混合模式分析

        在此模式下，部分模块使用真实实现，部分模块使用 mock。
        当某个真实模块未实现或失败时，自动降级到 mock。

        当前阶段（v0.0.2）所有真实模块尚未完成，因此 hybrid 模式
        会自动降级为 full_mock 模式。

        Args:
            state: 流水线状态
            request: 分析请求

        Returns:
            DueDiligenceOutput: 混合模式生成的背调结果
        """
        start_time = time.time()
        state.debug_info["execution_path"] = "hybrid"

        # 当前阶段所有模块都未实现，记录警告并降级到 mock
        state.add_warning(
            stage=PipelineStage.INIT,
            warning_type="ModuleNotImplemented",
            warning_message="Hybrid 模式下所有真实模块尚未实现，降级到 full_mock",
        )

        # 降级到 full_mock
        result = await self._run_full_mock(state, request)
        state.stage_timings["total"] = time.time() - start_time

        return result

    async def _run_full_pipeline(
        self, state: PipelineState, request: AnalysisRequest
    ) -> DueDiligenceOutput:
        """
        执行全真实链路分析

        在此模式下，所有模块都使用真实实现。
        当前阶段（v0.0.2）尚不支持此模式，会自动降级。

        未来实现时，将按照以下顺序执行：
        1. context_builder - 构建分析上下文
        2. entity_resolver - 确认企业实体
        3. collection - 数据采集
        4. preprocessing - 证据预处理
        5. extraction - 事实抽取
        6. analysis - 业务分析
        7. scoring - 评分计算
        8. generation - 内容生成
        9. assembly - 结果组装

        Args:
            state: 流水线状态
            request: 分析请求

        Returns:
            DueDiligenceOutput: 真实链路生成的背调结果
        """
        start_time = time.time()
        state.debug_info["execution_path"] = "full_pipeline"

        # 当前阶段不支持 full_pipeline 模式
        state.add_warning(
            stage=PipelineStage.INIT,
            warning_type="ModeNotSupported",
            warning_message="Full pipeline 模式当前阶段不支持，降级到 hybrid",
        )

        # 降级到 hybrid（再由 hybrid 降级到 mock）
        result = await self._run_hybrid(state, request)
        state.stage_timings["total"] = time.time() - start_time

        return result

    async def _get_fallback_mock_result(
        self, request: AnalysisRequest
    ) -> DueDiligenceOutput:
        """
        获取兜底的 Mock 结果

        当主流程失败时，使用此方法返回 mock 结果作为兜底，
        确保系统始终能够返回有效响应。

        Args:
            request: 分析请求

        Returns:
            DueDiligenceOutput: Mock 生成的背调结果
        """
        from ..mock_analyzer import get_mock_analysis

        return get_mock_analysis(
            company_name=request.company_name,
            user_company_product=request.user_company_product,
            company_website=request.company_website,
            user_target_customer_profile=request.user_target_customer_profile,
            sales_goal=request.sales_goal,
            target_role=request.target_role,
            extra_context=request.extra_context,
        )

    def get_state_summary(self, state: PipelineState) -> Dict[str, Any]:
        """
        获取流水线状态摘要

        用于日志输出和调试追踪。

        Args:
            state: 流水线状态

        Returns:
            Dict: 状态摘要信息
        """
        return state.get_summary()


# 模块级单例实例，便于直接导入使用
_default_orchestrator: Optional[AnalysisOrchestrator] = None


def get_orchestrator(
    default_run_mode: RunMode = RunMode.FULL_MOCK,
) -> AnalysisOrchestrator:
    """
    获取编排器单例实例

    Args:
        default_run_mode: 默认运行模式

    Returns:
        AnalysisOrchestrator: 编排器实例
    """
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = AnalysisOrchestrator(default_run_mode)
    return _default_orchestrator