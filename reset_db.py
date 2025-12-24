# reset_db.py
"""
Скрипт для пересоздания базы данных с новыми моделями
"""

import os
import sys
import time

# Добавляем путь к корню проекта
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app import create_app
from database.models import db, Mouthpiece, Tube, Bell, Flute, Hole, CalibrationData

print("=" * 60)
print("🔄 ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ WITG")
print("=" * 60)

# Создаем приложение
app = create_app()

with app.app_context():
    db_path = os.path.join(current_dir, 'flutes.db')
    
    # Останавливаем все соединения с БД
    db.session.close()
    
    # Ждем немного, чтобы закрылись все соединения
    time.sleep(1)
    
    # Пытаемся удалить старую базу
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️  Старая база данных удалена")
        except PermissionError as e:
            print(f"⚠️  Не удалось удалить файл: {e}")
            print("Попробуйте закрыть все программы, использующие базу данных")
            print("или удалите файл вручную: flutes.db")
            sys.exit(1)
    
    # Удаляем все таблицы (если база все еще существует)
    try:
        db.drop_all()
    except:
        pass  # Игнорируем ошибки если базы нет
    
    # Создаем все таблицы
    db.create_all()
    print("✅ Созданы новые таблицы с обновленной структурой")
    
    # Остальной код без изменений...
    print("📝 Добавляем тестовые данные...")
    
    # Тестовый мундштук (кларнет)
    mp1 = Mouthpiece(
        name="Тестовый кларнетный мундштук",
        type="clarinet",
        brand="Yamaha",
        d_tip=13.5,
        d_out=14.7,
        L_m=75.0,
        delta_m=68.0,
        material="ebonite",
        embouchure="rounded"
    )
    db.session.add(mp1)
    
    # Тестовый мундштук (альт саксофон)
    mp2 = Mouthpiece(
        name="Альт саксофонный мундштук",
        type="alto_sax",
        brand="Selmer",
        d_tip=16.5,
        d_out=17.5,
        L_m=85.0,
        delta_m=72.0,
        material="metal",
        embouchure="flat"
    )
    db.session.add(mp2)
    
    # Тестовая трубка (алюминий)
    tube1 = Tube(
        name="Алюминиевая трубка 20мм",
        material="aluminum",
        d_in=20.0,
        d_out=22.0,
        wall_thickness=1.0,
        v_eff=33500.0,
        roughness="smooth"
    )
    db.session.add(tube1)
    
    # Тестовая трубка (PVC)
    tube2 = Tube(
        name="PVC трубка 20мм",
        material="pvc",
        d_in=20.0,
        d_out=22.0,
        wall_thickness=1.0,
        v_eff=29000.0,
        roughness="medium"
    )
    db.session.add(tube2)
    
    # Тестовый раструб
    bell1 = Bell(
        name="Малый металлический раструб",
        type="flare",
        material="metal",
        start_diameter=28.0,
        end_diameter=80.0,
        length=150.0,
        wall_thickness=0.5,
        expansion_ratio=2.86,
        flare_angle=15.0,
        delta_L=-12.5,
        acoustic_effect="medium"
    )
    db.session.add(bell1)
    
    # Тестовая флейта
    flute1 = Flute(
        name="Моя первая флейта",
        key="D",
        scale="minor",
        tube_length=450.0,
        hole_count=6,
        mouthpiece_id=1,
        tube_id=1,
        bell_id=1,
        is_verified=True,
        custom_notes='["D4", "E4", "F#4", "G4", "A4", "B4"]',
        holes_data='[{"note": "D4", "position": 225.0, "diameter": 8.0}, {"note": "E4", "position": 202.5, "diameter": 8.0}]'
    )
    db.session.add(flute1)
    
    # Тестовые калибровочные данные
    cal1 = CalibrationData(
        note="D4",
        frequency=293.66,
        position=225.0,
        diameter=8.0,
        tube_diameter=20.0,
        tube_length=450.0,
        tube_material="aluminum",
        mouthpiece_delta_m=68.0,
        mouthpiece_type="clarinet",
        bell_delta_L=-12.5,
        temperature=20.0,
        source="test",
        confidence=0.9,
        notes="Тестовые калибровочные данные"
    )
    db.session.add(cal1)
    
    cal2 = CalibrationData(
        note="E4",
        frequency=329.63,
        position=202.5,
        diameter=8.0,
        tube_diameter=20.0,
        tube_length=450.0,
        tube_material="aluminum",
        mouthpiece_delta_m=68.0,
        mouthpiece_type="clarinet",
        bell_delta_L=-12.5,
        temperature=20.0,
        source="test",
        confidence=0.9,
        notes="Тестовые калибровочные данные"
    )
    db.session.add(cal2)
    
    # Сохраняем все изменения
    db.session.commit()
    
    print("✅ Тестовые данные добавлены")
    
    # Выводим статистику
    print("\n📊 СТАТИСТИКА БАЗЫ ДАННЫХ:")
    print("-" * 40)
    print(f"Мундштуков: {Mouthpiece.query.count()}")
    print(f"Трубок: {Tube.query.count()}")
    print(f"Раструбов: {Bell.query.count()}")
    print(f"Флейт: {Flute.query.count()}")
    print(f"Калибровочных данных: {CalibrationData.query.count()}")
    
    print("\n" + "=" * 60)
    print("🎉 База данных успешно пересоздана!")
    print("=" * 60)
    print("\nЗапустите сервер командой: python run.py")