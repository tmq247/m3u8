#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base scraper class cho tất cả các scrapers
"""

import aiohttp
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config import Config

class BaseScraper(ABC):
    """Lớp cơ sở cho tất cả các scrapers"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=Config.DEFAULT_HEADERS
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_html(self, url: str, max_retries: int = None) -> Optional[str]:
        """
        Lấy HTML từ URL
        
        Args:
            url: URL cần lấy
            max_retries: Số lần thử lại tối đa
            
        Returns:
            HTML content hoặc None nếu lỗi
        """
        if max_retries is None:
            max_retries = Config.MAX_RETRIES
        
        if not self.session:
            # Tạo connector với SSL verification disabled cho một số trang web
            connector = aiohttp.TCPConnector(ssl=False, limit=100, limit_per_host=30)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=Config.DEFAULT_HEADERS,
                connector=connector
            )
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"Đang lấy HTML từ: {url} (lần thử {attempt + 1})")
                
                # Thêm delay ngẫu nhiên để tránh bị chặn
                if attempt > 0:
                    import random
                    delay = random.uniform(1, 3)
                    await asyncio.sleep(delay)
                
                async with self.session.get(
                    url, 
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=45)
                ) as response:
                    if response.status == 200:
                        html = await response.text(encoding='utf-8')
                        self.logger.info(f"Lấy HTML thành công từ: {url}")
                        return html
                    elif response.status in [403, 429]:
                        self.logger.warning(f"Bị chặn truy cập: HTTP {response.status} từ {url}")
                        # Tăng delay khi bị chặn
                        await asyncio.sleep(5 * (attempt + 1))
                    else:
                        self.logger.warning(f"HTTP {response.status} từ {url}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout khi lấy {url} (lần thử {attempt + 1})")
            except aiohttp.ClientError as e:
                self.logger.error(f"Lỗi client khi lấy {url}: {e} (lần thử {attempt + 1})")
            except Exception as e:
                self.logger.error(f"Lỗi không xác định khi lấy {url}: {e} (lần thử {attempt + 1})")
            
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        self.logger.error(f"Không thể lấy HTML từ {url} sau {max_retries + 1} lần thử")
        return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML với BeautifulSoup
        
        Args:
            html: HTML content
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')
    
    def extract_video_urls(self, soup: BeautifulSoup) -> List[str]:
        """
        Trích xuất URLs video từ HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List các URLs video
        """
        video_urls = []
        
        # Tìm trong các thẻ video
        for video in soup.find_all('video'):
            src = video.get('src')
            if src and self.is_video_url(src):
                video_urls.append(src)
        
        # Tìm trong các thẻ source
        for source in soup.find_all('source'):
            src = source.get('src')
            if src and self.is_video_url(src):
                video_urls.append(src)
        
        # Tìm trong các thẻ iframe
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src and any(host in src for host in Config.VIDEO_HOSTS):
                video_urls.append(src)
        
        # Tìm trong các thẻ a có chứa link video
        for link in soup.find_all('a', href=True):
            href = link['href']
            if self.is_video_url(href):
                video_urls.append(href)
        
        return list(set(video_urls))  # Loại bỏ duplicate
    
    def is_video_url(self, url: str) -> bool:
        """
        Kiểm tra URL có phải là video không
        
        Args:
            url: URL cần kiểm tra
            
        Returns:
            True nếu là video URL
        """
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Kiểm tra extension
        for ext in Config.VIDEO_FORMATS:
            if ext in url_lower:
                return True
        
        # Kiểm tra video hosts
        for host in Config.VIDEO_HOSTS:
            if host in url_lower:
                return True
        
        return False
    
    def format_stream_info(self, url: str, quality: str = "Unknown", source: str = "Unknown") -> Dict[str, str]:
        """
        Format thông tin stream
        
        Args:
            url: Stream URL
            quality: Chất lượng video
            source: Nguồn video
            
        Returns:
            Dict chứa thông tin stream
        """
        return {
            'url': url,
            'quality': quality,
            'source': source
        }
    
    @abstractmethod
    async def extract_stream_links(self, url: str) -> List[Dict[str, str]]:
        """
        Trích xuất stream links từ URL
        
        Args:
            url: URL trang phim
            
        Returns:
            List các stream links với thông tin
        """
        pass
    
    @abstractmethod
    def get_supported_domains(self) -> List[str]:
        """
        Lấy danh sách domains được hỗ trợ
        
        Returns:
            List các domains
        """
        pass
