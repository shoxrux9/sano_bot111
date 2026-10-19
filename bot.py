# ============================================================
# SANO BOOKS BOT - Asosiy fayl
# ============================================================
import asyncio
import logging
import sys
import os

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_config
from app.database import init_db

# Handler'larni import qilish
from app.handlers import (
    main_menu, catalog, cart,
    admin_orders, admin_books, admin_catalog, admin_settings
)

# Middleware va filter
from app.middlewares.middleware import UserMiddleware, LoggingMiddleware


async def main():
    config = get_config()

    # Token tekshirish
    if not config.bot_token or config.bot_token == "your_bot_token_here":
        logger.error(
            "❌ BOT_TOKEN ko'rsatilmagan!\n"
            ".env faylini oching va BOT_TOKEN=... qatorini to'ldiring."
        )
        sys.exit(1)

    if not config.admin_ids:
        logger.warning(
            "⚠️ ADMIN_IDS ko'rsatilmagan!\n"
            ".env faylida ADMIN_IDS=123456789 ko'rinishida kiriting."
        )

    # Ma'lumotlar bazasini ishga tushirish
    logger.info("📦 Ma'lumotlar bazasi yaratilmoqda...")
    await init_db()

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware qo'shish
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # Router'larni ro'yxatdan o'tkazish
    # MUHIM: Admin router'lar avval ro'yxatdan o'tkazilsin
    # (ular filter bilan foydalanuvchi router'lardan ajralib turadi)
    dp.include_router(admin_orders.router)
    dp.include_router(admin_books.router)
    dp.include_router(admin_catalog.router)
    dp.include_router(admin_settings.router)

    # Foydalanuvchi router'lari
    dp.include_router(main_menu.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)

    # Bot ma'lumotlarini olish
    bot_info = await bot.get_me()
    logger.info(f"🤖 Bot ishga tushdi: @{bot_info.username}")
    logger.info(f"👥 Adminlar: {config.admin_ids}")
    logger.info(f"🏪 Do'kon: {config.shop_name}")

    # Adminlarga start xabari yuborish
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"✅ <b>SANO BOOKS Bot ishga tushdi!</b>\n\n"
                f"🤖 Bot: @{bot_info.username}\n"
                f"🏪 Do'kon: {config.shop_name}\n\n"
                f"Admin panel uchun /admin buyrug'ini bosing.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Admin {admin_id} ga xabar yuborib bo'lmadi: {e}")

    # Polling boshlash
    logger.info("🚀 Polling boshlandi...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("🔴 Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())
