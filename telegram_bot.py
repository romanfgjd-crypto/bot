import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.filters import Command
import threading

# Імпортуємо наш сервіс скріншотів
from sreenshot_service import ScreenshotService

class TelegramBot:
    def __init__(self, core, token: str):
        self.core = core
        self.token = token
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.router = Router()
        
        # Реєструємо обробники
        self.setup_handlers()
        self.dp.include_router(self.router)
        
        # Запускаємо бота в окремому потоці
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        
    def setup_handlers(self):
        """Налаштування команд бота"""
        
        @self.router.message(Command("start"))
        async def start_cmd(message: Message):
            await message.answer(
                "🤖 Привіт! Я AI-бот, інтегрований з десктопним додатком.\n"
                f"Поточний режим: {self.core.mode}\n\n"
                "📸 **Нові команди:**\n"
                "/screenshot - зробити скріншот екрана\n\n"
                "Обери режим або напиши повідомлення.",
                reply_markup=self.get_keyboard(),
                parse_mode="Markdown"
            )
            self.core.log_event(f"Telegram user started: {message.from_user.id}")
        
        @self.router.message(Command("screenshot"))
        async def screenshot_cmd(message: Message):
            """Команда для скріншоту екрана"""
            await message.answer("📸 Роблю скріншот...")
            
            # Логуємо спробу
            self.core.log_event(f"Telegram: користувач {message.from_user.id} запросив скріншот")
            
            # Робимо скріншот
            result = ScreenshotService.take_screenshot()
            
            if result["success"]:
                # Створюємо об'єкт файлу для Telegram
                photo_file = BufferedInputFile(
                    result["image_bytes"].getvalue(),
                    filename=result["filename"]
                )
                
                # Формуємо підпис
                caption = (
                    f"🖥️ **Скріншот екрана**\n"
                    f"⏰ Час: `{result['timestamp']}`\n"
                    f"📏 Розмір: `{result['size'][0]}x{result['size'][1]}`\n"
                    f"👤 Запитувач: {message.from_user.full_name}"
                )
                
                # Відправляємо фото
                await message.answer_photo(
                    photo_file,
                    caption=caption,
                    parse_mode="Markdown"
                )
                
                # Логуємо успіх
                self.core.log_event(f"Telegram: скріншот відправлено користувачу {message.from_user.id}")
                
                # Також можна зберегти у файл
                ScreenshotService.save_screenshot_to_file()
                
            else:
                error_msg = f"❌ **Помилка при створенні скріншоту:**\n`{result['error']}`"
                await message.answer(error_msg, parse_mode="Markdown")
                self.core.log_event(f"Telegram: помилка скріншоту: {result['error']}")
        
        @self.router.message(Command("screen"))
        async def screen_shortcut(message: Message):
            """Коротка версія команди"""
            await screenshot_cmd(message)
        
        @self.router.message(lambda m: m.text in ["👨‍💻 Програміст", "🧠 Психолог", "ℹ️ Режими"])
        async def handle_buttons(message: Message):
            if message.text == "👨‍💻 Програміст":
                self.core.set_mode("programmer")
                await message.answer("✅ Режим 👨‍💻 Програміст активовано")
                
            elif message.text == "🧠 Психолог":
                self.core.set_mode("asistant")
                await message.answer("✅ Режим 🧠 Психолог активовано")
                
            elif message.text == "ℹ️ Режими":
                modes = self.core.get_available_modes()
                await message.answer(
                    "📌 **Доступні режими:**\n" + "\n".join(f"• {m}" for m in modes),
                    parse_mode="Markdown"
                )
        
        @self.router.message()
        async def ai_chat(message: Message):
            if message.text.startswith('/'):
                return
                
            
            self.core.log_event(f"Telegram: {message.text}")
            
            await message.answer("⏳ Думаю...")
            
            
            response = self.core.ask_ai(message.text, source="telegram")
            
            
            max_len = 4000
            for i in range(0, len(response), max_len):
                await message.answer(response[i:i+max_len])
    
    def get_keyboard(self):
        """Створити клавіатуру"""
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👨‍💻 Програміст"), KeyboardButton(text="🧠 Психолог")],
                [KeyboardButton(text="ℹ️ Режими")]
            ],
            resize_keyboard=True
        )
    
    # def run_bot(self):
    #     """Запустити бота (викликається в потоці)"""
    #     async def main():
    #         print("🤖 Telegram Bot запущено")
    #         await self.dp.start_polling(self.bot)
        
    #     asyncio.run(main())
    def run_bot(self):
        """Запустити бота (викликається в потоці)"""
        asyncio.run(self._run_polling())

    async def _run_polling(self):
        """Асинхронний запуск polling"""
        try:
            print("🤖 Telegram Bot запущено на сервері")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            print(f"❌ Помилка: {e}")
            # Автоматичний перезапуск через 30 секунд
            import time
            time.sleep(30)
            await self._run_polling()
    
    def start(self):
        """Запустити бота в окремому потоці"""
        self.bot_thread.start()