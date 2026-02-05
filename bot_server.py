# bot_server.py - серверна версія БЕЗ pyautogui
import os
import sys
import asyncio

# Додаємо поточну папку
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Запускаю AI Telegram Bot (серверна версія)...")

# Перевіряємо токени
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не знайдено!")
    sys.exit(1)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("❌ GEMINI_API_KEY не знайдено!")
    sys.exit(1)

# Підміняємо screenshot_service на заглушку
sys.modules['screenshot_service'] = type(sys)('screenshot_service')

# Створюємо заглушку для ScreenshotService
class ScreenshotServiceStub:
    @staticmethod
    def take_screenshot():
        return {
            "success": False,
            "error": "Скріншоти недоступні на сервері"
        }
    
    @staticmethod 
    def take_and_analyze_screenshot():
        return {
            "success": False,
            "error": "Скріншоти недоступні на сервері"
        }

# Ін'єктуємо нашу заглушку
import screenshot_service
screenshot_service.ScreenshotService = ScreenshotServiceStub

# Тепер імпортуємо все інше
try:
    from telegram_bot import TelegramBot
    from gemini_client import GeminiClient
    from core import AICore
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

async def main():
    print("🤖 Ініціалізую AI систему...")
    
    # Ініціалізуємо
    ai_client = GeminiClient()
    core = AICore(ai_client)
    
    # Створюємо бота
    bot = TelegramBot(core, BOT_TOKEN)
    
    print("✅ Бот ініціалізовано!")
    print("📡 Чекаю повідомлень в Telegram...")
    print("👉 Напиши /start своєму боту")
    
    # Запускаємо
    await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(main())