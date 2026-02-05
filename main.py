import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from gemini_client import GeminiClient
from core import AICore
from gui import ChatGUI
from telegram_bot import TelegramBot
from config import BOT_TOKEN

def main():
    # 1. Ініціалізація
    print("🚀 Запуск AI Assistant System...")
    
    ai_client = GeminiClient()
    core = AICore(ai_client)
    
    # 2. Запуск Telegram бота (в окремому потоці)
    bot = TelegramBot(core, token=BOT_TOKEN)
    bot.start()
    
    core.log_event("Telegram bot started")
    
    # 3. Запуск GUI
    app = QApplication(sys.argv)
    window = ChatGUI(core)
    window.show()
    
    core.log_event("GUI started")
    
    # 4. Система сповіщень з ядра в Telegram
    def check_telegram_queue():
        """Перевіряє чергу повідомлень для Telegram"""
        try:
            while not core.to_telegram_queue.empty():
                message = core.to_telegram_queue.get()
                if message["type"] == "message":
                    # Тут можна реалізувати відправку конкретному користувачу
                    # Поки що просто логуємо
                    core.log_event(f"Telegram queue: {message['content']}")
        except:
            pass
    
    # Таймер для перевірки черги Telegram
    tg_timer = QTimer()
    tg_timer.timeout.connect(check_telegram_queue)
    tg_timer.start(500)  # Кожні 500мс
    
    # 5. Функція для безпечного закриття
    def on_exit():
        core.stop()
        tg_timer.stop()
        print("👋 System stopped")
    
    # 6. Запуск
    sys.exit(app.exec())

if __name__ == "__main__":
    main()