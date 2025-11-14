"""
Power Manager - Gestiona datos de poderes, combos y validación
SOLO datos y lógica de combos - NO gestiona estado de slots
"""
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class PowerManager:
    """Gestiona datos de poderes y lógica de combos"""
    
    def __init__(self, config_path: str = "config/powers.json"):
        """Inicializar el gestor de poderes"""
        self.config_path = Path(config_path)
        self.powers_data = {}
        self.combos_data = {}
        self.combo_powers_data = {}
        
        self.load_config()
    
    def load_config(self):
        """Cargar configuración de poderes desde JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.powers_data = data.get('powers', {})
                self.combos_data = data.get('combos', {})
                self.combo_powers_data = data.get('combo_powers', {})
        except FileNotFoundError:
            print(f"Archivo de configuración no encontrado: {self.config_path}")
        except json.JSONDecodeError as e:
            print(f"Error al cargar configuración: {e}")
    
    def _is_combo_power(self, power_id: str) -> bool:
        """Verificar si un poder es resultado de un combo"""
        return power_id in self.combo_powers_data
    
    def _is_nested_combo(self, power_id: str) -> bool:
        """Verificar si un combo es anidado (incluye otros combos en sus componentes)"""
        if not self._is_combo_power(power_id):
            return False
        
        combo_data = self.combo_powers_data[power_id]
        components = combo_data.get('components', [])
        
        # Es anidado si alguno de sus componentes es un combo
        return any(comp in self.combo_powers_data for comp in components)
    
    def _get_future_combos(self, power_id: str) -> List[Dict]:
        """
        Obtener combos futuros posibles con un poder/combo dado.
        Retorna qué más se puede combinar con este resultado.
        """
        future_combos = []
        
        for combo_key, combo_data in self.combos_data.items():
            powers_in_combo = combo_key.split('+')
            
            # Si este poder está en un combo
            if power_id in powers_in_combo:
                other_power = powers_in_combo[0] if powers_in_combo[1] == power_id else powers_in_combo[1]
                other_info = self.get_power_info(other_power)
                
                if other_info:
                    future_result_id = combo_data.get('result')
                    future_result_info = self.get_power_info(future_result_id)
                    
                    future_combo = {
                        'needs_power': other_power,
                        'needs_power_name': other_info.get('name', other_power),
                        'needs_is_combo': other_info.get('is_combo', False),
                        'creates': future_result_id,
                        'creates_name': future_result_info.get('name', future_result_id) if future_result_info else future_result_id,
                        'combo_key': combo_key
                    }
                    future_combos.append(future_combo)
        
        return future_combos
    
    def _get_base_powers_recursive(self, power_id: str) -> List[str]:
        """Obtener poderes base de forma recursiva"""
        if not self._is_combo_power(power_id):
            # Es poder base
            return [power_id]
        
        # Es combo, descomponer
        combo_data = self.combo_powers_data[power_id]
        components = combo_data.get('components', [])
        
        base_powers = []
        for comp in components:
            base_powers.extend(self._get_base_powers_recursive(comp))
        
        return base_powers
    
    def get_available_powers(self) -> Dict[str, Dict]:
        """Obtener lista de poderes disponibles (básicos y combos)"""
        available = {}
        # Poderes básicos
        available.update(self.powers_data)
        # Poderes combinados
        available.update(self.combo_powers_data)
        return available
    
    def get_power_info(self, power_id: str) -> Optional[Dict]:
        """Obtener información de un poder específico (básico o combo)"""
        all_powers = self.get_available_powers()
        power_info = all_powers.get(power_id)
        
        if power_info:
            # Agregar metadata útil
            power_info_copy = power_info.copy()
            power_info_copy['id'] = power_id
            power_info_copy['is_combo'] = self._is_combo_power(power_id)
            power_info_copy['is_nested'] = self._is_nested_combo(power_id)
            return power_info_copy
        
        return None
    
    def get_possible_combos(self, power_id: str) -> List[Dict]:
        """
        Obtener posibles combos para un poder específico.
        Soporta combos anidados (combo+poder, combo+combo).
        """
        possible_combos = []
        
        for combo_key, combo_data in self.combos_data.items():
            powers_in_combo = combo_key.split('+')
            
            if power_id in powers_in_combo:
                # Encontrar el otro poder del combo
                other_power = powers_in_combo[0] if powers_in_combo[1] == power_id else powers_in_combo[1]
                other_info = self.get_power_info(other_power)
                
                if other_info:
                    result_id = combo_data.get('result')
                    result_info = self.get_power_info(result_id)
                    
                    # Buscar combos futuros posibles con este resultado
                    future_combos = self._get_future_combos(result_id)
                    
                    combo_info = {
                        'other_power': other_power,
                        'other_power_name': other_info.get('name', other_power),
                        'other_is_combo': other_info.get('is_combo', False),
                        'result': result_info if result_info else {'name': result_id},
                        'result_id': result_id,
                        'combo_key': combo_key,
                        'is_nested': other_info.get('is_combo', False) or self._is_combo_power(power_id),
                        'future_combos': future_combos
                    }
                    possible_combos.append(combo_info)
        
        return possible_combos
    
    def can_combine_powers(self, *power_ids: str) -> Tuple[bool, Optional[str]]:
        """
        Verificar si 2 o 3 poderes se pueden combinar.
        Soporta combos anidados y combos de múltiples componentes.
        
        Returns:
            (can_combine, combo_key)
        """
        if len(power_ids) < 2 or len(power_ids) > 3:
            return False, None
        
        # Generar todas las permutaciones posibles
        from itertools import permutations
        for perm in permutations(power_ids):
            combo_key = '+'.join(perm)
            if combo_key in self.combos_data:
                return True, combo_key
        
        return False, None
    
    def get_combo_result(self, combo_key: str) -> Optional[Dict]:
        """Obtener información del resultado de un combo"""
        combo_data = self.combos_data.get(combo_key)
        if not combo_data:
            return None
        
        result_id = combo_data.get('result')
        result_info = self.get_power_info(result_id)
        
        return {
            'result_id': result_id,
            'result_info': result_info,
            'combo_data': combo_data
        }
    
    def validate_power_id(self, power_id: str) -> bool:
        """Validar que un power_id existe"""
        return power_id in self.get_available_powers()
