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

from ...config import get_run_mode_config, RunModeConfig
from ...config.run_mode import RunMode
from ...schemas import (
    DueDiligenceOutput,
    Input,
    SalesGoalEnum,
)
from .pipeline_state import (
    PipelineStage,
    PipelineState,
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
    run_mode: RunMode = RunMode.FULL_PIPELINE  # 默认使用 full_pipeline 模式


class AnalysisOrchestrator:
    """
    分析流程主编排器

    负责协调各服务模块完成完整的企业背调分析任务。
    支持 full_mock、hybrid 和 full_pipeline 三种运行模式。

    使用方式：
        orchestrator = AnalysisOrchestrator()
        result = await orchestrator.analyze(request)
    """

    def __init__(
        self,
        default_run_mode: Optional[RunMode] = None,
        run_mode_config: Optional[RunModeConfig] = None,
    ):
        """
        初始化编排器

        Args:
            default_run_mode: 默认运行模式，如果为 None 则从配置获取
            run_mode_config: 运行模式配置实例，如果为 None 则使用全局配置
        """
        self.run_mode_config = run_mode_config or get_run_mode_config()
        self.default_run_mode = default_run_mode or self.run_mode_config.default_run_mode

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
        # 根据配置确定实际运行模式
        actual_run_mode = self.run_mode_config.get_run_mode(request.run_mode)

        # 初始化流水线状态
        state = PipelineState(
            run_mode=actual_run_mode,
            request=request.model_dump(),
        )

        # 记录模式切换信息
        if actual_run_mode != request.run_mode:
            state.add_warning(
                stage=PipelineStage.INIT,
                warning_type="RunModeChanged",
                warning_message=f"运行模式从 {request.run_mode.value} 切换到 {actual_run_mode.value}",
            )

        try:
            # 根据运行模式选择执行路径
            if actual_run_mode == RunMode.FULL_MOCK:
                result = await self._run_full_mock(state, request)
            elif actual_run_mode == RunMode.HYBRID:
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
            if self.run_mode_config.enable_auto_fallback:
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

            # 如果不允许自动降级，重新抛出异常
            raise

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
        from ..mock import get_mock_analysis

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

        根据配置中模块的实现状态决定使用真实实现还是 mock。

        Args:
            state: 流水线状态
            request: 分析请求

        Returns:
            DueDiligenceOutput: 混合模式生成的背调结果
        """
        start_time = time.time()
        state.debug_info["execution_path"] = "hybrid"

        # 获取模块状态摘要
        module_status = self.run_mode_config.get_module_status_summary()
        state.debug_info["module_status"] = module_status

        # 检查哪些模块可以使用真实实现
        can_use_real = []
        must_use_mock = []

        modules_to_check = [
            "context_builder",
            "entity_resolver",
            "website_collector",
            "news_collector",
            "company_profile_analyzer",
            "recent_development_analyzer",
            "output_assembler",
        ]

        for module_name in modules_to_check:
            if self.run_mode_config.should_use_mock_for_module(module_name):
                must_use_mock.append(module_name)
            else:
                can_use_real.append(module_name)

        state.debug_info["can_use_real"] = can_use_real
        state.debug_info["must_use_mock"] = must_use_mock

        # 如果大部分模块需要 mock，记录警告并降级
        if len(must_use_mock) > len(can_use_real):
            state.add_warning(
                stage=PipelineStage.INIT,
                warning_type="MostModulesNotImplemented",
                warning_message=f"Hybrid 模式下多数模块尚未实现 ({len(must_use_mock)}/{len(modules_to_check)})，降级到 full_mock",
            )
            result = await self._run_full_mock(state, request)
        else:
            state.add_warning(
                stage=PipelineStage.INIT,
                warning_type="PartialRealImplementation",
                warning_message=f"Hybrid 模式：{len(can_use_real)} 个模块使用真实实现，{len(must_use_mock)} 个模块使用 mock",
            )
            # 尝试走真实链路，失败则降级到 mock
            try:
                result = await self._run_full_pipeline(state, request)
            except Exception as e:
                state.add_warning(
                    stage=PipelineStage.INIT,
                    warning_type="HybridFallback",
                    warning_message=f"真实链路失败({e})，降级到 full_mock",
                )
                result = await self._run_full_mock(state, request)

        state.stage_timings["total"] = time.time() - start_time

        return result

    async def _run_full_pipeline(
        self, state: PipelineState, request: AnalysisRequest
    ) -> DueDiligenceOutput:
        """
        执行全真实链路分析

        流程：
        1. context_builder - 构建分析上下文
        2. entity_resolver - 通过企查查模糊搜索确认企业实体
        3. collection - 通过企查查企业信息核验获取企业数据
        4. analysis - 调用大模型(POE/gpt-5.4)生成全部分析结果
        5. assembly - 组装最终输出

        Args:
            state: 流水线状态
            request: 分析请求

        Returns:
            DueDiligenceOutput: 真实链路生成的背调结果
        """
        start_time = time.time()
        state.debug_info["execution_path"] = "full_pipeline"

        # ========== 阶段1: 构建分析上下文 ==========
        stage_start = time.time()
        state.update_stage(PipelineStage.CONTEXT_BUILD)
        state.set_stage_status("context_build", "started")

        from ..context.context_builder import get_context_builder

        context_builder = get_context_builder()
        context = context_builder.build(
            company_name=request.company_name,
            company_website=request.company_website,
            user_company_product=request.user_company_product,
            user_target_customer_profile=request.user_target_customer_profile,
            sales_goal=request.sales_goal,
            target_role=request.target_role,
            extra_context=request.extra_context,
        )
        state.context = context.model_dump()
        state.set_stage_status("context_build", "completed")
        state.set_stage_timing("context_build", time.time() - stage_start)

        # ========== 阶段2: 企查查数据采集（实体确认 + 企业信息）==========
        stage_start = time.time()
        state.update_stage(PipelineStage.COLLECTION)
        state.set_stage_status("collection", "started")

        company_data = {}
        try:
            from ..collection.qichacha_client import get_qichacha_client

            qcc_client = get_qichacha_client()
            company_data = qcc_client.get_company_info(request.company_name)

            # 更新 resolved_company
            verify_data = company_data.get("verify_data", {})
            accurate_name = company_data.get("accurate_name", request.company_name)

            state.resolved_company = ResolvedCompany(
                standard_name=accurate_name,
                domain=None,
                aliases=[request.company_name] if request.company_name != accurate_name else [],
                confidence=0.95,
                resolution_notes="通过企查查模糊搜索确认企业实体",
            )

            # 将企查查数据存入 raw_evidence
            from .pipeline_state import RawEvidence
            state.add_raw_evidence(RawEvidence(
                evidence_id="qcc_verify_001",
                source_type="企查查企业信息核验",
                url=None,
                title=f"{accurate_name} - 企业工商信息",
                content=_format_qcc_data(verify_data),
                metadata={"raw_verify_data": verify_data},
            ))

            state.set_stage_status("collection", "completed")

        except Exception as e:
            state.add_error(
                stage=PipelineStage.COLLECTION,
                error_type="QichachaError",
                error_message=f"企查查数据采集失败: {e}",
                is_recoverable=True,
            )
            state.set_stage_status("collection", "failed_with_fallback")
            # 即使采集失败，也继续用有限信息进行分析

        state.set_stage_timing("collection", time.time() - stage_start)

        # ========== 阶段3: 大模型分析（跳过预处理和抽取，直接分析）==========
        stage_start = time.time()
        state.update_stage(PipelineStage.ANALYSIS)
        state.set_stage_status("analysis", "started")

        try:
            from ..llm.llm_analysis import run_llm_analysis

            analysis_results = run_llm_analysis(
                company_name=company_data.get("accurate_name", request.company_name),
                verify_data=company_data.get("verify_data", {}),
                user_company_product=request.user_company_product,
                sales_goal=request.sales_goal.value if hasattr(request.sales_goal, 'value') else str(request.sales_goal),
                target_role=request.target_role,
                extra_context=request.extra_context,
            )

            # 将分析结果存入 PipelineState
            from .pipeline_state import AnalysisResult

            for result_type, result_data in analysis_results.items():
                state.set_analysis_result(
                    result_type,
                    AnalysisResult(
                        result_type=result_type,
                        result_data=result_data,
                        confidence=0.8,
                    ),
                )

            state.set_stage_status("analysis", "completed")

        except Exception as e:
            state.add_error(
                stage=PipelineStage.ANALYSIS,
                error_type="LLMAnalysisError",
                error_message=f"大模型分析失败: {e}",
                is_recoverable=True,
            )
            state.set_stage_status("analysis", "failed_with_fallback")

        state.set_stage_timing("analysis", time.time() - stage_start)

        # ========== 阶段4: 组装输出 ==========
        stage_start = time.time()
        state.update_stage(PipelineStage.ASSEMBLY)
        state.set_stage_status("assembly", "started")

        from ..assembly.output_assembler import get_output_assembler
        from ...schemas import Input

        user_input = Input(
            company_name=request.company_name,
            company_website=request.company_website,
            user_company_product=request.user_company_product,
            user_target_customer_profile=request.user_target_customer_profile,
            sales_goal=request.sales_goal,
            target_role=request.target_role,
            extra_context=request.extra_context,
        )

        assembler = get_output_assembler()
        result = assembler.assemble(state, user_input)

        state.set_stage_status("assembly", "completed")
        state.set_stage_timing("assembly", time.time() - stage_start)
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
        from ..mock import get_mock_analysis

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
    default_run_mode: Optional[RunMode] = None,
) -> AnalysisOrchestrator:
    """
    获取编排器单例实例

    Args:
        default_run_mode: 默认运行模式，如果为 None 则从配置获取

    Returns:
        AnalysisOrchestrator: 编排器实例
    """
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = AnalysisOrchestrator(default_run_mode)
    return _default_orchestrator


def reset_orchestrator() -> None:
    """
    重置编排器单例实例

    用于测试或需要重新加载配置的场景。
    """
    global _default_orchestrator
    _default_orchestrator = None


def _format_qcc_data(verify_data: Dict[str, Any]) -> str:
    """
    将企查查核验数据格式化为可读文本，用于作为 LLM 分析的输入

    Args:
        verify_data: 企查查企业信息核验返回的 Data 字典

    Returns:
        格式化后的文本
    """
    if not verify_data:
        return "无企业数据"

    parts = []
    parts.append(f"企业名称: {verify_data.get('Name', '未知')}")
    parts.append(f"英文名称: {verify_data.get('EnglishName', '无')}")
    parts.append(f"统一社会信用代码: {verify_data.get('CreditCode', '无')}")
    parts.append(f"法定代表人: {verify_data.get('OperName', '未知')}")
    parts.append(f"经营状态: {verify_data.get('Status', '未知')}")
    parts.append(f"成立日期: {verify_data.get('StartDate', '未知')}")
    parts.append(f"注册资本: {verify_data.get('RegistCapi', '未知')}")
    parts.append(f"企业类型: {verify_data.get('EconKind', '未知')}")
    parts.append(f"纳税人类型: {verify_data.get('TaxpayerType', '未知')}")
    parts.append(f"参保人数: {verify_data.get('InsuredCount', '未知')}")
    parts.append(f"企业规模: {verify_data.get('Scale', '未知')}")
    parts.append(f"是否小微企业: {'是' if verify_data.get('IsSmall') == '1' else '否'}")

    # 地区信息
    area = verify_data.get("Area", {})
    if area:
        parts.append(f"所在地区: {area.get('Province', '')}{area.get('City', '')}{area.get('County', '')}")

    parts.append(f"详细地址: {verify_data.get('Address', '未知')}")

    # 行业信息
    industry = verify_data.get("Industry", {})
    if industry:
        parts.append(f"行业分类: {industry.get('Industry', '未知')}")

    qcc_industry = verify_data.get("QccIndustry", {})
    if qcc_industry:
        parts.append(f"细分行业: {qcc_industry.get('AName', '')}-{qcc_industry.get('BName', '')}-{qcc_industry.get('CName', '')}-{qcc_industry.get('DName', '')}")

    # 经营范围
    scope = verify_data.get("Scope", "")
    if scope:
        parts.append(f"经营范围: {scope}")

    # 联系信息
    contact = verify_data.get("ContactInfo", {})
    if contact:
        if contact.get("Email"):
            parts.append(f"邮箱: {contact['Email']}")
        if contact.get("Tel"):
            parts.append(f"电话: {contact['Tel']}")

    return "\n".join(parts)