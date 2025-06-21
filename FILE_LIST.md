# Danh Sách File Bot Telegram Stream Link Extractor

## Cấu trúc thư mục và file:

```
stream-link-bot/
├── bot/
│   ├── __init__.py
│   ├── bot.py
│   └── handlers.py
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── scraper_factory.py
│   └── tvhay_scraper.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── validators.py
├── .env
├── .env.example
├── .replit
├── config.py
├── main.py
├── requirements-list.txt
├── pyproject.toml
└── uv.lock
```

## Mô tả các file chính:

### 1. File khởi động:
- **main.py** - File chính để chạy bot
- **.env** - File chứa API keys và cấu hình

### 2. Module Bot:
- **bot/bot.py** - Class bot chính sử dụng Pyrogram
- **bot/handlers.py** - Xử lý các lệnh và tin nhắn

### 3. Module Scrapers:
- **scrapers/base_scraper.py** - Class cơ sở cho tất cả scrapers
- **scrapers/tvhay_scraper.py** - Scraper cho trang tvhay.fm
- **scrapers/scraper_factory.py** - Factory tạo scrapers

### 4. Module Utils:
- **utils/logger.py** - Cấu hình logging
- **utils/validators.py** - Validation URL và dữ liệu

### 5. File cấu hình:
- **config.py** - Cấu hình chung và messages
- **.env.example** - Mẫu file environment
- **requirements-list.txt** - Danh sách thư viện cần thiết

## Cách sử dụng:

1. Tải tất cả file về máy
2. Cài đặt Python 3.11+
3. Chạy: `pip install -r requirements-list.txt`
4. Cấu hình file .env với API keys
5. Chạy: `python main.py`

## Tính năng hiện tại:

✅ Bot Telegram hoàn chình với Pyrogram
✅ Xử lý lệnh /start, /help, /supported
✅ Trích xuất link streaming từ tvhay.fm
✅ Hệ thống scraper mở rộng được
✅ Logging và error handling
✅ Validation URL và dữ liệu

## Bot đang chạy thành công!
Bot đã được khởi động và sẵn sàng xử lý tin nhắn từ người dùng.
