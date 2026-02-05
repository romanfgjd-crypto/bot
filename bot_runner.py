# bot_runner.py - максимально просто
import os
import sys
import asyncio

# Додаємо шлях
sys.path.append('.')

try:
    from telegram_bot import TelegramBot
    from gemini_client import GeminiClient
    from core import AICore
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

async def main():
    print("🚀 Запускаю AI Telegram Bot на Render...")
    
    # Перевіряємо токени
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не знайдено!")
        return
    
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("❌ GEMINI_API_KEY не знайдено!")
        return
    
    # Ініціалізуємо
    ai_client = GeminiClient()
    core = AICore(ai_client)
    
    # Запускаємо бота
    bot = TelegramBot(core, BOT_TOKEN)
    
    print("🤖 Бот запущено! Чекаю повідомлень...")
    print("🔗 Telegram: https://t.me/your_bot_username")
    
    # Просто запускаємо polling
    await bot.dp.start_polling(bot.bot)

if __name__ == "__main__":
    asyncio.run(main())