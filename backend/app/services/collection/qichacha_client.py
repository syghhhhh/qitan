# -*- coding: utf-8 -*-
"""
企查查 API 客户端封装

封装企查查 API 的调用逻辑，提供：
- 模糊搜索：根据关键词搜索企业
- 企业信息核验：根据准确企业名获取详细信息
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class QichachaClient:
    """企查查 API 客户端"""

    # 缓存目录：项目根目录下的 api_qichacha/test_result
    CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "api_qichacha", "test_result")

    def __init__(
        self,
        app_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.app_key = app_key or os.getenv("QICHACHA_KEY", "")
        self.secret_key = secret_key or os.getenv("QICHACHA_SECRETKEY", "")
        if not self.app_key or not self.secret_key:
            raise ValueError("未配置企查查 API 密钥，请设置 QICHACHA_KEY 和 QICHACHA_SECRETKEY 环境变量")
        self.cache_dir = os.path.normpath(self.CACHE_DIR)

    def _get_headers(self) -> Dict[str, str]:
        """生成请求头（含 Token 签名）"""
        timespan = str(int(time.time()))
        token_raw = self.app_key + timespan + self.secret_key
        token = hashlib.md5(token_raw.encode("utf-8")).hexdigest().upper()
        return {"Token": token, "Timespan": timespan}

    def _get_cache_path(self, prefix: str, key: str) -> str:
        """生成缓存文件路径"""
        return os.path.join(self.cache_dir, f"[{prefix}]{key}.json")

    def _load_cache(self, prefix: str, key: str) -> Optional[Dict[str, Any]]:
        """尝试从缓存文件加载结果"""
        cache_path = self._get_cache_path(prefix, key)
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                print(f"[企查查] 命中本地缓存: {cache_path}")
                return json.load(f)
        return None

    def _save_cache(self, prefix: str, key: str, data: Dict[str, Any]) -> None:
        """将结果保存到缓存文件"""
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_path = self._get_cache_path(prefix, key)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[企查查] 结果已缓存: {cache_path}")

    def fuzzy_search(self, search_key: str) -> Dict[str, Any]:
        """
        企业模糊搜索

        Args:
            search_key: 搜索关键词（企业名、人名、产品名等）

        Returns:
            API 返回的 JSON 字典
        """
        # 优先从本地缓存读取
        cached = self._load_cache("企业模糊搜索", search_key)
        if cached is not None:
            return cached

        url = f"https://api.qichacha.com/FuzzySearch/GetList?key={self.app_key}&searchKey={search_key}"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        # 保存到本地缓存
        self._save_cache("企业模糊搜索", search_key, result)
        return result

    def enterprise_info_verify(self, search_key: str) -> Dict[str, Any]:
        """
        企业信息核验

        Args:
            search_key: 统一社会信用代码或完整企业名称

        Returns:
            API 返回的 JSON 字典
        """
        # 优先从本地缓存读取
        cached = self._load_cache("企业信息核验", search_key)
        if cached is not None:
            return cached

        url = f"https://api.qichacha.com/EnterpriseInfo/Verify?key={self.app_key}&searchKey={search_key}"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        # 保存到本地缓存
        self._save_cache("企业信息核验", search_key, result)
        return result

    def get_company_info(self, search_key: str) -> Dict[str, Any]:
        """
        完整流程：模糊搜索 → 获取准确企业名 → 企业信息核验

        Args:
            search_key: 搜索关键词

        Returns:
            包含 fuzzy_result（模糊搜索第一条）和 verify_result（核验详情）的字典
        """
        # 1. 模糊搜索
        fuzzy_result = self.fuzzy_search(search_key)
        if fuzzy_result.get("Status") != "200":
            raise ValueError(f"企查查模糊搜索失败: {fuzzy_result.get('Message', '未知错误')}")

        results = fuzzy_result.get("Result", [])
        if not results:
            raise ValueError(f"企查查模糊搜索未找到结果: {search_key}")

        # 取第一条结果的准确名称
        first_result = results[0]
        accurate_name = first_result.get("Name", "")

        # 2. 企业信息核验
        verify_result = self.enterprise_info_verify(accurate_name)
        if verify_result.get("Status") != "200":
            raise ValueError(f"企查查企业信息核验失败: {verify_result.get('Message', '未知错误')}")

        return {
            "fuzzy_results": results,
            "accurate_name": accurate_name,
            "verify_data": verify_result.get("Result", {}).get("Data", {}),
        }


# 模块级单例
_default_client: Optional[QichachaClient] = None


def get_qichacha_client() -> QichachaClient:
    """获取企查查客户端单例"""
    global _default_client
    if _default_client is None:
        _default_client = QichachaClient()
    return _default_client


def reset_qichacha_client() -> None:
    """重置企查查客户端单例"""
    global _default_client
    _default_client = None
