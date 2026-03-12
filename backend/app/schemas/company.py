# -*- coding: utf-8 -*-
"""企业相关数据模型定义"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RecentDevelopmentTypeEnum(str, Enum):
    """近期动态类型枚举"""

    NEWS = "news"
    FINANCING = "financing"
    HIRING = "hiring"
    EXPANSION = "expansion"
    NEW_PRODUCT = "new_product"
    BIDDING = "bidding"
    PARTNERSHIP = "partnership"
    DIGITAL_TRANSFORMATION = "digital_transformation"
    MANAGEMENT_CHANGE = "management_change"
    COMPLIANCE = "compliance"
    OTHER = "other"


class CompanyProfile(BaseModel):
    """企业画像"""

    company_name: str = Field(..., description="企业名称")
    short_name: Optional[str] = Field(None, description="企业简称")
    industry: List[str] = Field(default_factory=list, description="行业标签")
    company_type: str = Field(..., description="企业类型，如民营/国企/外企/上市公司/子公司等")
    founded_year: Optional[int] = Field(None, ge=1800, le=2100, description="成立年份")
    headquarters: Optional[str] = Field(None, description="总部所在地")
    business_scope: List[str] = Field(default_factory=list, description="主营业务范围")
    main_products_or_services: List[str] = Field(default_factory=list, description="主要产品或服务")
    estimated_size: str = Field(..., description="员工规模或规模估计")
    region_coverage: Optional[List[str]] = Field(default_factory=list, description="业务覆盖区域")
    official_website: Optional[str] = Field(None, description="官网地址")
    official_accounts: Optional[List[str]] = Field(default_factory=list, description="官方账号")
    profile_summary: Optional[str] = Field(None, description="企业画像摘要")


class RecentDevelopment(BaseModel):
    """近期动态"""

    date: str = Field(..., description="事件日期，建议 YYYY-MM-DD，未知可写 YYYY-MM 或 YYYY")
    type: RecentDevelopmentTypeEnum = Field(..., description="动态类型")
    title: str = Field(..., description="动态标题")
    summary: str = Field(..., description="动态摘要")
    source: str = Field(..., description="信息来源")
    source_ref_ids: Optional[List[str]] = Field(default_factory=list, description="关联证据ID列表")
    confidence: float = Field(..., ge=0, le=1, description="置信度")