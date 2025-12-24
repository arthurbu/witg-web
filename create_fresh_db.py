# create_fresh_db.py
from app import create_app
from database.models import db

app = create_app()

with app.app_context():
    # Удаляем все таблицы
    db.drop_all()
    
    # Создаем новые таблицы с правильной структурой
    db.create_all()
    
    print("✅ База данных пересоздана с новой структурой")
    
    # Добавляем тестовые данные
    from database.models import Mouthpiece, Tube, Bell
    
    # Тестовый мундштук
    mp = Mouthpiece(
        name="Тестовый кларнетный мундштук",
        type="clarinet",
        brand="Yamaha",
        d_tip=13.5,
        d_out=14.7,
        L_m=75.0,
        delta_m=68.0
    )
    db.session.add(mp)
    
    # Тестовая трубка
    tube = Tube(
        name="Алюминиевая трубка 20мм",
        material="aluminum",
        d_in=20.0,
        d_out=22.0,
        v_eff=33500.0
    )
    db.session.add(tube)
    
    # Тестовый раструб
    bell = Bell(
        name="Малый раструб",
        type="flare",
        start_diameter=28.0,
        end_diameter=80.0,
        length=150.0,
        delta_L=-12.5
    )
    db.session.add(bell)
    
    db.session.commit()
    print("✅ Тестовые данные добавлены")