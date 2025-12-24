"""
Модели базы данных WITG с акустическими параметрами
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Mouthpiece(db.Model):
    """Мундштук с акустическими параметрами"""
    __tablename__ = 'mouthpieces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    
    # Геометрические параметры (без inner_diameter!)
    d_tip = db.Column(db.Float)  # Диаметр у трости (мм)
    d_out = db.Column(db.Float)  # Диаметр выхода (мм)
    L_m = db.Column(db.Float)    # Длина акустического конуса (мм)
    L_cyl = db.Column(db.Float)  # Длина цилиндрической части (мм)
    baffle = db.Column(db.String(50))
    chamber_depth = db.Column(db.Float)
    
    # Акустические измерения
    delta_m = db.Column(db.Float)  # Энд-коррекция (мм)
    
    # Данные для калибровки
    L_calib = db.Column(db.Float)
    d_calib = db.Column(db.Float)
    f_meas = db.Column(db.Float)
    temperature = db.Column(db.Float)
    
    # Дополнительные параметры
    material = db.Column(db.String(50))
    embouchure = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'brand': self.brand,
            'model': self.model,
            'd_tip': self.d_tip,
            'd_out': self.d_out,
            'L_m': self.L_m,
            'L_cyl': self.L_cyl,
            'baffle': self.baffle,
            'chamber_depth': self.chamber_depth,
            'delta_m': self.delta_m,
            'L_calib': self.L_calib,
            'd_calib': self.d_calib,
            'f_meas': self.f_meas,
            'temperature': self.temperature,
            'material': self.material,
            'embouchure': self.embouchure,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
class Tube(db.Model):
    """Трубка (основная часть) с акустическими параметрами"""
    __tablename__ = 'tubes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    material = db.Column(db.String(50))  # aluminum, steel, bronze, brass, pp, petg, glass, wood, rubber, pvc, carbon, copper, acrylic, bamboo
    
    # Геометрические параметры
    length = db.Column(db.Float, default=500.0)  # Стандартная длина (мм)
    d_in = db.Column(db.Float)  # Внутренний диаметр (мм) - ГЛАВНЫЙ ПАРАМЕТР!
    d_out = db.Column(db.Float)  # Внешний диаметр (мм)
    wall_thickness = db.Column(db.Float)  # Толщина стенки: (d_out - d_in)/2
    taper = db.Column(db.Float, default=0.0)  # Конусность (мм/мм)
    form = db.Column(db.String(50))  # round, oval, rectangular
    roughness = db.Column(db.String(50))  # very_smooth, smooth, medium, rough, very_rough
    
    # Акустические параметры
    v_air = db.Column(db.Float, default=34300.0)  # Скорость звука в воздухе при 20°C (см/с)
    v_eff = db.Column(db.Float, default=34300.0)  # Эффективная скорость звука в трубке (см/с)
    damping = db.Column(db.String(50))  # high, medium, low - Добротность
    
    # Данные для калибровки скорости звука
    f_tube = db.Column(db.Float)  # Частота собственного тона (Гц)
    L_total = db.Column(db.Float)  # Длина при измерении (мм)
    
    # Справочные данные материалов
    density = db.Column(db.Float)  # Плотность материала (г/см³)
    thermal_coeff = db.Column(db.Float)  # Температурный коэффициент (мм/°C)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'material': self.material,
            
            # Геометрические параметры
            'length': self.length,
            'd_in': self.d_in,
            'd_out': self.d_out,
            'wall_thickness': self.wall_thickness,
            'taper': self.taper,
            'form': self.form,
            'roughness': self.roughness,
            
            # Акустические параметры
            'v_air': self.v_air,
            'v_eff': self.v_eff,
            'damping': self.damping,
            
            # Данные калибровки
            'f_tube': self.f_tube,
            'L_total': self.L_total,
            
            # Справочные данные
            'density': self.density,
            'thermal_coeff': self.thermal_coeff,
            
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Bell(db.Model):
    """Раструб (может отсутствовать) с акустическими параметрами"""
    __tablename__ = 'bells'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), default='flare')  # flare, straight, none, exponential, parabolic, step, trumpet, flute
    material = db.Column(db.String(50))  # same, metal, brass, plastic, wood, acrylic
    
    # Геометрические параметры
    start_diameter = db.Column(db.Float)  # Диаметр входа (d_bell_in) (мм)
    end_diameter = db.Column(db.Float)    # Диаметр выхода (d_bell_out) (мм)
    length = db.Column(db.Float)          # Длина раструба (L_bell) (мм)
    wall_thickness = db.Column(db.Float)  # Толщина стенки (мм)
    expansion_ratio = db.Column(db.Float) # Коэффициент расширения: d_out/d_in
    flare_angle = db.Column(db.Float)     # Угол раскрытия (°)
    
    # Акустические параметры
    delta_L = db.Column(db.Float)         # Эффективная добавленная длина (ΔL_bell) (мм)
    acoustic_effect = db.Column(db.String(50))  # strong, medium, weak, none
    
    # Профиль кривой
    profile = db.Column(db.Text)          # Измеренные диаметры по длине
    
    # Данные для калибровки
    f_no_bell = db.Column(db.Float)      # Частота без раструба (f_no_bell)
    f_with_bell = db.Column(db.Float)    # Частота с раструбом (f_with_bell)
    v_sound = db.Column(db.Float, default=34300.0)  # Скорость звука при калибровке (см/с)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'material': self.material,
            
            # Геометрические параметры
            'start_diameter': self.start_diameter,
            'end_diameter': self.end_diameter,
            'length': self.length,
            'wall_thickness': self.wall_thickness,
            'expansion_ratio': self.expansion_ratio,
            'flare_angle': self.flare_angle,
            
            # Акустические параметры
            'delta_L': self.delta_L,
            'acoustic_effect': self.acoustic_effect,
            
            # Профиль
            'profile': self.profile,
            
            # Данные калибровки
            'f_no_bell': self.f_no_bell,
            'f_with_bell': self.f_with_bell,
            'v_sound': self.v_sound,
            
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Flute(db.Model):
    """Полная конфигурация флейты (дудикса)"""
    __tablename__ = 'flutes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(10))      # C, D, E, F, G, A, B
    scale = db.Column(db.String(50))    # major, minor, blues, custom, dorian, phrygian, etc.
    tube_length = db.Column(db.Float)   # общая длина трубки (мм)
    hole_count = db.Column(db.Integer, default=6)
    custom_notes = db.Column(db.Text)   # пользовательские ноты для кастомного строя
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Компоненты
    mouthpiece_id = db.Column(db.Integer, db.ForeignKey('mouthpieces.id'))
    tube_id = db.Column(db.Integer, db.ForeignKey('tubes.id'))
    bell_id = db.Column(db.Integer, db.ForeignKey('bells.id'))
    
    # Калибровочные данные отверстий (JSON)
    holes_data = db.Column(db.Text, default='[]')
    
    # Акустические параметры всей системы
    total_effective_length = db.Column(db.Float)  # L_eff_total = L_tube + 2*δ_m + ΔL_bell
    base_frequency = db.Column(db.Float)  # f_base = v / (2 * L_eff_total)
    temperature = db.Column(db.Float, default=20.0)  # Температура при создании
    
    # Связи
    mouthpiece = db.relationship('Mouthpiece', backref='flutes')
    tube = db.relationship('Tube', backref='flutes')
    bell = db.relationship('Bell', backref='flutes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
            'scale': self.scale,
            'tube_length': self.tube_length,
            'hole_count': self.hole_count,
            'custom_notes': json.loads(self.custom_notes) if self.custom_notes else [],
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            
            # Компоненты
            'mouthpiece': self.mouthpiece.to_dict() if self.mouthpiece else None,
            'tube': self.tube.to_dict() if self.tube else None,
            'bell': self.bell.to_dict() if self.bell else None,
            
            # Отверстия
            'holes': json.loads(self.holes_data) if self.holes_data else [],
            
            # Акустические параметры
            'total_effective_length': self.total_effective_length,
            'base_frequency': self.base_frequency,
            'temperature': self.temperature
        }


class Hole(db.Model):
    """Отдельное отверстие (для сложных конфигураций)"""
    __tablename__ = 'holes'
    
    id = db.Column(db.Integer, primary_key=True)
    flute_id = db.Column(db.Integer, db.ForeignKey('flutes.id'), nullable=False)
    note = db.Column(db.String(10))        # D4, E4, F4, etc.
    position = db.Column(db.Float)         # позиция от мундштука (мм)
    diameter = db.Column(db.Float)         # диаметр отверстия (мм)
    angle = db.Column(db.Float, default=0) # угол (градусы)
    is_calibrated = db.Column(db.Boolean, default=False)
    
    # Акустические параметры отверстия
    acoustic_length_correction = db.Column(db.Float)  # Поправка на энд-эффект отверстия
    is_under_cut = db.Column(db.Boolean, default=False)  # Подрезка отверстия
    chimney_height = db.Column(db.Float)  # Высота дымохода (если есть)
    
    def to_dict(self):
        return {
            'id': self.id,
            'flute_id': self.flute_id,
            'note': self.note,
            'position': self.position,
            'diameter': self.diameter,
            'angle': self.angle,
            'is_calibrated': self.is_calibrated,
            'acoustic_length_correction': self.acoustic_length_correction,
            'is_under_cut': self.is_under_cut,
            'chimney_height': self.chimney_height
        }


class CalibrationData(db.Model):
    """База проверенных калибровочных данных"""
    __tablename__ = 'calibration_data'
    
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(10), nullable=False)  # D4, E4, F4, etc.
    frequency = db.Column(db.Float)  # Измеренная частота (Гц)
    position = db.Column(db.Float)   # Позиция отверстия (мм)
    diameter = db.Column(db.Float)   # Диаметр отверстия (мм)
    
    # Параметры трубки при калибровке
    tube_diameter = db.Column(db.Float)  # d_in трубки (мм)
    tube_length = db.Column(db.Float)    # Общая длина трубки (мм)
    tube_material = db.Column(db.String(50))
    
    # Параметры мундштука при калибровке
    mouthpiece_delta_m = db.Column(db.Float)  # δ_m мундштука (мм)
    mouthpiece_type = db.Column(db.String(50))
    
    # Параметры раструба при калибровке
    bell_delta_L = db.Column(db.Float)  # ΔL_bell раструба (мм)
    
    # Условия измерения
    temperature = db.Column(db.Float, default=20.0)  # Температура (°C)
    humidity = db.Column(db.Float)  # Влажность (%)
    pressure = db.Column(db.Float)  # Давление (гПа)
    
    # Метаданные
    source = db.Column(db.String(100))  # Кто/что измерил
    confidence = db.Column(db.Float, default=1.0)  # Достоверность (0-1)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'note': self.note,
            'frequency': self.frequency,
            'position': self.position,
            'diameter': self.diameter,
            
            'tube_diameter': self.tube_diameter,
            'tube_length': self.tube_length,
            'tube_material': self.tube_material,
            
            'mouthpiece_delta_m': self.mouthpiece_delta_m,
            'mouthpiece_type': self.mouthpiece_type,
            
            'bell_delta_L': self.bell_delta_L,
            
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            
            'source': self.source,
            'confidence': self.confidence,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }