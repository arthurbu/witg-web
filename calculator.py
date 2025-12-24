# calculator.py
"""
Модуль расчета позиций отверстий для WITG
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class DudexCalculator:
    """Калькулятор для расчета позиций отверстий дудикса"""
    
    def __init__(self):
        # Базовые константы для расчета
        self.speed_of_sound = 343.0  # м/с при 20°C
        self.note_frequencies = self._generate_note_frequencies()
        
        # Коэффициенты для разных материалов
        self.material_coefficients = {
            'pvc': 1.0,
            'bamboo': 0.95,
            'metal': 1.1,
            'wood': 0.98,
            'carbon': 1.05
        }
        
        # База проверенных данных
        self.calibrated_data = self._load_calibrated_data()
    
    def _generate_note_frequencies(self) -> Dict[str, float]:
        """Генерирует частоты для всех нот всех октав"""
        frequencies = {}
        
        # Стандартная частота A4 = 440 Гц
        a4_freq = 440.0
        
        for octave in range(1, 6):
            # Ноты в октаве
            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            for i, note in enumerate(notes):
                # Формула для расчета частоты ноты
                # Расстояние от A4 в полутонах
                a4_index = 9 + 12 * (4 - 4)  # A4 находится на 9 позиции в 4 октаве
                current_index = i + 12 * (octave - 4)
                semitone_distance = current_index - a4_index
                
                frequency = a4_freq * (2 ** (semitone_distance / 12))
                note_name = f"{note}{octave}"
                frequencies[note_name] = round(frequency, 2)
        
        return frequencies
    
    def _load_calibrated_data(self) -> List[Dict]:
        """Загружает проверенные данные из базы"""
        # Пока заглушка - в реальности будет загружаться из БД
        return [
            {
                "note": "D4",
                "position": 225.0,
                "tube_diameter": 20.0,
                "tube_length": 450.0,
                "material": "pvc",
                "is_verified": True,
                "created_at": "2024-01-01"
            },
            {
                "note": "E4",
                "position": 202.5,
                "tube_diameter": 20.0,
                "tube_length": 450.0,
                "material": "pvc",
                "is_verified": True,
                "created_at": "2024-01-01"
            }
        ]
    
    def calculate_hole_positions(
        self,
        notes: List[str],
        tube_length: float,
        tube_diameter: float,
        tube_material: str = "pvc",
        mouthpiece_end_correction: float = 15.0,
        temperature: float = 20.0
    ) -> Dict[str, Dict]:
        """
        Рассчитывает позиции отверстий для заданных нот
        
        Args:
            notes: Список нот (например ["D4", "E4", "F#4"])
            tube_length: Длина трубки в мм
            tube_diameter: Диаметр трубки в мм
            tube_material: Материал трубки
            mouthpiece_end_correction: Энд-коррекция мундштука в мм
            temperature: Температура воздуха в °C
        
        Returns:
            Словарь с расчетами для каждой ноты
        """
        results = {}
        
        # Корректировка скорости звука на температуру
        speed_of_sound = self.speed_of_sound * math.sqrt(1 + (temperature - 20) / 273)
        
        # Коэффициент материала
        material_coef = self.material_coefficients.get(tube_material, 1.0)
        
        for note in notes:
            if note not in self.note_frequencies:
                print(f"⚠️  Неизвестная нота: {note}")
                continue
            
            frequency = self.note_frequencies[note]
            
            # Ищем проверенные данные
            calibrated_result = self._find_calibrated_data(
                note, tube_diameter, tube_length, tube_material
            )
            
            if calibrated_result:
                # Используем проверенные данные
                results[note] = {
                    "position": calibrated_result["position"],
                    "diameter": 8.0,  # стандартный диаметр отверстия
                    "source": "calibrated",
                    "confidence": 1.0,
                    "calibrated_id": calibrated_result.get("id"),
                    "note": note,
                    "is_verified": True
                }
            else:
                # Расчетная формула для открытой трубки
                # Длина волны = скорость звука / частота
                wavelength = (speed_of_sound * 1000) / frequency  # в мм
                
                # Для открытой трубки основная частота: L = λ/2
                # С учетом энд-коррекции
                theoretical_length = wavelength / 2 - mouthpiece_end_correction
                
                # Адаптация для конкретного диаметра
                diameter_factor = tube_diameter / 20.0  # нормализация к 20мм
                
                # Эмпирическая корректировка
                position = theoretical_length * (1 - 0.1 * math.log(diameter_factor))
                
                # Ограничение длиной трубки
                position = min(position, tube_length * 0.9)
                position = max(position, tube_length * 0.1)
                
                results[note] = {
                    "position": round(position, 1),
                    "diameter": 8.0,
                    "source": "calculated",
                    "confidence": 0.7,
                    "note": note,
                    "is_verified": False,
                    "formula_used": "open_tube_wavelength"
                }
        
        # Сортировка по позиции (от мундштука к концу)
        sorted_results = dict(sorted(
            results.items(),
            key=lambda x: x[1]["position"]
        ))
        
        return sorted_results
    
    def _find_calibrated_data(
        self,
        note: str,
        tube_diameter: float,
        tube_length: float,
        tube_material: str
    ) -> Optional[Dict]:
        """
        Ищет проверенные данные для похожей конфигурации
        """
        for data in self.calibrated_data:
            if data["note"] != note:
                continue
            
            # Проверяем схожесть параметров
            diameter_diff = abs(data["tube_diameter"] - tube_diameter) / tube_diameter
            length_diff = abs(data["tube_length"] - tube_length) / tube_length
            
            if (diameter_diff < 0.1 and  # до 10% разницы в диаметре
                length_diff < 0.1 and    # до 10% разницы в длине
                data["material"] == tube_material and
                data["is_verified"]):
                
                return {
                    "id": data.get("id"),
                    "position": data["position"],
                    "diameter_diff": diameter_diff,
                    "length_diff": length_diff
                }
        
        return None
    
    def calculate_single_note(
        self,
        note: str,
        tube_length: float,
        tube_diameter: float,
        **kwargs
    ) -> Dict:
        """Рассчитывает позицию для одной ноты"""
        return self.calculate_hole_positions(
            [note],
            tube_length,
            tube_diameter,
            **kwargs
        ).get(note, {})
    
    def add_calibrated_data(
        self,
        note: str,
        position: float,
        tube_diameter: float,
        tube_length: float,
        tube_material: str = "pvc"
    ) -> bool:
        """Добавляет проверенные данные в базу"""
        new_data = {
            "note": note,
            "position": position,
            "tube_diameter": tube_diameter,
            "tube_length": tube_length,
            "material": tube_material,
            "is_verified": True,
            "created_at": datetime.now().isoformat()
        }
        
        self.calibrated_data.append(new_data)
        return True
    
    def get_similar_calibrations(
        self,
        note: str,
        tube_diameter: float,
        tube_length: float,
        threshold: float = 0.15
    ) -> List[Dict]:
        """Находит похожие проверенные конфигурации"""
        similar = []
        
        for data in self.calibrated_data:
            if data["note"] != note or not data["is_verified"]:
                continue
            
            diameter_diff = abs(data["tube_diameter"] - tube_diameter) / tube_diameter
            length_diff = abs(data["tube_length"] - tube_length) / tube_length
            
            if diameter_diff < threshold and length_diff < threshold:
                similarity = 1.0 - max(diameter_diff, length_diff) / threshold
                similar.append({
                    **data,
                    "similarity": round(similarity, 2)
                })
        
        # Сортируем по схожести
        return sorted(similar, key=lambda x: x["similarity"], reverse=True)
    
    def get_note_info(self, note: str) -> Dict:
        """Возвращает информацию о ноте"""
        return {
            "note": note,
            "frequency": self.note_frequencies.get(note),
            "octave": int(''.join(filter(str.isdigit, note))) if any(c.isdigit() for c in note) else None,
            "note_name": ''.join(filter(str.isalpha, note))
        }


# Синглтон экземпляр калькулятора
_calculator_instance = None

def get_calculator() -> DudexCalculator:
    """Возвращает экземпляр калькулятора"""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = DudexCalculator()
    return _calculator_instance


# API функции для использования из других модулей
def calculate_positions_api(
    notes: List[str],
    tube_length: float,
    tube_diameter: float,
    tube_material: str = "pvc",
    mouthpiece_end_correction: float = 15.0
) -> Dict:
    """API функция для расчета позиций"""
    calculator = get_calculator()
    return calculator.calculate_hole_positions(
        notes=notes,
        tube_length=tube_length,
        tube_diameter=tube_diameter,
        tube_material=tube_material,
        mouthpiece_end_correction=mouthpiece_end_correction
    )


def add_calibration_api(
    note: str,
    position: float,
    tube_diameter: float,
    tube_length: float,
    tube_material: str = "pvc"
) -> Dict:
    """API функция для добавления калибровочных данных"""
    calculator = get_calculator()
    success = calculator.add_calibrated_data(
        note=note,
        position=position,
        tube_diameter=tube_diameter,
        tube_length=tube_length,
        tube_material=tube_material
    )
    
    return {
        "success": success,
        "message": "Калибровочные данные добавлены" if success else "Ошибка добавления"
    }


def get_similar_calibrations_api(
    note: str,
    tube_diameter: float,
    tube_length: float
) -> Dict:
    """API функция для поиска похожих калибровок"""
    calculator = get_calculator()
    similar = calculator.get_similar_calibrations(
        note=note,
        tube_diameter=tube_diameter,
        tube_length=tube_length
    )
    
    return {
        "note": note,
        "similar_calibrations": similar,
        "count": len(similar)
    }