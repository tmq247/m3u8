#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Handlers cho các lệnh và tin nhắn của bot
"""

import logging
from pyrogram import Client
from pyrogram.types import Message
from config import Messages
from scrapers.scraper_factory import ScraperFactory
from utils.validators import is_valid_url, is_supported_site

class BotHandlers:
    """Lớp xử lý các handlers của bot"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scraper_factory = ScraperFactory()
    
    async def start_command(self, client: Client, message: Message):
        """Xử lý lệnh /start"""
        try:
            await message.reply_text(
                Messages.START_MESSAGE,
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            self.logger.info(f"Người dùng {message.from_user.id} đã bắt đầu sử dụng bot")
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý lệnh start: {e}")
    
    async def help_command(self, client: Client, message: Message):
        """Xử lý lệnh /help"""
        try:
            await message.reply_text(
                Messages.HELP_MESSAGE,
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            self.logger.info(f"Người dùng {message.from_user.id} đã xem hướng dẫn")
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý lệnh help: {e}")
    
    async def supported_command(self, client: Client, message: Message):
        """Xử lý lệnh /supported"""
        try:
            await message.reply_text(
                Messages.SUPPORTED_SITES_MESSAGE,
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            self.logger.info(f"Người dùng {message.from_user.id} đã xem danh sách trang web được hỗ trợ")
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý lệnh supported: {e}")
    
    async def url_handler(self, client: Client, message: Message):
        """Xử lý URL được gửi bởi người dùng"""
        try:
            url = message.text.strip()
            user_id = message.from_user.id
            
            self.logger.info(f"Người dùng {user_id} gửi URL: {url}")
            
            # Kiểm tra URL hợp lệ
            if not is_valid_url(url):
                await message.reply_text(Messages.INVALID_URL_MESSAGE)
                return
            
            # Kiểm tra trang web được hỗ trợ
            if not is_supported_site(url):
                await message.reply_text(Messages.UNSUPPORTED_SITE_MESSAGE)
                return
            
            # Gửi thông báo đang xử lý
            processing_msg = await message.reply_text(Messages.PROCESSING_MESSAGE)
            
            # Lấy scraper phù hợp
            scraper = self.scraper_factory.get_scraper(url)
            if not scraper:
                await processing_msg.edit_text(Messages.UNSUPPORTED_SITE_MESSAGE)
                return
            
            # Trích xuất link stream
            stream_links = await scraper.extract_stream_links(url)
            
            if not stream_links:
                await processing_msg.edit_text(Messages.NO_STREAM_FOUND_MESSAGE)
                return
            
            # Tạo thông điệp kết quả
            result_message = f"{Messages.SUCCESS_MESSAGE}\n\n"
            
            for i, link_info in enumerate(stream_links, 1):
                quality = link_info.get('quality', 'Unknown')
                link = link_info.get('url', '')
                source = link_info.get('source', 'Unknown')
                
                result_message += f"**{i}. {quality} - {source}**\n"
                result_message += f"`{link}`\n\n"
            
            result_message += "💡 **Lưu ý:** Nhấn vào link để copy, sau đó dán vào trình phát video."
            
            # Gửi kết quả
            await processing_msg.edit_text(
                result_message,
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            
            self.logger.info(f"Đã trích xuất thành công {len(stream_links)} link cho người dùng {user_id}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý URL: {e}")
            error_message = Messages.ERROR_MESSAGE.format(error=str(e))
            
            try:
                await processing_msg.edit_text(error_message)
            except:
                await message.reply_text(error_message)
    
    async def default_handler(self, client: Client, message: Message):
        """Xử lý tin nhắn mặc định"""
        try:
            help_text = """
❓ **Không hiểu tin nhắn của bạn**

Vui lòng:
• Gửi link phim từ các trang web được hỗ trợ
• Sử dụng /help để xem hướng dẫn
• Sử dụng /supported để xem danh sách trang web

**Ví dụ:** Gửi link như `https://tvhay.fm/phim/ten-phim`
"""
            
            await message.reply_text(
                help_text,
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý tin nhắn mặc định: {e}")
