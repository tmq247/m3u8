#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger configuration và setup
"""

import logging
import sys
from datetime import datetime
from config import Config

def setup_logger(name: str = None, level: str = None) -> logging.Logger:
    """
    Setup logger với cấu hình chuẩn
    
    Args:
        name: Tên logger (mặc định là root logger)
        level: Log level (mặc định lấy từ config)
        
    Returns:
        Logger instance
    """
    if level is None:
        level = Config.LOG_LEVEL
    
    # Tạo logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Kiểm tra nếu đã có handlers (tránh duplicate)
    if logger.hasHandlers():
        return logger
    
    # Tạo formatter
    formatter = logging.Formatter(
        Config.LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # File handler
    file_handler = logging.FileHandler(
        f'bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Thêm handlers vào logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Tránh propagate để không duplicate logs
    logger.propagate = False
    
    return logger

class LoggerMixin:
    """Mixin class để thêm logger vào các class khác"""
    
    @property
    def logger(self):
        """Lấy logger cho class hiện tại"""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger

def log_execution_time(func):
    """
    Decorator để log thời gian thực thi của function
    
    Args:
        func: Function cần log
        
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        logger = setup_logger(func.__name__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Function {func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper

async def log_async_execution_time(func):
    """
    Decorator để log thời gian thực thi của async function
    
    Args:
        func: Async function cần log
        
    Returns:
        Wrapped async function
    """
    async def wrapper(*args, **kwargs):
        logger = setup_logger(func.__name__)
        start_time = datetime.now()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Async function {func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Async function {func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper
