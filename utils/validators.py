#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validators cho URL và các input khác
"""

import re
import logging
from urllib.parse import urlparse
from typing import List
from config import Config

logger = logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    """
    Kiểm tra URL có hợp lệ không
    
    Args:
        url: URL cần kiểm tra
        
    Returns:
        True nếu URL hợp lệ
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        # Kiểm tra format URL cơ bản
        parsed = urlparse(url.strip())
        
        # Phải có scheme và netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Scheme phải là http hoặc https
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Netloc không được chứa ký tự đặc biệt
        if not re.match(r'^[a-zA-Z0-9.-]+$', parsed.netloc):
            return False
        
        logger.debug(f"URL {url} là hợp lệ")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi validate URL {url}: {e}")
        return False

def is_supported_site(url: str) -> bool:
    """
    Kiểm tra trang web có được hỗ trợ không
    
    Args:
        url: URL cần kiểm tra
        
    Returns:
        True nếu trang web được hỗ trợ
    """
    if not is_valid_url(url):
        return False
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Loại bỏ 'www.' nếu có
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Kiểm tra trong danh sách sites được hỗ trợ
        supported_domains = [site.lower() for site in Config.SUPPORTED_SITES.keys()]
        
        is_supported = domain in supported_domains
        
        if is_supported:
            logger.info(f"Trang web {domain} được hỗ trợ")
        else:
            logger.warning(f"Trang web {domain} chưa được hỗ trợ")
        
        return is_supported
        
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra site support cho {url}: {e}")
        return False

def extract_domain(url: str) -> str:
    """
    Trích xuất domain từ URL
    
    Args:
        url: URL cần trích xuất
        
    Returns:
        Domain string hoặc empty string nếu lỗi
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Loại bỏ 'www.' nếu có
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
        
    except Exception as e:
        logger.error(f"Lỗi khi extract domain từ {url}: {e}")
        return ""

def is_video_file_url(url: str) -> bool:
    """
    Kiểm tra URL có phải là file video không
    
    Args:
        url: URL cần kiểm tra
        
    Returns:
        True nếu là video file URL
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Kiểm tra extension
    for ext in Config.VIDEO_FORMATS:
        if url_lower.endswith(ext) or f"{ext}?" in url_lower:
            return True
    
    return False

def is_streaming_url(url: str) -> bool:
    """
    Kiểm tra URL có phải là streaming URL không
    
    Args:
        url: URL cần kiểm tra
        
    Returns:
        True nếu là streaming URL
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Kiểm tra các host streaming
    for host in Config.VIDEO_HOSTS:
        if host in url_lower:
            return True
    
    # Kiểm tra các pattern streaming
    streaming_patterns = [
        '.m3u8',
        'master.m3u8',
        'playlist.m3u8',
        '/hls/',
        '/dash/',
        'stream',
        'play'
    ]
    
    for pattern in streaming_patterns:
        if pattern in url_lower:
            return True
    
    return False

def validate_telegram_user_id(user_id) -> bool:
    """
    Validate Telegram user ID
    
    Args:
        user_id: User ID cần validate
        
    Returns:
        True nếu hợp lệ
    """
    try:
        # User ID phải là số nguyên dương
        if isinstance(user_id, int):
            return user_id > 0
        elif isinstance(user_id, str):
            return user_id.isdigit() and int(user_id) > 0
        else:
            return False
    except:
        return False

def sanitize_filename(filename: str) -> str:
    """
    Làm sạch tên file để tránh ký tự đặc biệt
    
    Args:
        filename: Tên file gốc
        
    Returns:
        Tên file đã được làm sạch
    """
    if not filename:
        return "untitled"
    
    # Loại bỏ ký tự đặc biệt
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Loại bỏ khoảng trắng thừa
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Giới hạn độ dài
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized or "untitled"

def extract_video_id_from_url(url: str) -> str:
    """
    Trích xuất video ID từ URL (nếu có)
    
    Args:
        url: URL chứa video ID
        
    Returns:
        Video ID hoặc empty string
    """
    try:
        # Các pattern phổ biến cho video ID
        patterns = [
            r'/watch\?v=([^&]+)',  # YouTube style
            r'/video/([^/?]+)',    # Generic video path
            r'/v/([^/?]+)',        # Short video path
            r'video_id=([^&]+)',   # Query parameter
            r'/(\d+)/?$',          # Numeric ID at end
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
        
    except Exception as e:
        logger.error(f"Lỗi khi extract video ID từ {url}: {e}")
        return ""
