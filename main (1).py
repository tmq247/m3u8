import logging
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from m3u8_finder import M3U8Finder
from config import TELEGRAM_BOT_TOKEN, LOG_LEVEL, LOG_FORMAT, MESSAGES, MAX_REQUESTS_PER_MINUTE

# Cấu hình logging
logging.basicConfig(
    format=LOG_FORMAT,
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

# Khởi tạo M3U8 Finder
m3u8_finder = M3U8Finder()

# Rate limiting
user_requests = defaultdict(list)

def check_rate_limit(user_id: int) -> bool:
    """Kiểm tra giới hạn số lượng request"""
    now = datetime.now()
    user_requests[user_id] = [
        req_time for req_time in user_requests[user_id]
        if now - req_time < timedelta(minutes=1)
    ]
    
    if len(user_requests[user_id]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    user_requests[user_id].append(now)
    return True

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start"""
    await update.message.reply_text(MESSAGES['start'])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /help"""
    await update.message.reply_text(MESSAGES['help'])

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý URL được gửi từ người dùng"""
    user_id = update.effective_user.id
    url = update.message.text.strip()
    
    # Kiểm tra rate limit
    if not check_rate_limit(user_id):
        await update.message.reply_text(MESSAGES['rate_limit'])
        return
    
    # Kiểm tra URL hợp lệ
    if not m3u8_finder.is_valid_url(url):
        await update.message.reply_text(MESSAGES['invalid_url'])
        return
    
    # Gửi thông báo đang xử lý
    processing_message = await update.message.reply_text(MESSAGES['processing'])
    
    try:
        # Tìm kiếm link m3u8
        m3u8_links = m3u8_finder.find_m3u8_links(url)
        
        # Xóa thông báo đang xử lý
        await processing_message.delete()
        
        if not m3u8_links:
            await update.message.reply_text(MESSAGES['no_m3u8_found'])
            return
        
        # Tạo thông báo kết quả
        response = MESSAGES['found_m3u8'].format(len(m3u8_links)) + '\n\n'
        
        for i, link in enumerate(m3u8_links, 1):
            response += f"{i}. {link}\n"
            
            # Telegram có giới hạn độ dài tin nhắn
            if len(response) > 4000:
                await update.message.reply_text(response)
                response = f"Tiếp tục ({i+1}-{len(m3u8_links)}):\n\n"
        
        if response.strip():
            await update.message.reply_text(response)
            
    except ValueError as e:
        await processing_message.delete()
        await update.message.reply_text(MESSAGES['invalid_url'])
        logger.error(f"Invalid URL from user {user_id}: {url}")
        
    except Exception as e:
        await processing_message.delete()
        error_msg = MESSAGES['error_fetching'].format(str(e))
        await update.message.reply_text(error_msg)
        logger.error(f"Error processing URL {url} from user {user_id}: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý text message"""
    text = update.message.text.strip()
    
    # Kiểm tra xem có phải URL không
    if text.startswith(('http://', 'https://')):
        await handle_url(update, context)
    else:
        await update.message.reply_text(
            "🤔 Tôi chỉ có thể xử lý URL. Vui lòng gửi một URL hợp lệ bắt đầu với http:// hoặc https://\n\n"
            "Ví dụ: https://example.com/video"
        )

def main():
    """Khởi chạy bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables")
        return
    
    # Tạo application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Đăng ký handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Chạy bot
    logger.info("Starting M3U8 Finder Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()