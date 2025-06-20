import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Set
from config import REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)

class PracticalM3U8Finder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://google.com/'
        })
        
        # Comprehensive M3U8 patterns
        self.m3u8_patterns = [
            # Direct URL patterns
            r'https?://[^\s"\'<>\[\]{}|\\^`]+\.m3u8(?:\?[^\s"\'<>\[\]{}|\\^`]*)?',
            r'["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'src\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'url\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'file\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'stream\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'playlist\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'hls\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'hlsUrl\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'video\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'source\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            # Data attributes
            r'data-[^=]*=\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            # JavaScript variable assignments
            r'(?:var|let|const)\s+\w+\s*=\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            # Function calls with M3U8
            r'\w+\(["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            # Array elements
            r'\[["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            # Object properties
            r'\{\s*[^}]*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\'][^}]*\}',
        ]
    
    def is_valid_url(self, url: str) -> bool:
        """Kiểm tra URL có hợp lệ không"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def extract_m3u8_from_content(self, content: str, base_url: str) -> Set[str]:
        """Trích xuất M3U8 từ nội dung trang"""
        m3u8_urls = set()
        
        for pattern in self.m3u8_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Handle tuple results from regex groups
                if isinstance(match, tuple):
                    match = next((m for m in match if m and '.m3u8' in m), '')
                
                if match and '.m3u8' in str(match):
                    # Clean the URL
                    url = str(match).strip().strip('"\'')
                    
                    # Convert relative URLs to absolute
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = urljoin(base_url, url)
                    elif not url.startswith(('http://', 'https://')):
                        url = urljoin(base_url, url)
                    
                    if self.is_valid_url(url):
                        m3u8_urls.add(url)
        
        return m3u8_urls
    
    def check_common_endpoints(self, base_url: str) -> Set[str]:
        """Kiểm tra các endpoint phổ biến"""
        m3u8_urls = set()
        parsed_url = urlparse(base_url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Common M3U8 endpoints
        common_paths = [
            '/playlist.m3u8',
            '/index.m3u8',
            '/stream.m3u8',
            '/live.m3u8',
            '/video.m3u8',
            '/hls/stream.m3u8',
            '/streams/live.m3u8',
            '/api/stream.m3u8',
            '/media/playlist.m3u8'
        ]
        
        for path in common_paths:
            test_url = domain + path
            try:
                response = self.session.head(test_url, timeout=5)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'mpegurl' in content_type or 'vnd.apple' in content_type:
                        m3u8_urls.add(test_url)
            except:
                continue
        
        return m3u8_urls
    
    def check_iframe_sources(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Kiểm tra các iframe"""
        m3u8_urls = set()
        
        iframes = soup.find_all('iframe', src=True)
        for iframe in iframes[:3]:  # Limit to first 3 iframes
            src = iframe.get('src')
            if src:
                iframe_url = urljoin(base_url, src)
                try:
                    response = self.session.get(iframe_url, timeout=8)
                    if response.status_code == 200:
                        iframe_content = response.text
                        iframe_m3u8 = self.extract_m3u8_from_content(iframe_content, iframe_url)
                        m3u8_urls.update(iframe_m3u8)
                except:
                    continue
        
        return m3u8_urls
    
    def find_m3u8_links(self, url: str) -> List[str]:
        """Tìm kiếm M3U8 links"""
        if not self.is_valid_url(url):
            raise ValueError("URL không hợp lệ")
        
        all_m3u8_urls = set()
        
        try:
            # Check if URL is already a direct M3U8 link
            if url.endswith('.m3u8') or 'm3u8' in url:
                all_m3u8_urls.add(url)
                logger.info(f"Direct M3U8 URL detected: {url}")
                return [url]
            
            # Fetch main page
            self.session.headers['Referer'] = url
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            content = response.text
            content_type = response.headers.get('content-type', '').lower()
            final_url = response.url
            
            # Check if response is already M3U8 content
            if 'mpegurl' in content_type or 'vnd.apple' in content_type or '#EXTM3U' in content[:100]:
                all_m3u8_urls.add(final_url)
                logger.info(f"M3U8 content detected in response from {url}")
                return [final_url]
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Extract M3U8 from main content
            main_m3u8 = self.extract_m3u8_from_content(content, final_url)
            all_m3u8_urls.update(main_m3u8)
            
            # 2. Check iframe sources
            iframe_m3u8 = self.check_iframe_sources(soup, final_url)
            all_m3u8_urls.update(iframe_m3u8)
            
            # 3. Check common endpoints
            common_m3u8 = self.check_common_endpoints(final_url)
            all_m3u8_urls.update(common_m3u8)
            
            # 4. Extract script content for additional patterns
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.get_text() if script.get_text() else ''
                if script_content:
                    script_m3u8 = self.extract_m3u8_from_content(script_content, final_url)
                    all_m3u8_urls.update(script_m3u8)
            
            # Convert to sorted list
            valid_links = sorted(list(all_m3u8_urls))
            
            logger.info(f"Found {len(valid_links)} M3U8 links in {url}")
            return valid_links
            
        except Exception as e:
            logger.error(f"Error finding M3U8 links in {url}: {e}")
            raise
    
    def validate_m3u8_link(self, url: str) -> bool:
        """Kiểm tra xem link M3U8 có tồn tại không"""
        try:
            response = self.session.head(url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                return 'mpegurl' in content_type or 'vnd.apple' in content_type or response.url.endswith('.m3u8')
            return False
        except Exception:
            try:
                # Try GET request if HEAD fails
                response = self.session.get(url, timeout=10, stream=True)
                if response.status_code == 200:
                    # Read first few bytes to check if it's a playlist
                    first_chunk = next(response.iter_content(chunk_size=512), b'')
                    response.close()
                    return b'#EXTM3U' in first_chunk or b'#EXT-X-' in first_chunk
                return False
            except Exception:
                return False
