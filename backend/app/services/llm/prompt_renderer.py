# -*- coding: utf-8 -*-
"""
Prompt 渲染模块

提供模板化的 Prompt 构建能力，支持变量插值、条件渲染等功能。
当前阶段为基础实现，为后续扩展预留接口。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class PromptTemplateType(str, Enum):
    """Prompt 模板类型"""

    EXTRACTION = "extraction"  # 信息抽取
    ANALYSIS = "analysis"  # 业务分析
    GENERATION = "generation"  # 内容生成
    SUMMARIZATION = "summarization"  # 内容摘要
    CLASSIFICATION = "classification"  # 分类任务


@dataclass
class PromptTemplate:
    """
    Prompt 模板结构

    支持变量插值、条件块等基础模板功能。
    """

    name: str
    template_type: PromptTemplateType
    system_prompt: Optional[str] = None
    user_prompt_template: str = ""
    description: str = ""
    variables: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render(
        self,
        variables: Optional[Dict[str, Any]] = None,
        include_examples: bool = False,
    ) -> str:
        """
        渲染 Prompt

        Args:
            variables: 变量字典
            include_examples: 是否包含示例

        Returns:
            str: 渲染后的 Prompt
        """
        variables = variables or {}

        # 渲染用户 Prompt
        rendered = self._render_template(self.user_prompt_template, variables)

        # 添加示例
        if include_examples and self.examples:
            examples_text = self._format_examples()
            rendered = f"{examples_text}\n\n{rendered}"

        return rendered

    def render_with_system(
        self,
        variables: Optional[Dict[str, Any]] = None,
        include_examples: bool = False,
    ) -> Dict[str, str]:
        """
        渲染包含系统消息的完整 Prompt

        Args:
            variables: 变量字典
            include_examples: 是否包含示例

        Returns:
            Dict[str, str]: 包含 system 和 user 消息的字典
        """
        result = {}

        if self.system_prompt:
            result["system"] = self._render_template(self.system_prompt, variables)

        result["user"] = self.render(variables, include_examples)

        return result

    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板字符串

        支持 {{variable}} 语法和 {% if condition %}...{% endif %} 语法。
        """
        result = template

        # 渲染条件块
        condition_pattern = r"\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}"
        for match in re.finditer(condition_pattern, template, re.DOTALL):
            var_name = match.group(1)
            block_content = match.group(2)

            # 检查变量是否存在且为真
            if var_name in variables and variables[var_name]:
                result = result.replace(match.group(0), block_content)
            else:
                result = result.replace(match.group(0), "")

        # 渲染变量插值
        var_pattern = r"\{\{\s*(\w+)\s*\}\}"
        for match in re.finditer(var_pattern, result):
            var_name = match.group(1)
            value = variables.get(var_name, "")
            result = result.replace(match.group(0), str(value))

        return result.strip()

    def _format_examples(self) -> str:
        """格式化示例"""
        if not self.examples:
            return ""

        lines = ["以下是几个示例：\n"]
        for i, example in enumerate(self.examples, 1):
            lines.append(f"示例 {i}:")
            for key, value in example.items():
                lines.append(f"{key}: {value}")
            lines.append("")

        return "\n".join(lines)


