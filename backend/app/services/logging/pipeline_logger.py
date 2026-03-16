# -*- coding: utf-8 -*-
"""
流水线日志模块

每次分析请求生成一份独立的日志文件，记录：
- 用户输入内容
- 各模块函数的入参、返回结果、完成用时
- 日志命名: {调用时间}_{企业名}.log
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional

# 日志目录：backend/logs/
LOG_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs"))


def get_log_dir() -> str:
    """获取日志目录路径"""
    return LOG_DIR


def _sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def _truncate(obj: Any, max_len: int = 2000) -> str:
    """将对象序列化为字符串，超长截断"""
    try:
        if isinstance(obj, str):
            text = obj
        elif isinstance(obj, dict) or isinstance(obj, list):
            text = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
        else:
            text = str(obj)
    except Exception:
        text = repr(obj)

    if len(text) > max_len:
        return text[:max_len] + f"\n... [截断，总长度 {len(text)} 字符]"
    return text


class PipelineLogger:
    """
    流水线日志记录器

    每个分析请求创建一个实例，对应一个独立的日志文件。

    用法:
        logger = PipelineLogger(company_name="华为")
        logger.log_user_input({...})
        result = logger.log_function_call("模块名", "函数名", func, arg1, arg2, key=val)
    """

    def __init__(self, company_name: str):
        os.makedirs(LOG_DIR, exist_ok=True)

        self.company_name = company_name
        self.created_at = datetime.now()
        timestamp = self.created_at.strftime("%Y%m%d_%H%M%S")
        safe_name = _sanitize_filename(company_name)
        self.filename = f"{timestamp}_{safe_name}.log"
        self.filepath = os.path.join(LOG_DIR, self.filename)

        # 写入日志头
        self._write_header()

    def _write_header(self) -> None:
        """写入日志文件头部"""
        sep = "=" * 80
        header = (
            f"{sep}\n"
            f"  企业背调分析日志\n"
            f"  企业名称: {self.company_name}\n"
            f"  创建时间: {self.created_at.strftime('%Y-%m-%d %H:%M:%S.%f')}\n"
            f"{sep}\n\n"
        )
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(header)

    def _append(self, text: str) -> None:
        """追加内容到日志文件"""
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(text)

    def log_user_input(self, user_input: Dict[str, Any]) -> None:
        """记录用户输入内容"""
        lines = [
            "-" * 60 + "\n",
            f"[用户输入] {datetime.now().strftime('%H:%M:%S.%f')}\n",
            "-" * 60 + "\n",
        ]
        for key, value in user_input.items():
            lines.append(f"  {key}: {value}\n")
        lines.append("\n")
        self._append("".join(lines))

    def log_function_call(
        self,
        module: str,
        func_name: str,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        执行并记录一个同步函数调用

        记录入参、返回结果和用时，然后返回函数的实际返回值。

        Args:
            module: 模块名称（如 "企查查采集"、"LLM分析"）
            func_name: 函数名称
            func: 要调用的函数
            *args, **kwargs: 函数参数

        Returns:
            函数的返回值
        """
        now = datetime.now().strftime("%H:%M:%S.%f")

        # 记录入参
        params_parts = []
        if args:
            for i, arg in enumerate(args):
                params_parts.append(f"    arg[{i}]: {_truncate(arg, 1000)}")
        if kwargs:
            for k, v in kwargs.items():
                params_parts.append(f"    {k}: {_truncate(v, 1000)}")
        params_text = "\n".join(params_parts) if params_parts else "    (无参数)"

        self._append(
            f"{'─' * 60}\n"
            f"[{module}] {func_name}  @ {now}\n"
            f"  ▶ 入参:\n{params_text}\n"
        )

        # 执行函数并计时
        start = time.time()
        error_occurred = False
        result = None
        error_info = None

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_occurred = True
            error_info = e
            raise
        finally:
            elapsed = time.time() - start
            elapsed_text = f"{elapsed:.3f}s" if elapsed < 60 else f"{elapsed / 60:.1f}min"

            if error_occurred:
                self._append(
                    f"  ✗ 异常: {type(error_info).__name__}: {error_info}\n"
                    f"  ⏱ 用时: {elapsed_text}\n\n"
                )
            else:
                self._append(
                    f"  ◀ 返回结果:\n    {_truncate(result)}\n"
                    f"  ⏱ 用时: {elapsed_text}\n\n"
                )

    def log_stage_start(self, stage_name: str) -> None:
        """记录阶段开始"""
        now = datetime.now().strftime("%H:%M:%S.%f")
        self._append(
            f"\n{'=' * 60}\n"
            f"  阶段开始: {stage_name}  @ {now}\n"
            f"{'=' * 60}\n"
        )

    def log_stage_end(self, stage_name: str, elapsed: float) -> None:
        """记录阶段结束"""
        elapsed_text = f"{elapsed:.3f}s" if elapsed < 60 else f"{elapsed / 60:.1f}min"
        self._append(
            f"  阶段完成: {stage_name}  用时: {elapsed_text}\n"
            f"{'=' * 60}\n\n"
        )

    def log_info(self, module: str, message: str) -> None:
        """记录一般信息"""
        now = datetime.now().strftime("%H:%M:%S.%f")
        self._append(f"[{module}] {now} | {message}\n")

    def log_error(self, module: str, error: Exception) -> None:
        """记录错误信息"""
        now = datetime.now().strftime("%H:%M:%S.%f")
        self._append(f"[{module}] {now} | ✗ ERROR: {type(error).__name__}: {error}\n")

    def log_summary(self, total_elapsed: float, success: bool) -> None:
        """记录日志总结"""
        elapsed_text = f"{total_elapsed:.3f}s" if total_elapsed < 60 else f"{total_elapsed / 60:.1f}min"
        status = "成功" if success else "失败"
        self._append(
            f"\n{'=' * 80}\n"
            f"  分析完成  状态: {status}  总用时: {elapsed_text}\n"
            f"  日志文件: {self.filename}\n"
            f"{'=' * 80}\n"
        )
