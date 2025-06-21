#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced scraper với nhiều phương pháp trích xuất
"""

import requests
import trafilatura
import re
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin, unquote
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EnhancedScraper:
    """Enhanced scraper với multiple strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification
        
        # Updated headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
        })
    
    def extract_all_streams(self, url: str) -> List[Dict[str, str]]:
        """
        Trích xuất tất cả streaming links từ URL
        
        Args:
            url: URL trang phim
            
        Returns:
            List các streaming links
        """
        all_links = []
        
        # Method 1: Trafilatura
        trafilatura_links = self._extract_with_trafilatura(url)
        all_links.extend(trafilatura_links)
        
        # Method 2: Direct requests
        requests_links = self._extract_with_requests(url)
        all_links.extend(requests_links)
        
        # Method 3: Common video hosting patterns
        hosting_links = self._extract_common_hosts(url)
        all_links.extend(hosting_links)
        
        # Remove duplicates and sort
        unique_links = self._process_links(all_links)
        
        self.logger.info(f"Tổng cộng tìm thấy {len(unique_links)} unique streaming links")
        return unique_links
    
    def _extract_with_trafilatura(self, url: str) -> List[Dict[str, str]]:
        """Sử dụng trafilatura để trích xuất"""
        try:
            self.logger.info(f"Trafilatura: Đang trích xuất từ {url}")
            
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return []
            
            links = []
            
            # Enhanced patterns for video detection
            patterns = [
                # Direct video files
                r'(https?://[^\s"\'<>]+\.(?:mp4|m3u8|mkv|avi|mov|wmv|flv|webm)(?:\?[^\s"\'<>]*)?)',
                
                # Streaming services
                r'(https?://(?:www\.)?streamtape\.com/[^\s"\'<>]+)',
                r'(https?://(?:www\.)?doodstream\.com/[^\s"\'<>]+)',
                r'(https?://(?:www\.)?mixdrop\.co/[^\s"\'<>]+)',
                r'(https?://(?:www\.)?upstream\.to/[^\s"\'<>]+)',
                r'(https?://(?:www\.)?filesupload\.org/[^\s"\'<>]+)',
                r'(https?://(?:www\.)?streamlare\.com/[^\s"\'<>]+)',
                r'(https?://(?:www\.)?supervideo\.tv/[^\s"\'<>]+)',
                
                # Embedded players
                r'(?:player|embed|iframe)[^"\']*["\']([^"\']*(?:\.mp4|\.m3u8|streamtape|doodstream|mixdrop)[^"\']*)["\']',
                r'(?:src|url|file)[^"\']*["\']([^"\']*(?:\.mp4|\.m3u8|streamtape|doodstream|mixdrop)[^"\']*)["\']',
                
                # Base64 or encoded URLs
                r'(?:data-src|data-url)[^"\']*["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, downloaded, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    if self._is_valid_stream_url(match):
                        links.append(self._create_link_info(match, url))
            
            self.logger.info(f"Trafilatura tìm thấy {len(links)} links")
            return links
            
        except Exception as e:
            self.logger.error(f"Lỗi trafilatura: {e}")
            return []
    
    def _extract_with_requests(self, url: str) -> List[Dict[str, str]]:
        """Sử dụng requests để trích xuất"""
        try:
            self.logger.info(f"Requests: Đang trích xuất từ {url}")
            
            # Add delay to avoid being blocked
            time.sleep(2)
            
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                self.logger.warning(f"HTTP {response.status_code} từ {url}")
                return []
            
            content = response.text
            links = []
            
            # Advanced patterns
            patterns = [
                # JavaScript variable assignments
                r'(?:videoUrl|streamUrl|playerUrl|fileUrl)\s*[=:]\s*["\']([^"\']+)["\']',
                r'(?:src|source|url|file)\s*[=:]\s*["\']([^"\']*(?:\.mp4|\.m3u8|streamtape|doodstream|mixdrop)[^"\']*)["\']',
                
                # JSON-like structures
                r'"(?:url|src|file|source)"\s*:\s*"([^"]+)"',
                r"'(?:url|src|file|source)'\s*:\s*'([^']+)'",
                
                # Iframe sources
                r'<iframe[^>]+src=["\']([^"\']+)["\'][^>]*>',
                
                # Video tags
                r'<video[^>]+src=["\']([^"\']+)["\'][^>]*>',
                r'<source[^>]+src=["\']([^"\']+)["\'][^>]*>',
                
                # Direct links in text
                r'(https?://[^\s"\'<>()]+\.(?:mp4|m3u8|mkv|avi|mov)(?:\?[^\s"\'<>()]*)?)',
                
                # Hosting services
                r'(https?://(?:[a-zA-Z0-9-]+\.)?(?:streamtape|doodstream|mixdrop|upstream|filesupload|streamlare|supervideo)\.(?:com|co|tv|org)/[^\s"\'<>()]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    # Clean and validate URL
                    clean_url = self._clean_url(match, url)
                    if clean_url and self._is_valid_stream_url(clean_url):
                        links.append(self._create_link_info(clean_url, url))
            
            self.logger.info(f"Requests tìm thấy {len(links)} links")
            return links
            
        except Exception as e:
            self.logger.error(f"Lỗi requests: {e}")
            return []
    
    def _extract_common_hosts(self, url: str) -> List[Dict[str, str]]:
        """Tìm kiếm các hosting phổ biến"""
        try:
            # Common hosting URL patterns for tvhay.fm
            common_patterns = [
                f"{url.rstrip('/')}/embed",
                f"{url.rstrip('/')}/player",
                f"{url.rstrip('/')}/stream",
            ]
            
            links = []
            for test_url in common_patterns:
                try:
                    response = self.session.get(test_url, timeout=15)
                    if response.status_code == 200:
                        content = response.text
                        
                        # Look for embedded players
                        iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\']'
                        matches = re.findall(iframe_pattern, content, re.IGNORECASE)
                        
                        for match in matches:
                            clean_url = self._clean_url(match, test_url)
                            if clean_url and self._is_valid_stream_url(clean_url):
                                links.append(self._create_link_info(clean_url, url))
                
                except:
                    continue
            
            return links
            
        except Exception as e:
            self.logger.error(f"Lỗi common hosts: {e}")
            return []
    
    def _clean_url(self, url: str, base_url: str) -> Optional[str]:
        """Clean và normalize URL"""
        try:
            if not url:
                return None
            
            # Decode URL if needed
            url = unquote(url)
            
            # Handle relative URLs
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = urljoin(base_url, url)
            elif not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)
            
            # Remove common unwanted parameters
            if '?' in url:
                base_part = url.split('?')[0]
                if self._is_valid_stream_url(base_part):
                    return url
                else:
                    return base_part
            
            return url
            
        except Exception:
            return None
    
    def _is_valid_stream_url(self, url: str) -> bool:
        """Kiểm tra URL có phải là streaming link không"""
        if not url or len(url) < 10:
            return False
        
        url_lower = url.lower()
        
        # Video file extensions
        video_exts = ['.mp4', '.m3u8', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']
        if any(ext in url_lower for ext in video_exts):
            return True
        
        # Streaming hosts
        hosts = [
            'streamtape.com', 'doodstream.com', 'mixdrop.co', 'upstream.to',
            'filesupload.org', 'streamlare.com', 'supervideo.tv',
            'vidcloud.co', 'fembed.com', 'embedgram.com'
        ]
        if any(host in url_lower for host in hosts):
            return True
        
        return False
    
    def _create_link_info(self, url: str, source_url: str) -> Dict[str, str]:
        """Tạo thông tin link"""
        return {
            'url': url,
            'quality': self._detect_quality(url),
            'source': self._detect_source(url),
            'type': self._detect_type(url)
        }
    
    def _detect_quality(self, url: str) -> str:
        """Phát hiện chất lượng"""
        url_lower = url.lower()
        
        if any(q in url_lower for q in ['2160p', '4k', 'uhd']):
            return '4K'
        elif any(q in url_lower for q in ['1080p', 'fhd', 'fullhd']):
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
        """Phát hiện nguồn"""
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
    
    def _detect_type(self, url: str) -> str:
        """Phát hiện loại file"""
        url_lower = url.lower()
        
        if '.m3u8' in url_lower:
            return 'HLS'
        elif '.mp4' in url_lower:
            return 'MP4'
        elif '.mkv' in url_lower:
            return 'MKV'
        else:
            return 'Stream'
    
    def _process_links(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Xử lý và loại bỏ duplicate links"""
        seen_urls = set()
        unique_links = []
        
        # Sort by quality
        quality_order = {'4K': 0, '1080p': 1, '720p': 2, '480p': 3, '360p': 4, 'Unknown': 5}
        sorted_links = sorted(links, key=lambda x: quality_order.get(x['quality'], 5))
        
        for link in sorted_links:
            url = link['url']
            if url not in seen_urls and len(url) > 10:
                seen_urls.add(url)
                unique_links.append(link)
        
        return unique_links