class PromptRenderer:
    """
    Prompt 渲染器

    管理 Prompt 模板并提供渲染能力。
    """

    def __init__(self):
        """初始化 Prompt 渲染器"""
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_builtin_templates()

    def _load_builtin_templates(self) -> None:
        """加载内置模板"""
        # 企业画像抽取模板
        self.register_template(
            PromptTemplate(
                name="company_profile_extraction",
                template_type=PromptTemplateType.EXTRACTION,
                system_prompt="你是一个专业的企业信息分析助手，擅长从文本中提取企业画像信息。",
                user_prompt_template="""请从以下内容中提取企业画像信息：

企业名称：{{company_name}}
内容：
{{content}}

请提取以下信息（如果存在）：
1. 行业标签
2. 企业类型
3. 成立时间
4. 总部所在地
5. 主营业务
6. 主要产品或服务
7. 员工规模
8. 业务覆盖区域

请以 JSON 格式返回结果。""",
                description="企业画像信息抽取模板",
                variables=["company_name", "content"],
            )
        )

        # 近期动态抽取模板
        self.register_template(
            PromptTemplate(
                name="development_extraction",
                template_type=PromptTemplateType.EXTRACTION,
                system_prompt="你是一个专业的企业动态分析助手，擅长从新闻和公开信息中提取企业发展动态。",
                user_prompt_template="""请从以下新闻内容中提取企业近期发展动态：

企业名称：{{company_name}}
新闻标题：{{title}}
新闻内容：
{{content}}

请提取以下信息：
1. 事件类型（融资、招聘、扩张、合作、产品发布等）
2. 事件日期
3. 事件摘要
4. 事件重要性

请以 JSON 格式返回结果。""",
                description="近期动态抽取模板",
                variables=["company_name", "title", "content"],
            )
        )

        # 需求信号分析模板
        self.register_template(
            PromptTemplate(
                name="demand_signal_analysis",
                template_type=PromptTemplateType.ANALYSIS,
                system_prompt="你是一个专业的商业分析助手，擅长从企业信息中识别潜在需求信号。",
                user_prompt_template="""请分析以下企业信息，识别潜在的需求信号：

企业画像：
{{company_profile}}

近期动态：
{{recent_developments}}

我方产品：{{our_product}}

请分析：
1. 该企业可能存在哪些需求痛点？
2. 这些需求与我方产品的匹配程度如何？
3. 推荐的切入点是什么？

请以 JSON 格式返回结果。""",
                description="需求信号分析模板",
                variables=["company_profile", "recent_developments", "our_product"],
            )
        )

        # 内容摘要模板
        self.register_template(
            PromptTemplate(
                name="content_summarization",
                template_type=PromptTemplateType.SUMMARIZATION,
                system_prompt="你是一个专业的文本摘要助手。",
                user_prompt_template="""请对以下内容进行摘要：

{{content}}

要求：
1. 保留关键信息
2. 简洁明了
3. 不超过 200 字""",
                description="内容摘要模板",
                variables=["content"],
            )
        )

    def register_template(self, template: PromptTemplate) -> None:
        """
        注册 Prompt 模板

        Args:
            template: Prompt 模板对象
        """
        self._templates[template.name] = template

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        获取 Prompt 模板

        Args:
            name: 模板名称

        Returns:
            Optional[PromptTemplate]: 模板对象，如果不存在返回 None
        """
        return self._templates.get(name)

    def render(
        self,
        template_name: str,
        variables: Optional[Dict[str, Any]] = None,
        include_examples: bool = False,
    ) -> str:
        """
        渲染指定模板

        Args:
            template_name: 模板名称
            variables: 变量字典
            include_examples: 是否包含示例

        Returns:
            str: 渲染后的 Prompt

        Raises:
            ValueError: 模板不存在时抛出
        """
        template = self.get_template(template_name)
        if template is None:
            raise ValueError(f"模板不存在: {template_name}")

        return template.render(variables, include_examples)

    def render_with_system(
        self,
        template_name: str,
        variables: Optional[Dict[str, Any]] = None,
        include_examples: bool = False,
    ) -> Dict[str, str]:
        """
        渲染包含系统消息的完整 Prompt

        Args:
            template_name: 模板名称
            variables: 变量字典
            include_examples: 是否包含示例

        Returns:
            Dict[str, str]: 包含 system 和 user 消息的字典
        """
        template = self.get_template(template_name)
        if template is None:
            raise ValueError(f"模板不存在: {template_name}")

        return template.render_with_system(variables, include_examples)

    def list_templates(self) -> List[str]:
        """
        列出所有已注册的模板名称

        Returns:
            List[str]: 模板名称列表
        """
        return list(self._templates.keys())

    def create_custom_template(
        self,
        name: str,
        template_type: PromptTemplateType,
        user_prompt_template: str,
        system_prompt: Optional[str] = None,
        variables: Optional[List[str]] = None,
        description: str = "",
    ) -> PromptTemplate:
        """
        创建自定义模板

        Args:
            name: 模板名称
            template_type: 模板类型
            user_prompt_template: 用户 Prompt 模板
            system_prompt: 系统 Prompt（可选）
            variables: 变量列表
            description: 描述

        Returns:
            PromptTemplate: 创建的模板对象
        """
        # 自动提取变量
        if variables is None:
            var_pattern = r"\{\{\s*(\w+)\s*\}\}"
            variables = list(set(re.findall(var_pattern, user_prompt_template)))

        template = PromptTemplate(
            name=name,
            template_type=template_type,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            description=description,
            variables=variables or [],
        )

        self.register_template(template)
        return template


# 模块级单例
_default_renderer: Optional[PromptRenderer] = None


def get_prompt_renderer() -> PromptRenderer:
    """
    获取 Prompt 渲染器单例

    Returns:
        PromptRenderer: Prompt 渲染器实例
    """
    global _default_renderer
    if _default_renderer is None:
        _default_renderer = PromptRenderer()
    return _default_renderer


def render_prompt(
    template_name: str,
    variables: Optional[Dict[str, Any]] = None,
) -> str:
    """
    便捷函数：渲染指定模板

    Args:
        template_name: 模板名称
        variables: 变量字典

    Returns:
        str: 渲染后的 Prompt
    """
    return get_prompt_renderer().render(template_name, variables)