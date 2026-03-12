# -*- coding: utf-8 -*-
"""基础数据模型定义"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LanguageEnum(str, Enum):
    """输出语言枚举"""

    ZH_CN = "zh-CN"
    EN_US = "en-US"


class SalesGoalEnum(str, Enum):
    """本次跟进目标枚举"""

    LEAD_GENERATION = "lead_generation"
    FIRST_TOUCH = "first_touch"
    MEETING_PREP = "meeting_prep"
    SOLUTION_PITCH = "solution_pitch"
    ACCOUNT_PLANNING = "account_planning"
    OTHER = "other"


class Meta(BaseModel):
    """报告元数据"""

    report_id: str = Field(..., description="报告唯一ID")
    generated_at: datetime = Field(..., description="生成时间")
    language: LanguageEnum = Field(..., description="输出语言")
    version: str = Field(..., description="Schema或Prompt版本")


class Input(BaseModel):
    """用户输入数据"""

    company_name: str = Field(..., description="目标企业名称")
    company_website: Optional[str] = Field(None, description="目标企业官网")
    user_company_product: str = Field(..., description="我方产品/服务描述")
    user_target_customer_profile: Optional[str] = Field(None, description="我方理想客户画像")
    sales_goal: SalesGoalEnum = Field(..., description="本次跟进目标")
    target_role: Optional[str] = Field(None, description="用户希望接触的角色")
    extra_context: Optional[str] = Field(None, description="用户补充背景")