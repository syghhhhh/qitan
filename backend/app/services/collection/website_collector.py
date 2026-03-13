# -*- coding: utf-8 -*-
"""
WebsiteCollector - 企业官网采集器

从企业官网采集基础信息，输出 RawEvidence 列表。
v0.0.2 实现最小版本能力：
- 通过 HTTP 请求获取官网首页内容
- 提取页面标题和主要内容
- 无官网或请求失败时返回空结果

后续版本可扩展：
- 爬取多个页面（关于我们、产品介绍等）
- 更智能的内容提取
- 网站结构分析
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

import httpx

from .base import BaseCollector, CollectorInput, CollectorOutput, SourceType


class WebsiteCollector(BaseCollector):
    """
    企业官网采集器

    从企业官网采集基础信息，作为企业画像构建的重要证据来源。

    使用方式：
        collector = WebsiteCollector()
        output = await collector.collect(input_data)

    Attributes:
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
        user_agent: 请求 User-Agent
    """

    # 默认配置
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 2
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        user_agent: Optional[str] = None,
    ):
        """
        初始化官网采集器

        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            user_agent: 自定义 User-Agent
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT

    @property
    def source_type(self) -> SourceType:
        """返回数据源类型"""
        return SourceType.WEBSITE

    async def collect(self, input_data: CollectorInput) -> CollectorOutput:
        """
        执行官网数据采集

        采集流程：
        1. 验证输入（必须有企业域名）
        2. 构建请求 URL
        3. 发送 HTTP 请求获取页面内容
        4. 提取页面标题和主要内容
        5. 构建 RawEvidence 输出

        Args:
            input_data: 采集器输入数据

        Returns:
            CollectorOutput: 包含原始证据的采集结果
        """
        start_time = time.time()

        # 验证输入 - 必须有域名
        if not input_data.company_domain:
            return self.create_empty_output(reason="未提供企业官网域名")

        # 构建请求 URL
        url = self._build_url(input_data.company_domain)
        if not url:
            return self.create_empty_output(reason="无法构建有效的官网 URL")

        try:
            # 发送 HTTP 请求
            response_content, final_url = await self._fetch_page(url)

            if not response_content:
                return self.create_empty_output(
                    reason=f"获取官网内容失败: {url}"
                )

            # 提取页面信息
            title = self._extract_title(response_content)
            content = self._extract_content(response_content)

            if not title and not content:
                return self.create_empty_output(
                    reason="无法从官网提取有效内容"
                )

            # 创建证据
            evidence = self.create_evidence(
                title=title or f"{input_data.company_name}官网",
                content=content,
                url=final_url or url,
                metadata={
                    "company_name": input_data.company_name,
                    "original_domain": input_data.company_domain,
                    "content_length": len(content) if content else 0,
                },
            )

            # 计算耗时
            elapsed_time = time.time() - start_time

            return CollectorOutput(
                source_type=self.source_type,
                evidence_list=[evidence],
                success=True,
                metadata={
                    "url": final_url or url,
                    "elapsed_seconds": round(elapsed_time, 3),
                    "retries": 0,
                },
            )

        except Exception as e:
            return self.create_error_output(
                error_type=type(e).__name__,
                error_message=f"采集官网失败: {str(e)}",
            )

    def _build_url(self, domain: str) -> Optional[str]:
        """
        构建完整的官网 URL

        Args:
            domain: 企业域名

        Returns:
            完整的 URL，如果无法构建则返回 None
        """
        if not domain:
            return None

        # 清理域名
        clean_domain = domain.strip().lower()

        # 移除可能的协议前缀
        for prefix in ["https://", "http://", "www."]:
            if clean_domain.startswith(prefix):
                clean_domain = clean_domain[len(prefix):]

        # 移除路径部分
        if "/" in clean_domain:
            clean_domain = clean_domain.split("/")[0]

        # 构建完整 URL
        return f"https://{clean_domain}"

    async def _fetch_page(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """
        发送 HTTP 请求获取页面内容

        Args:
            url: 目标 URL

        Returns:
            tuple: (页面内容, 最终 URL)，失败时返回 (None, None)
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.get(url, headers=headers)

                    if response.status_code == 200:
                        # 尝试检测编码
                        content = response.text
                        return content, str(response.url)

                    # 非 200 状态码
                    if attempt < self.max_retries:
                        await self._sleep(1)  # 简单的重试等待
                        continue

                    return None, None

                except httpx.TimeoutException:
                    if attempt < self.max_retries:
                        await self._sleep(1)
                        continue
                    return None, None

                except Exception:
                    return None, None

        return None, None

    async def _sleep(self, seconds: float) -> None:
        """异步等待"""
        await httpx.AsyncClient().aclose()  # placeholder, use asyncio.sleep
        import asyncio
        await asyncio.sleep(seconds)

    def _extract_title(self, html_content: str) -> Optional[str]:
        """
        从 HTML 内容中提取页面标题

        Args:
            html_content: HTML 内容

        Returns:
            页面标题，如果无法提取则返回 None
        """
        if not html_content:
            return None

        # 尝试匹配 <title> 标签
        title_pattern = re.compile(
            r"<title[^>]*>(.*?)</title>",
            re.IGNORECASE | re.DOTALL
        )
        match = title_pattern.search(html_content)

        if match:
            title = match.group(1).strip()
            # 清理标题中的多余空白和特殊字符
            title = re.sub(r"\s+", " ", title)
            # 移除常见的网站后缀
            for suffix in [" - ", " | ", " _ ", "——", "——"]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
                    break
            return title if title else None

        return None

    def _extract_content(self, html_content: str) -> str:
        """
        从 HTML 内容中提取正文内容

        v0.0.2 最小版本：简单提取可见文本
        后续版本可使用更智能的内容提取算法

        Args:
            html_content: HTML 内容

        Returns:
            提取的正文内容
        """
        if not html_content:
            return ""

        # 移除 script 和 style 标签及其内容
        content = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            html_content,
            flags=re.IGNORECASE | re.DOTALL
        )
        content = re.sub(
            r"<style[^>]*>.*?</style>",
            "",
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

        # 移除 HTML 注释
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

        # 移除所有 HTML 标签
        content = re.sub(r"<[^>]+>", " ", content)

        # 解码 HTML 实体
        content = self._decode_html_entities(content)

        # 清理多余空白
        content = re.sub(r"\s+", " ", content)

        # 限制内容长度，避免过大
        max_length = 10000
        if len(content) > max_length:
            content = content[:max_length] + "..."

        return content.strip()

    def _decode_html_entities(self, text: str) -> str:
        """
        解码常见的 HTML 实体

        Args:
            text: 包含 HTML 实体的文本

        Returns:
            解码后的文本
        """
        entities = {
            "&nbsp;": " ",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&apos;": "'",
        }

        for entity, char in entities.items():
            text = text.replace(entity, char)

        # 解码数字实体
        text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
        text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)

        return text


# 模块级单例实例
_default_collector: Optional[WebsiteCollector] = None


def get_website_collector(
    timeout: int = WebsiteCollector.DEFAULT_TIMEOUT,
    max_retries: int = WebsiteCollector.DEFAULT_MAX_RETRIES,
) -> WebsiteCollector:
    """
    获取官网采集器单例实例

    Args:
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数

    Returns:
        WebsiteCollector: 官网采集器实例
    """
    global _default_collector
    if _default_collector is None:
        _default_collector = WebsiteCollector(
            timeout=timeout,
            max_retries=max_retries,
        )
    return _default_collector


async def collect_website(input_data: CollectorInput) -> CollectorOutput:
    """
    便捷函数：执行官网采集

    Args:
        input_data: 采集器输入数据

    Returns:
        CollectorOutput: 采集结果
    """
    collector = get_website_collector()
    return await collector.collect(input_data)