# -*- coding: utf-8 -*-
"""
ContextBuilder - 分析上下文构建器

负责将 API 请求转换为统一的分析上下文（AnalysisContext），
标准化输入字段，处理缺省值，为后续 resolution 和 collection 模块提供输入基础。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from ...schemas import SalesGoalEnum


class AnalysisContext(BaseModel):
    """
    分析上下文 - 统一的分析任务上下文容器

    将 API 请求参数标准化为内部统一格式，包含：
    - 企业信息（名称、官网等）
    - 销售目标与策略
    - 目标角色
    - 用户补充信息
    - 上下文元数据

    该上下文对象将作为后续 resolution、collection 等模块的输入基础。
    """

    # ========== 上下文标识 ==========
    context_id: str = Field(
        default_factory=lambda: f"ctx_{uuid4().hex[:12]}",
        description="上下文唯一ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="上下文创建时间"
    )

    # ========== 企业信息 ==========
    company_name: str = Field(
        ...,
        description="目标企业名称（必填）"
    )
    company_website: Optional[str] = Field(
        None,
        description="目标企业官网URL"
    )
    company_website_normalized: Optional[str] = Field(
        None,
        description="标准化后的官网域名"
    )

    # ========== 销售策略 ==========
    user_company_product: str = Field(
        default="CRM系统",
        description="我方产品/服务描述"
    )
    user_target_customer_profile: Optional[str] = Field(
        None,
        description="我方理想客户画像"
    )
    sales_goal: SalesGoalEnum = Field(
        default=SalesGoalEnum.FIRST_TOUCH,
        description="本次跟进目标"
    )
    sales_goal_description: Optional[str] = Field(
        None,
        description="销售目标描述（从枚举映射）"
    )

    # ========== 目标角色 ==========
    target_role: Optional[str] = Field(
        None,
        description="用户希望接触的角色"
    )
    target_role_normalized: Optional[str] = Field(
        None,
        description="标准化后的目标角色"
    )

    # ========== 用户补充信息 ==========
    extra_context: Optional[str] = Field(
        None,
        description="用户补充背景信息"
    )

    # ========== 上下文元数据 ==========
    input_completeness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="输入完整度评分（0-1）"
    )
    missing_fields: List[str] = Field(
        default_factory=list,
        description="缺失字段列表"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="上下文构建警告"
    )

    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ContextBuilder:
    """
    上下文构建器

    负责将 API 请求转换为统一的 AnalysisContext 对象。
    主要职责：
    1. 字段标准化（如官网域名提取）
    2. 缺省值处理
    3. 输入完整度评估
    4. 警告信息生成

    使用方式：
        builder = ContextBuilder()
        context = builder.build(request)
    """

    # 销售目标描述映射
    SALES_GOAL_DESCRIPTIONS: Dict[SalesGoalEnum, str] = {
        SalesGoalEnum.LEAD_GENERATION: "判断企业是否值得进入销售线索池",
        SalesGoalEnum.FIRST_TOUCH: "生成初次沟通建议和切入点",
        SalesGoalEnum.MEETING_PREP: "为销售拜访或线上会议提供背景材料",
        SalesGoalEnum.SOLUTION_PITCH: "辅助识别业务场景和价值表达方向",
        SalesGoalEnum.ACCOUNT_PLANNING: "针对重点客户做账户规划和角色分析",
        SalesGoalEnum.OTHER: "保留扩展用途",
    }

    # 关键字段权重（用于计算完整度）
    FIELD_WEIGHTS: Dict[str, float] = {
        "company_name": 0.30,  # 企业名称是必须的
        "company_website": 0.20,  # 官网有助于采集
        "user_company_product": 0.15,  # 产品描述
        "sales_goal": 0.15,  # 销售目标
        "target_role": 0.10,  # 目标角色
        "user_target_customer_profile": 0.05,  # 客户画像
        "extra_context": 0.05,  # 补充信息
    }

    def build(
        self,
        company_name: str,
        company_website: Optional[str] = None,
        user_company_product: str = "CRM系统",
        user_target_customer_profile: Optional[str] = None,
        sales_goal: SalesGoalEnum = SalesGoalEnum.FIRST_TOUCH,
        target_role: Optional[str] = None,
        extra_context: Optional[str] = None,
    ) -> AnalysisContext:
        """
        构建分析上下文

        Args:
            company_name: 目标企业名称（必填）
            company_website: 目标企业官网URL
            user_company_product: 我方产品/服务描述
            user_target_customer_profile: 我方理想客户画像
            sales_goal: 本次跟进目标
            target_role: 用户希望接触的角色
            extra_context: 用户补充背景信息

        Returns:
            AnalysisContext: 标准化后的分析上下文
        """
        # 收集缺失字段和警告
        missing_fields: List[str] = []
        warnings: List[str] = []

        # 1. 标准化企业名称
        normalized_company_name = self._normalize_company_name(company_name)

        # 2. 标准化官网
        normalized_website = None
        if company_website:
            normalized_website = self._normalize_website(company_website)
        else:
            missing_fields.append("company_website")
            warnings.append("未提供企业官网，可能影响数据采集质量")

        # 3. 标准化目标角色
        normalized_role = None
        if target_role:
            normalized_role = self._normalize_role(target_role)
        else:
            missing_fields.append("target_role")

        # 4. 处理其他可选字段
        if not user_target_customer_profile:
            missing_fields.append("user_target_customer_profile")

        if not extra_context:
            missing_fields.append("extra_context")

        # 5. 获取销售目标描述
        sales_goal_description = self.SALES_GOAL_DESCRIPTIONS.get(
            sales_goal, "未知目标"
        )

        # 6. 计算输入完整度
        input_completeness = self._calculate_completeness(
            company_name=company_name,
            company_website=company_website,
            user_company_product=user_company_product,
            user_target_customer_profile=user_target_customer_profile,
            sales_goal=sales_goal,
            target_role=target_role,
            extra_context=extra_context,
        )

        # 7. 构建上下文对象
        context = AnalysisContext(
            company_name=normalized_company_name,
            company_website=company_website,
            company_website_normalized=normalized_website,
            user_company_product=user_company_product,
            user_target_customer_profile=user_target_customer_profile,
            sales_goal=sales_goal,
            sales_goal_description=sales_goal_description,
            target_role=target_role,
            target_role_normalized=normalized_role,
            extra_context=extra_context,
            input_completeness=input_completeness,
            missing_fields=missing_fields,
            warnings=warnings,
        )

        return context

    def build_from_dict(self, request: Dict[str, Any]) -> AnalysisContext:
        """
        从字典构建分析上下文

        Args:
            request: 请求参数字典

        Returns:
            AnalysisContext: 标准化后的分析上下文
        """
        return self.build(
            company_name=request.get("company_name", ""),
            company_website=request.get("company_website"),
            user_company_product=request.get("user_company_product", "CRM系统"),
            user_target_customer_profile=request.get("user_target_customer_profile"),
            sales_goal=request.get("sales_goal", SalesGoalEnum.FIRST_TOUCH),
            target_role=request.get("target_role"),
            extra_context=request.get("extra_context"),
        )

    def _normalize_company_name(self, name: str) -> str:
        """
        标准化企业名称

        Args:
            name: 原始企业名称

        Returns:
            标准化后的企业名称
        """
        if not name:
            return ""

        # 去除首尾空白
        normalized = name.strip()

        # 去除多余空格
        normalized = " ".join(normalized.split())

        return normalized

    def _normalize_website(self, website: str) -> str:
        """
        标准化官网 URL，提取域名

        Args:
            website: 原始官网 URL

        Returns:
            标准化后的域名
        """
        if not website:
            return ""

        # 去除首尾空白
        normalized = website.strip()

        # 去除协议前缀
        for prefix in ["https://", "http://", "www."]:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]

        # 去除路径部分
        if "/" in normalized:
            normalized = normalized.split("/")[0]

        return normalized.lower()

    def _normalize_role(self, role: str) -> str:
        """
        标准化目标角色

        Args:
            role: 原始角色描述

        Returns:
            标准化后的角色描述
        """
        if not role:
            return ""

        # 去除首尾空白
        normalized = role.strip()

        # 去除多余空格
        normalized = " ".join(normalized.split())

        return normalized

    def _calculate_completeness(
        self,
        company_name: str,
        company_website: Optional[str],
        user_company_product: str,
        user_target_customer_profile: Optional[str],
        sales_goal: SalesGoalEnum,
        target_role: Optional[str],
        extra_context: Optional[str],
    ) -> float:
        """
        计算输入完整度评分

        Args:
            各字段值

        Returns:
            完整度评分（0-1）
        """
        completeness = 0.0

        # 企业名称（必须）
        if company_name and company_name.strip():
            completeness += self.FIELD_WEIGHTS["company_name"]

        # 官网
        if company_website and company_website.strip():
            completeness += self.FIELD_WEIGHTS["company_website"]

        # 产品描述
        if user_company_product and user_company_product.strip():
            completeness += self.FIELD_WEIGHTS["user_company_product"]

        # 销售目标
        if sales_goal:
            completeness += self.FIELD_WEIGHTS["sales_goal"]

        # 目标角色
        if target_role and target_role.strip():
            completeness += self.FIELD_WEIGHTS["target_role"]

        # 客户画像
        if user_target_customer_profile and user_target_customer_profile.strip():
            completeness += self.FIELD_WEIGHTS["user_target_customer_profile"]

        # 补充信息
        if extra_context and extra_context.strip():
            completeness += self.FIELD_WEIGHTS["extra_context"]

        return round(completeness, 2)


# 模块级单例实例，便于直接导入使用
_default_builder: Optional[ContextBuilder] = None


def get_context_builder() -> ContextBuilder:
    """
    获取上下文构建器单例实例

    Returns:
        ContextBuilder: 上下文构建器实例
    """
    global _default_builder
    if _default_builder is None:
        _default_builder = ContextBuilder()
    return _default_builder


def build_context(
    company_name: str,
    company_website: Optional[str] = None,
    user_company_product: str = "CRM系统",
    user_target_customer_profile: Optional[str] = None,
    sales_goal: SalesGoalEnum = SalesGoalEnum.FIRST_TOUCH,
    target_role: Optional[str] = None,
    extra_context: Optional[str] = None,
) -> AnalysisContext:
    """
    便捷函数：构建分析上下文

    Args:
        company_name: 目标企业名称（必填）
        company_website: 目标企业官网URL
        user_company_product: 我方产品/服务描述
        user_target_customer_profile: 我方理想客户画像
        sales_goal: 本次跟进目标
        target_role: 用户希望接触的角色
        extra_context: 用户补充背景信息

    Returns:
        AnalysisContext: 标准化后的分析上下文
    """
    builder = get_context_builder()
    return builder.build(
        company_name=company_name,
        company_website=company_website,
        user_company_product=user_company_product,
        user_target_customer_profile=user_target_customer_profile,
        sales_goal=sales_goal,
        target_role=target_role,
        extra_context=extra_context,
    )