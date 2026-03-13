# -*- coding: utf-8 -*-
"""
EntityResolver - 企业实体确认器

在信息采集前，确认当前分析对象是哪一家企业，解决：
- 同名企业混淆
- 品牌名与注册主体不一致
- 官网域名与公司名映射不一致
- 用户仅给出简称或不完整名称

输出标准化的 ResolvedCompany 对象，为后续采集与分析提供统一企业标识。
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from ..orchestrator.pipeline_state import ResolvedCompany


class EntityResolver:
    """
    企业实体确认器

    根据公司名称和官网 URL 产出标准化企业实体信息，包括：
    - 标准公司名
    - 官网域名
    - 别名列表
    - 实体识别置信度
    - 解析备注

    使用方式：
        resolver = EntityResolver()
        resolved = resolver.resolve(
            company_name="阿里巴巴",
            company_website="https://www.alibaba.com"
        )
    """

    # 常见公司后缀（用于提取核心名称）
    COMPANY_SUFFIXES = [
        "有限公司", "有限责任公司", "股份有限公司",
        "集团", "集团公司",
        "科技有限公司", "网络科技有限公司", "信息技术有限公司",
        "科技发展有限公司", "技术发展有限公司",
        "有限公司", "CO., LTD.", "CO.,LTD", "LTD.", "LTD",
        "CORP.", "CORPORATION", "INC.", "INCORPORATED",
        "CO.", "COMPANY",
    ]

    # 常见品牌名映射（示例，后续可扩展为配置或数据库）
    BRAND_MAPPINGS = {
        # 阿里系
        "阿里巴巴": ("阿里巴巴集团控股有限公司", "alibaba.com"),
        "阿里": ("阿里巴巴集团控股有限公司", "alibaba.com"),
        "alibaba": ("Alibaba Group", "alibaba.com"),
        "淘宝": ("浙江淘宝网络有限公司", "taobao.com"),
        "天猫": ("浙江天猫网络有限公司", "tmall.com"),
        "支付宝": ("支付宝（中国）网络技术有限公司", "alipay.com"),
        "阿里云": ("阿里云计算有限公司", "aliyun.com"),
        # 腾讯系
        "腾讯": ("深圳市腾讯计算机系统有限公司", "tencent.com"),
        "tencent": ("Tencent Holdings Limited", "tencent.com"),
        "微信": ("深圳市腾讯计算机系统有限公司", "weixin.qq.com"),
        "wechat": ("Tencent Holdings Limited", "wechat.com"),
        # 百度系
        "百度": ("北京百度网讯科技有限公司", "baidu.com"),
        "baidu": ("Baidu, Inc.", "baidu.com"),
        # 字节系
        "字节跳动": ("北京字节跳动科技有限公司", "bytedance.com"),
        "抖音": ("北京抖音信息服务有限公司", "douyin.com"),
        "今日头条": ("北京字节跳动科技有限公司", "toutiao.com"),
        # 美团
        "美团": ("北京三快在线科技有限公司", "meituan.com"),
        # 京东
        "京东": ("北京京东世纪贸易有限公司", "jd.com"),
        "jd": ("JD.com, Inc.", "jd.com"),
        # 华为
        "华为": ("华为技术有限公司", "huawei.com"),
        "huawei": ("Huawei Technologies Co., Ltd.", "huawei.com"),
        # 小米
        "小米": ("小米科技有限责任公司", "mi.com"),
        "xiaomi": ("Xiaomi Corporation", "mi.com"),
    }

    # 域名到公司的反向映射
    DOMAIN_MAPPINGS = {
        "alibaba.com": "阿里巴巴集团控股有限公司",
        "taobao.com": "浙江淘宝网络有限公司",
        "tmall.com": "浙江天猫网络有限公司",
        "alipay.com": "支付宝（中国）网络技术有限公司",
        "aliyun.com": "阿里云计算有限公司",
        "tencent.com": "深圳市腾讯计算机系统有限公司",
        "weixin.qq.com": "深圳市腾讯计算机系统有限公司",
        "wechat.com": "Tencent Holdings Limited",
        "baidu.com": "北京百度网讯科技有限公司",
        "bytedance.com": "北京字节跳动科技有限公司",
        "douyin.com": "北京抖音信息服务有限公司",
        "toutiao.com": "北京字节跳动科技有限公司",
        "meituan.com": "北京三快在线科技有限公司",
        "jd.com": "北京京东世纪贸易有限公司",
        "huawei.com": "华为技术有限公司",
        "mi.com": "小米科技有限责任公司",
    }

    def resolve(
        self,
        company_name: Optional[str] = None,
        company_website: Optional[str] = None,
    ) -> ResolvedCompany:
        """
        解析企业实体

        Args:
            company_name: 公司名称
            company_website: 公司官网 URL

        Returns:
            ResolvedCompany: 标准化的企业实体信息

        Raises:
            ValueError: 当公司名和官网都未提供时
        """
        # 校验至少有一个输入
        if not company_name and not company_website:
            raise ValueError("必须提供公司名称或公司官网")

        # 提取域名
        domain = None
        if company_website:
            domain = self._extract_domain(company_website)

        # 解析逻辑分支
        if company_name and domain:
            # 同时有名称和域名，进行匹配验证
            return self._resolve_with_both(company_name, domain)
        elif company_name:
            # 仅有名称
            return self._resolve_with_name_only(company_name)
        else:
            # 仅有域名
            return self._resolve_with_domain_only(domain)

    def _resolve_with_both(
        self, company_name: str, domain: str
    ) -> ResolvedCompany:
        """
        同时有公司名和域名时的解析

        Args:
            company_name: 公司名称
            domain: 官网域名

        Returns:
            ResolvedCompany: 标准化的企业实体信息
        """
        # 清理公司名
        cleaned_name = self._clean_company_name(company_name)

        # 检查品牌映射
        brand_info = self._lookup_brand(company_name)
        domain_company = self._lookup_domain(domain)

        # 初始化别名列表
        aliases: List[str] = []

        # 确定标准名称
        standard_name = cleaned_name
        confidence = 0.7  # 基础置信度
        resolution_notes_parts: List[str] = []

        # 如果有品牌映射
        if brand_info:
            mapped_name, mapped_domain = brand_info
            standard_name = mapped_name
            aliases.append(cleaned_name)
            confidence = 0.95
            resolution_notes_parts.append("基于品牌名称映射")

            # 验证域名是否匹配
            if mapped_domain and domain != mapped_domain:
                # 域名不匹配，降低置信度
                confidence = 0.75
                resolution_notes_parts.append(f"域名 {domain} 与品牌默认域名 {mapped_domain} 不完全匹配")
        elif domain_company:
            # 域名有映射
            standard_name = domain_company
            aliases.append(cleaned_name)
            confidence = 0.9
            resolution_notes_parts.append("基于官网域名映射")
        else:
            # 无映射，使用清理后的名称
            # 尝试从域名推断公司名
            inferred_name = self._infer_name_from_domain(domain)
            if inferred_name:
                aliases.append(inferred_name)
            resolution_notes_parts.append("基于输入信息直接标准化")

        # 构建备注
        resolution_notes = "; ".join(resolution_notes_parts) if resolution_notes_parts else None

        return ResolvedCompany(
            standard_name=standard_name,
            domain=domain,
            aliases=aliases,
            confidence=confidence,
            resolution_notes=resolution_notes,
        )

    def _resolve_with_name_only(self, company_name: str) -> ResolvedCompany:
        """
        仅有公司名时的解析

        Args:
            company_name: 公司名称

        Returns:
            ResolvedCompany: 标准化的企业实体信息
        """
        # 清理公司名
        cleaned_name = self._clean_company_name(company_name)

        # 检查品牌映射
        brand_info = self._lookup_brand(company_name)

        if brand_info:
            mapped_name, mapped_domain = brand_info
            return ResolvedCompany(
                standard_name=mapped_name,
                domain=mapped_domain,
                aliases=[cleaned_name],
                confidence=0.85,
                resolution_notes="基于品牌名称映射，无官网信息验证",
            )

        # 无映射，使用清理后的名称
        return ResolvedCompany(
            standard_name=cleaned_name,
            domain=None,
            aliases=[],
            confidence=0.6,
            resolution_notes="仅提供公司名称，无官网信息，置信度降低",
        )

    def _resolve_with_domain_only(self, domain: str) -> ResolvedCompany:
        """
        仅有域名时的解析

        Args:
            domain: 官网域名

        Returns:
            ResolvedCompany: 标准化的企业实体信息
        """
        # 检查域名映射
        domain_company = self._lookup_domain(domain)

        if domain_company:
            return ResolvedCompany(
                standard_name=domain_company,
                domain=domain,
                aliases=[],
                confidence=0.85,
                resolution_notes="基于官网域名映射",
            )

        # 无映射，从域名推断公司名
        inferred_name = self._infer_name_from_domain(domain)

        return ResolvedCompany(
            standard_name=inferred_name or domain,
            domain=domain,
            aliases=[],
            confidence=0.5,
            resolution_notes="仅提供官网域名，从域名推断公司名称，置信度较低",
        )

    def _clean_company_name(self, name: str) -> str:
        """
        清理公司名称

        移除常见后缀、多余空格等，提取核心名称

        Args:
            name: 原始公司名称

        Returns:
            清理后的公司名称
        """
        if not name:
            return ""

        # 去除首尾空白
        cleaned = name.strip()

        # 去除多余空格
        cleaned = " ".join(cleaned.split())

        # 移除常见后缀（从长到短匹配）
        for suffix in sorted(self.COMPANY_SUFFIXES, key=len, reverse=True):
            if cleaned.upper().endswith(suffix.upper()):
                cleaned = cleaned[:-len(suffix)].strip()
                break

        return cleaned

    def _extract_domain(self, website: str) -> str:
        """
        从 URL 提取域名

        Args:
            website: 完整 URL 或域名

        Returns:
            清理后的域名（小写）
        """
        if not website:
            return ""

        domain = website.strip().lower()

        # 移除协议前缀
        for prefix in ["https://", "http://", "www."]:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]

        # 移除路径部分
        if "/" in domain:
            domain = domain.split("/")[0]

        # 移除端口
        if ":" in domain:
            domain = domain.split(":")[0]

        return domain

    def _lookup_brand(self, name: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        查找品牌映射

        Args:
            name: 公司名称或品牌名

        Returns:
            如果找到映射，返回 (标准公司名, 默认域名)；否则返回 None
        """
        # 清理名称用于匹配
        cleaned = name.strip().lower()
        return self.BRAND_MAPPINGS.get(cleaned)

    def _lookup_domain(self, domain: str) -> Optional[str]:
        """
        查找域名映射

        Args:
            domain: 域名

        Returns:
            如果找到映射，返回标准公司名；否则返回 None
        """
        cleaned = domain.strip().lower()
        return self.DOMAIN_MAPPINGS.get(cleaned)

    def _infer_name_from_domain(self, domain: str) -> Optional[str]:
        """
        从域名推断公司名

        简单实现：提取域名的主体部分并转换为首字母大写

        Args:
            domain: 域名

        Returns:
            推断的公司名
        """
        if not domain:
            return None

        # 移除顶级域名后缀
        name_part = domain.split(".")[0]

        # 将连字符转为空格
        name_part = name_part.replace("-", " ")

        # 首字母大写
        return name_part.title()


# 模块级单例实例
_default_resolver: Optional[EntityResolver] = None


def get_entity_resolver() -> EntityResolver:
    """
    获取实体解析器单例实例

    Returns:
        EntityResolver: 实体解析器实例
    """
    global _default_resolver
    if _default_resolver is None:
        _default_resolver = EntityResolver()
    return _default_resolver


def resolve_entity(
    company_name: Optional[str] = None,
    company_website: Optional[str] = None,
) -> ResolvedCompany:
    """
    便捷函数：解析企业实体

    Args:
        company_name: 公司名称
        company_website: 公司官网 URL

    Returns:
        ResolvedCompany: 标准化的企业实体信息
    """
    resolver = get_entity_resolver()
    return resolver.resolve(
        company_name=company_name,
        company_website=company_website,
    )