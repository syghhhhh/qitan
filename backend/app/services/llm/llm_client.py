# -*- coding: utf-8 -*-
"""
LLM 客户端模块

提供统一的大模型调用接口，支持多种 LLM 提供商。
当前阶段以 stub/mock 实现为主，为后续接入真实模型预留扩展点。
"""

from __future__ import annotations

import json

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Union


class LLMProvider(str, Enum):
    """LLM 提供商枚举"""

    POE = "poe"  # Poe API
    OPENAI = "openai"  # OpenAI API
    ANTHROPIC = "anthropic"  # Anthropic API
    MOCK = "mock"  # Mock 实现（用于测试）


class LLMStatus(str, Enum):
    """LLM 调用状态"""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


@dataclass
class LLMMessage:
    """LLM 消息结构"""

    role: str  # "system" | "user" | "assistant"
    content: str

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {"role": self.role, "content": self.content}


@dataclass
class LLMRequest:
    """LLM 请求结构"""

    messages: List[LLMMessage]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    stop_sequences: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_api_format(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        return {
            "model": self.model,
            "messages": [m.to_dict() for m in self.messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stop": self.stop_sequences if self.stop_sequences else None,
        }


@dataclass
class LLMResponse:
    """LLM 响应结构"""

    content: str
    model: str
    provider: LLMProvider
    status: LLMStatus
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

    @property
    def is_success(self) -> bool:
        """判断是否成功"""
        return self.status == LLMStatus.SUCCESS

    @property
    def total_tokens(self) -> int:
        """获取总 token 数"""
        return self.usage.get("total_tokens", 0)


class BaseLLMClient(ABC):
    """
    LLM 客户端基类

    定义统一的 LLM 调用接口，所有具体实现需继承此类。
    """

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """
        执行文本补全请求

        Args:
            request: LLM 请求对象

        Returns:
            LLMResponse: LLM 响应对象
        """
        pass

    @abstractmethod
    async def complete_async(self, request: LLMRequest) -> LLMResponse:
        """
        异步执行文本补全请求

        Args:
            request: LLM 请求对象

        Returns:
            LLMResponse: LLM 响应对象
        """
        pass

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[dict, None]:
        """
        流式文本补全请求

        Args:
            request: LLM 请求对象

        Yields:
            dict: {"type": "token"|"thinking"|"done", "content": "..."}
        """
        # 默认降级实现：调用 complete_async 后一次性返回
        response = await self.complete_async(request)
        if response.is_success:
            yield {"type": "token", "content": response.content}
        else:
            yield {"type": "token", "content": f"[错误] {response.error_message}"}
        yield {"type": "done", "content": ""}

    def simple_chat(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        简单对话接口

        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            **kwargs: 其他参数

        Returns:
            str: 模型回复内容
        """
        messages = []
        if system_message:
            messages.append(LLMMessage(role="system", content=system_message))
        messages.append(LLMMessage(role="user", content=user_message))

        request = LLMRequest(messages=messages, **kwargs)
        response = self.complete(request)

        if response.is_success:
            return response.content
        else:
            raise LLMClientError(f"LLM 调用失败: {response.error_message}")


class MockLLMClient(BaseLLMClient):
    """
    Mock LLM 客户端

    用于测试和开发环境，返回预设的响应内容。
    """

    def __init__(
        self,
        default_response: str = "这是一个模拟的 LLM 响应。",
        model: str = "mock-model",
    ):
        """
        初始化 Mock LLM 客户端

        Args:
            default_response: 默认响应内容
            model: 模型名称
        """
        self.default_response = default_response
        self.model = model
        self.call_count = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        """执行 Mock 补全"""
        self.call_count += 1

        # 模拟响应延迟
        import time

        start_time = time.time()

        # 根据请求内容生成简单响应
        response_content = self._generate_mock_response(request)

        latency = (time.time() - start_time) * 1000

        return LLMResponse(
            content=response_content,
            model=self.model,
            provider=LLMProvider.MOCK,
            status=LLMStatus.SUCCESS,
            usage={
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
            latency_ms=latency,
        )

    async def complete_async(self, request: LLMRequest) -> LLMResponse:
        """异步执行 Mock 补全"""
        import asyncio

        # 模拟异步延迟
        await asyncio.sleep(0.01)
        return self.complete(request)

    def _generate_mock_response(self, request: LLMRequest) -> str:
        """根据请求生成 Mock 响应"""
        # 检查是否有特定关键词
        user_messages = [m.content for m in request.messages if m.role == "user"]
        if user_messages:
            last_message = user_messages[-1].lower()

            # 根据关键词返回不同响应
            if "企业" in last_message or "公司" in last_message:
                return "该企业是一家专注于科技创新的公司，主营业务包括软件开发和数字化服务。"
            elif "分析" in last_message:
                return "基于提供的信息，分析结果如下：该企业具有良好的发展潜力，建议进一步关注。"
            elif "风险" in last_message:
                return "风险分析结果：暂未发现重大风险信号，建议保持关注。"

        return self.default_response


class PoeLLMClient(BaseLLMClient):
    """
    Poe API LLM 客户端

    通过 Poe API 调用大模型，支持多种模型。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-5.4",
        base_url: str = "https://api.poe.com/v1/chat/completions",
        proxy: Optional[str] = None,
    ):
        """
        初始化 Poe LLM 客户端

        Args:
            api_key: API 密钥，如未提供则从环境变量 POE_API_KEY 获取
            model: 模型名称
            base_url: API 基础 URL
            proxy: 代理地址（可选）
        """
        import os

        from dotenv import load_dotenv
        load_dotenv()

        self.api_key = api_key or os.environ.get("POE_API_KEY")
        self.model = model
        self.base_url = base_url
        self.proxy = proxy

        if not self.api_key:
            raise LLMClientError("未配置 POE_API_KEY，请在 .env 文件中设置或传入 api_key 参数")

    def complete(self, request: LLMRequest) -> LLMResponse:
        """执行 Poe API 补全"""
        import time

        import requests

        start_time = time.time()

        # 构建请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = request.to_api_format()
        if payload["model"] is None:
            payload["model"] = self.model

        # 设置代理
        proxies = None
        if self.proxy:
            proxies = {"http": self.proxy, "https": self.proxy}

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                proxies=proxies,
                timeout=60,
            )
            response.raise_for_status()

            latency = (time.time() - start_time) * 1000
            result = response.json()

            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = result.get("usage", {})

            return LLMResponse(
                content=content,
                model=self.model,
                provider=LLMProvider.POE,
                status=LLMStatus.SUCCESS,
                usage=usage,
                latency_ms=latency,
                raw_response=result,
            )

        except requests.exceptions.Timeout:
            return LLMResponse(
                content="",
                model=self.model,
                provider=LLMProvider.POE,
                status=LLMStatus.TIMEOUT,
                error_message="请求超时",
            )
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 429:
                return LLMResponse(
                    content="",
                    model=self.model,
                    provider=LLMProvider.POE,
                    status=LLMStatus.RATE_LIMITED,
                    error_message="请求频率限制",
                )
            return LLMResponse(
                content="",
                model=self.model,
                provider=LLMProvider.POE,
                status=LLMStatus.ERROR,
                error_message=f"HTTP 错误: {e}",
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=LLMProvider.POE,
                status=LLMStatus.ERROR,
                error_message=f"请求失败: {e}",
            )

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[dict, None]:
        """流式执行 Poe API 补全"""
        import aiohttp

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = request.to_api_format()
        if payload["model"] is None:
            payload["model"] = self.model
        payload["stream"] = True

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    if response.status != 200:
                        result = await response.text()
                        yield {"type": "token", "content": f"[错误] HTTP {response.status}: {result}"}
                        yield {"type": "done", "content": ""}
                        return

                    # 读取 SSE 流
                    async for line in response.content:
                        line_str = line.decode("utf-8").strip()
                        if not line_str or not line_str.startswith("data: "):
                            continue

                        data_str = line_str[6:]  # 去掉 "data: " 前缀
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})

                            # 思考内容
                            reasoning = delta.get("reasoning_content") or delta.get("reasoning")
                            if reasoning:
                                yield {"type": "thinking", "content": reasoning}

                            # 正常内容
                            content = delta.get("content")
                            if content:
                                yield {"type": "token", "content": content}
                        except json.JSONDecodeError:
                            continue

                    yield {"type": "done", "content": ""}

        except Exception as e:
            yield {"type": "token", "content": f"[错误] 流式请求失败: {e}"}
            yield {"type": "done", "content": ""}

    async def complete_async(self, request: LLMRequest) -> LLMResponse:
        """异步执行 Poe API 补全"""
        import asyncio

        import aiohttp

        start_time = asyncio.get_event_loop().time()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = request.to_api_format()
        if payload["model"] is None:
            payload["model"] = self.model

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    latency = (asyncio.get_event_loop().time() - start_time) * 1000
                    result = await response.json()

                    if response.status != 200:
                        return LLMResponse(
                            content="",
                            model=self.model,
                            provider=LLMProvider.POE,
                            status=LLMStatus.ERROR,
                            error_message=f"HTTP {response.status}: {result}",
                        )

                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    usage = result.get("usage", {})

                    return LLMResponse(
                        content=content,
                        model=self.model,
                        provider=LLMProvider.POE,
                        status=LLMStatus.SUCCESS,
                        usage=usage,
                        latency_ms=latency,
                        raw_response=result,
                    )

        except asyncio.TimeoutError:
            return LLMResponse(
                content="",
                model=self.model,
                provider=LLMProvider.POE,
                status=LLMStatus.TIMEOUT,
                error_message="请求超时",
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=LLMProvider.POE,
                status=LLMStatus.ERROR,
                error_message=f"异步请求失败: {e}",
            )


class LLMClientError(Exception):
    """LLM 客户端错误"""

    pass


# 模块级单例
_default_client: Optional[BaseLLMClient] = None


def get_llm_client(
    provider: LLMProvider = LLMProvider.MOCK,
    **kwargs: Any,
) -> BaseLLMClient:
    """
    获取 LLM 客户端实例

    Args:
        provider: LLM 提供商
        **kwargs: 客户端初始化参数

    Returns:
        BaseLLMClient: LLM 客户端实例
    """
    global _default_client

    if _default_client is not None:
        return _default_client

    if provider == LLMProvider.MOCK:
        _default_client = MockLLMClient(**kwargs)
    elif provider == LLMProvider.POE:
        _default_client = PoeLLMClient(**kwargs)
    else:
        raise LLMClientError(f"不支持的 LLM 提供商: {provider}")

    return _default_client


def set_llm_client(client: BaseLLMClient) -> None:
    """
    设置全局 LLM 客户端

    Args:
        client: LLM 客户端实例
    """
    global _default_client
    _default_client = client


def reset_llm_client() -> None:
    """重置全局 LLM 客户端"""
    global _default_client
    _default_client = None