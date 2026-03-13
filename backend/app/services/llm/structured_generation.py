# -*- coding: utf-8 -*-
"""
结构化生成模块

提供基于 LLM 的结构化输出生成能力，支持 JSON Schema 约束、
Pydantic 模型转换等功能。当前阶段为基础实现。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_type_hints

from pydantic import BaseModel, ValidationError

from .llm_client import (
    BaseLLMClient,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMStatus,
    get_llm_client,
)
from .prompt_renderer import PromptRenderer, get_prompt_renderer

T = TypeVar("T", bound=BaseModel)


class OutputFormat(str, Enum):
    """输出格式类型"""

    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


@dataclass
class StructuredOutputConfig:
    """结构化输出配置"""

    output_format: OutputFormat = OutputFormat.JSON
    enforce_schema: bool = True
    max_retries: int = 3
    temperature: float = 0.3  # 结构化输出建议使用较低温度
    include_reasoning: bool = False
    fallback_value: Optional[Dict[str, Any]] = None


@dataclass
class StructuredOutputResult:
    """结构化输出结果"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    raw_response: str = ""
    error_message: Optional[str] = None
    retries: int = 0
    latency_ms: float = 0.0


class StructuredGenerator:
    """
    结构化输出生成器

    支持基于 JSON Schema 或 Pydantic 模型的结构化输出生成。
    """

    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        prompt_renderer: Optional[PromptRenderer] = None,
        config: Optional[StructuredOutputConfig] = None,
    ):
        """
        初始化结构化生成器

        Args:
            llm_client: LLM 客户端（可选，默认使用全局客户端）
            prompt_renderer: Prompt 渲染器（可选）
            config: 输出配置
        """
        self.llm_client = llm_client or get_llm_client()
        self.prompt_renderer = prompt_renderer or get_prompt_renderer()
        self.config = config or StructuredOutputConfig()

    def generate(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        config: Optional[StructuredOutputConfig] = None,
    ) -> StructuredOutputResult:
        """
        生成结构化输出

        Args:
            prompt: 用户 Prompt
            schema: JSON Schema（可选）
            system_prompt: 系统提示（可选）
            config: 输出配置（可选）

        Returns:
            StructuredOutputResult: 结构化输出结果
        """
        config = config or self.config
        start_time = datetime.now()

        # 构建 Prompt
        full_prompt = self._build_structured_prompt(prompt, schema, config)

        # 构建请求
        messages = []
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        messages.append(LLMMessage(role="user", content=full_prompt))

        request = LLMRequest(
            messages=messages,
            temperature=config.temperature,
            max_tokens=4096,
        )

        # 重试机制
        last_error = None
        for attempt in range(config.max_retries):
            response = self.llm_client.complete(request)

            if not response.is_success:
                last_error = f"LLM 调用失败: {response.error_message}"
                continue

            # 解析结构化输出
            parsed = self._parse_response(response.content, config)

            if parsed is not None:
                # 验证 Schema
                if schema and config.enforce_schema:
                    validation_error = self._validate_against_schema(parsed, schema)
                    if validation_error:
                        last_error = validation_error
                        continue

                latency = (datetime.now() - start_time).total_seconds() * 1000
                return StructuredOutputResult(
                    success=True,
                    data=parsed,
                    raw_response=response.content,
                    retries=attempt,
                    latency_ms=latency,
                )
            else:
                last_error = "无法解析结构化输出"

        # 所有重试都失败
        latency = (datetime.now() - start_time).total_seconds() * 1000
        return StructuredOutputResult(
            success=False,
            raw_response=response.content if "response" in dir() else "",
            error_message=last_error,
            retries=config.max_retries,
            latency_ms=latency,
        )

    def generate_model(
        self,
        prompt: str,
        model_class: Type[T],
        system_prompt: Optional[str] = None,
        config: Optional[StructuredOutputConfig] = None,
    ) -> Optional[T]:
        """
        生成 Pydantic 模型实例

        Args:
            prompt: 用户 Prompt
            model_class: Pydantic 模型类
            system_prompt: 系统提示（可选）
            config: 输出配置（可选）

        Returns:
            Optional[T]: 模型实例，解析失败返回 None
        """
        schema = model_class.model_json_schema()
        result = self.generate(prompt, schema, system_prompt, config)

        if result.success and result.data:
            try:
                return model_class.model_validate(result.data)
            except ValidationError as e:
                return None

        return None

    async def generate_async(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        config: Optional[StructuredOutputConfig] = None,
    ) -> StructuredOutputResult:
        """
        异步生成结构化输出

        Args:
            prompt: 用户 Prompt
            schema: JSON Schema（可选）
            system_prompt: 系统提示（可选）
            config: 输出配置（可选）

        Returns:
            StructuredOutputResult: 结构化输出结果
        """
        # 当前阶段使用同步实现
        return self.generate(prompt, schema, system_prompt, config)

    def _build_structured_prompt(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]],
        config: StructuredOutputConfig,
    ) -> str:
        """构建结构化输出 Prompt"""
        parts = [prompt]

        if schema:
            parts.append("\n\n请按以下 JSON Schema 格式输出：")
            parts.append(f"\n```json\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n```")

        parts.append("\n\n请直接输出 JSON 格式的结果，不要包含其他说明文字。")

        if config.include_reasoning:
            parts.append("\n在给出最终结果前，可以先简要说明推理过程。")

        return "\n".join(parts)

    def _parse_response(
        self,
        response: str,
        config: StructuredOutputConfig,
    ) -> Optional[Dict[str, Any]]:
        """解析 LLM 响应为结构化数据"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 代码块
        json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(json_block_pattern, response)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # 尝试查找 JSON 对象
        json_object_pattern = r"\{[\s\S]*\}"
        matches = re.findall(json_object_pattern, response)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        return None

    def _validate_against_schema(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> Optional[str]:
        """验证数据是否符合 Schema"""
        try:
            # 基础验证：检查必填字段
            required_fields = schema.get("required", [])
            properties = schema.get("properties", {})

            for field_name in required_fields:
                if field_name not in data:
                    return f"缺少必填字段: {field_name}"

            # 类型验证
            for field_name, field_value in data.items():
                if field_name in properties:
                    field_schema = properties[field_name]
                    expected_type = field_schema.get("type")

                    if expected_type == "string" and not isinstance(field_value, str):
                        return f"字段 {field_name} 应为字符串类型"
                    elif expected_type == "number" and not isinstance(field_value, (int, float)):
                        return f"字段 {field_name} 应为数值类型"
                    elif expected_type == "integer" and not isinstance(field_value, int):
                        return f"字段 {field_name} 应为整数类型"
                    elif expected_type == "boolean" and not isinstance(field_value, bool):
                        return f"字段 {field_name} 应为布尔类型"
                    elif expected_type == "array" and not isinstance(field_value, list):
                        return f"字段 {field_name} 应为数组类型"
                    elif expected_type == "object" and not isinstance(field_value, dict):
                        return f"字段 {field_name} 应为对象类型"

            return None

        except Exception as e:
            return f"验证错误: {e}"


class MockStructuredGenerator(StructuredGenerator):
    """
    Mock 结构化生成器

    用于测试，返回预设的结构化数据。
    """

    def __init__(
        self,
        mock_data: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化 Mock 生成器

        Args:
            mock_data: 预设的 mock 数据
        """
        super().__init__()
        self.mock_data = mock_data or {
            "company_name": "示例科技有限公司",
            "industry": ["科技", "软件"],
            "founded_year": 2020,
            "headquarters": "上海",
        }

    def generate(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        config: Optional[StructuredOutputConfig] = None,
    ) -> StructuredOutputResult:
        """返回 Mock 结构化输出"""
        return StructuredOutputResult(
            success=True,
            data=self.mock_data,
            raw_response=json.dumps(self.mock_data, ensure_ascii=False),
            retries=0,
            latency_ms=10.0,
        )


# 模块级单例
_default_generator: Optional[StructuredGenerator] = None


def get_structured_generator(
    use_mock: bool = True,
) -> StructuredGenerator:
    """
    获取结构化生成器单例

    Args:
        use_mock: 是否使用 Mock 生成器

    Returns:
        StructuredGenerator: 结构化生成器实例
    """
    global _default_generator

    if _default_generator is not None:
        return _default_generator

    if use_mock:
        _default_generator = MockStructuredGenerator()
    else:
        _default_generator = StructuredGenerator()

    return _default_generator


def set_structured_generator(generator: StructuredGenerator) -> None:
    """
    设置全局结构化生成器

    Args:
        generator: 结构化生成器实例
    """
    global _default_generator
    _default_generator = generator


def generate_structured_output(
    prompt: str,
    schema: Optional[Dict[str, Any]] = None,
    use_mock: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    便捷函数：生成结构化输出

    Args:
        prompt: 用户 Prompt
        schema: JSON Schema（可选）
        use_mock: 是否使用 Mock 生成器

    Returns:
        Optional[Dict[str, Any]]: 结构化数据，失败返回 None
    """
    generator = get_structured_generator(use_mock)
    result = generator.generate(prompt, schema)

    if result.success:
        return result.data
    return None