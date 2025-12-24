"""
Веб-маршруты WITG с обновленными моделями
"""

from flask import render_template, jsonify, request, send_file
from io import BytesIO
import json
from datetime import datetime
import sys
import os

# Добавляем путь к корню проекта для корректных импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Импорты из нашей структуры
try:
    from database.models import db, Mouthpiece, Tube, Bell, Flute, Hole, CalibrationData
    MODELS_LOADED = True
    print("✅ Модели загружены успешно")
except ImportError as e:
    print(f"⚠️  Ошибка импорта моделей: {e}")
    MODELS_LOADED = False
    # Создаем заглушки
    db = None
    class Mouthpiece:
        @staticmethod
        def query(): return type('Query', (), {'all': lambda: [], 'count': lambda: 0, 'get': lambda x: None})()
    class Tube:
        @staticmethod
        def query(): return type('Query', (), {'all': lambda: [], 'count': lambda: 0, 'get': lambda x: None})()
    class Bell:
        @staticmethod
        def query(): return type('Query', (), {'all': lambda: [], 'count': lambda: 0, 'get': lambda x: None})()
    class Flute:
        @staticmethod
        def query(): 
            return type('Query', (), {
                'all': lambda: [], 'count': lambda: 0, 'get': lambda x: None,
                'filter_by': lambda **kwargs: type('Query', (), {
                    'count': lambda: 0, 'order_by': lambda x: type('Query', (), {'all': lambda: []})()
                })(),
                'get_or_404': lambda x: None
            })()
    class Hole:
        @staticmethod
        def query(): return type('Query', (), {'all': lambda: [], 'filter_by': lambda **kwargs: type('Query', (), {'all': lambda: []})()})()
    class CalibrationData:
        @staticmethod
        def query(): return type('Query', (), {'all': lambda: [], 'filter_by': lambda **kwargs: type('Query', (), {'all': lambda: []})()})()

# Пытаемся импортировать калькулятор
try:
    from calculator import calculate_positions_api
    CALCULATOR_LOADED = True
    print("✅ Калькулятор загружен успешно")
except ImportError as e:
    print(f"⚠️  Ошибка импорта калькулятора: {e}")
    CALCULATOR_LOADED = False

