# -*- coding: utf-8 -*-
"""
PipelineState - 统一运行时状态容器

作为一次分析任务的运行时状态容器，记录分析链路中的中间产物：
- 原始请求
- 分析上下文
- 已确认企业对象
- 原始证据
- 清洗后证据
- 各类候选事实
- 各分析模块结果
- 评分明细
- 最终输出草稿
- 错误与降级信息
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class PipelineStage(str, Enum):
    """分析流程阶段枚举"""

    INIT = "init"  # 初始化
    CONTEXT_BUILD = "context_build"  # 上下文构建
    ENTITY_RESOLUTION = "entity_resolution"  # 实体确认
    COLLECTION = "collection"  # 数据采集
    PREPROCESSING = "preprocessing"  # 证据预处理
    EXTRACTION = "extraction"  # 事实抽取
    ANALYSIS = "analysis"  # 业务分析
    SCORING = "scoring"  # 评分计算
    GENERATION = "generation"  # 内容生成
    ASSEMBLY = "assembly"  # 结果组装
    COMPLETED = "completed"  # 完成
    FAILED = "failed"  # 失败


class RunMode(str, Enum):
    """运行模式枚举"""

    FULL_MOCK = "full_mock"  # 全流程 mock
    HYBRID = "hybrid"  # 混合模式：部分真实，部分 mock
    FULL_PIPELINE = "full_pipeline"  # 全流程真实


class StageError(BaseModel):
    """阶段错误记录"""

    stage: PipelineStage = Field(..., description="发生错误的阶段")
    error_type: str = Field(..., description="错误类型")
    error_message: str = Field(..., description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误发生时间")
    is_recoverable: bool = Field(default=True, description="是否可恢复")
    fallback_used: bool = Field(default=False, description="是否使用了降级方案")
    fallback_description: Optional[str] = Field(None, description="降级方案描述")


class StageWarning(BaseModel):
    """阶段警告记录"""

    stage: PipelineStage = Field(..., description="发生警告的阶段")
    warning_type: str = Field(..., description="警告类型")
    warning_message: str = Field(..., description="警告信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="警告发生时间")


class ResolvedCompany(BaseModel):
    """已确认的企业实体"""

    standard_name: str = Field(..., description="标准公司名称")
    domain: Optional[str] = Field(None, description="官网域名")
    aliases: List[str] = Field(default_factory=list, description="别名列表")
    confidence: float = Field(default=1.0, ge=0, le=1, description="实体识别置信度")
    resolution_notes: Optional[str] = Field(None, description="解析备注")


class RawEvidence(BaseModel):
    """原始证据"""

    evidence_id: str = Field(..., description="证据唯一ID")
    source_type: str = Field(..., description="来源类型，如官网/新闻/招聘/用户补充")
    url: Optional[str] = Field(None, description="来源URL")
    title: str = Field(..., description="证据标题")
    content: str = Field(..., description="证据内容")
    collected_at: datetime = Field(default_factory=datetime.now, description="采集时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class ProcessedEvidence(BaseModel):
    """处理后的证据"""

    evidence_id: str = Field(..., description="证据唯一ID")
    raw_evidence_id: str = Field(..., description="关联的原始证据ID")
    source_type: str = Field(..., description="来源类型")
    url: Optional[str] = Field(None, description="来源URL")
    title: str = Field(..., description="证据标题")
    cleaned_content: str = Field(..., description="清洗后的内容")
    normalized_date: Optional[str] = Field(None, description="标准化日期")
    quality_score: float = Field(default=0.5, ge=0, le=1, description="质量评分")
    relevance_score: float = Field(default=0.5, ge=0, le=1, description="相关性评分")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class CandidateFact(BaseModel):
    """候选事实"""

    fact_id: str = Field(..., description="事实唯一ID")
    fact_type: str = Field(..., description="事实类型，如 company_profile/recent_development/demand_signal 等")
    fact_data: Dict[str, Any] = Field(..., description="事实数据")
    source_evidence_ids: List[str] = Field(default_factory=list, description="来源证据ID列表")
    confidence: float = Field(default=0.5, ge=0, le=1, description="置信度")
    extracted_at: datetime = Field(default_factory=datetime.now, description="抽取时间")


class AnalysisResult(BaseModel):
    """分析结果"""

    result_type: str = Field(..., description="结果类型")
    result_data: Dict[str, Any] = Field(..., description="结果数据")
    source_fact_ids: List[str] = Field(default_factory=list, description="来源候选事实ID列表")
    confidence: float = Field(default=0.5, ge=0, le=1, description="置信度")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="分析时间")


class PipelineState(BaseModel):
    """
    分析链路统一运行时状态容器

    用于记录一次完整分析任务的所有中间状态和结果，支持：
    - 阶段性写入与读取
    - 错误记录与降级处理
    - 结果回放与调试追踪
    """

    # ========== 基础信息 ==========
    pipeline_id: str = Field(default_factory=lambda: f"pipe_{uuid4().hex[:12]}", description="流水线唯一ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="最后更新时间")

    # ========== 运行配置 ==========
    run_mode: RunMode = Field(default=RunMode.FULL_MOCK, description="运行模式")
    current_stage: PipelineStage = Field(default=PipelineStage.INIT, description="当前阶段")

    # ========== 输入数据 ==========
    request: Optional[Dict[str, Any]] = Field(None, description="原始请求参数")

    # ========== 分析上下文 ==========
    context: Optional[Dict[str, Any]] = Field(None, description="分析上下文")

    # ========== 实体确认 ==========
    resolved_company: Optional[ResolvedCompany] = Field(None, description="已确认的企业实体")

    # ========== 证据数据 ==========
    raw_evidence: List[RawEvidence] = Field(default_factory=list, description="原始证据列表")
    processed_evidence: List[ProcessedEvidence] = Field(default_factory=list, description="处理后证据列表")

    # ========== 候选事实 ==========
    candidate_facts: List[CandidateFact] = Field(default_factory=list, description="候选事实列表")

    # ========== 分析结果 ==========
    analysis_results: Dict[str, AnalysisResult] = Field(default_factory=dict, description="分析结果，按类型索引")

    # ========== 评分结果 ==========
    scoring_results: Optional[Dict[str, Any]] = Field(None, description="评分结果")

    # ========== 最终输出 ==========
    final_output: Optional[Dict[str, Any]] = Field(None, description="最终输出")

    # ========== 错误与警告 ==========
    errors: List[StageError] = Field(default_factory=list, description="错误记录")
    warnings: List[StageWarning] = Field(default_factory=list, description="警告记录")

    # ========== 调试信息 ==========
    debug_info: Dict[str, Any] = Field(default_factory=dict, description="调试信息")

    # ========== 统计信息 ==========
    stage_timings: Dict[str, float] = Field(default_factory=dict, description="各阶段耗时(秒)")
    stage_status: Dict[str, str] = Field(default_factory=dict, description="各阶段状态")

    # ========== 方法 ==========

    def update_stage(self, stage: PipelineStage) -> None:
        """更新当前阶段"""
        self.current_stage = stage
        self.updated_at = datetime.now()

    def add_error(
        self,
        stage: PipelineStage,
        error_type: str,
        error_message: str,
        is_recoverable: bool = True,
        fallback_used: bool = False,
        fallback_description: Optional[str] = None,
    ) -> None:
        """添加错误记录"""
        error = StageError(
            stage=stage,
            error_type=error_type,
            error_message=error_message,
            is_recoverable=is_recoverable,
            fallback_used=fallback_used,
            fallback_description=fallback_description,
        )
        self.errors.append(error)
        self.updated_at = datetime.now()

    def add_warning(
        self,
        stage: PipelineStage,
        warning_type: str,
        warning_message: str,
    ) -> None:
        """添加警告记录"""
        warning = StageWarning(
            stage=stage,
            warning_type=warning_type,
            warning_message=warning_message,
        )
        self.warnings.append(warning)
        self.updated_at = datetime.now()

    def add_raw_evidence(self, evidence: RawEvidence) -> None:
        """添加原始证据"""
        self.raw_evidence.append(evidence)
        self.updated_at = datetime.now()

    def add_processed_evidence(self, evidence: ProcessedEvidence) -> None:
        """添加处理后证据"""
        self.processed_evidence.append(evidence)
        self.updated_at = datetime.now()

    def add_candidate_fact(self, fact: CandidateFact) -> None:
        """添加候选事实"""
        self.candidate_facts.append(fact)
        self.updated_at = datetime.now()

    def set_analysis_result(self, result_type: str, result: AnalysisResult) -> None:
        """设置分析结果"""
        self.analysis_results[result_type] = result
        self.updated_at = datetime.now()

    def get_analysis_result(self, result_type: str) -> Optional[AnalysisResult]:
        """获取分析结果"""
        return self.analysis_results.get(result_type)

    def set_stage_timing(self, stage: str, duration_seconds: float) -> None:
        """设置阶段耗时"""
        self.stage_timings[stage] = duration_seconds
        self.updated_at = datetime.now()

    def set_stage_status(self, stage: str, status: str) -> None:
        """设置阶段状态"""
        self.stage_status[stage] = status
        self.updated_at = datetime.now()

    def has_errors(self) -> bool:
        """是否存在错误"""
        return len(self.errors) > 0

    def has_unrecoverable_errors(self) -> bool:
        """是否存在不可恢复的错误"""
        return any(not e.is_recoverable for e in self.errors)

    def get_summary(self) -> Dict[str, Any]:
        """获取状态摘要，用于日志和调试"""
        return {
            "pipeline_id": self.pipeline_id,
            "run_mode": self.run_mode.value,
            "current_stage": self.current_stage.value,
            "has_errors": self.has_errors(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "raw_evidence_count": len(self.raw_evidence),
            "processed_evidence_count": len(self.processed_evidence),
            "candidate_fact_count": len(self.candidate_facts),
            "analysis_result_types": list(self.analysis_results.keys()),
            "has_final_output": self.final_output is not None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def get_debug_summary(self) -> Dict[str, Any]:
        """获取详细调试摘要"""
        return {
            "summary": self.get_summary(),
            "resolved_company": self.resolved_company.model_dump() if self.resolved_company else None,
            "errors": [e.model_dump() for e in self.errors],
            "warnings": [w.model_dump() for w in self.warnings],
            "stage_timings": self.stage_timings,
            "stage_status": self.stage_status,
            "debug_info": self.debug_info,
        }

    class Config:
        """Pydantic 配置"""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }