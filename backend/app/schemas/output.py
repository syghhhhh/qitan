# -*- coding: utf-8 -*-
"""输出数据模型定义"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .common import Input, Meta
from .company import CompanyProfile, RecentDevelopment
from .analysis import DemandSignal, OrganizationInsights, RiskSignal
from .assessment import CommunicationStrategy, SalesAssessment


class EvidenceReference(BaseModel):
    """证据引用"""

    reference_id: str = Field(..., description="证据唯一ID")
    source: str = Field(..., description="来源类型，如官网/新闻/招聘/用户补充")
    title: str = Field(..., description="证据标题")
    url: Optional[str] = Field(None, description="来源URL")
    date: Optional[str] = Field(None, description="证据日期")
    excerpt: Optional[str] = Field(None, description="摘录内容")


class DueDiligenceOutput(BaseModel):
    """企业背调完整输出"""

    meta: Meta = Field(..., description="报告元数据")
    input: Input = Field(..., description="用户输入")
    company_profile: CompanyProfile = Field(..., description="企业画像")
    recent_developments: List[RecentDevelopment] = Field(default_factory=list, description="近期动态")
    demand_signals: List[DemandSignal] = Field(default_factory=list, description="需求信号")
    organization_insights: OrganizationInsights = Field(..., description="组织洞察")
    risk_signals: List[RiskSignal] = Field(default_factory=list, description="风险信号")
    sales_assessment: SalesAssessment = Field(..., description="商务判断")
    communication_strategy: CommunicationStrategy = Field(..., description="沟通策略")
    evidence_references: List[EvidenceReference] = Field(default_factory=list, description="证据引用")