def register_routes(app):
    """Зарегистрировать все маршруты"""
    
    # ========== HTML СТРАНИЦЫ ==========
    
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/flute/<int:flute_id>')
    def view_flute(flute_id):
        return render_template('flute_view.html')
    
    @app.route('/manage-components')
    def manage_components():
        return render_template('manage_components.html')
    
    # ========== API ДЛЯ ДАННЫХ ==========
    
    @app.route('/api/flutes')
    def get_flutes():
        try:
            if not MODELS_LOADED:
                return jsonify({'count': 0, 'verified_count': 0, 'flutes': []})
            
            flutes = Flute.query.order_by(Flute.created_at.desc()).all()
            verified_count = Flute.query.filter_by(is_verified=True).count()
            
            return jsonify({
                'count': len(flutes),
                'verified_count': verified_count,
                'flutes': [f.to_dict() for f in flutes]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/flutes/<int:flute_id>')
    def get_flute(flute_id):
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            flute = Flute.query.get_or_404(flute_id)
            return jsonify(flute.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/flutes', methods=['POST'])
    def create_flute():
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            data = request.json
            
            if 'name' not in data:
                return jsonify({'error': 'Отсутствует название дудикса'}), 400
            
            if 'tube_id' not in data:
                return jsonify({'error': 'Не выбрана трубка'}), 400
            
            flute = Flute(
                name=data.get('name', 'Новый дудикс'),
                key=data.get('key', 'D'),
                scale=data.get('scale', 'minor'),
                tube_length=float(data.get('tube_length', 450.0)),
                hole_count=int(data.get('hole_count', 6)),
                mouthpiece_id=data.get('mouthpiece_id'),
                tube_id=data.get('tube_id'),
                bell_id=data.get('bell_id'),
                custom_notes=data.get('custom_notes', '[]'),
                holes_data=data.get('holes_data', '[]'),
                is_verified=data.get('is_verified', False),
                temperature=data.get('temperature', 20.0)
            )
            
            db.session.add(flute)
            db.session.commit()
            
            if data.get('holes_data') and data['holes_data'] != '[]':
                holes = json.loads(data['holes_data'])
                for hole_data in holes:
                    hole = Hole(
                        flute_id=flute.id,
                        note=hole_data.get('note'),
                        position=hole_data.get('position'),
                        diameter=hole_data.get('diameter', 8.0),
                        angle=hole_data.get('angle', 0),
                        is_calibrated=hole_data.get('is_calibrated', False),
                        acoustic_length_correction=hole_data.get('acoustic_length_correction'),
                        is_under_cut=hole_data.get('is_under_cut', False),
                        chimney_height=hole_data.get('chimney_height')
                    )
                    db.session.add(hole)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Дудикс создан',
                'flute': flute.to_dict()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/flutes/<int:flute_id>', methods=['DELETE'])
    def delete_flute(flute_id):
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            flute = Flute.query.get_or_404(flute_id)
            Hole.query.filter_by(flute_id=flute_id).delete()
            db.session.delete(flute)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Дудикс удален'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/flutes/<int:flute_id>', methods=['PUT'])
    def update_flute(flute_id):
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            flute = Flute.query.get_or_404(flute_id)
            data = request.json
            
            if 'name' in data:
                flute.name = data['name']
            if 'is_verified' in data:
                flute.is_verified = data['is_verified']
            if 'holes_data' in data:
                flute.holes_data = data['holes_data']
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Дудикс обновлен', 'flute': flute.to_dict()})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== API ДЛЯ КОМПОНЕНТОВ ==========
    
    @app.route('/api/mouthpieces')
    def get_mouthpieces():
        try:
            if not MODELS_LOADED:
                return jsonify({'count': 0, 'mouthpieces': []})
            
            mouthpieces = Mouthpiece.query.order_by(Mouthpiece.name).all()
            return jsonify({
                'count': len(mouthpieces),
                'mouthpieces': [mp.to_dict() for mp in mouthpieces]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tubes')
    def get_tubes():
        try:
            if not MODELS_LOADED:
                return jsonify({'count': 0, 'tubes': []})
            
            tubes = Tube.query.order_by(Tube.name).all()
            return jsonify({
                'count': len(tubes),
                'tubes': [t.to_dict() for t in tubes]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bells')
    def get_bells():
        try:
            if not MODELS_LOADED:
                return jsonify({'count': 0, 'bells': []})
            
            bells = Bell.query.order_by(Bell.name).all()
            return jsonify({
                'count': len(bells),
                'bells': [b.to_dict() for b in bells]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/mouthpieces', methods=['POST'])
    def create_mouthpiece():
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            data = request.json
            if 'name' not in data:
                return jsonify({'error': 'Отсутствует название'}), 400
            
            mouthpiece = Mouthpiece(
                name=data['name'],
                type=data.get('type'),
                brand=data.get('brand'),
                model=data.get('model'),
                d_tip=data.get('d_tip'),
                d_out=data.get('d_out'),
                L_m=data.get('L_m'),
                L_cyl=data.get('L_cyl'),
                baffle=data.get('baffle'),
                chamber_depth=data.get('chamber_depth'),
                delta_m=data.get('delta_m'),
                L_calib=data.get('L_calib'),
                d_calib=data.get('d_calib'),
                f_meas=data.get('f_meas'),
                temperature=data.get('temperature'),
                material=data.get('material'),
                embouchure=data.get('embouchure'),
                notes=data.get('notes')
            )
            
            db.session.add(mouthpiece)
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': 'Мундштук создан', 
                'mouthpiece': mouthpiece.to_dict()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/mouthpieces/<int:mp_id>', methods=['DELETE'])
    def delete_mouthpiece(mp_id):
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            mouthpiece = Mouthpiece.query.get_or_404(mp_id)
            db.session.delete(mouthpiece)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Мундштук удален'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tubes', methods=['POST'])
    def create_tube():
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            data = request.json
            if 'name' not in data:
                return jsonify({'error': 'Отсутствует название'}), 400
            if 'd_in' not in data:
                return jsonify({'error': 'Отсутствует внутренний диаметр'}), 400
            
            tube = Tube(
                name=data['name'],
                material=data.get('material'),
                length=data.get('length', 500.0),
                d_in=data['d_in'],
                d_out=data.get('d_out'),
                wall_thickness=data.get('wall_thickness'),
                taper=data.get('taper', 0.0),
                form=data.get('form', 'round'),
                roughness=data.get('roughness'),
                v_air=data.get('v_air', 34300.0),
                v_eff=data.get('v_eff', 34300.0),
                damping=data.get('damping'),
                f_tube=data.get('f_tube'),
                L_total=data.get('L_total'),
                density=data.get('density'),
                thermal_coeff=data.get('thermal_coeff')
            )
            
            db.session.add(tube)
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': 'Трубка создана', 
                'tube': tube.to_dict()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tubes/<int:tube_id>', methods=['DELETE'])
    def delete_tube(tube_id):
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            tube = Tube.query.get_or_404(tube_id)
            db.session.delete(tube)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Трубка удалена'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bells', methods=['POST'])
    def create_bell():
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            data = request.json
            if 'name' not in data:
                return jsonify({'error': 'Отсутствует название'}), 400
            
            bell = Bell(
                name=data['name'],
                type=data.get('type', 'flare'),
                material=data.get('material', 'same'),
                start_diameter=data.get('start_diameter'),
                end_diameter=data.get('end_diameter'),
                length=data.get('length'),
                wall_thickness=data.get('wall_thickness'),
                expansion_ratio=data.get('expansion_ratio'),
                flare_angle=data.get('flare_angle'),
                delta_L=data.get('delta_L'),
                acoustic_effect=data.get('acoustic_effect'),
                profile=data.get('profile'),
                f_no_bell=data.get('f_no_bell'),
                f_with_bell=data.get('f_with_bell'),
                v_sound=data.get('v_sound', 34300.0)
            )
            
            db.session.add(bell)
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': 'Раструб создан', 
                'bell': bell.to_dict()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bells/<int:bell_id>', methods=['DELETE'])
    def delete_bell(bell_id):
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            bell = Bell.query.get_or_404(bell_id)
            db.session.delete(bell)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Раструб удален'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== API ДЛЯ КАЛИБРАЦИОННЫХ ДАННЫХ ==========
    
    @app.route('/api/calibration', methods=['POST'])
    def add_calibration():
        try:
            if not MODELS_LOADED:
                return jsonify({'error': 'Модели не загружены'}), 500
            
            data = request.json
            
            if 'note' not in data or 'position' not in data:
                return jsonify({'error': 'Отсутствует нота или позиция'}), 400
            
            calibration = CalibrationData(
                note=data['note'],
                frequency=data.get('frequency'),
                position=data['position'],
                diameter=data.get('diameter', 8.0),
                tube_diameter=data.get('tube_diameter'),
                tube_length=data.get('tube_length'),
                tube_material=data.get('tube_material'),
                mouthpiece_delta_m=data.get('mouthpiece_delta_m'),
                mouthpiece_type=data.get('mouthpiece_type'),
                bell_delta_L=data.get('bell_delta_L'),
                temperature=data.get('temperature', 20.0),
                humidity=data.get('humidity'),
                pressure=data.get('pressure'),
                source=data.get('source', 'user'),
                confidence=data.get('confidence', 1.0),
                notes=data.get('notes')
            )
            
            db.session.add(calibration)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Калибровочные данные добавлены',
                'calibration': calibration.to_dict()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/calibration/<note>')
    def get_calibrations(note):
        try:
            if not MODELS_LOADED:
                return jsonify({'calibrations': [], 'count': 0})
            
            calibrations = CalibrationData.query.filter_by(note=note).all()
            return jsonify({
                'note': note,
                'calibrations': [c.to_dict() for c in calibrations],
                'count': len(calibrations)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/calibration/similar')
    def get_similar_calibrations():
        try:
            if not MODELS_LOADED:
                return jsonify({'calibrations': [], 'count': 0})
            
            tube_diameter = float(request.args.get('diameter', 20.0))
            tube_length = float(request.args.get('length', 450.0))
            note = request.args.get('note', '')
            tolerance = float(request.args.get('tolerance', 0.1))  # 10%
            
            # Получаем все калибровки для данной ноты
            calibrations = CalibrationData.query.filter_by(note=note).all()
            
            # Фильтруем по схожести параметров
            similar = []
            for cal in calibrations:
                if cal.tube_diameter and cal.tube_length:
                    diameter_diff = abs(cal.tube_diameter - tube_diameter) / tube_diameter
                    length_diff = abs(cal.tube_length - tube_length) / tube_length
                    
                    if diameter_diff <= tolerance and length_diff <= tolerance:
                        similarity = 1.0 - max(diameter_diff, length_diff) / tolerance
                        cal_dict = cal.to_dict()
                        cal_dict['similarity'] = round(similarity, 2)
                        similar.append(cal_dict)
            
            # Сортируем по схожести
            similar.sort(key=lambda x: x['similarity'], reverse=True)
            
            return jsonify({
                'note': note,
                'tube_diameter': tube_diameter,
                'tube_length': tube_length,
                'calibrations': similar,
                'count': len(similar)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== РАСЧЕТ ОТВЕРСТИЙ (СТАРЫЙ) ==========
    
    @app.route('/api/calculate', methods=['POST'])
    def calculate_holes():
        try:
            data = request.json
            tube_length = float(data.get('tube_length', 450.0))
            key = data.get('key', 'D')
            hole_count = int(data.get('hole_count', 6))
            
            base_ratios = {
                'C': [0.65, 0.58, 0.51, 0.44, 0.37, 0.30],
                'D': [0.60, 0.54, 0.48, 0.42, 0.36, 0.30],
                'E': [0.56, 0.50, 0.44, 0.38, 0.32, 0.26],
                'F': [0.53, 0.47, 0.41, 0.35, 0.29, 0.23],
                'G': [0.50, 0.44, 0.38, 0.32, 0.26, 0.20],
                'A': [0.47, 0.41, 0.35, 0.29, 0.23, 0.17],
                'B': [0.44, 0.38, 0.32, 0.26, 0.20, 0.14]
            }
            
            ratios = base_ratios.get(key, base_ratios['D'])
            
            holes = []
            for i in range(min(hole_count, 6)):
                position = tube_length * ratios[i]
                notes = {
                    'C': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4'],
                    'D': ['D4', 'E4', 'F#4', 'G4', 'A4', 'B4'],
                    'E': ['E4', 'F#4', 'G#4', 'A4', 'B4', 'C#5'],
                    'F': ['F4', 'G4', 'A4', 'A#4', 'C5', 'D5'],
                    'G': ['G4', 'A4', 'B4', 'C5', 'D5', 'E5'],
                    'A': ['A4', 'B4', 'C#5', 'D5', 'E5', 'F#5'],
                    'B': ['B4', 'C#5', 'D#5', 'E5', 'F#5', 'G#5']
                }
                
                note = notes.get(key, notes['D'])[i] if i < len(notes.get(key, [])) else f'Note{i+1}'
                
                holes.append({
                    'id': i + 1,
                    'note': note,
                    'position': round(position, 1),
                    'diameter': 8.0,
                    'angle': (i * 60) % 360,
                    'is_calibrated': False
                })
            
            return jsonify({'success': True, 'holes': holes})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== НОВЫЕ МАРШРУТЫ ДЛЯ КАЛЬКУЛЯТОРА ==========
    
    @app.route('/api/calculate/advanced', methods=['POST'])
    def calculate_advanced():
        """Расчет позиций через калькулятор с учетом компонентов"""
        try:
            data = request.json
            
            if 'notes' not in data:
                return jsonify({'error': 'Отсутствует список нот'}), 400
            if 'tube_length' not in data:
                return jsonify({'error': 'Отсутствует длина трубки'}), 400
            if 'tube_diameter' not in data:
                return jsonify({'error': 'Отсутствует диаметр трубки'}), 400
            
            notes = data['notes']
            tube_length = float(data['tube_length'])
            tube_diameter = float(data['tube_diameter'])
            tube_material = data.get('tube_material', 'pvc')
            
            # Получаем параметры компонентов если они указаны
            mouthpiece_delta_m = data.get('mouthpiece_delta_m')
            bell_delta_L = data.get('bell_delta_L')
            
            # Проверяем, есть ли калькулятор
            if CALCULATOR_LOADED:
                try:
                    # Используем калькулятор
                    results = calculate_positions_api(
                        notes=notes,
                        tube_length=tube_length,
                        tube_diameter=tube_diameter,
                        tube_material=tube_material,
                        mouthpiece_end_correction=float(data.get('mouthpiece_end_correction', 15.0))
                    )
                    
                    holes = []
                    for note, calculation in results.items():
                        holes.append({
                            'note': note,
                            'position': calculation['position'],
                            'diameter': calculation.get('diameter', 8.0),
                            'source': calculation['source'],
                            'is_verified': calculation.get('is_verified', False),
                            'confidence': calculation.get('confidence', 0.0),
                            'calculated_value': calculation['position']
                        })
                    
                    calibrated_count = len([h for h in holes if h['source'] == 'calibrated'])
                    calculated_count = len([h for h in holes if h['source'] == 'calculated'])
                    
                    return jsonify({
                        'success': True,
                        'holes': holes,
                        'calculated_count': calculated_count,
                        'calibrated_count': calibrated_count,
                        'message': 'Расчет выполнен (калькулятор)'
                    })
                except Exception as calc_error:
                    print(f"Ошибка в калькуляторе: {calc_error}")
                    # Если калькулятор не работает, используем простой метод
                    return calculate_advanced_simple(notes, tube_length, tube_diameter, tube_material)
            else:
                # Используем простой расчет
                return calculate_advanced_simple(notes, tube_length, tube_diameter, tube_material)
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def calculate_advanced_simple(notes, tube_length, tube_diameter, tube_material):
        """Простой расчет позиций без калькулятора"""
        try:
            holes = []
            for i, note in enumerate(notes[:12]):
                base_ratios = {
                    'C': 0.65, 'C#': 0.62, 'D': 0.60, 'D#': 0.57,
                    'E': 0.55, 'F': 0.52, 'F#': 0.50, 'G': 0.47,
                    'G#': 0.45, 'A': 0.42, 'A#': 0.40, 'B': 0.38
                }
                
                note_name = ''.join([c for c in note if not c.isdigit()])
                octave = int(''.join([c for c in note if c.isdigit()])) if any(c.isdigit() for c in note) else 4
                
                base_ratio = base_ratios.get(note_name, 0.5)
                
                if octave == 1: base_ratio *= 0.6
                elif octave == 2: base_ratio *= 0.7
                elif octave == 3: base_ratio *= 0.8
                elif octave == 5: base_ratio *= 1.2
                
                position = tube_length * base_ratio
                
                # Ищем проверенные данные в калибровках
                is_verified = False
                source = 'calculated'
                
                if MODELS_LOADED:
                    # Ищем в калибровочных данных
                    similar_calibrations = CalibrationData.query.filter_by(note=note).all()
                    for cal in similar_calibrations:
                        if cal.tube_diameter and abs(cal.tube_diameter - tube_diameter) < 2.0:
                            position = cal.position
                            is_verified = True
                            source = 'calibrated'
                            break
                
                holes.append({
                    'note': note,
                    'position': round(position, 1),
                    'diameter': 8.0,
                    'source': source,
                    'is_verified': is_verified,
                    'confidence': 1.0 if is_verified else 0.7,
                    'calculated_value': round(position, 1)
                })
            
            return jsonify({
                'success': True,
                'holes': holes,
                'message': 'Расчет выполнен (простой метод)'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/calculate/single', methods=['POST'])
    def calculate_single():
        """Расчет для одной ноты"""
        try:
            data = request.json
            
            if 'note' not in data:
                return jsonify({'error': 'Отсутствует нота'}), 400
            if 'tube_length' not in data:
                return jsonify({'error': 'Отсутствует длина трубки'}), 400
            if 'tube_diameter' not in data:
                return jsonify({'error': 'Отсутствует диаметр трубки'}), 400
            
            note = data['note']
            tube_length = float(data['tube_length'])
            tube_diameter = float(data['tube_diameter'])
            
            base_ratios = {
                'C': 0.65, 'C#': 0.62, 'D': 0.60, 'D#': 0.57,
                'E': 0.55, 'F': 0.52, 'F#': 0.50, 'G': 0.47,
                'G#': 0.45, 'A': 0.42, 'A#': 0.40, 'B': 0.38
            }
            
            note_name = ''.join([c for c in note if not c.isdigit()])
            octave = int(''.join([c for c in note if c.isdigit()])) if any(c.isdigit() for c in note) else 4
            
            base_ratio = base_ratios.get(note_name, 0.5)
            
            if octave == 1: base_ratio *= 0.6
            elif octave == 2: base_ratio *= 0.7
            elif octave == 3: base_ratio *= 0.8
            elif octave == 5: base_ratio *= 1.2
            
            position = tube_length * base_ratio
            
            # Ищем похожие калибровки
            similar_calibrations = []
            if MODELS_LOADED:
                calibrations = CalibrationData.query.filter_by(note=note).all()
                for cal in calibrations:
                    if cal.tube_diameter and cal.tube_length:
                        diameter_diff = abs(cal.tube_diameter - tube_diameter) / tube_diameter
                        length_diff = abs(cal.tube_length - tube_length) / tube_length
                        similarity = 1.0 - max(diameter_diff, length_diff)
                        
                        similar_calibrations.append({
                            'position': cal.position,
                            'tube_diameter': cal.tube_diameter,
                            'tube_length': cal.tube_length,
                            'similarity': round(similarity, 2),
                            'source': cal.source
                        })
            
            # Определяем источник
            is_verified = False
            source = 'calculated'
            if similar_calibrations:
                best_match = max(similar_calibrations, key=lambda x: x['similarity'])
                if best_match['similarity'] > 0.8:
                    position = best_match['position']
                    is_verified = True
                    source = 'calibrated'
            
            return jsonify({
                'success': True,
                'calculation': {
                    'note': note,
                    'position': round(position, 1),
                    'source': source,
                    'is_verified': is_verified,
                    'confidence': 1.0 if is_verified else 0.7
                },
                'similar_calibrations': similar_calibrations
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/similar/<note>')
    def get_similar(note):
        """Поиск похожих калибровок"""
        try:
            if not MODELS_LOADED:
                return jsonify({'note': note, 'similar_calibrations': [], 'count': 0})
            
            tube_diameter = float(request.args.get('diameter', 20.0))
            tube_length = float(request.args.get('length', 450.0))
            
            similar_calibrations = []
            calibrations = CalibrationData.query.filter_by(note=note).all()
            
            for cal in calibrations:
                if cal.tube_diameter and cal.tube_length:
                    diameter_diff = abs(cal.tube_diameter - tube_diameter) / tube_diameter
                    length_diff = abs(cal.tube_length - tube_length) / tube_length
                    similarity = 1.0 - max(diameter_diff, length_diff)
                    
                    if similarity > 0.7:
                        similar_calibrations.append({
                            'position': cal.position,
                            'tube_diameter': cal.tube_diameter,
                            'tube_length': cal.tube_length,
                            'similarity': round(similarity, 2),
                            'source': cal.source
                        })
            
            return jsonify({
                'note': note,
                'similar_calibrations': similar_calibrations,
                'count': len(similar_calibrations)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== РАСЧЕТ АКУСТИЧЕСКИХ ПАРАМЕТРОВ ==========
    
    @app.route('/api/acoustic/effective-length', methods=['POST'])
    def calculate_effective_length():
        """Расчет общей эффективной длины системы"""
        try:
            data = request.json
            
            tube_length = float(data.get('tube_length', 450.0))
            mouthpiece_delta_m = float(data.get('mouthpiece_delta_m', 0.0))
            bell_delta_L = float(data.get('bell_delta_L', 0.0))
            v_sound = float(data.get('v_sound', 34300.0))
            
            # Формула: L_eff_total = L_tube + 2*δ_m + ΔL_bell
            total_effective_length = tube_length + 2 * mouthpiece_delta_m + bell_delta_L
            
            # Базовая частота: f_base = v / (2 * L_eff_total)
            f_base = v_sound / (2 * total_effective_length)  # в Гц
            
            return jsonify({
                'success': True,
                'total_effective_length': round(total_effective_length, 2),
                'base_frequency': round(f_base, 2),
                'formula': 'L_eff_total = L_tube + 2*δ_m + ΔL_bell',
                'v_sound': v_sound
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== ШАБЛОНЫ ==========
    
    @app.route('/api/flutes/<int:flute_id>/template')
    def get_template(flute_id):
        try:
            if not MODELS_LOADED:
                svg_content = '''<svg width="1000" height="300"><text x="50" y="50">Шаблон дудикса</text></svg>'''
                return send_file(
                    BytesIO(svg_content.encode('utf-8')),
                    mimetype='image/svg+xml',
                    as_attachment=True,
                    download_name=f'dudex_{flute_id}_template.svg'
                )
            
            flute = Flute.query.get_or_404(flute_id)
            svg_content = f'''<svg width="1000" height="400">
                <text x="50" y="50">Дудикс: {flute.name}</text>
                <text x="50" y="80">Тональность: {flute.key}, Длина: {flute.tube_length}мм</text>
            </svg>'''
            
            return send_file(
                BytesIO(svg_content.encode('utf-8')),
                mimetype='image/svg+xml',
                as_attachment=True,
                download_name=f'dudex_{flute_id}_template.svg'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== СТАТУС ==========
    
    @app.route('/api/status')
    def api_status():
        try:
            if not MODELS_LOADED:
                return jsonify({
                    'status': 'running',
                    'version': '1.0.0',
                    'database': {'name': 'flutes.db', 'records': {'flutes': 0, 'verified': 0}}
                })
            
            flute_count = Flute.query.count()
            verified_count = Flute.query.filter_by(is_verified=True).count()
            mp_count = Mouthpiece.query.count()
            tube_count = Tube.query.count()
            bell_count = Bell.query.count()
            cal_count = CalibrationData.query.count()
            
            return jsonify({
                'status': 'running',
                'version': '1.0.0',
                'database': {
                    'name': 'flutes.db',
                    'records': {
                        'mouthpieces': mp_count,
                        'tubes': tube_count,
                        'bells': bell_count,
                        'flutes': flute_count,
                        'verified': verified_count,
                        'calibrations': cal_count
                    }
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== ОБРАБОТКА ОШИБОК ==========
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Страница не найдена'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500