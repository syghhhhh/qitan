# -*- coding: utf-8 -*-
"""
Collection Base - 采集模块基础接口定义

定义统一的 collector 接口协议，包括：
- SourceType: 数据源类型枚举
- CollectorInput: 采集器统一输入结构
- CollectorOutput: 采集器统一输出结构
- BaseCollector: 采集器抽象基类

所有具体采集器（website_collector、news_collector 等）都需继承 BaseCollector，
确保输入输出协议一致，便于 orchestrator 统一调度。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from ..orchestrator.pipeline_state import RawEvidence


class SourceType(str, Enum):
    """
    数据源类型枚举

    定义系统支持的所有数据源类型，便于采集器注册和路由分发。
    """

    WEBSITE = "website"  # 企业官网
    NEWS = "news"  # 新闻资讯
    JOBS = "jobs"  # 招聘信息
    RISK = "risk"  # 风险信息（工商、诉讼等）
    SOCIAL = "social"  # 社交媒体
    PATENT = "patent"  # 专利信息
    FINANCE = "finance"  # 财务信息
    USER_SUPPLIED = "user_supplied"  # 用户补充信息


class CollectorInput(BaseModel):
    """
    采集器统一输入结构

    将分析上下文和企业实体信息封装为采集器所需的统一输入格式。

    Attributes:
        company_name: 标准企业名称
        company_domain: 企业官网域名
        aliases: 企业别名列表（可用于扩大搜索范围）
        context: 分析上下文元数据
        options: 采集选项配置
    """

    # ========== 企业信息 ==========
    company_name: str = Field(..., description="标准企业名称")
    company_domain: Optional[str] = Field(None, description="企业官网域名")
    aliases: List[str] = Field(default_factory=list, description="企业别名列表")

    # ========== 上下文信息 ==========
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="分析上下文元数据，包含 sales_goal、target_role 等"
    )

    # ========== 采集选项 ==========
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="采集选项配置，如超时时间、结果数量限制等"
    )

    class Config:
        """Pydantic 配置"""
        use_enum_values = True


class CollectorOutput(BaseModel):
    """
    采集器统一输出结构

    封装采集器的输出结果，包括原始证据列表和采集状态信息。

    Attributes:
        source_type: 数据源类型
        evidence_list: 采集到的原始证据列表
        success: 采集是否成功
        error_message: 错误信息（如失败）
        metadata: 采集过程元数据
    """

    # ========== 结果数据 ==========
    source_type: SourceType = Field(..., description="数据源类型")
    evidence_list: List[RawEvidence] = Field(
        default_factory=list,
        description="采集到的原始证据列表"
    )

    # ========== 状态信息 ==========
    success: bool = Field(default=True, description="采集是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    error_type: Optional[str] = Field(None, description="错误类型")

    # ========== 元数据 ==========
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="采集过程元数据，如耗时、请求次数等"
    )

    @property
    def evidence_count(self) -> int:
        """获取证据数量"""
        return len(self.evidence_list)

    class Config:
        """Pydantic 配置"""
        use_enum_values = True


class BaseCollector(ABC):
    """
    采集器抽象基类

    定义所有采集器必须实现的接口，确保采集行为一致性。

    子类需要实现：
    - collect(): 执行采集的核心方法
    - get_source_type(): 返回采集器支持的数据源类型

    可选覆写：
    - validate_input(): 验证输入数据
    - normalize_evidence(): 标准化证据格式

    使用方式：
        class WebsiteCollector(BaseCollector):
            def get_source_type(self) -> SourceType:
                return SourceType.WEBSITE

            async def collect(self, input_data: CollectorInput) -> CollectorOutput:
                # 实现采集逻辑
                ...
    """

    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        """
        采集器支持的数据源类型

        Returns:
            SourceType: 数据源类型枚举值
        """
        pass

    @abstractmethod
    async def collect(self, input_data: CollectorInput) -> CollectorOutput:
        """
        执行数据采集

        Args:
            input_data: 采集器输入数据

        Returns:
            CollectorOutput: 采集结果，包含原始证据列表和状态信息
        """
        pass

    def validate_input(self, input_data: CollectorInput) -> bool:
        """
        验证输入数据是否有效

        子类可覆写此方法添加特定的验证逻辑。

        Args:
            input_data: 采集器输入数据

        Returns:
            bool: 输入数据是否有效
        """
        # 基础验证：必须有企业名称
        return bool(input_data.company_name and input_data.company_name.strip())

    def create_evidence(
        self,
        title: str,
        content: str,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RawEvidence:
        """
        创建原始证据对象的便捷方法

        Args:
            title: 证据标题
            content: 证据内容
            url: 来源 URL
            metadata: 额外元数据

        Returns:
            RawEvidence: 原始证据对象
        """
        return RawEvidence(
            evidence_id=f"ev_{uuid4().hex[:12]}",
            source_type=self.source_type.value,
            url=url,
            title=title,
            content=content,
            collected_at=datetime.now(),
            metadata=metadata or {},
        )

    def create_empty_output(self, reason: str = "无数据") -> CollectorOutput:
        """
        创建空输出结果的便捷方法

        Args:
            reason: 空结果原因

        Returns:
            CollectorOutput: 空采集结果
        """
        return CollectorOutput(
            source_type=self.source_type,
            evidence_list=[],
            success=True,
            metadata={"reason": reason},
        )

    def create_error_output(
        self,
        error_type: str,
        error_message: str,
    ) -> CollectorOutput:
        """
        创建错误输出结果的便捷方法

        Args:
            error_type: 错误类型
            error_message: 错误信息

        Returns:
            CollectorOutput: 错误采集结果
        """
        return CollectorOutput(
            source_type=self.source_type,
            evidence_list=[],
            success=False,
            error_type=error_type,
            error_message=error_message,
        )


class CollectorRegistry:
    """
    采集器注册表

    管理所有采集器实例，支持按数据源类型查找和获取采集器。

    使用方式：
        registry = CollectorRegistry()
        registry.register(website_collector)
        registry.register(news_collector)

        collectors = registry.get_collectors([SourceType.WEBSITE, SourceType.NEWS])
    """

    def __init__(self):
        """初始化注册表"""
        self._collectors: Dict[SourceType, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> None:
        """
        注册采集器

        Args:
            collector: 采集器实例
        """
        self._collectors[collector.source_type] = collector

    def get_collector(self, source_type: SourceType) -> Optional[BaseCollector]:
        """
        获取指定类型的采集器

        Args:
            source_type: 数据源类型

        Returns:
            BaseCollector: 采集器实例，如不存在返回 None
        """
        return self._collectors.get(source_type)

    def get_collectors(
        self, source_types: Optional[List[SourceType]] = None
    ) -> List[BaseCollector]:
        """
        获取多个采集器

        Args:
            source_types: 数据源类型列表，如为 None 则返回所有已注册的采集器

        Returns:
            List[BaseCollector]: 采集器实例列表
        """
        if source_types is None:
            return list(self._collectors.values())

        return [
            self._collectors[st]
            for st in source_types
            if st in self._collectors
        ]

    def get_available_source_types(self) -> List[SourceType]:
        """
        获取已注册的数据源类型列表

        Returns:
            List[SourceType]: 已注册的数据源类型
        """
        return list(self._collectors.keys())

    def is_registered(self, source_type: SourceType) -> bool:
        """
        检查指定类型的采集器是否已注册

        Args:
            source_type: 数据源类型

        Returns:
            bool: 是否已注册
        """
        return source_type in self._collectors


# 模块级全局注册表实例
_global_registry: Optional[CollectorRegistry] = None


def get_collector_registry() -> CollectorRegistry:
    """
    获取全局采集器注册表实例

    Returns:
        CollectorRegistry: 全局注册表实例
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = CollectorRegistry()
    return _global_registry


def register_collector(collector: BaseCollector) -> None:
    """
    便捷函数：注册采集器到全局注册表

    Args:
        collector: 采集器实例
    """
    registry = get_collector_registry()
    registry.register(collector)


def get_collector(source_type: SourceType) -> Optional[BaseCollector]:
    """
    便捷函数：从全局注册表获取采集器

    Args:
        source_type: 数据源类型

    Returns:
        BaseCollector: 采集器实例，如不存在返回 None
    """
    registry = get_collector_registry()
    return registry.get_collector(source_type)