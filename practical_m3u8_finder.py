import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import logging
import json
import time
from typing import List, Set, Dict
from config import REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)

class EnhancedM3U8Finder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://google.com/',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Enhanced M3U8 patterns for Vietnamese streaming sites
        self.m3u8_patterns = [
            # Direct M3U8 URLs
            r'https?://[^\s"\'<>\[\]{}|\\^`]+\.m3u8(?:\?[^\s"\'<>\[\]{}|\\^`]*)?',
            r'["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            
            # Common variable patterns
            r'(?:src|url|file|stream|source|playlist|hls|hlsUrl|video)\s*[:=]\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            
            # Data attributes
            r'data-[^=]*=\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            
            # JavaScript patterns
            r'(?:var|let|const)\s+\w+\s*=\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'\w+\(["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            
            # Array and object patterns
            r'\[["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
            r'["\'][^"\']*\.m3u8[^"\']*["\']',
            
            # Encoded patterns
            r'\\u002F[^\\]*\.m3u8[^\\]*',
            r'%2F[^%]*\.m3u8[^%]*',
            
            # WordPress/PHP patterns
            r'wp-content[^"\']*\.m3u8[^"\']*',
            r'uploads[^"\']*\.m3u8[^"\']*'
        ]
        
        # Site-specific patterns for Vietnamese streaming sites
        self.vn_site_patterns = {
            'tvhay.fm': {
                'player_selectors': ['.player', '#player', '.video-player', '.tvhay-player'],
                'api_patterns': [
                    r'ajax_url["\']?\s*:\s*["\']([^"\']*)["\']',
                    r'["\']([^"\']*wp-admin/admin-ajax\.php[^"\']*)["\']',
                    r'["\']([^"\']*api[^"\']*)["\']'
                ],
                'embed_patterns': [
                    r'embed["\']?\s*:\s*["\']([^"\']*)["\']',
                    r'iframe[^>]*src=["\']([^"\']*)["\']'
                ]
            }
        }
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def detect_site_type(self, url: str) -> str:
        """Detect the type of streaming site"""
        for site_key in self.vn_site_patterns.keys():
            if site_key in url.lower():
                return site_key
        return 'generic'
    
    def extract_wordpress_ajax_data(self, content: str, base_url: str) -> List[str]:
        """Extract WordPress AJAX endpoints and try to get streaming data"""
        m3u8_links = []
        
        # Look for WordPress AJAX URL
        ajax_patterns = [
            r'ajaxurl["\']?\s*:\s*["\']([^"\']*admin-ajax\.php[^"\']*)["\']',
            r'ajax_url["\']?\s*:\s*["\']([^"\']*)["\']',
            r'["\']([^"\']*wp-admin/admin-ajax\.php[^"\']*)["\']'
        ]
        
        ajax_urls = set()
        for pattern in ajax_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                ajax_url = urljoin(base_url, match)
                ajax_urls.add(ajax_url)
        
        # Try common WordPress AJAX actions for video streaming
        common_actions = [
            'get_stream_url',
            'load_player',
            'get_video_source',
            'load_video',
            'get_embed_url',
            'fetch_stream',
            'player_data'
        ]
        
        for ajax_url in list(ajax_urls)[:3]:  # Limit to first 3 AJAX URLs
            for action in common_actions:
                try:
                    post_data = {
                        'action': action,
                        'security': '',  # Will try without nonce first
                    }
                    
                    response = self.session.post(ajax_url, data=post_data, timeout=10)
                    if response.status_code == 200:
                        content = response.text
                        
                        # Try to parse as JSON
                        try:
                            json_data = json.loads(content)
                            json_m3u8 = self._extract_m3u8_from_json(json_data)
                            m3u8_links.extend(json_m3u8)
                        except:
                            pass
                        
                        # Search for M3U8 in response
                        for pattern in self.m3u8_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if isinstance(match, tuple):
                                    match = match[0] if match[0] else match[1] if len(match) > 1 else ''
                                if match and '.m3u8' in str(match):
                                    full_url = urljoin(ajax_url, str(match))
                                    m3u8_links.append(full_url)
                        
                        if m3u8_links:
                            break
                            
                except Exception as e:
                    logger.debug(f"AJAX request failed for {action}: {e}")
                    continue
            
            if m3u8_links:
                break
        
        return m3u8_links
    
    def extract_player_config(self, content: str, base_url: str) -> List[str]:
        """Extract player configuration data"""
        m3u8_links = []
        
        # Look for common player configuration patterns
        config_patterns = [
            r'player\s*=\s*new\s+\w+\(([^)]+)\)',
            r'videojs\([^,]+,\s*({[^}]+})',
            r'jwplayer\([^)]*\)\.setup\(({[^}]+})\)',
            r'player\.setup\(({[^}]+})\)',
            r'new\s+Player\(([^)]+)\)'
        ]
        
        for pattern in config_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    # Try to extract URLs from the configuration
                    if isinstance(match, str):
                        for m3u8_pattern in self.m3u8_patterns:
                            urls = re.findall(m3u8_pattern, match, re.IGNORECASE)
                            for url in urls:
                                if isinstance(url, tuple):
                                    url = url[0] if url[0] else url[1] if len(url) > 1 else ''
                                if url and '.m3u8' in str(url):
                                    full_url = urljoin(base_url, str(url))
                                    m3u8_links.append(full_url)
                except Exception as e:
                    logger.debug(f"Error parsing player config: {e}")
                    continue
        
        return m3u8_links
    
    def try_common_streaming_endpoints(self, base_url: str, site_type: str) -> List[str]:
        """Try common streaming endpoints based on site type"""
        m3u8_links = []
        parsed_url = urlparse(base_url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Common endpoints for Vietnamese streaming sites
        endpoints = [
            '/wp-content/uploads/stream.m3u8',
            '/stream/playlist.m3u8',
            '/api/stream.m3u8',
            '/player/stream.m3u8',
            '/hls/index.m3u8',
            '/media/stream.m3u8'
        ]
        
        # Site-specific endpoints
        if site_type == 'tvhay.fm':
            endpoints.extend([
                '/tvhay-stream.m3u8',
                '/wp-content/themes/tvhay/stream.m3u8'
            ])
        
        for endpoint in endpoints:
            test_url = domain + endpoint
            try:
                response = self.session.head(test_url, timeout=5)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'mpegurl' in content_type or 'vnd.apple' in content_type:
                        m3u8_links.append(test_url)
            except:
                continue
        
        return m3u8_links
    
    def _extract_m3u8_from_json(self, data) -> List[str]:
        """Extract M3U8 URLs from JSON data"""
        urls = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and '.m3u8' in value:
                    urls.append(value)
                elif isinstance(value, (dict, list)):
                    urls.extend(self._extract_m3u8_from_json(value))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str) and '.m3u8' in item:
                    urls.append(item)
                elif isinstance(item, (dict, list)):
                    urls.extend(self._extract_m3u8_from_json(item))
        
        return urls
    
    def extract_m3u8_from_content(self, content: str, base_url: str) -> Set[str]:
        """Extract M3U8 URLs from content"""
        m3u8_urls = set()
        
        for pattern in self.m3u8_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = next((m for m in match if m and '.m3u8' in m), '')
                
                if match and '.m3u8' in str(match):
                    url = str(match).strip().strip('"\'')
                    
                    # Handle URL encoding
                    if '%2F' in url:
                        url = url.replace('%2F', '/')
                    if '\\u002F' in url:
                        url = url.replace('\\u002F', '/')
                    
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
    
    def find_m3u8_links(self, url: str) -> List[str]:
        """Main method to find M3U8 links with enhanced detection"""
        if not self.is_valid_url(url):
            raise ValueError("URL không hợp lệ")
        
        all_m3u8_urls = set()
        site_type = self.detect_site_type(url)
        
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
            
            # 1. Standard M3U8 extraction from main content
            main_m3u8 = self.extract_m3u8_from_content(content, final_url)
            all_m3u8_urls.update(main_m3u8)
            
            # 2. Extract WordPress AJAX data (for sites like tvhay.fm)
            wp_m3u8 = self.extract_wordpress_ajax_data(content, final_url)
            all_m3u8_urls.update(wp_m3u8)
            
            # 3. Extract player configuration
            player_m3u8 = self.extract_player_config(content, final_url)
            all_m3u8_urls.update(player_m3u8)
            
            # 4. Try common streaming endpoints
            endpoint_m3u8 = self.try_common_streaming_endpoints(final_url, site_type)
            all_m3u8_urls.update(endpoint_m3u8)
            
            # 5. Extract from script tags with enhanced patterns
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.get_text() if script.get_text() else ''
                if script_content:
                    script_m3u8 = self.extract_m3u8_from_content(script_content, final_url)
                    all_m3u8_urls.update(script_m3u8)
            
            # 6. Check iframes (enhanced)
            iframes = soup.find_all('iframe', src=True)
            for iframe in iframes[:3]:
                src = iframe.get('src')
                if src:
                    iframe_url = urljoin(final_url, src)
                    try:
                        iframe_response = self.session.get(iframe_url, timeout=8)
                        if iframe_response.status_code == 200:
                            iframe_content = iframe_response.text
                            iframe_m3u8 = self.extract_m3u8_from_content(iframe_content, iframe_url)
                            all_m3u8_urls.update(iframe_m3u8)
                    except:
                        continue
            
            # Convert to sorted list and remove duplicates
            valid_links = sorted(list(all_m3u8_urls))
            
            logger.info(f"Found {len(valid_links)} M3U8 links in {url}")
            return valid_links
            
        except Exception as e:
            logger.error(f"Error finding M3U8 links in {url}: {e}")
            raise
    
    def validate_m3u8_link(self, url: str) -> bool:
        """Validate if M3U8 link actually exists"""
        try:
            response = self.session.head(url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                return 'mpegurl' in content_type or 'vnd.apple' in content_type or response.url.endswith('.m3u8')
            return False
        except Exception:
            try:
                response = self.session.get(url, timeout=10, stream=True)
                if response.status_code == 200:
                    first_chunk = next(response.iter_content(chunk_size=512), b'')
                    response.close()
                    return b'#EXTM3U' in first_chunk or b'#EXT-X-' in first_chunk
                return False
            except Exception:
                return False
