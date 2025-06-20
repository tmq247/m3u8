import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Set
from config import REQUEST_TIMEOUT, USER_AGENT, M3U8_PATTERNS

logger = logging.getLogger(__name__)

class M3U8Finder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def is_valid_url(self, url: str) -> bool:
        """Kiểm tra URL có hợp lệ không"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def fetch_page_content(self, url: str) -> tuple:
        """Lấy nội dung trang web"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text, response.url
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
    
    def extract_m3u8_from_html(self, html_content: str, base_url: str) -> Set[str]:
        """Trích xuất link m3u8 từ HTML"""
        m3u8_links = set()
        
        # Tìm kiếm trong HTML thuần
        for pattern in M3U8_PATTERNS:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1]
                
                # Loại bỏ các ký tự đặc biệt ở đầu và cuối
                match = match.strip().strip('"\'')
                
                if match and match.endswith('.m3u8'):
                    # Chuyển đổi thành URL tuyệt đối
                    full_url = urljoin(base_url, match)
                    m3u8_links.add(full_url)
        
        return m3u8_links
    
    def extract_m3u8_from_scripts(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Trích xuất link m3u8 từ JavaScript"""
        m3u8_links = set()
        
        # Tìm kiếm trong các thẻ script
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                script_content = script.string
                for pattern in M3U8_PATTERNS:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0] if match[0] else match[1]
                        
                        match = match.strip().strip('"\'')
                        
                        if match and match.endswith('.m3u8'):
                            full_url = urljoin(base_url, match)
                            m3u8_links.add(full_url)
        
        return m3u8_links
    
    def extract_m3u8_from_attributes(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Trích xuất link m3u8 từ các thuộc tính HTML"""
        m3u8_links = set()
        
        # Tìm kiếm trong các thuộc tính thường chứa m3u8
        attributes = ['src', 'href', 'data-src', 'data-url', 'data-playlist']
        
        for attr in attributes:
            elements = soup.find_all(attrs={attr: True})
            for element in elements:
                attr_value = element.get(attr, '')
                if attr_value and '.m3u8' in attr_value:
                    # Kiểm tra xem có phải là link m3u8 không
                    if attr_value.endswith('.m3u8') or '.m3u8?' in attr_value:
                        full_url = urljoin(base_url, attr_value)
                        m3u8_links.add(full_url)
        
        return m3u8_links
    
    def find_m3u8_links(self, url: str) -> List[str]:
        """Tìm kiếm tất cả link m3u8 trong trang web"""
        if not self.is_valid_url(url):
            raise ValueError("URL không hợp lệ")
        
        try:
            # Lấy nội dung trang web
            html_content, final_url = self.fetch_page_content(url)
            
            # Phân tích HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Tìm kiếm m3u8 links từ nhiều nguồn
            m3u8_links = set()
            
            # 1. Tìm trong HTML thuần
            m3u8_links.update(self.extract_m3u8_from_html(html_content, final_url))
            
            # 2. Tìm trong JavaScript
            m3u8_links.update(self.extract_m3u8_from_scripts(soup, final_url))
            
            # 3. Tìm trong các thuộc tính HTML
            m3u8_links.update(self.extract_m3u8_from_attributes(soup, final_url))
            
            # Chuyển đổi set thành list và sắp xếp
            result = list(m3u8_links)
            result.sort()
            
            logger.info(f"Found {len(result)} m3u8 links in {url}")
            return result
            
        except Exception as e:
            logger.error(f"Error finding m3u8 links in {url}: {e}")
            raise
    
    def validate_m3u8_link(self, url: str) -> bool:
        """Kiểm tra xem link m3u8 có thực sự tồn tại không"""
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
