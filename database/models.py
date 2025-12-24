"""
Модели базы данных WITG
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Mouthpiece(db.Model):
    """Мундштук"""
    __tablename__ = 'mouthpieces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # clarinet, sax, native, flute
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    inner_diameter = db.Column(db.Float)  # ID в мм
    outer_diameter = db.Column(db.Float)  # OD в мм
    length = db.Column(db.Float)  # длина в мм
    end_correction = db.Column(db.Float)  # энд-коррекция в мм
    embouchure = db.Column(db.String(50))  # rounded, flat, v-shaped
    material = db.Column(db.String(50))  # plastic, ebonite, metal, wood
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'brand': self.brand,
            'model': self.model,
            'inner_diameter': self.inner_diameter,
            'outer_diameter': self.outer_diameter,
            'length': self.length,
            'end_correction': self.end_correction,
            'embouchure': self.embouchure,
            'material': self.material
        }


class Tube(db.Model):
    """Трубка (основная часть)"""
    __tablename__ = 'tubes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    material = db.Column(db.String(50))  # pvc, bamboo, metal, wood, carbon
    form = db.Column(db.String(50))  # round, oval, rectangular
    inner_diameter = db.Column(db.Float, nullable=False)  # ID в мм
    outer_diameter = db.Column(db.Float, nullable=False)  # OD в мм
    wall_thickness = db.Column(db.Float)  # толщина стенки
    expansion = db.Column(db.Float, default=1.0)  # коэффициент расширения
    standard_length = db.Column(db.Float, default=500.0)  # стандартная длина
    density = db.Column(db.Float)  # плотность материала г/см³
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'material': self.material,
            'form': self.form,
            'inner_diameter': self.inner_diameter,
            'outer_diameter': self.outer_diameter,
            'wall_thickness': self.wall_thickness,
            'expansion': self.expansion,
            'standard_length': self.standard_length,
            'density': self.density
        }


class Bell(db.Model):
    """Раструб (может отсутствовать)"""
    __tablename__ = 'bells'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), default='flare')  # flare, straight, none, exponential
    material = db.Column(db.String(50))  # same, metal, plastic, wood
    start_diameter = db.Column(db.Float)  # диаметр в начале (мм)
    end_diameter = db.Column(db.Float)    # диаметр в конце (мм)
    length = db.Column(db.Float)          # длина раструба (мм)
    expansion_ratio = db.Column(db.Float) # коэффициент расширения
    flare_angle = db.Column(db.Float)     # угол раскрытия в градусах
    wall_thickness = db.Column(db.Float)  # толщина стенки
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'material': self.material,
            'start_diameter': self.start_diameter,
            'end_diameter': self.end_diameter,
            'length': self.length,
            'expansion_ratio': self.expansion_ratio,
            'flare_angle': self.flare_angle,
            'wall_thickness': self.wall_thickness
        }


class Flute(db.Model):
    """Полная конфигурация флейты"""
    __tablename__ = 'flutes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(10))      # C, D, E, F, G, A, B
    scale = db.Column(db.String(50))    # major, minor, blues, custom
    tube_length = db.Column(db.Float)   # длина трубки (мм)
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
            'mouthpiece': self.mouthpiece.to_dict() if self.mouthpiece else None,
            'tube': self.tube.to_dict() if self.tube else None,
            'bell': self.bell.to_dict() if self.bell else None,
            'holes': json.loads(self.holes_data) if self.holes_data else []
        }


class Hole(db.Model):
    """Отдельное отверстие (для сложных конфигураций)"""
    __tablename__ = 'holes'
    
    id = db.Column(db.Integer, primary_key=True)
    flute_id = db.Column(db.Integer, db.ForeignKey('flutes.id'), nullable=False)
    note = db.Column(db.String(10))        # D4, E4, F4
    position = db.Column(db.Float)         # позиция от мундштука (мм)
    diameter = db.Column(db.Float)         # диаметр отверстия (мм)
    angle = db.Column(db.Float, default=0) # угол (градусы)
    is_calibrated = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'flute_id': self.flute_id,
            'note': self.note,
            'position': self.position,
            'diameter': self.diameter,
            'angle': self.angle,
            'is_calibrated': self.is_calibrated
        }