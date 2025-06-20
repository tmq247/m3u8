# M3U8 Finder Bot

Bot Telegram để tìm kiếm và trích xuất các link M3U8 từ các trang web phát video trực tuyến.

## Tính năng

- 🔍 Tìm kiếm link M3U8 từ bất kỳ URL nào
- 🎯 Hỗ trợ nhiều pattern tìm kiếm khác nhau
- 📱 Giao diện Telegram tiếng Việt
- ⚡ Rate limiting để tránh spam (10 request/phút)
- 🛡️ Xử lý lỗi toàn diện

## Cài đặt

1. Clone repository
2. Cài đặt dependencies:
```bash
uv add python-telegram-bot==20.8 beautifulsoup4 requests lxml
```

3. Tạo bot Telegram:
   - Tìm @BotFather trên Telegram
   - Gửi lệnh `/newbot`
   - Lấy token từ BotFather

4. Thiết lập biến môi trường:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

## Chạy bot

```bash
python main.py
```

## Cách sử dụng

1. Tìm bot trên Telegram
2. Gửi `/start` để bắt đầu
3. Gửi URL của trang web chứa video
4. Bot sẽ trả về danh sách các link M3U8 tìm được

## Cấu trúc project

- `main.py` - File chính chạy bot Telegram
- `m3u8_finder.py` - Module tìm kiếm M3U8
- `config.py` - Cấu hình bot
- `dependencies.txt` - Danh sách thư viện cần thiết

## Tính năng tìm kiếm

Bot có thể tìm M3U8 links từ:
- HTML thuần
- JavaScript code
- Các thuộc tính HTML (src, href, data-*)
- Nhiều pattern regex khác nhau

## Giới hạn

- Tối đa 10 request mỗi phút cho mỗi user
- Timeout 30 giây cho mỗi request
- Hỗ trợ các trang web công khai