# -*- coding: utf-8 -*-
"""数据模型模块导出"""

from .common import Input, Meta, LanguageEnum, SalesGoalEnum
from .company import CompanyProfile, RecentDevelopment, RecentDevelopmentTypeEnum
from .analysis import (
    DemandSignal,
    DemandSignalTypeEnum,
    RiskSignal,
    RiskTypeEnum,
    StrengthEnum,
    OrganizationInsights,
    RecommendedTargetRole,
    KeyPeoplePublicInfo,
)
from .assessment import (
    SalesAssessment,
    CommunicationStrategy,
    CustomerFitLevelEnum,
    OpportunityLevelEnum,
    FollowUpPriorityEnum,
)
from .output import DueDiligenceOutput, EvidenceReference
from .enums import (
    LANGUAGE_LABELS,
    SALES_GOAL_LABELS,
    RECENT_DEVELOPMENT_TYPE_LABELS,
    DEMAND_SIGNAL_TYPE_LABELS,
    STRENGTH_LABELS,
    RISK_TYPE_LABELS,
    CUSTOMER_FIT_LEVEL_LABELS,
    OPPORTUNITY_LEVEL_LABELS,
    FOLLOW_UP_PRIORITY_LABELS,
    ROLE_PRIORITY_LABELS,
    NORMALIZED_COMPANY_SIZE_LABELS,
    NORMALIZED_COMPANY_TYPE_LABELS,
    EVIDENCE_SOURCE_LABELS,
    get_enum_label,
)

__all__ = [
    # common
    "Meta",
    "Input",
    "LanguageEnum",
    "SalesGoalEnum",
    # company
    "CompanyProfile",
    "RecentDevelopment",
    "RecentDevelopmentTypeEnum",
    # analysis
    "DemandSignal",
    "DemandSignalTypeEnum",
    "RiskSignal",
    "RiskTypeEnum",
    "StrengthEnum",
    "OrganizationInsights",
    "RecommendedTargetRole",
    "KeyPeoplePublicInfo",
    # assessment
    "SalesAssessment",
    "CommunicationStrategy",
    "CustomerFitLevelEnum",
    "OpportunityLevelEnum",
    "FollowUpPriorityEnum",
    # output
    "DueDiligenceOutput",
    "EvidenceReference",
    # enums labels
    "LANGUAGE_LABELS",
    "SALES_GOAL_LABELS",
    "RECENT_DEVELOPMENT_TYPE_LABELS",
    "DEMAND_SIGNAL_TYPE_LABELS",
    "STRENGTH_LABELS",
    "RISK_TYPE_LABELS",
    "CUSTOMER_FIT_LEVEL_LABELS",
    "OPPORTUNITY_LEVEL_LABELS",
    "FOLLOW_UP_PRIORITY_LABELS",
    "ROLE_PRIORITY_LABELS",
    "NORMALIZED_COMPANY_SIZE_LABELS",
    "NORMALIZED_COMPANY_TYPE_LABELS",
    "EVIDENCE_SOURCE_LABELS",
    "get_enum_label",
]