#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram để trích xuất link phát trực tiếp từ các trang web xem phim
"""

import asyncio
import os
from dotenv import load_dotenv
from bot.bot import StreamBot
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

async def main():
    """Hàm chính để khởi chạy bot"""
    # Setup logger
    logger = setup_logger()
    
    # Kiểm tra API credentials
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not all([api_id, api_hash, bot_token]):
        logger.error("Thiếu thông tin API! Vui lòng kiểm tra file .env")
        return
    
    # Khởi tạo và chạy bot
    bot = StreamBot(
        api_id=int(api_id),
        api_hash=api_hash,
        bot_token=bot_token
    )
    
    try:
        logger.info("Đang khởi động bot...")
        await bot.start()
        logger.info("Bot đã khởi động thành công!")
        
        # Giữ bot chạy
        await bot.idle()
        
    except Exception as e:
        logger.error(f"Lỗi khi chạy bot: {e}")
    finally:
        await bot.stop()
        logger.info("Bot đã dừng hoạt động")

if __name__ == "__main__":
    asyncio.run(main())
