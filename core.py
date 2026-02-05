import threading
import queue
import json
import time
from typing import Dict, Any, List

class AICore:
    """Центральне ядро програми"""
    
    def __init__(self, gemini_client):
        self.ai = gemini_client
        self.mode = "asistant"
        
        # Черги для спілкування між компонентами
        self.to_telegram_queue = queue.Queue()  # Повідомлення для Telegram
        self.to_gui_queue = queue.Queue()       # Повідомлення для GUI
        self.system_log = []                    # Лог всіх подій
        
        # Підписники (callbacks)
        self.on_mode_change_callbacks = []
        self.on_message_callbacks = []
        
        self.is_running = True
        
    def set_mode(self, mode: str):
        """Змінити режим AI"""
        self.mode = mode
        self.ai.set_mode(mode)
        
        # Повідомляємо всіх підписників
        for callback in self.on_mode_change_callbacks:
            callback(mode)
        
        self.log_event(f"Mode changed to: {mode}")
        
    def ask_ai(self, prompt: str, source: str = "unknown") -> str:
        """Запитати AI і записати в лог"""
        self.log_event(f"{source}: {prompt}")
        
        # Отримуємо відповідь
        response = self.ai.ask(prompt)
        
        self.log_event(f"AI ({self.mode}): {response[:50]}...")
        
        # Повідомляємо GUI про нову відповідь
        self.to_gui_queue.put({
            "type": "ai_response",
            "content": response,
            "mode": self.mode,
            "source": source
        })
        
        return response
    
    def send_to_telegram(self, message: str, user_id: str = None):
        """Надіслати повідомлення через Telegram"""
        self.to_telegram_queue.put({
            "type": "message",
            "content": message,
            "user_id": user_id
        })
    
    def log_event(self, event: str):
        """Логування подій"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {event}"
        self.system_log.append(log_entry)
        print(log_entry)  # Також в консоль
        
        # Повідомляємо GUI про новий лог
        self.to_gui_queue.put({
            "type": "log",
            "content": log_entry
        })
    
    def get_available_modes(self):
        """Отримати доступні режими"""
        return self.ai.get_available_modes()
    
    def stop(self):
        """Зупинити ядро"""
        self.is_running = False
        self.log_event("System stopped")