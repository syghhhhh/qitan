# -*- coding: utf-8 -*-
"""
分析模块

负责对候选事实进行归并、冲突消解和结果结构化。
"""

from __future__ import annotations

from .company_profile_analyzer import (
    CompanyProfileAnalyzer,
    analyze_company_profile,
    get_company_profile_analyzer,
)

__all__ = [
    "CompanyProfileAnalyzer",
    "analyze_company_profile",
    "get_company_profile_analyzer",
]