#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo scraper với dữ liệu mẫu để test bot
"""

import logging
from typing import List, Dict
import random

class DemoScraper:
    """Demo scraper trả về dữ liệu mẫu để test"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_demo_links(self, url: str) -> List[Dict[str, str]]:
        """
        Trả về các link demo để test bot
        
        Args:
            url: URL trang phim
            
        Returns:
            List các demo streaming links
        """
        try:
            self.logger.info(f"Demo: Tạo link mẫu cho {url}")
            
            # Tạo một số link demo với các hosting phổ biến
            demo_links = [
                {
                    'url': 'https://streamtape.com/v/demo123/video.mp4',
                    'quality': '1080p',
                    'source': 'StreamTape',
                    'type': 'MP4'
                },
                {
                    'url': 'https://doodstream.com/d/demo456',
                    'quality': '720p', 
                    'source': 'DoodStream',
                    'type': 'Stream'
                },
                {
                    'url': 'https://mixdrop.co/f/demo789',
                    'quality': '480p',
                    'source': 'MixDrop',
                    'type': 'Stream'
                },
                {
                    'url': 'https://example.com/video/sample.m3u8',
                    'quality': '720p',
                    'source': 'Direct',
                    'type': 'HLS'
                }
            ]
            
            # Trả về 2-3 link ngẫu nhiên
            num_links = random.randint(2, 3)
            selected_links = random.sample(demo_links, num_links)
            
            self.logger.info(f"Demo: Tạo thành công {len(selected_links)} link mẫu")
            return selected_links
            
        except Exception as e:
            self.logger.error(f"Lỗi demo scraper: {e}")
            return []
