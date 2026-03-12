# -*- coding: utf-8 -*-
"""判断相关数据模型定义"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CustomerFitLevelEnum(str, Enum):
    """客户匹配度枚举"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OpportunityLevelEnum(str, Enum):
    """商机等级枚举"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FollowUpPriorityEnum(str, Enum):
    """跟进优先级枚举"""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    DISCARD = "discard"


class SalesAssessment(BaseModel):
    """商务判断"""

    customer_fit_level: CustomerFitLevelEnum = Field(..., description="客户匹配度")
    opportunity_level: OpportunityLevelEnum = Field(..., description="商机等级")
    follow_up_priority: FollowUpPriorityEnum = Field(..., description="跟进优先级")
    core_opportunity_scenarios: List[str] = Field(default_factory=list, description="核心机会场景")
    main_obstacles: List[str] = Field(default_factory=list, description="主要障碍")
    assessment_summary: str = Field(..., description="判断摘要")
    should_follow_up: Optional[bool] = Field(None, description="是否应该跟进")


class CommunicationStrategy(BaseModel):
    """沟通策略"""

    recommended_entry_points: List[str] = Field(default_factory=list, description="推荐切入点")
    avoid_points: List[str] = Field(default_factory=list, description="应避免的切入点")
    opening_message: str = Field(..., description="一句话破冰建议")
    phone_script: str = Field(..., description="电话话术")
    wechat_message: str = Field(..., description="微信话术")
    email_message: str = Field(..., description="邮件话术")
    next_step_suggestion: str = Field(..., description="下一步建议")