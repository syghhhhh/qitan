# -*- coding: utf-8 -*-
"""
NewsCollector - 新闻资讯采集器

根据企业名称采集相关新闻证据，输出 RawEvidence 列表。
v0.0.2 实现最小版本能力：
- 基于企业名称搜索新闻
- 返回结构化新闻证据
- 空结果时返回空列表而不是抛异常

后续版本可扩展：
- 对接真实新闻 API（如百度、搜狗等搜索引擎 API）
- 更智能的新闻筛选和过滤
- 多数据源聚合
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .base import BaseCollector, CollectorInput, CollectorOutput, SourceType


class NewsCollector(BaseCollector):
    """
    新闻资讯采集器

    从公开新闻源采集与企业相关的新闻信息，作为企业画像和动态分析的证据来源。

    使用方式：
        collector = NewsCollector()
        output = await collector.collect(input_data)

    v0.0.2 阶段：
    - 使用模拟数据源返回新闻证据
    - 确保接口结构符合真实链路设计
    - 便于后续接入真实新闻 API

    Attributes:
        max_results: 最大返回结果数量
        mock_enabled: 是否使用模拟数据
    """

    # 默认配置
    DEFAULT_MAX_RESULTS = 5
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        max_results: int = DEFAULT_MAX_RESULTS,
        mock_enabled: bool = True,
    ):
        """
        初始化新闻采集器

        Args:
            max_results: 最大返回结果数量
            mock_enabled: 是否使用模拟数据（v0.0.2 默认启用）
        """
        self.max_results = max_results
        self.mock_enabled = mock_enabled

    @property
    def source_type(self) -> SourceType:
        """返回数据源类型"""
        return SourceType.NEWS

    async def collect(self, input_data: CollectorInput) -> CollectorOutput:
        """
        执行新闻数据采集

        采集流程：
        1. 验证输入（必须有企业名称）
        2. 根据企业名称搜索新闻
        3. 构建 RawEvidence 列表
        4. 返回采集结果

        Args:
            input_data: 采集器输入数据

        Returns:
            CollectorOutput: 包含原始证据的采集结果
        """
        start_time = time.time()

        # 验证输入 - 必须有企业名称
        if not input_data.company_name or not input_data.company_name.strip():
            return self.create_empty_output(reason="未提供企业名称")

        company_name = input_data.company_name.strip()

        try:
            # v0.0.2 阶段使用模拟数据
            if self.mock_enabled:
                news_items = self._get_mock_news(company_name)
            else:
                # 后续版本：对接真实新闻 API
                news_items = await self._fetch_real_news(company_name)

            # 构建 RawEvidence 列表
            evidence_list = []
            for item in news_items[:self.max_results]:
                evidence = self.create_evidence(
                    title=item["title"],
                    content=item["content"],
                    url=item.get("url"),
                    metadata={
                        "company_name": company_name,
                        "publish_date": item.get("publish_date"),
                        "source_name": item.get("source_name"),
                        "news_type": item.get("news_type"),
                    },
                )
                evidence_list.append(evidence)

            # 计算耗时
            elapsed_time = time.time() - start_time

            return CollectorOutput(
                source_type=self.source_type,
                evidence_list=evidence_list,
                success=True,
                metadata={
                    "company_name": company_name,
                    "total_results": len(news_items),
                    "returned_results": len(evidence_list),
                    "elapsed_seconds": round(elapsed_time, 3),
                    "mock_mode": self.mock_enabled,
                },
            )

        except Exception as e:
            return self.create_error_output(
                error_type=type(e).__name__,
                error_message=f"采集新闻失败: {str(e)}",
            )

    def _get_mock_news(self, company_name: str) -> List[Dict[str, Any]]:
        """
        获取模拟新闻数据

        v0.0.2 阶段使用模拟数据，确保接口可用性和结构正确。
        后续版本将对接真实新闻 API。

        Args:
            company_name: 企业名称

        Returns:
            List[Dict]: 模拟新闻列表
        """
        # 模拟新闻数据模板
        # 实际应用中应该从真实 API 获取
        today = datetime.now()
        mock_news = [
            {
                "title": f"{company_name}发布最新产品动态",
                "content": f"{company_name}近日宣布推出全新产品线，进一步拓展市场布局。据公司相关负责人介绍，新产品将为用户带来更加优质的体验和服务。",
                "url": f"https://news.example.com/{company_name}/product-update",
                "publish_date": today.strftime("%Y-%m-%d"),
                "source_name": "行业资讯网",
                "news_type": "product",
            },
            {
                "title": f"{company_name}获得行业认可",
                "content": f"在近日举办的行业峰会上，{company_name}凭借卓越的技术创新和服务能力，荣获多项行业大奖，充分展示了企业的综合实力。",
                "url": f"https://news.example.com/{company_name}/award",
                "publish_date": (today.replace(day=today.day - 1) if today.day > 1 else today).strftime("%Y-%m-%d"),
                "source_name": "科技日报",
                "news_type": "honor",
            },
            {
                "title": f"{company_name}战略合作签约",
                "content": f"{company_name}与多家知名企业签署战略合作协议，将在技术研发、市场推广等领域展开深度合作，共同推动行业发展。",
                "url": f"https://news.example.com/{company_name}/partnership",
                "publish_date": (today.replace(day=today.day - 2) if today.day > 2 else today).strftime("%Y-%m-%d"),
                "source_name": "商业观察",
                "news_type": "business",
            },
        ]

        return mock_news

    async def _fetch_real_news(self, company_name: str) -> List[Dict[str, Any]]:
        """
        获取真实新闻数据（预留接口）

        后续版本实现真实新闻 API 对接。
        当前返回空列表，确保流程不中断。

        Args:
            company_name: 企业名称

        Returns:
            List[Dict]: 新闻列表
        """
        # TODO: 后续版本对接真实新闻 API
        # 可能的数据源：
        # - 百度搜索 API
        # - 搜狗新闻 API
        # - 企业工商信息 API 中的新闻模块
        return []


# 模块级单例实例
_default_collector: Optional[NewsCollector] = None


def get_news_collector(
    max_results: int = NewsCollector.DEFAULT_MAX_RESULTS,
    mock_enabled: bool = True,
) -> NewsCollector:
    """
    获取新闻采集器单例实例

    Args:
        max_results: 最大返回结果数量
        mock_enabled: 是否使用模拟数据

    Returns:
        NewsCollector: 新闻采集器实例
    """
    global _default_collector
    if _default_collector is None:
        _default_collector = NewsCollector(
            max_results=max_results,
            mock_enabled=mock_enabled,
        )
    return _default_collector


async def collect_news(input_data: CollectorInput) -> CollectorOutput:
    """
    便捷函数：执行新闻采集

    Args:
        input_data: 采集器输入数据

    Returns:
        CollectorOutput: 采集结果
    """
    collector = get_news_collector()
    return await collector.collect(input_data)