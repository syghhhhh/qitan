# -*- coding: utf-8 -*-
"""
抽取模块

负责从处理后的证据中抽取结构化候选事实。

模块组成：
- company_profile_extractor: 企业画像抽取器
- development_extractor: 近期动态抽取器
"""

from __future__ import annotations

from .company_profile_extractor import (
    CompanyProfileExtractor,
    extract_company_profile,
    get_company_profile_extractor,
)
from .development_extractor import (
    DevelopmentExtractor,
    extract_developments,
    get_development_extractor,
)

__all__ = [
    # 企业画像抽取器
    "CompanyProfileExtractor",
    "extract_company_profile",
    "get_company_profile_extractor",
    # 近期动态抽取器
    "DevelopmentExtractor",
    "extract_developments",
    "get_development_extractor",
]