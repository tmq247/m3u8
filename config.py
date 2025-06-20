import os
import logging

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Request Configuration
REQUEST_TIMEOUT = 30
MAX_REQUESTS_PER_MINUTE = 10
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# M3U8 Search Configuration
M3U8_PATTERNS = [
    r'https?://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?',
    r'["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
    r'url\s*:\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
    r'src\s*=\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
    r'playlist\s*:\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']',
    r'source\s*:\s*["\']([^"\']*\.m3u8(?:\?[^"\']*)?)["\']'
]

# Messages in Vietnamese
MESSAGES = {
    'start': '🤖 Chào mừng bạn đến với M3U8 Finder Bot!\n\nGửi cho tôi một URL và tôi sẽ tìm kiếm các link m3u8 trong trang web đó.',
    'help': '📋 Hướng dẫn sử dụng:\n\n1. Gửi một URL hợp lệ\n2. Bot sẽ phân tích trang web\n3. Trả về danh sách các link m3u8 tìm được\n\n⚠️ Lưu ý: Chỉ gửi tối đa 10 request mỗi phút',
    'invalid_url': '❌ URL không hợp lệ. Vui lòng gửi một URL đầy đủ (bắt đầu với http:// hoặc https://)',
    'no_m3u8_found': '😔 Không tìm thấy link m3u8 nào trong trang web này.',
    'error_fetching': '❌ Lỗi khi truy cập trang web: {}',
    'rate_limit': '⏳ Bạn đã gửi quá nhiều request. Vui lòng chờ một chút.',
    'found_m3u8': '✅ Đã tìm thấy {} link m3u8:',
    'processing': '🔍 Đang phân tích trang web...'
}
