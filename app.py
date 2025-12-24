"""
Главное приложение WITG
"""

import os
from flask import Flask

def create_app():
    """Фабрика приложения"""
    
    print("=" * 50)
    print("🎵 СОЗДАНИЕ ПРИЛОЖЕНИЯ WITG")
    print("=" * 50)
    
    # Абсолютные пути к папкам
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'web', 'templates')
    static_dir = os.path.join(base_dir, 'web', 'static')
    
    print(f"📁 Базовый путь: {base_dir}")
    print(f"📁 Папка шаблонов: {template_dir}")
    print(f"📁 Папка статики: {static_dir}")
    
    # Проверяем существование папок
    if not os.path.exists(template_dir):
        print(f"⚠️  Папка шаблонов не найдена! Создаю: {template_dir}")
        os.makedirs(template_dir, exist_ok=True)
    
    if not os.path.exists(static_dir):
        print(f"⚠️  Папка статики не найдена! Создаю: {static_dir}")
        os.makedirs(static_dir, exist_ok=True)
    
    # Создаем приложение с правильными путями
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    
    # Конфигурация
    app.config['SECRET_KEY'] = 'witg-dev-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'flutes.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Проверяем существование index.html
    index_path = os.path.join(template_dir, 'index.html')
    if os.path.exists(index_path):
        print(f"✅ Шаблон index.html найден: {index_path}")
    else:
        print(f"⚠️  Шаблон index.html НЕ найден! Создаю пустой файл")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('<h1>WITG работает! 🎵</h1><p>Добавьте содержимое index.html</p>')
    
    # Инициализация базы данных
    try:
        from database.models import db
        db.init_app(app)
        print("✅ База данных инициализирована")
    except ImportError as e:
        print(f"⚠️  Ошибка инициализации БД: {e}")
    
    # Создаем таблицы если их нет
    with app.app_context():
        try:
            db.create_all()
            print("✅ Таблицы проверены/созданы")
        except Exception as e:
            print(f"⚠️  Ошибка при создании таблиц: {e}")
    
    # Регистрация маршрутов
    try:
        from web.routes import register_routes
        register_routes(app)
        print("✅ Маршруты зарегистрированы")
    except ImportError as e:
        print(f"⚠️  Ошибка регистрации маршрутов: {e}")
        @app.route('/')
        def home():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WITG - Временная страница</title>
                <style>
                    body { 
                        font-family: Arial; 
                        padding: 50px; 
                        text-align: center; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    h1 { font-size: 3em; margin-bottom: 20px; }
                    .container { 
                        background: rgba(255,255,255,0.1); 
                        padding: 40px; 
                        border-radius: 15px;
                        backdrop-filter: blur(10px);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎵 WITG работает!</h1>
                    <p>Сервер запущен успешно!</p>
                    <p>Шаблон index.html не найден в папке web/templates/</p>
                    <p><a href="/api/status" style="color: #4CAF50; font-weight: bold;">Проверить API статуса</a></p>
                </div>
            </body>
            </html>
            """
    
    print("=" * 50)
    return app


if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК СЕРВЕРА WITG")
    print("=" * 60)
    print("🌐 Адрес: http://localhost:5000")
    print("⚡ Остановка: Ctrl+C")
    print("=" * 60)
    
    app.run(debug=True, port=5000, use_reloader=False)