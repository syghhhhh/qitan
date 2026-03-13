# -*- coding: utf-8 -*-
"""
Source Router - 数据源路由器

根据分析上下文和配置决定启用哪些数据源，为 orchestrator 提供采集器选择策略。

主要功能：
- 根据输入信息推断可用的数据源
- 支持配置驱动的数据源启用/禁用
- 支持动态数据源优先级排序
- 为采集阶段提供待执行的采集器列表

v0.0.2 先支持 website 与 news 两类 source。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from .base import SourceType


class SourceConfig(BaseModel):
    """
    数据源配置

    定义单个数据源的启用状态和优先级。

    Attributes:
        enabled: 是否启用
        priority: 优先级（数值越小优先级越高）
        timeout_seconds: 超时时间（秒）
        max_results: 最大结果数量
        requires_domain: 是否需要企业域名才能采集
        requires_company_name: 是否需要企业名称才能采集
    """

    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=100, description="优先级，数值越小优先级越高")
    timeout_seconds: int = Field(default=30, description="超时时间（秒）")
    max_results: int = Field(default=10, description="最大结果数量")
    requires_domain: bool = Field(default=False, description="是否需要企业域名才能采集")
    requires_company_name: bool = Field(default=True, description="是否需要企业名称才能采集")


class SourceRouterConfig(BaseModel):
    """
    数据源路由器配置

    定义所有数据源的默认配置和启用状态。

    Attributes:
        sources: 各数据源的配置字典
        default_timeout: 默认超时时间
        default_max_results: 默认最大结果数量
    """

    sources: Dict[SourceType, SourceConfig] = Field(
        default_factory=lambda: SourceRouterConfig._get_default_configs(),
        description="各数据源配置"
    )
    default_timeout: int = Field(default=30, description="默认超时时间（秒）")
    default_max_results: int = Field(default=10, description="默认最大结果数量")

    @staticmethod
    def _get_default_configs() -> Dict[SourceType, SourceConfig]:
        """
        获取默认数据源配置

        v0.0.2 阶段只启用 website 和 news 两类数据源。
        """
        return {
            # v0.0.2 已支持的数据源
            SourceType.WEBSITE: SourceConfig(
                enabled=True,
                priority=10,
                requires_domain=True,
                requires_company_name=True,
            ),
            SourceType.NEWS: SourceConfig(
                enabled=True,
                priority=20,
                requires_domain=False,
                requires_company_name=True,
            ),
            # 后续版本将支持的数据源（默认禁用）
            SourceType.JOBS: SourceConfig(
                enabled=False,
                priority=30,
                requires_domain=False,
                requires_company_name=True,
            ),
            SourceType.RISK: SourceConfig(
                enabled=False,
                priority=40,
                requires_domain=False,
                requires_company_name=True,
            ),
            SourceType.SOCIAL: SourceConfig(
                enabled=False,
                priority=50,
                requires_domain=True,
                requires_company_name=True,
            ),
            SourceType.PATENT: SourceConfig(
                enabled=False,
                priority=60,
                requires_domain=False,
                requires_company_name=True,
            ),
            SourceType.FINANCE: SourceConfig(
                enabled=False,
                priority=70,
                requires_domain=False,
                requires_company_name=True,
            ),
            SourceType.USER_SUPPLIED: SourceConfig(
                enabled=False,
                priority=5,  # 用户补充信息优先级最高
                requires_domain=False,
                requires_company_name=False,
            ),
        }

    def get_config(self, source_type: SourceType) -> SourceConfig:
        """
        获取指定数据源的配置

        Args:
            source_type: 数据源类型

        Returns:
            SourceConfig: 数据源配置，如不存在则返回默认配置
        """
        if source_type in self.sources:
            return self.sources[source_type]
        return SourceConfig()


@dataclass
class RoutingContext:
    """
    路由上下文

    封装路由决策所需的上下文信息。
    """

    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    aliases: List[str] = None
    sales_goal: Optional[str] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []

    @property
    def has_company_name(self) -> bool:
        """是否有企业名称"""
        return bool(self.company_name and self.company_name.strip())

    @property
    def has_domain(self) -> bool:
        """是否有企业域名"""
        return bool(self.company_domain and self.company_domain.strip())


class SourceRouter:
    """
    数据源路由器

    根据输入上下文和配置决定启用哪些数据源。

    主要职责：
    1. 根据输入信息完整性过滤可用的数据源
    2. 根据配置启用/禁用数据源
    3. 按优先级排序返回数据源列表
    4. 提供采集参数建议

    使用方式：
        router = SourceRouter()
        sources = router.route(
            company_name="阿里巴巴",
            company_domain="alibaba.com"
        )
        # 返回 [SourceType.WEBSITE, SourceType.NEWS]
    """

    def __init__(self, config: Optional[SourceRouterConfig] = None):
        """
        初始化路由器

        Args:
            config: 路由器配置，如不提供则使用默认配置
        """
        self.config = config or SourceRouterConfig()

    def route(
        self,
        company_name: Optional[str] = None,
        company_domain: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        sales_goal: Optional[str] = None,
    ) -> List[SourceType]:
        """
        根据上下文路由到合适的数据源

        Args:
            company_name: 企业名称
            company_domain: 企业域名
            aliases: 企业别名列表
            sales_goal: 销售目标

        Returns:
            List[SourceType]: 排序后的可用数据源列表
        """
        context = RoutingContext(
            company_name=company_name,
            company_domain=company_domain,
            aliases=aliases or [],
            sales_goal=sales_goal,
        )
        return self._route_with_context(context)

    def _route_with_context(self, context: RoutingContext) -> List[SourceType]:
        """
        基于上下文执行路由决策

        Args:
            context: 路由上下文

        Returns:
            List[SourceType]: 排序后的可用数据源列表
        """
        available_sources: List[SourceType] = []

        for source_type, source_config in self.config.sources.items():
            # 检查是否启用
            if not source_config.enabled:
                continue

            # 检查前置条件是否满足
            if not self._check_prerequisites(source_type, source_config, context):
                continue

            available_sources.append(source_type)

        # 按优先级排序
        available_sources.sort(
            key=lambda s: self.config.get_config(s).priority
        )

        return available_sources

    def _check_prerequisites(
        self,
        source_type: SourceType,
        source_config: SourceConfig,
        context: RoutingContext,
    ) -> bool:
        """
        检查数据源的前置条件是否满足

        Args:
            source_type: 数据源类型
            source_config: 数据源配置
            context: 路由上下文

        Returns:
            bool: 是否满足前置条件
        """
        # 检查是否需要企业名称
        if source_config.requires_company_name and not context.has_company_name:
            return False

        # 检查是否需要企业域名
        if source_config.requires_domain and not context.has_domain:
            return False

        return True

    def get_source_config(self, source_type: SourceType) -> SourceConfig:
        """
        获取指定数据源的配置

        Args:
            source_type: 数据源类型

        Returns:
            SourceConfig: 数据源配置
        """
        return self.config.get_config(source_type)

    def get_enabled_sources(self) -> List[SourceType]:
        """
        获取所有已启用的数据源

        Returns:
            List[SourceType]: 已启用的数据源列表
        """
        return [
            st for st, cfg in self.config.sources.items()
            if cfg.enabled
        ]

    def is_source_available(
        self,
        source_type: SourceType,
        company_name: Optional[str] = None,
        company_domain: Optional[str] = None,
    ) -> bool:
        """
        检查指定数据源在当前上下文下是否可用

        Args:
            source_type: 数据源类型
            company_name: 企业名称
            company_domain: 企业域名

        Returns:
            bool: 数据源是否可用
        """
        source_config = self.config.get_config(source_type)

        # 检查是否启用
        if not source_config.enabled:
            return False

        # 检查前置条件
        if source_config.requires_company_name and not company_name:
            return False

        if source_config.requires_domain and not company_domain:
            return False

        return True

    def get_collection_params(
        self,
        source_type: SourceType,
    ) -> Dict[str, any]:
        """
        获取指定数据源的采集参数

        Args:
            source_type: 数据源类型

        Returns:
            Dict: 采集参数字典，包含 timeout_seconds、max_results 等
        """
        source_config = self.config.get_config(source_type)
        return {
            "timeout_seconds": source_config.timeout_seconds,
            "max_results": source_config.max_results,
        }


# 模块级单例实例
_default_router: Optional[SourceRouter] = None


def get_source_router() -> SourceRouter:
    """
    获取数据源路由器单例实例

    Returns:
        SourceRouter: 路由器实例
    """
    global _default_router
    if _default_router is None:
        _default_router = SourceRouter()
    return _default_router


def route_sources(
    company_name: Optional[str] = None,
    company_domain: Optional[str] = None,
    aliases: Optional[List[str]] = None,
    sales_goal: Optional[str] = None,
) -> List[SourceType]:
    """
    便捷函数：路由数据源

    Args:
        company_name: 企业名称
        company_domain: 企业域名
        aliases: 企业别名列表
        sales_goal: 销售目标

    Returns:
        List[SourceType]: 排序后的可用数据源列表
    """
    router = get_source_router()
    return router.route(
        company_name=company_name,
        company_domain=company_domain,
        aliases=aliases,
        sales_goal=sales_goal,
    )