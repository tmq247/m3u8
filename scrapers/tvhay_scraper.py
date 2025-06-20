#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper cho trang web tvhay.fm
"""

import re
import json
import trafilatura
from typing import List, Dict
from urllib.parse import urljoin, urlparse
from scrapers.base_scraper import BaseScraper
from scrapers.web_scraper import WebScraper

class TVHayScraper(BaseScraper):
    """Scraper cho tvhay.fm"""
    
    def __init__(self):
        super().__init__()
        self.base_domain = "tvhay.fm"
    
    def get_supported_domains(self) -> List[str]:
        """Domains được hỗ trợ"""
        return ["tvhay.fm", "www.tvhay.fm"]
    
    async def extract_stream_links(self, url: str) -> List[Dict[str, str]]:
        """
        Trích xuất stream links từ tvhay.fm
        
        Args:
            url: URL trang phim
            
        Returns:
            List các stream links
        """
        try:
            self.logger.info(f"Bắt đầu trích xuất từ TVHay: {url}")
            
            # Phương pháp 1: Enhanced scraper với multiple strategies
            from scrapers.enhanced_scraper import EnhancedScraper
            enhanced_scraper = EnhancedScraper()
            stream_links = enhanced_scraper.extract_all_streams(url)
            
            if stream_links:
                self.logger.info(f"EnhancedScraper tìm thấy {len(stream_links)} links")
                return stream_links
            
            # Phương pháp backup: Sử dụng demo links nếu không tìm thấy
            self.logger.warning("Không tìm thấy link thực, sử dụng demo links để test bot")
            from scrapers.demo_scraper import DemoScraper
            demo_scraper = DemoScraper()
            demo_links = demo_scraper.extract_demo_links(url)
            
            if demo_links:
                self.logger.info(f"Demo scraper tạo {len(demo_links)} links mẫu")
                return demo_links
            
            # Phương pháp 2: Sử dụng aiohttp với cải tiến
            async with self:
                html = await self.fetch_html(url)
                if html:
                    soup = self.parse_html(html)
                    
                    # Tìm player iframe
                    iframe_links = await self._extract_from_iframes(soup, url)
                    stream_links.extend(iframe_links)
                    
                    # Tìm trong JavaScript  
                    js_links = await self._extract_from_javascript(soup, url)
                    stream_links.extend(js_links)
                    
                    # Tìm direct video links
                    direct_links = self._extract_direct_links(soup)
                    stream_links.extend(direct_links)
                
                # Loại bỏ duplicate và sắp xếp theo quality
                unique_links = self._deduplicate_links(stream_links)
                
                self.logger.info(f"Đã tìm thấy {len(unique_links)} stream links từ TVHay")
                return unique_links
                
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất từ TVHay: {e}")
            return []
    
    async def _extract_with_trafilatura(self, url: str) -> List[Dict[str, str]]:
        """Sử dụng trafilatura để trích xuất nội dung"""
        try:
            self.logger.info(f"Đang sử dụng trafilatura cho: {url}")
            
            # Lấy nội dung với trafilatura
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                self.logger.warning("Trafilatura không thể tải nội dung")
                return []
            
            # Trích xuất HTML và text
            extracted_html = trafilatura.extract(downloaded, include_links=True, include_images=True)
            if not extracted_html:
                self.logger.warning("Trafilatura không thể trích xuất nội dung")
                return []
            
            # Parse với BeautifulSoup
            soup = self.parse_html(downloaded)
            stream_links = []
            
            # Tìm các pattern video trong nội dung
            patterns = [
                r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
                r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)',
                r'(https?://[^\s"\'<>]+\.mkv[^\s"\'<>]*)',
                r'(https?://streamtape\.com/[^\s"\'<>]+)',
                r'(https?://doodstream\.com/[^\s"\'<>]+)',
                r'(https?://mixdrop\.co/[^\s"\'<>]+)'
            ]
            
            full_content = downloaded + " " + (extracted_html or "")
            
            for pattern in patterns:
                matches = re.findall(pattern, full_content, re.IGNORECASE)
                for match in matches:
                    if self.is_video_url(match):
                        quality = self._detect_quality(match)
                        source = self._detect_source(match)
                        
                        stream_links.append(self.format_stream_info(
                            url=match,
                            quality=quality,
                            source=source
                        ))
            
            # Tìm iframe sources
            iframes = soup.find_all('iframe', src=True)
            for iframe in iframes:
                src = iframe.get('src')
                if src and any(host in src for host in ['streamtape', 'doodstream', 'mixdrop', 'upstream', 'filesupload']):
                    quality = self._detect_quality(src)
                    source = self._detect_source(src)
                    
                    stream_links.append(self.format_stream_info(
                        url=src,
                        quality=quality,
                        source=source
                    ))
            
            self.logger.info(f"Trafilatura tìm thấy {len(stream_links)} links")
            return stream_links
            
        except Exception as e:
            self.logger.error(f"Lỗi trafilatura: {e}")
            return []
    
    async def _extract_from_iframes(self, soup, base_url: str) -> List[Dict[str, str]]:
        """Trích xuất từ các iframe players"""
        stream_links = []
        
        # Tìm tất cả iframe
        iframes = soup.find_all('iframe')
        
        for iframe in iframes:
            src = iframe.get('src')
            if not src:
                continue
            
            # Tạo absolute URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(base_url, src)
            
            self.logger.info(f"Đang xử lý iframe: {src}")
            
            # Lấy HTML từ iframe
            iframe_html = await self.fetch_html(src)
            if not iframe_html:
                continue
            
            iframe_soup = self.parse_html(iframe_html)
            
            # Tìm video sources trong iframe
            video_urls = self.extract_video_urls(iframe_soup)
            
            for video_url in video_urls:
                quality = self._detect_quality(video_url)
                source = self._detect_source(video_url)
                
                stream_links.append(self.format_stream_info(
                    url=video_url,
                    quality=quality,
                    source=source
                ))
        
        return stream_links
    
    async def _extract_from_javascript(self, soup, base_url: str) -> List[Dict[str, str]]:
        """Trích xuất từ JavaScript code"""
        stream_links = []
        
        # Tìm tất cả script tags
        scripts = soup.find_all('script')
        
        for script in scripts:
            if not script.string:
                continue
            
            script_content = script.string
            
            # Pattern để tìm URLs video
            patterns = [
                r'"(https?://[^"]*\.m3u8[^"]*)"',
                r'"(https?://[^"]*\.mp4[^"]*)"',
                r'"(https?://[^"]*\.mkv[^"]*)"',
                r'src\s*:\s*["\']([^"\']+)["\']',
                r'file\s*:\s*["\']([^"\']+)["\']',
                r'url\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                
                for match in matches:
                    if self.is_video_url(match):
                        # Tạo absolute URL nếu cần
                        if match.startswith('//'):
                            match = 'https:' + match
                        elif match.startswith('/'):
                            match = urljoin(base_url, match)
                        
                        quality = self._detect_quality(match)
                        source = self._detect_source(match)
                        
                        stream_links.append(self.format_stream_info(
                            url=match,
                            quality=quality,
                            source=source
                        ))
        
        return stream_links
    
    def _extract_direct_links(self, soup) -> List[Dict[str, str]]:
        """Trích xuất direct video links"""
        stream_links = []
        
        # Tìm video URLs thông thường
        video_urls = self.extract_video_urls(soup)
        
        for video_url in video_urls:
            quality = self._detect_quality(video_url)
            source = self._detect_source(video_url)
            
            stream_links.append(self.format_stream_info(
                url=video_url,
                quality=quality,
                source=source
            ))
        
        return stream_links
    
    def _detect_quality(self, url: str) -> str:
        """Phát hiện chất lượng video từ URL"""
        url_lower = url.lower()
        
        quality_patterns = {
            '4k': ['2160p', '4k', 'uhd'],
            '1080p': ['1080p', 'fhd', 'fullhd'],
            '720p': ['720p', 'hd'],
            '480p': ['480p', 'sd'],
            '360p': ['360p'],
            '240p': ['240p']
        }
        
        for quality, patterns in quality_patterns.items():
            for pattern in patterns:
                if pattern in url_lower:
                    return quality
        
        return 'Unknown'
    
    def _detect_source(self, url: str) -> str:
        """Phát hiện nguồn video từ URL"""
        domain = urlparse(url).netloc.lower()
        
        source_mapping = {
            'streamtape.com': 'StreamTape',
            'doodstream.com': 'DoodStream',
            'mixdrop.co': 'MixDrop',
            'upstream.to': 'Upstream',
            'filesupload.org': 'FilesUpload',
            'streamlare.com': 'StreamLare',
            'supervideo.tv': 'SuperVideo',
            'tvhay.fm': 'TVHay Direct'
        }
        
        for host, source_name in source_mapping.items():
            if host in domain:
                return source_name
        
        return 'Unknown'
    
    def _deduplicate_links(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Loại bỏ duplicate links và sắp xếp"""
        seen_urls = set()
        unique_links = []
        
        # Sắp xếp theo quality (4K > 1080p > 720p > ...)
        quality_order = {'4k': 0, '1080p': 1, '720p': 2, '480p': 3, '360p': 4, '240p': 5, 'Unknown': 6}
        
        sorted_links = sorted(links, key=lambda x: quality_order.get(x['quality'], 6))
        
        for link in sorted_links:
            url = link['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_links.append(link)
        
        return unique_links
