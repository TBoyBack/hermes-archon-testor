"""
日志工具模块

提供统一的日志配置和管理功能，基于 loguru 实现。
支持：
- 彩色控制台输出
- 文件日志轮转
- 结构化日志
- 性能追踪

Usage:
    from src.core.logger import logger, setup_logger
    
    # 基本使用
    logger.info("Hello world")
    logger.error("Something went wrong")
    
    # 结构化日志
    logger.info("User logged in", extra={"user_id": 123, "action": "login"})
    
    # 性能追踪
    with logger.profile("fetch_data"):
        data = fetch_data()
"""

from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from loguru import logger as _logger

from src.core.config import settings


class Logger:
    """
    日志管理器
    
    封装 loguru，提供更方便的接口
    """
    
    def __init__(self):
        self._logger = _logger
        self._context: Dict[str, Any] = {}
        self._setup = False
    
    def setup(
        self,
        level: Optional[str] = None,
        log_dir: Optional[Union[str, Path]] = None,
        rotation: str = "100 MB",
        retention: str = "30 days",
        format_string: Optional[str] = None,
    ) -> None:
        """
        配置日志系统
        
        Args:
            level: 日志级别
            log_dir: 日志文件目录
            rotation: 日志轮转大小
            retention: 日志保留时间
            format_string: 日志格式
        """
        if self._setup:
            return
        
        level = level or settings.logging.level
        log_dir = Path(log_dir) if log_dir else Path(settings.logging.dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认格式
        if format_string is None:
            format_string = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        
        # 移除默认处理器
        self._logger.remove()
        
        # 添加控制台处理器
        self._logger.add(
            sys.stdout,
            level=level,
            format=format_string,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        
        # 添加文件处理器
        log_file = log_dir / f"app_{datetime.now():%Y%m%d}.log"
        self._logger.add(
            log_file,
            level=level,
            format=format_string,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )
        
        # 添加错误日志单独文件
        error_file = log_dir / f"error_{datetime.now():%Y%m%d}.log"
        self._logger.add(
            error_file,
            level="ERROR",
            format=format_string,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )
        
        self._setup = True
    
    def add_context(self, **kwargs: Any) -> None:
        """添加日志上下文"""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """清除日志上下文"""
        self._context.clear()
    
    def _format_message(self, message: str, **kwargs: Any) -> str:
        """格式化消息"""
        extra = {**self._context, **kwargs}
        if extra:
            extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            return f"{message} | {extra_str}"
        return message
    
    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(self._format_message(message, **kwargs))
    
    def success(self, message: str, **kwargs: Any) -> None:
        self._logger.success(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs: Any) -> None:
        self._logger.critical(self._format_message(message, **kwargs))
    
    def exception(self, message: str, **kwargs: Any) -> None:
        self._logger.exception(self._format_message(message, **kwargs))
    
    @contextmanager
    def context(self, **kwargs: Any):
        """上下文管理器，在块内添加临时上下文"""
        old_context = self._context.copy()
        self._context.update(kwargs)
        try:
            yield self
        finally:
            self._context = old_context
    
    @contextmanager
    def profile(self, name: str, **kwargs: Any):
        """性能追踪上下文管理器"""
        start_time = time.perf_counter()
        self.info(f"[START] {name}", **kwargs)
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            self.info(f"[END] {name} - 耗时: {elapsed:.3f}s", **kwargs)
    
    def track(self, operation: str) -> Callable:
        """装饰器：追踪函数执行"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter()
                self.info(f"[CALL] {operation}: {func.__name__}")
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.perf_counter() - start_time
                    self.info(f"[RETURN] {operation}: {func.__name__} - 耗时: {elapsed:.3f}s")
                    return result
                except Exception as e:
                    elapsed = time.perf_counter() - start_time
                    self.error(f"[ERROR] {operation}: {func.__name__} - 耗时: {elapsed:.3f}s - {e}")
                    raise
            return wrapper
        return decorator
    
    def section(self, title: str) -> "SectionContext":
        """日志分区"""
        return SectionContext(self._logger, title)
    
    @property
    def _loguru(self):
        return self._logger


class SectionContext:
    """日志分区上下文"""
    
    def __init__(self, logger: Any, title: str):
        self._logger = logger
        self._title = title
        self._width = 80
    
    def __enter__(self) -> "SectionContext":
        line = "=" * self._width
        self._logger.info(line)
        self._logger.info(f"  {self._title.center(self._width - 4)}  ")
        self._logger.info(line)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None:
            self._logger.info(f"{' END '.center(self._width, '=')}")
        else:
            self._logger.error(f"{' ERROR '.center(self._width, '=')}")


# 创建全局日志实例
logger = Logger()


# 便捷函数
def setup_logger(**kwargs: Any) -> None:
    """配置日志系统"""
    logger.setup(**kwargs)


def get_logger(name: Optional[str] = None) -> Logger:
    """获取日志实例"""
    if name:
        new_logger = Logger()
        new_logger._logger = logger._loguru.bind(name=name)
        return new_logger
    return logger


# 导出
__all__ = [
    "logger",
    "Logger",
    "setup_logger",
    "get_logger",
]
