import pyautogui
from PIL import Image
import io
from datetime import datetime
import os

class ScreenshotService:
    @staticmethod
    def take_screenshot():
        """Зробити скріншот всього екрана"""
        try:
            # Робимо скріншот
            screenshot = pyautogui.screenshot()
            
            # Конвертуємо в байти для Telegram
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Додаємо timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "success": True,
                "image_bytes": img_byte_arr,
                "timestamp": timestamp,
                "size": screenshot.size,
                "filename": f"screenshot_{timestamp.replace(':', '-').replace(' ', '_')}.png"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def save_screenshot_to_file():
        """Зберегти скріншот у файл (опціонально)"""
        result = ScreenshotService.take_screenshot()
        if result["success"]:
            # Створюємо папку screenshots якщо немає
            os.makedirs("screenshots", exist_ok=True)
            
            # Зберігаємо файл
            filepath = os.path.join("screenshots", result["filename"])
            with open(filepath, "wb") as f:
                f.write(result["image_bytes"].getvalue())
            
            result["filepath"] = filepath
        return result