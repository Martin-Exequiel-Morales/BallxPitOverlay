"""
State Manager - Gestiona el estado de slots, historial y acciones
Separado de PowerManager para seguir Single Responsibility Principle
"""
from typing import List, Optional, Dict, Any
from datetime import datetime


class StateManager:
    """Gestiona el estado de slots de poderes e items, historial de cambios"""
    
    def __init__(self, num_power_slots: int = 4, num_item_slots: int = 4):
        """Inicializar gestor de estado"""
        self.num_power_slots = num_power_slots
        self.num_item_slots = num_item_slots
        
        # Estado actual
        self.power_slots = [None] * num_power_slots
        self.item_slots = [None] * num_item_slots
        
        # Historial para deshacer
        self.history = []
        self.max_history = 20
    
    def save_state(self):
        """Guardar estado actual en el historial"""
        state = {
            'power_slots': self.power_slots.copy(),
            'item_slots': self.item_slots.copy(),
            'timestamp': datetime.now()
        }
        self.history.append(state)
        
        # Mantener límite de historial
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def undo(self) -> bool:
        """Deshacer última acción"""
        if not self.history:
            return False
        
        last_state = self.history.pop()
        self.power_slots = last_state['power_slots']
        self.item_slots = last_state['item_slots']
        return True
    
    def can_undo(self) -> bool:
        """Verificar si se puede deshacer"""
        return len(self.history) > 0
    
    # ========== POWER SLOTS ==========
    
    def set_power(self, slot_index: int, power_id: Optional[str]) -> bool:
        """Establecer poder en un slot (con historial)"""
        if slot_index < 0 or slot_index >= self.num_power_slots:
            return False
        
        self.save_state()
        self.power_slots[slot_index] = power_id
        return True
    
    def get_power(self, slot_index: int) -> Optional[str]:
        """Obtener poder de un slot"""
        if slot_index < 0 or slot_index >= self.num_power_slots:
            return None
        return self.power_slots[slot_index]
    
    def clear_power(self, slot_index: int) -> bool:
        """Limpiar poder de un slot"""
        return self.set_power(slot_index, None)
    
    def clear_all_powers(self):
        """Limpiar todos los slots de poderes"""
        self.save_state()
        self.power_slots = [None] * self.num_power_slots
    
    def get_all_powers(self) -> List[Optional[str]]:
        """Obtener todos los poderes actuales"""
        return self.power_slots.copy()
    
    def get_filled_power_slots(self) -> List[int]:
        """Obtener índices de slots con poderes"""
        return [i for i, power in enumerate(self.power_slots) if power is not None]
    
    def get_empty_power_slots(self) -> List[int]:
        """Obtener índices de slots vacíos"""
        return [i for i, power in enumerate(self.power_slots) if power is None]
    
    def has_power(self, power_id: str) -> bool:
        """Verificar si un poder está en uso"""
        return power_id in self.power_slots
    
    def get_power_slot_index(self, power_id: str) -> Optional[int]:
        """Obtener índice del slot que contiene un poder"""
        try:
            return self.power_slots.index(power_id)
        except ValueError:
            return None
    
    # ========== ITEM SLOTS ==========
    
    def set_item(self, slot_index: int, item_id: Optional[str]) -> bool:
        """Establecer item en un slot (con historial)"""
        if slot_index < 0 or slot_index >= self.num_item_slots:
            return False
        
        self.save_state()
        self.item_slots[slot_index] = item_id
        return True
    
    def get_item(self, slot_index: int) -> Optional[str]:
        """Obtener item de un slot"""
        if slot_index < 0 or slot_index >= self.num_item_slots:
            return None
        return self.item_slots[slot_index]
    
    def clear_item(self, slot_index: int) -> bool:
        """Limpiar item de un slot"""
        return self.set_item(slot_index, None)
    
    def clear_all_items(self):
        """Limpiar todos los slots de items"""
        self.save_state()
        self.item_slots = [None] * self.num_item_slots
    
    def get_all_items(self) -> List[Optional[str]]:
        """Obtener todos los items actuales"""
        return self.item_slots.copy()
    
    def get_filled_item_slots(self) -> List[int]:
        """Obtener índices de slots con items"""
        return [i for i, item in enumerate(self.item_slots) if item is not None]
    
    def get_empty_item_slots(self) -> List[int]:
        """Obtener índices de slots vacíos"""
        return [i for i, item in enumerate(self.item_slots) if item is None]
    
    def has_item(self, item_id: str) -> bool:
        """Verificar si un item está en uso"""
        return item_id in self.item_slots
    
    # ========== BULK OPERATIONS ==========
    
    def set_powers_bulk(self, powers: List[Optional[str]]):
        """Establecer múltiples poderes a la vez"""
        if len(powers) != self.num_power_slots:
            return False
        
        self.save_state()
        self.power_slots = powers.copy()
        return True
    
    def set_items_bulk(self, items: List[Optional[str]]):
        """Establecer múltiples items a la vez"""
        if len(items) != self.num_item_slots:
            return False
        
        self.save_state()
        self.item_slots = items.copy()
        return True
    
    def clear_all(self):
        """Limpiar todos los slots"""
        self.save_state()
        self.power_slots = [None] * self.num_power_slots
        self.item_slots = [None] * self.num_item_slots
    
    # ========== ESTADO Y DEBUG ==========
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Obtener resumen del estado actual"""
        return {
            'power_slots': {
                'total': self.num_power_slots,
                'filled': len(self.get_filled_power_slots()),
                'empty': len(self.get_empty_power_slots()),
                'powers': self.power_slots
            },
            'item_slots': {
                'total': self.num_item_slots,
                'filled': len(self.get_filled_item_slots()),
                'empty': len(self.get_empty_item_slots()),
                'items': self.item_slots
            },
            'history': {
                'can_undo': self.can_undo(),
                'states_saved': len(self.history)
            }
        }
    
    def reset(self):
        """Resetear todo el estado (sin guardar en historial)"""
        self.power_slots = [None] * self.num_power_slots
        self.item_slots = [None] * self.num_item_slots
        self.history = []
