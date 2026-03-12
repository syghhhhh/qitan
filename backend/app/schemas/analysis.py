# -*- coding: utf-8 -*-
"""分析相关数据模型定义"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DemandSignalTypeEnum(str, Enum):
    """需求信号类型枚举"""

    RECRUITMENT_SIGNAL = "recruitment_signal"
    EXPANSION_SIGNAL = "expansion_signal"
    DIGITALIZATION_SIGNAL = "digitalization_signal"
    GROWTH_SIGNAL = "growth_signal"
    MANAGEMENT_SIGNAL = "management_signal"
    COST_REDUCTION_SIGNAL = "cost_reduction_signal"
    COMPLIANCE_SIGNAL = "compliance_signal"
    CUSTOMER_OPERATION_SIGNAL = "customer_operation_signal"
    SALES_MANAGEMENT_SIGNAL = "sales_management_signal"
    DATA_GOVERNANCE_SIGNAL = "data_governance_signal"
    OTHER = "other"


class RiskTypeEnum(str, Enum):
    """风险类型枚举"""

    LEGAL = "legal"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    REPUTATION = "reputation"
    PROCUREMENT_COMPLEXITY = "procurement_complexity"
    ORGANIZATION_INSTABILITY = "organization_instability"
    LOW_BUDGET_PROBABILITY = "low_budget_probability"
    UNCLEAR_DEMAND = "unclear_demand"
    LONG_DECISION_CYCLE = "long_decision_cycle"
    OTHER = "other"


class StrengthEnum(str, Enum):
    """信号强度枚举"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DemandSignal(BaseModel):
    """需求信号"""

    signal_type: DemandSignalTypeEnum = Field(..., description="信号类型")
    signal: str = Field(..., description="观察到的客观信号")
    evidence: str = Field(..., description="支撑该信号的证据摘要")
    inference: str = Field(..., description="基于事实得出的商务推断")
    strength: StrengthEnum = Field(..., description="信号强度")
    source: Optional[str] = Field(None, description="信息来源")
    source_ref_ids: Optional[List[str]] = Field(default_factory=list, description="关联证据ID列表")
    date: Optional[str] = Field(None, description="信号日期")


class RiskSignal(BaseModel):
    """风险信号"""

    risk_type: RiskTypeEnum = Field(..., description="风险类型")
    risk: str = Field(..., description="风险描述")
    description: str = Field(..., description="风险详细说明")
    impact: str = Field(..., description="风险影响")
    level: StrengthEnum = Field(..., description="风险等级")
    source: Optional[str] = Field(None, description="信息来源")
    source_ref_ids: Optional[List[str]] = Field(default_factory=list, description="关联证据ID列表")
    date: Optional[str] = Field(None, description="风险发现日期")


class RecommendedTargetRole(BaseModel):
    """推荐目标角色"""

    role: str = Field(..., description="角色名称")
    department: Optional[str] = Field(None, description="所属部门")
    reason: str = Field(..., description="推荐理由")
    priority: int = Field(..., ge=1, le=10, description="优先级，1为最高")


class KeyPeoplePublicInfo(BaseModel):
    """关键人物公开信息"""

    name: str = Field(..., description="姓名")
    role: str = Field(..., description="职位")
    public_context: Optional[str] = Field(None, description="公开背景信息")
    source_ref_ids: Optional[List[str]] = Field(default_factory=list, description="关联证据ID列表")


class OrganizationInsights(BaseModel):
    """组织洞察"""

    possible_target_departments: List[str] = Field(default_factory=list, description="可能的目标部门")
    recommended_target_roles: List[RecommendedTargetRole] = Field(default_factory=list, description="推荐目标角色")
    possible_decision_chain: Optional[List[str]] = Field(default_factory=list, description="可能的决策链")
    key_people_public_info: Optional[List[KeyPeoplePublicInfo]] = Field(default_factory=list, description="关键人物公开信息")