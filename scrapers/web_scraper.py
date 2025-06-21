#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web scraper sử dụng trafilatura cho việc trích xuất content
"""

import trafilatura
import re
import logging
from typing import List, Dict
from urllib.parse import urlparse

class WebScraper:
    """Web scraper đơn giản sử dụng trafilatura"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_website_text_content(self, url: str) -> str:
        """
        Lấy nội dung text từ website
        
        Args:
            url: URL cần lấy nội dung
            
        Returns:
            Text content từ website
        """
        try:
            self.logger.info(f"Đang lấy nội dung từ: {url}")
            
            # Send a request to the website
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                self.logger.warning(f"Không thể tải nội dung từ {url}")
                return ""
            
            # Extract text content
            text = trafilatura.extract(downloaded)
            if not text:
                self.logger.warning(f"Không thể trích xuất text từ {url}")
                return ""
            
            self.logger.info(f"Đã lấy {len(text)} ký tự từ {url}")
            return text
            
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy nội dung từ {url}: {e}")
            return ""
    
    def extract_video_links(self, url: str) -> List[Dict[str, str]]:
        """
        Trích xuất link video từ trang web
        
        Args:
            url: URL trang web
            
        Returns:
            List các video links
        """
        try:
            self.logger.info(f"Đang trích xuất video links từ: {url}")
            
            # Lấy HTML raw
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return []
            
            video_links = []
            
            # Các pattern để tìm video links
            video_patterns = [
                # M3U8 streams
                r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
                # MP4 files
                r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)',
                # MKV files
                r'(https?://[^\s"\'<>]+\.mkv[^\s"\'<>]*)',
                # Streaming hosts
                r'(https?://streamtape\.com/[^\s"\'<>]+)',
                r'(https?://doodstream\.com/[^\s"\'<>]+)',
                r'(https?://mixdrop\.co/[^\s"\'<>]+)',
                r'(https?://upstream\.to/[^\s"\'<>]+)',
                r'(https?://filesupload\.org/[^\s"\'<>]+)',
                r'(https?://streamlare\.com/[^\s"\'<>]+)',
                r'(https?://supervideo\.tv/[^\s"\'<>]+)',
                # Embed patterns
                r'embed[^"\']*["\']([^"\']+)["\']',
                r'src[^"\']*["\']([^"\']*(?:\.mp4|\.m3u8|streamtape|doodstream|mixdrop)[^"\']*)["\']',
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, downloaded, re.IGNORECASE)
                for match in matches:
                    if self._is_valid_video_url(match):
                        quality = self._detect_quality(match)
                        source = self._detect_source(match)
                        
                        video_links.append({
                            'url': match,
                            'quality': quality,
                            'source': source
                        })
            
            # Loại bỏ duplicate
            unique_links = self._deduplicate_links(video_links)
            
            self.logger.info(f"Tìm thấy {len(unique_links)} video links")
            return unique_links
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất video links: {e}")
            return []
    
    def _is_valid_video_url(self, url: str) -> bool:
        """Kiểm tra URL có phải là video không"""
        if not url or len(url) < 10:
            return False
        
        url_lower = url.lower()
        
        # Video file extensions
        video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m3u8']
        for ext in video_exts:
            if ext in url_lower:
                return True
        
        # Video hosting domains
        video_hosts = [
            'streamtape.com', 'doodstream.com', 'mixdrop.co',
            'upstream.to', 'filesupload.org', 'streamlare.com',
            'supervideo.tv', 'vidcloud.co', 'fembed.com'
        ]
        for host in video_hosts:
            if host in url_lower:
                return True
        
        return False
    
    def _detect_quality(self, url: str) -> str:
        """Phát hiện chất lượng video"""
        url_lower = url.lower()
        
        if any(q in url_lower for q in ['2160p', '4k', 'uhd']):
            return '4K'
        elif any(q in url_lower for q in ['1080p', 'fhd', 'fullhd']):
            return '1080p'
        elif any(q in url_lower for q in ['720p', 'hd']):
            return '720p'
        elif any(q in url_lower for q in ['480p', 'sd']):
            return '480p'
        elif any(q in url_lower for q in ['360p']):
            return '360p'
        else:
            return 'Unknown'
    
    def _detect_source(self, url: str) -> str:
        """Phát hiện nguồn video"""
        domain = urlparse(url).netloc.lower()
        
        source_map = {
            'streamtape.com': 'StreamTape',
            'doodstream.com': 'DoodStream', 
            'mixdrop.co': 'MixDrop',
            'upstream.to': 'Upstream',
            'filesupload.org': 'FilesUpload',
            'streamlare.com': 'StreamLare',
            'supervideo.tv': 'SuperVideo',
            'tvhay.fm': 'TVHay Direct'
        }
        
        for host, source_name in source_map.items():
            if host in domain:
                return source_name
        
        return 'Unknown'
    
    def _deduplicate_links(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Loại bỏ duplicate links"""
        seen_urls = set()
        unique_links = []
        
        # Sắp xếp theo quality
        quality_order = {'4K': 0, '1080p': 1, '720p': 2, '480p': 3, '360p': 4, 'Unknown': 5}
        sorted_links = sorted(links, key=lambda x: quality_order.get(x['quality'], 5))
        
        for link in sorted_links:
            url = link['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_links.append(link)
        
        return unique_links
