from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton,
    QComboBox, QLabel, QGroupBox
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont

class ChatGUI(QWidget):
    def __init__(self, core):
        super().__init__()
        self.core = core
        
        self.core.on_mode_change_callbacks.append(self.on_mode_changed)
        
        self.init_ui()
        self.setup_update_timer()
        
    def init_ui(self):
        self.setWindowTitle("AI Assistant + Telegram Integration")
        self.resize(800, 600)
        
        # Стилі
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #ffffff; }
            QTextEdit { 
                background-color: #2d2d2d; 
                border: 1px solid #3f3f3f; 
                border-radius: 8px; 
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit { 
                background-color: #3d3d3f; 
                border: 2px solid #0078d4; 
                border-radius: 15px; 
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton { 
                background-color: #0078d4; 
                border-radius: 15px; 
                padding: 8px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2b88d8; }
            QComboBox { 
                background-color: #3d3d3f; 
                border-radius: 8px; 
                padding: 5px;
                min-width: 150px;
            }
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                padding-top: 10px;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        
        status_layout = QHBoxLayout()
        
        self.mode_label = QLabel("Режим: assistant")
        self.mode_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        
        self.telegram_status = QLabel("Telegram: 🟢 Активний")
        self.telegram_status.setStyleSheet("color: #4db8ff;")
        
        status_layout.addWidget(self.mode_label)
        status_layout.addStretch()
        status_layout.addWidget(self.telegram_status)
        main_layout.addLayout(status_layout)
        
        mode_group = QGroupBox("Режим AI")
        mode_layout = QHBoxLayout()
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(self.core.get_available_modes())
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        
        mode_layout.addWidget(QLabel("Обрати режим:"))
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)
        

        chat_group = QGroupBox("Чат з AI")
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        
        chat_layout.addWidget(self.chat_display)
        chat_group.setLayout(chat_layout)
        main_layout.addWidget(chat_group)
        
       
        log_group = QGroupBox("Лог системи")
        log_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)
        self.log_display.setFont(QFont("Consolas", 9))
        
        log_layout.addWidget(self.log_display)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
       
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Напишіть повідомлення або команду...")
        
        self.send_button = QPushButton("Надіслати")
        self.send_button.clicked.connect(self.send_message)
        
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        self.setLayout(main_layout)
        
        # Підключення Enter для відправки
        self.input_field.returnPressed.connect(self.send_message)
    
    def setup_update_timer(self):
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queues)
        self.timer.start(100)  
    
    def check_queues(self):
        while not self.core.to_gui_queue.empty():
            message = self.core.to_gui_queue.get()
            
            if message["type"] == "ai_response":
                self.display_ai_response(message["content"], message["source"])
            elif message["type"] == "log":
                self.add_log(message["content"])
    
    def change_mode(self, mode):
        self.core.set_mode(mode)
    
    def on_mode_changed(self, mode):
        self.mode_label.setText(f"Режим: {mode}")
        self.mode_combo.setCurrentText(mode)
        
        self.add_log(f"Режим змінено на: {mode}")
    
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        

        self.chat_display.append(f'<div style="color: #4db8ff;"><b>Ви:</b> {text}</div>')
        self.input_field.clear()
        
        self.core.ask_ai(text, source="GUI")
    
    def display_ai_response(self, response, source):
        if source == "telegram":
            prefix = "📱 Telegram: "
            color = "#00ff88"
        else:
            prefix = "🤖 AI: "
            color = "#ff66cc"
        
        self.chat_display.append(
            f'<div style="color: {color}; margin-top: 10px;">'
            f'<b>{prefix}</b><br>{response}</div>'
            '<hr style="border: 1px dashed #444;">'
        )
        
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def add_log(self, log_entry):
        self.log_display.append(log_entry)
        
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        self.core.stop()
        self.timer.stop()
        event.accept()