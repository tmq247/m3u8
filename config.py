#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cấu hình cho bot Telegram
"""

import os
from typing import Dict, List

class Config:
    """Lớp cấu hình chính"""
    
    # Telegram API Configuration
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Bot Configuration
    BOT_NAME = "Stream Link Extractor Bot"
    BOT_USERNAME = "@streamlinkbot"
    
    # Supported websites
    SUPPORTED_SITES = {
        "tvhay.fm": "TVHay",
        "phimmoi.net": "PhimMoi",
        "bilutv.com": "BiluTV",
        "motphim.com": "MotPhim"
    }
    
    # Request configuration
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Headers for requests
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
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
    }
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Video formats to look for
    VIDEO_FORMATS = [
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m3u8'
    ]
    
    # Common video hosting domains
    VIDEO_HOSTS = [
        'streamtape.com',
        'doodstream.com',
        'mixdrop.co',
        'upstream.to',
        'filesupload.org',
        'streamlare.com',
        'supervideo.tv'
    ]

class Messages:
    """Các thông điệp của bot"""
    
    START_MESSAGE = """
🎬 **Chào mừng đến với Stream Link Extractor Bot!**

Bot này giúp bạn trích xuất link phát trực tiếp từ các trang web xem phim.

📝 **Cách sử dụng:**
• Gửi link trang phim bạn muốn xem
• Bot sẽ tự động trích xuất link phát trực tiếp
• Nhận link và thưởng thức phim!

🌐 **Các trang web được hỗ trợ:**
• tvhay.fm
• phimmoi.net
• bilutv.com
• motphim.com

⚡ **Lệnh có sẵn:**
/start - Bắt đầu sử dụng bot
/help - Xem hướng dẫn
/supported - Danh sách trang web được hỗ trợ
"""

    HELP_MESSAGE = """
📚 **Hướng dẫn sử dụng bot:**

1️⃣ **Gửi link phim:**
   Chỉ cần gửi link từ các trang web được hỗ trợ

2️⃣ **Nhận link phát trực tiếp:**
   Bot sẽ trích xuất và gửi link video cho bạn

3️⃣ **Xem phim:**
   Sử dụng link để xem phim trên trình phát yêu thích

⚠️ **Lưu ý:**
• Chỉ hoạt động với các trang web được hỗ trợ
• Một số link có thể yêu cầu VPN
• Link có thể hết hạn sau một thời gian
"""

    SUPPORTED_SITES_MESSAGE = """
🌐 **Các trang web được hỗ trợ:**

✅ **tvhay.fm** - Phim hay chất lượng cao
✅ **phimmoi.net** - Phim mới cập nhật
✅ **bilutv.com** - Phim bộ Hàn Quốc
✅ **motphim.com** - Phim lẻ và phim bộ

🔄 **Đang phát triển thêm:**
• Nhiều trang web khác sẽ được bổ sung

💡 **Đề xuất trang web:**
Nếu bạn muốn bot hỗ trợ thêm trang web nào, hãy liên hệ admin!
"""

    PROCESSING_MESSAGE = "🔄 Đang xử lý link của bạn..."
    SUCCESS_MESSAGE = "✅ **Đã tìm thấy link phát trực tiếp:**"
    ERROR_MESSAGE = "❌ **Lỗi:** {error}"
    UNSUPPORTED_SITE_MESSAGE = "❌ Trang web này chưa được hỗ trợ. Sử dụng /supported để xem danh sách trang web được hỗ trợ."
    INVALID_URL_MESSAGE = "❌ Link không hợp lệ. Vui lòng gửi một URL đúng định dạng."
    NO_STREAM_FOUND_MESSAGE = "❌ Không tìm thấy link phát trực tiếp từ trang này."
