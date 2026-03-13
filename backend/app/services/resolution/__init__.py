# -*- coding: utf-8 -*-
"""
实体解析模块

负责企业实体标准化，产出标准名、域名、别名等信息。
"""

from __future__ import annotations

from .entity_resolver import (
    EntityResolver,
    get_entity_resolver,
    resolve_entity,
)

__all__ = [
    "EntityResolver",
    "get_entity_resolver",
    "resolve_entity",
]