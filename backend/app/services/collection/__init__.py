# -*- coding: utf-8 -*-
"""
采集模块

负责从多数据源采集原始证据，包括官网、新闻等。

模块组成：
- base.py: 定义统一的 collector 接口协议
- source_router.py: 数据源路由器，决定启用哪些数据源
- website_collector.py: 企业官网采集器
- news_collector.py: 新闻资讯采集器（Task 9）
"""

from __future__ import annotations

from .base import (
    BaseCollector,
    CollectorInput,
    CollectorOutput,
    CollectorRegistry,
    SourceType,
    get_collector,
    get_collector_registry,
    register_collector,
)
from .source_router import (
    SourceConfig,
    SourceRouter,
    SourceRouterConfig,
    get_source_router,
    route_sources,
)
from .news_collector import (
    NewsCollector,
    collect_news,
    get_news_collector,
)
from .website_collector import (
    WebsiteCollector,
    collect_website,
    get_website_collector,
)

__all__ = [
    # 基础类型
    "SourceType",
    "CollectorInput",
    "CollectorOutput",
    # 采集器基类
    "BaseCollector",
    # 采集器注册表
    "CollectorRegistry",
    "get_collector_registry",
    "register_collector",
    "get_collector",
    # 数据源路由
    "SourceConfig",
    "SourceRouterConfig",
    "SourceRouter",
    "get_source_router",
    "route_sources",
    # 官网采集器
    "WebsiteCollector",
    "get_website_collector",
    "collect_website",
    # 新闻采集器
    "NewsCollector",
    "get_news_collector",
    "collect_news",
]