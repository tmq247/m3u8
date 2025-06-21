#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra các scraper
"""

import asyncio
from scrapers.enhanced_scraper import EnhancedScraper

def test_enhanced_scraper():
    """Test Enhanced Scraper"""
    print("=== Test Enhanced Scraper ===")
    scraper = EnhancedScraper()
    
    test_url = "https://tvhay.fm/xem-phim-nhung-ke-quyet-tu-656257"
    links = scraper.extract_all_streams(test_url)
    
    print(f"Tìm thấy {len(links)} links:")
    for i, link in enumerate(links, 1):
        print(f"{i}. [{link['quality']}] {link['source']} - {link['type']}")
        print(f"   URL: {link['url'][:100]}...")
    
    return links

if __name__ == "__main__":
    print("Bắt đầu test enhanced scraper...")
    
    # Test Enhanced Scraper
    enhanced_links = test_enhanced_scraper()
    
    print(f"\nTổng kết:")
    print(f"- Enhanced Scraper: {len(enhanced_links)} links")
    
    if enhanced_links:
        print("\nCác link tìm được:")
        for i, link in enumerate(enhanced_links[:10], 1):  # Hiển thị 10 link đầu
            print(f"{i}. [{link['quality']}] {link['source']} - {link['type']}")
            print(f"   {link['url']}")
            print()
