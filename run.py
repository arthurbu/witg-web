#!/usr/bin/env python3
"""
Запуск WITG сервера
"""

from app import create_app
import webbrowser
import threading
import time

def open_browser():
    """Открыть браузер после запуска сервера"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🎵 WIND INSTRUMENT TEMPLATE GENERATOR")
    print("=" * 60)
    print("🌐 Сервер запущен: http://localhost:5000")
    print("📂 Шаблоны в:", app.template_folder)
    print("⚡ Остановка: Ctrl+C")
    print("=" * 60)
    
    # Открываем браузер автоматически
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=True, port=5000, use_reloader=False)