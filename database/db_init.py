"""
Инициализация базы данных
"""

from .models import db

def init_database(app):
    """Инициализировать базу данных"""
    with app.app_context():
        try:
            # Создаем все таблицы
            db.create_all()
            print("✅ Таблицы базы данных созданы")
            
            # Добавляем тестовые данные
            from .models import Mouthpiece, Tube, Flute
            
            if Mouthpiece.query.count() == 0:
                print("📝 Добавляем тестовые данные...")
                
                # Тестовый мундштук
                mp = Mouthpiece(name="Тестовый мундштук", inner_diameter=15.0)
                db.session.add(mp)
                
                # Тестовая трубка
                tube = Tube(name="PVC 20mm", inner_diameter=20.0)
                db.session.add(tube)
                
                # Тестовая флейта
                flute = Flute(name="Моя первая флейта", key="D", tube_length=450.0)
                db.session.add(flute)
                
                db.session.commit()
                print("✅ Тестовые данные добавлены")
            
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            return False