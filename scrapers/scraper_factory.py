#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factory để tạo scrapers phù hợp cho từng trang web
"""

import logging
from typing import Optional
from urllib.parse import urlparse
from scrapers.base_scraper import BaseScraper
from scrapers.tvhay_scraper import TVHayScraper

class ScraperFactory:
    """Factory class để tạo scrapers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._scrapers = {}
        self._register_scrapers()
    
    def _register_scrapers(self):
        """Đăng ký tất cả scrapers có sẵn"""
        scrapers = [
            TVHayScraper(),
            # Thêm scrapers khác ở đây
            # PhimMoiScraper(),
            # BiluTVScraper(),
            # MotPhimScraper(),
        ]
        
        for scraper in scrapers:
            for domain in scraper.get_supported_domains():
                self._scrapers[domain.lower()] = scraper.__class__
                self.logger.info(f"Đã đăng ký scraper {scraper.__class__.__name__} cho domain {domain}")
    
    def get_scraper(self, url: str) -> Optional[BaseScraper]:
        """
        Lấy scraper phù hợp cho URL
        
        Args:
            url: URL cần scrape
            
        Returns:
            Scraper instance hoặc None nếu không hỗ trợ
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Loại bỏ 'www.' nếu có
            if domain.startswith('www.'):
                domain_without_www = domain[4:]
            else:
                domain_without_www = domain
            
            # Tìm scraper cho domain
            scraper_class = self._scrapers.get(domain) or self._scrapers.get(domain_without_www)
            
            if scraper_class:
                scraper = scraper_class()
                self.logger.info(f"Đã tạo scraper {scraper_class.__name__} cho domain {domain}")
                return scraper
            else:
                self.logger.warning(f"Không tìm thấy scraper cho domain {domain}")
                return None
                
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo scraper cho URL {url}: {e}")
            return None
    
    def get_supported_domains(self) -> list:
        """
        Lấy danh sách tất cả domains được hỗ trợ
        
        Returns:
            List các domains được hỗ trợ
        """
        return list(self._scrapers.keys())
    
    def is_supported(self, url: str) -> bool:
        """
        Kiểm tra URL có được hỗ trợ không
        
        Args:
            url: URL cần kiểm tra
            
        Returns:
            True nếu được hỗ trợ
        """
        return self.get_scraper(url) is not None
