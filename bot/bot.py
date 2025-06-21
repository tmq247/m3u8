#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot chính sử dụng Pyrogram
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import logging
from config import Config, Messages
from bot.handlers import BotHandlers

class StreamBot:
    """Lớp bot chính"""
    
    def __init__(self, api_id: int, api_hash: str, bot_token: str):
        """
        Khởi tạo bot
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            bot_token: Bot Token
        """
        self.app = Client(
            "stream_bot",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token
        )
        
        self.handlers = BotHandlers()
        self.logger = logging.getLogger(__name__)
        
        # Đăng ký handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Đăng ký các handlers cho bot"""
        
        # Start command
        @self.app.on_message(filters.command("start"))
        async def start_handler(client: Client, message: Message):
            await self.handlers.start_command(client, message)
        
        # Help command
        @self.app.on_message(filters.command("help"))
        async def help_handler(client: Client, message: Message):
            await self.handlers.help_command(client, message)
        
        # Supported sites command
        @self.app.on_message(filters.command("supported"))
        async def supported_handler(client: Client, message: Message):
            await self.handlers.supported_command(client, message)
        
        # URL handler
        @self.app.on_message(filters.regex(r'https?://\S+'))
        async def url_handler(client: Client, message: Message):
            await self.handlers.url_handler(client, message)
        
        # Default message handler
        @self.app.on_message(filters.text & ~filters.command(["start", "help", "supported"]))
        async def default_handler(client: Client, message: Message):
            await self.handlers.default_handler(client, message)
    
    async def start(self):
        """Khởi động bot"""
        await self.app.start()
        self.logger.info("Bot đã khởi động thành công!")
    
    async def stop(self):
        """Dừng bot"""
        await self.app.stop()
        self.logger.info("Bot đã dừng hoạt động")
    
    async def idle(self):
        """Giữ bot chạy"""
        import asyncio
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
