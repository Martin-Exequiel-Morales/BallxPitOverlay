"""
Item Manager - Gestiona los items, combos y sus recomendaciones
Soporta combos de items (solo entre items, no con poderes)
"""
import json
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from itertools import permutations


class ItemManager:
    def __init__(self, config_path: str = "config/items.json", num_slots: int = 4):
        """Inicializar el gestor de items"""
        self.config_path = Path(config_path)
        self.items_data = {}
        self.combos_data = {}
        self.combo_items_data = {}
        self.recommendations_data = {}
        self.num_slots = num_slots  # Configurable: 4 por defecto
        self.current_slots = [None] * num_slots  # Slots configurables
        self.history = []  # Para deshacer acciones
        
        self.load_config()
    
    def load_config(self):
        """Cargar configuración de items desde JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.items_data = data.get('items', {})
                self.combos_data = data.get('combos', {})
                self.combo_items_data = data.get('combo_items', {})
                self.recommendations_data = data.get('recommendations', {})
        except FileNotFoundError:
            print(f"Archivo de configuración no encontrado: {self.config_path}")
        except json.JSONDecodeError as e:
            print(f"Error al cargar configuración: {e}")
    
    def save_state(self):
        """Guardar estado actual para poder deshacerlo"""
        self.history.append({
            'slots': self.current_slots.copy(),
            'timestamp': None
        })
        
        # Mantener solo los últimos 10 estados
        if len(self.history) > 10:
            self.history.pop(0)
    
    def undo_last_action(self) -> bool:
        """Deshacer la última acción realizada"""
        if not self.history:
            return False
            
        last_state = self.history.pop()
        self.current_slots = last_state['slots']
        return True
    
    def _is_combo_item(self, item_id: str) -> bool:
        """Verificar si un item es resultado de un combo"""
        return item_id in self.combo_items_data
    
    def _is_nested_combo(self, item_id: str) -> bool:
        """Verificar si un combo es anidado (incluye otros combos en sus componentes)"""
        if not self._is_combo_item(item_id):
            return False
        
        combo_data = self.combo_items_data[item_id]
        components = combo_data.get('components', [])
        
        # Es anidado si alguno de sus componentes es un combo
        return any(comp in self.combo_items_data for comp in components)
    
    def get_available_items(self) -> Dict[str, Dict]:
        """Obtener lista de items disponibles (básicos y combos)"""
        available = {}
        # Items básicos
        available.update(self.items_data)
        # Items combinados ya creados
        available.update(self.combo_items_data)
        return available
    
    def add_item_to_slot(self, item_id: str, slot_index: int) -> bool:
        """Agregar un item a un slot específico"""
        if slot_index < 0 or slot_index >= 4:
            return False
        
        if item_id not in self.get_available_items():
            return False
        
        self.save_state()
        self.current_slots[slot_index] = item_id
        return True
    
    def remove_item_from_slot(self, slot_index: int) -> bool:
        """Remover item de un slot"""
        if slot_index < 0 or slot_index >= 4:
            return False
        
        self.save_state()
        self.current_slots[slot_index] = None
        return True
    
    def get_item_info(self, item_id: str) -> Optional[Dict]:
        """Obtener información de un item específico (básico o combo)"""
        all_items = self.get_available_items()
        item_info = all_items.get(item_id)
        
        if item_info:
            # Agregar metadata útil
            item_info_copy = item_info.copy()
            item_info_copy['id'] = item_id
            item_info_copy['is_combo'] = self._is_combo_item(item_id)
            item_info_copy['is_nested'] = self._is_nested_combo(item_id)
            return item_info_copy
        
        return None
    
    def can_combine_items(self, *item_ids: str) -> Tuple[bool, Optional[str]]:
        """
        Verificar si 2, 3 o 4 items se pueden combinar.
        Soporta combos anidados y combos de múltiples componentes.
        """
        if len(item_ids) < 2 or len(item_ids) > 4:
            return False, None
        
        # Generar todas las permutaciones posibles
        for perm in permutations(item_ids):
            combo_key = '+'.join(perm)
            if combo_key in self.combos_data:
                return True, combo_key
        
        return False, None
    
    def combine_items(self, *slots: int) -> Tuple[bool, Optional[str]]:
        """
        Combinar 2, 3 o 4 items en uno nuevo (COMBO).
        Solo funciona con items, no se pueden combinar con poderes.
        """
        if len(slots) < 2 or len(slots) > 4:
            return False, "Debes combinar 2, 3 o 4 items"
        
        # Validar slots
        for slot in slots:
            if slot < 0 or slot >= self.num_slots:
                return False, "Slots inválidos"
        
        # Verificar que no haya slots duplicados
        if len(set(slots)) != len(slots):
            return False, "No puedes usar el mismo slot múltiples veces"
        
        # Obtener items de los slots
        items = [self.current_slots[slot] for slot in slots]
        
        # Verificar que todos los slots tengan items
        if any(item is None for item in items):
            return False, "Todos los slots deben tener items"
        
        # Verificar si existe combo
        can_combine, combo_key = self.can_combine_items(*items)
        
        if not can_combine:
            # Mensajes más descriptivos
            item_names = []
            for item in items:
                i_type = "combo" if self._is_combo_item(item) else "item"
                i_info = self.get_item_info(item)
                i_name = i_info.get('name', item) if i_info else item
                item_names.append(f"{i_type} '{i_name}'")
            
            combo_desc = " + ".join(item_names)
            return False, f"No existe combo para {combo_desc}"
        
        # Realizar combo
        self.save_state()
        combo_data = self.combos_data[combo_key]
        result_item = combo_data['result']
        
        # Liberar todos los slots y colocar el nuevo item en el primer slot
        self.current_slots[slots[0]] = result_item
        for slot in slots[1:]:
            self.current_slots[slot] = None
        
        result_info = self.get_item_info(result_item)
        result_name = result_info.get('name', combo_data.get('name', result_item)) if result_info else combo_data.get('name', result_item)
        
        # Indicar tipo de combo
        is_nested = self._is_nested_combo(result_item)
        
        type_msg = ""
        if len(slots) == 4:
            type_msg = " (COMBO CUÁDRUPLE!)"
        elif len(slots) == 3:
            type_msg = " (COMBO TRIPLE!)"
        elif is_nested:
            type_msg = " (COMBO ANIDADO!)"
        
        return True, f"Combo de items creado: {result_name}{type_msg}"
    
    def get_possible_combos(self, item_id: str) -> List[Dict]:
        """
        Obtener posibles combos para un item específico.
        Soporta combos anidados (combo+item, combo+combo).
        """
        possible_combos = []
        
        for combo_key, combo_data in self.combos_data.items():
            items_in_combo = combo_key.split('+')
            
            if item_id in items_in_combo:
                # Encontrar los otros items del combo
                other_items = [i for i in items_in_combo if i != item_id]
                
                combo_info = {
                    'other_items': other_items,
                    'other_items_names': [self.get_item_info(i).get('name', i) for i in other_items if self.get_item_info(i)],
                    'result': combo_data,
                    'result_id': combo_data.get('result'),
                    'combo_key': combo_key,
                    'component_count': len(items_in_combo),
                    'is_triple': len(items_in_combo) == 3
                }
                possible_combos.append(combo_info)
        
        return possible_combos
    
    def get_current_items(self) -> Set[str]:
        """Obtener set de items actuales (sin None)"""
        return {item for item in self.current_slots if item is not None}
    
    def get_active_recommendations(self) -> List[Dict]:
        """Obtener recomendaciones activas basadas en items actuales"""
        current_items = self.get_current_items()
        active_recommendations = []
        
        for rec_id, rec_data in self.recommendations_data.items():
            required_items = set(rec_data['items'])
            
            # Verificar cuántos items de la recomendación están activos
            matching_items = current_items.intersection(required_items)
            
            if matching_items:  # Si al menos 1 item coincide
                recommendation = rec_data.copy()
                recommendation['id'] = rec_id
                recommendation['matching_items'] = list(matching_items)
                missing_items = list(required_items - current_items)
                recommendation['missing_items'] = missing_items
                recommendation['completion_percentage'] = len(matching_items) / len(required_items) * 100
                recommendation['is_complete'] = len(missing_items) == 0
                
                active_recommendations.append(recommendation)
        
        # Ordenar por porcentaje de completitud (descendente)
        active_recommendations.sort(key=lambda x: x['completion_percentage'], reverse=True)
        
        return active_recommendations
    
    def get_recommendations_for_item(self, item_id: str) -> List[Dict]:
        """Obtener recomendaciones que incluyen un item específico"""
        recommendations = []
        
        for rec_id, rec_data in self.recommendations_data.items():
            if item_id in rec_data['items']:
                rec_copy = rec_data.copy()
                rec_copy['id'] = rec_id
                
                # Calcular otros items necesarios
                other_items = [item for item in rec_data['items'] if item != item_id]
                rec_copy['other_items'] = other_items
                
                # Verificar cuáles ya tenemos
                current_items = self.get_current_items()
                rec_copy['items_we_have'] = [item for item in other_items if item in current_items]
                rec_copy['items_we_need'] = [item for item in other_items if item not in current_items]
                
                recommendations.append(rec_copy)
        
        return recommendations
    
    def get_suggested_items_for_slot(self, slot_index: int) -> List[str]:
        """Obtener sugerencias de items para un slot basado en items actuales"""
        if slot_index < 0 or slot_index >= 4:
            return []
        
        current_items = self.get_current_items()
        suggestions = []
        
        # Encontrar items que complementen las recomendaciones actuales
        for rec_id, rec_data in self.recommendations_data.items():
            required_items = set(rec_data['items'])
            missing_items = required_items - current_items
            
            # Si nos falta solo 1 item para completar, sugerirlo
            if len(missing_items) == 1:
                missing_item = list(missing_items)[0]
                if missing_item not in suggestions:
                    suggestions.append(missing_item)
        
        return suggestions
    
    def get_current_loadout(self) -> List[Optional[Dict]]:
        """Obtener la configuración actual de items"""
        loadout = []
        
        for item_id in self.current_slots:
            if item_id:
                item_info = self.items_data.get(item_id)
                if item_info:
                    item_info = item_info.copy()
                    item_info['id'] = item_id
                loadout.append(item_info)
            else:
                loadout.append(None)
        
        return loadout
    
    def get_empty_slots(self) -> List[int]:
        """Obtener lista de slots vacíos"""
        return [i for i, item in enumerate(self.current_slots) if item is None]
    
    def get_filled_slots(self) -> List[int]:
        """Obtener lista de slots ocupados"""
        return [i for i, item in enumerate(self.current_slots) if item is not None]
    
    def swap_items(self, slot1: int, slot2: int) -> bool:
        """Intercambiar items entre dos slots"""
        if slot1 < 0 or slot1 >= 4 or slot2 < 0 or slot2 >= 4:
            return False
        
        if slot1 == slot2:
            return False
        
        self.save_state()
        self.current_slots[slot1], self.current_slots[slot2] = \
            self.current_slots[slot2], self.current_slots[slot1]
        
        return True
    
    def get_optimization_suggestions(self) -> List[Dict]:
        """Obtener sugerencias para optimizar la configuración actual"""
        suggestions = []
        current_items = self.get_current_items()
        
        # Sugerir completar recomendaciones parciales
        for rec_id, rec_data in self.recommendations_data.items():
            required_items = set(rec_data['items'])
            matching_items = current_items.intersection(required_items)
            missing_items = required_items - current_items
            
            # Si tenemos 2+ items de una recomendación pero no está completa
            if len(matching_items) >= 2 and missing_items:
                suggestion = {
                    'type': 'complete_recommendation',
                    'recommendation': rec_data.copy(),
                    'recommendation_id': rec_id,
                    'current_items': list(matching_items),
                    'needed_items': list(missing_items),
                    'priority': len(matching_items)  # Más items = mayor prioridad
                }
                suggestions.append(suggestion)
        
        # Sugerir remover items que no forman parte de ninguna recomendación
        orphaned_items = []
        for item in current_items:
            is_useful = False
            for rec_data in self.recommendations_data.values():
                if item in rec_data['items']:
                    is_useful = True
                    break
            if not is_useful:
                orphaned_items.append(item)
        
        if orphaned_items:
            suggestions.append({
                'type': 'remove_orphaned',
                'items': orphaned_items,
                'priority': 1
            })
        
        # Ordenar por prioridad
        suggestions.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return suggestions
    
    def set_recommended_items_for_character(self, character_id: str, characters_config_path: str = "config/characters.json") -> bool:
        """Establecer items recomendados según el personaje"""
        try:
            with open(characters_config_path, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)
                
            character = characters_data['characters'].get(character_id)
            if character and 'recommended_items' in character:
                recommended_items = character['recommended_items']
                
                # Limpiar slots y agregar items recomendados
                self.current_slots = [None] * 4
                
                for i, item_id in enumerate(recommended_items[:4]):  # Máximo 4 items
                    if item_id in self.items_data:
                        self.current_slots[i] = item_id
                
                return True
                
        except Exception as e:
            print(f"Error al establecer items recomendados: {e}")
        
        return False
