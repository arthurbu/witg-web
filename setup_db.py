# setup_db.py
"""
Создание и настройка базы данных с нуля
"""

import os
import sqlite3

print("=" * 60)
print("🎵 НАСТРОЙКА БАЗЫ ДАННЫХ WITG")
print("=" * 60)

# Удаляем старую базу если существует
db_path = 'flutes.db'
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("🗑️  Старая база данных удалена")
    except:
        print("⚠️  Не удалось удалить файл, возможно он используется")

# Создаем новую базу SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔄 Создаем таблицы...")

# Создаем таблицу mouthpieces
cursor.execute('''
CREATE TABLE IF NOT EXISTS mouthpieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    brand TEXT,
    model TEXT,
    d_tip REAL,
    d_out REAL,
    L_m REAL,
    L_cyl REAL,
    baffle TEXT,
    chamber_depth REAL,
    delta_m REAL,
    L_calib REAL,
    d_calib REAL,
    f_meas REAL,
    temperature REAL,
    material TEXT,
    embouchure TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Создаем таблицу tubes
cursor.execute('''
CREATE TABLE IF NOT EXISTS tubes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    material TEXT,
    length REAL DEFAULT 500.0,
    d_in REAL,
    d_out REAL,
    wall_thickness REAL,
    taper REAL DEFAULT 0.0,
    form TEXT DEFAULT 'round',
    roughness TEXT,
    v_air REAL DEFAULT 34300.0,
    v_eff REAL DEFAULT 34300.0,
    damping TEXT,
    f_tube REAL,
    L_total REAL,
    density REAL,
    thermal_coeff REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Создаем таблицу bells
cursor.execute('''
CREATE TABLE IF NOT EXISTS bells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'flare',
    material TEXT DEFAULT 'same',
    start_diameter REAL,
    end_diameter REAL,
    length REAL,
    wall_thickness REAL,
    expansion_ratio REAL,
    flare_angle REAL,
    delta_L REAL,
    acoustic_effect TEXT,
    profile TEXT,
    f_no_bell REAL,
    f_with_bell REAL,
    v_sound REAL DEFAULT 34300.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Создаем таблицу flutes
cursor.execute('''
CREATE TABLE IF NOT EXISTS flutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    key TEXT,
    scale TEXT,
    tube_length REAL,
    hole_count INTEGER DEFAULT 6,
    custom_notes TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mouthpiece_id INTEGER,
    tube_id INTEGER,
    bell_id INTEGER,
    holes_data TEXT DEFAULT '[]',
    total_effective_length REAL,
    base_frequency REAL,
    temperature REAL DEFAULT 20.0,
    FOREIGN KEY (mouthpiece_id) REFERENCES mouthpieces(id),
    FOREIGN KEY (tube_id) REFERENCES tubes(id),
    FOREIGN KEY (bell_id) REFERENCES bells(id)
)
''')

# Создаем таблицу holes
cursor.execute('''
CREATE TABLE IF NOT EXISTS holes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flute_id INTEGER NOT NULL,
    note TEXT,
    position REAL,
    diameter REAL,
    angle REAL DEFAULT 0,
    is_calibrated BOOLEAN DEFAULT FALSE,
    acoustic_length_correction REAL,
    is_under_cut BOOLEAN DEFAULT FALSE,
    chimney_height REAL,
    FOREIGN KEY (flute_id) REFERENCES flutes(id)
)
''')

# Создаем таблицу calibration_data
cursor.execute('''
CREATE TABLE IF NOT EXISTS calibration_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note TEXT NOT NULL,
    frequency REAL,
    position REAL NOT NULL,
    diameter REAL DEFAULT 8.0,
    tube_diameter REAL,
    tube_length REAL,
    tube_material TEXT,
    mouthpiece_delta_m REAL,
    mouthpiece_type TEXT,
    bell_delta_L REAL,
    temperature REAL DEFAULT 20.0,
    humidity REAL,
    pressure REAL,
    source TEXT DEFAULT 'user',
    confidence REAL DEFAULT 1.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

print("✅ Таблицы созданы")

# Добавляем тестовые данные
print("📝 Добавляем тестовые данные...")

# Тестовые мундштуки
cursor.execute('''
INSERT INTO mouthpieces (name, type, brand, d_tip, d_out, L_m, delta_m, material, embouchure)
VALUES 
    ('Тестовый кларнетный мундштук', 'clarinet', 'Yamaha', 13.5, 14.7, 75.0, 68.0, 'ebonite', 'rounded'),
    ('Альт саксофонный мундштук', 'alto_sax', 'Selmer', 16.5, 17.5, 85.0, 72.0, 'metal', 'flat')
''')

# Тестовые трубки
cursor.execute('''
INSERT INTO tubes (name, material, d_in, d_out, wall_thickness, v_eff, roughness)
VALUES 
    ('Алюминиевая трубка 20мм', 'aluminum', 20.0, 22.0, 1.0, 33500.0, 'smooth'),
    ('PVC трубка 20мм', 'pvc', 20.0, 22.0, 1.0, 29000.0, 'medium')
''')

# Тестовые раструбы
cursor.execute('''
INSERT INTO bells (name, type, material, start_diameter, end_diameter, length, wall_thickness, expansion_ratio, flare_angle, delta_L, acoustic_effect)
VALUES 
    ('Малый металлический раструб', 'flare', 'metal', 28.0, 80.0, 150.0, 0.5, 2.86, 15.0, -12.5, 'medium')
''')

# Тестовые калибровочные данные
cursor.execute('''
INSERT INTO calibration_data (note, frequency, position, diameter, tube_diameter, tube_length, tube_material, mouthpiece_delta_m, mouthpiece_type, bell_delta_L, source, confidence, notes)
VALUES 
    ('D4', 293.66, 225.0, 8.0, 20.0, 450.0, 'aluminum', 68.0, 'clarinet', -12.5, 'test', 0.9, 'Тестовые данные'),
    ('E4', 329.63, 202.5, 8.0, 20.0, 450.0, 'aluminum', 68.0, 'clarinet', -12.5, 'test', 0.9, 'Тестовые данные')
''')

conn.commit()
conn.close()

print("✅ Тестовые данные добавлены")

print("\n📊 ПРОВЕРКА БАЗЫ ДАННЫХ:")
print("-" * 40)

# Проверяем созданные таблицы
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Таблицы в базе:")
for table in tables:
    print(f"  • {table[0]}")

# Считаем записи
for table_name in ['mouthpieces', 'tubes', 'bells', 'calibration_data']:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count} записей")

conn.close()

print("\n" + "=" * 60)
print("🎉 База данных успешно создана!")
print("=" * 60)
print("\nТеперь запустите сервер: python run.py")