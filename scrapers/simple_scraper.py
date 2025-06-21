#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple scraper sử dụng requests và regex patterns
"""

import requests
import re
import logging
from typing import List, Dict
from urllib.parse import urlparse, urljoin

class SimpleScraper:
    """Scraper đơn giản sử dụng requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def extract_streaming_links(self, url: str) -> List[Dict[str, str]]:
        """
        Trích xuất streaming links từ URL
        
        Args:
            url: URL trang phim
            
        Returns:
            List các streaming links
        """
        try:
            self.logger.info(f"Đang trích xuất từ: {url}")
            
            # Lấy HTML
            response = self.session.get(url, timeout=30, verify=False)
            if response.status_code != 200:
                self.logger.warning(f"HTTP {response.status_code} từ {url}")
                return []
            
            html_content = response.text
            links = []
            
            # Pattern 1: Direct video files
            video_patterns = [
                r'(?:src|href|url)=[\'"](https?://[^\'\"]+\.(?:mp4|m3u8|mkv|avi|mov)(?:\?[^\'\"]*)?)[\'"]',
                r'(https?://[^\s\'"<>]+\.(?:mp4|m3u8|mkv|avi|mov)(?:\?[^\s\'"<>]*)?)',
            ]
            
            # Pattern 2: Streaming hosts
            host_patterns = [
                r'(https?://(?:www\.)?streamtape\.com/[^\s\'"<>]+)',
                r'(https?://(?:www\.)?doodstream\.com/[^\s\'"<>]+)',
                r'(https?://(?:www\.)?mixdrop\.co/[^\s\'"<>]+)',
                r'(https?://(?:www\.)?upstream\.to/[^\s\'"<>]+)',
                r'(https?://(?:www\.)?filesupload\.org/[^\s\'"<>]+)',
            ]
            
            # Pattern 3: Embedded players
            embed_patterns = [
                r'<iframe[^>]+src=[\'"]([^\'\"]+)[\'\"[^>]*>',
                r'embed[^\'\"]*[\'\"]([^\'\"]+)[\'\"]',
            ]
            
            all_patterns = video_patterns + host_patterns + embed_patterns
            
            for pattern in all_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    if self._is_valid_stream_url(match):
                        # Tạo absolute URL nếu cần
                        if match.startswith('//'):
                            match = 'https:' + match
                        elif match.startswith('/'):
                            match = urljoin(url, match)
                        
                        quality = self._detect_quality(match)
                        source = self._detect_source(match)
                        
                        links.append({
                            'url': match,
                            'quality': quality,
                            'source': source
                        })
            
            # Loại bỏ duplicate
            unique_links = self._remove_duplicates(links)
            
            self.logger.info(f"Tìm thấy {len(unique_links)} streaming links")
            return unique_links
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất: {e}")
            return []
    
    def _is_valid_stream_url(self, url: str) -> bool:
        """Kiểm tra URL có phải là streaming link không"""
        if not url or len(url) < 10:
            return False
        
        url_lower = url.lower()
        
        # Video extensions
        video_exts = ['.mp4', '.m3u8', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        if any(ext in url_lower for ext in video_exts):
            return True
        
        # Streaming hosts
        hosts = ['streamtape.com', 'doodstream.com', 'mixdrop.co', 'upstream.to', 'filesupload.org']
        if any(host in url_lower for host in hosts):
            return True
        
        return False
    
    def _detect_quality(self, url: str) -> str:
        """Phát hiện chất lượng video"""
        url_lower = url.lower()
        
        if any(q in url_lower for q in ['2160p', '4k']):
            return '4K'
        elif any(q in url_lower for q in ['1080p', 'fhd']):
            return '1080p'
        elif any(q in url_lower for q in ['720p', 'hd']):
            return '720p'
        elif any(q in url_lower for q in ['480p', 'sd']):
            return '480p'
        elif '360p' in url_lower:
            return '360p'
        else:
            return 'Unknown'
    
    def _detect_source(self, url: str) -> str:
        """Phát hiện nguồn video"""
        domain = urlparse(url).netloc.lower()
        
        if 'streamtape.com' in domain:
            return 'StreamTape'
        elif 'doodstream.com' in domain:
            return 'DoodStream'
        elif 'mixdrop.co' in domain:
            return 'MixDrop'
        elif 'upstream.to' in domain:
            return 'Upstream'
        elif 'filesupload.org' in domain:
            return 'FilesUpload'
        elif 'tvhay.fm' in domain:
            return 'TVHay Direct'
        else:
            return 'Unknown'
    
    def _remove_duplicates(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Loại bỏ duplicate links"""
        seen = set()
        unique = []
        
        # Sắp xếp theo quality
        quality_order = {'4K': 0, '1080p': 1, '720p': 2, '480p': 3, '360p': 4, 'Unknown': 5}
        sorted_links = sorted(links, key=lambda x: quality_order.get(x['quality'], 5))
        
        for link in sorted_links:
            url = link['url']
            if url not in seen:
                seen.add(url)
                unique.append(link)
        
        return unique
