"""
Recommendation Engine - Lógica de recomendaciones, paths y contexto
Separado de la UI para mayor modularidad
"""
from typing import List, Dict, Tuple, Optional


class RecommendationEngine:
    def __init__(self, power_manager):
        self.power_manager = power_manager
        self.power_recommendations = [None, None, None, None]
        self.recommendation_groups = []  # Grupos de slots con el mismo color
        
    def calculate_recommendations(self, current_slots: List[Optional[str]]) -> Dict:
        """
        Calcular recomendaciones basadas en el contexto actual.
        
        Returns:
            Dict con 'recommendations' y 'color_groups'
        """
        self.power_recommendations = [None, None, None, None]
        self.recommendation_groups = []
        
        # Obtener poderes actuales (no None)
        current_powers = [(i, pid) for i, pid in enumerate(current_slots) if pid is not None]
        
        if not current_powers:
            return {
                'recommendations': self.power_recommendations,
                'color_groups': self.recommendation_groups
            }
        
        # Calcular grupos de colores para balls SELECCIONADAS
        self._calculate_color_groups(current_powers)
        
        # Verificar si ya tenemos un combo completo sin futuros combos
        if self._has_complete_combo_no_future(current_powers):
            # Ya tenemos el mejor combo alcanzable, no recomendar nada más
            return {
                'recommendations': self.power_recommendations,
                'color_groups': self.recommendation_groups
            }
        
        # Buscar el combo más valioso que sea alcanzable
        available_slots = [i for i in range(4) if current_slots[i] is None]
        best_path = self._find_valuable_combo_path(current_powers, available_slots)
        
        if best_path:
            # Aplicar recomendaciones del path
            for step in best_path['steps']:
                slot_idx = step['slot']
                if step.get('is_recommendation') and slot_idx < 4:
                    self.power_recommendations[slot_idx] = step['power_id']
        
        return {
            'recommendations': self.power_recommendations,
            'color_groups': self.recommendation_groups
        }
    
    def _has_complete_combo_no_future(self, current_powers) -> bool:
        """Verificar si los poderes actuales forman un combo completo sin combos futuros"""
        if len(current_powers) < 2:
            return False
        
        current_ids = [pid for _, pid in current_powers]
        
        # Verificar si se pueden combinar entre sí
        for i, pid1 in enumerate(current_ids):
            for j, pid2 in enumerate(current_ids):
                if i >= j:
                    continue
                
                can_combine, combo_key = self.power_manager.can_combine_powers(pid1, pid2)
                if can_combine:
                    # Pueden combinarse, verificar si el resultado tiene combos futuros
                    combo_data = self.power_manager.combos_data.get(combo_key)
                    if combo_data:
                        result_id = combo_data.get('result')
                        # Verificar si el resultado tiene combos futuros
                        future_combos = self.power_manager._get_future_combos(result_id)
                        if not future_combos or len(future_combos) == 0:
                            # No hay combos futuros, ya es el mejor combo alcanzable
                            return True
        
        return False
    
    def _calculate_color_groups(self, current_powers):
        """Calcular grupos de colores para balls seleccionadas que pueden combinarse"""
        if len(current_powers) < 2:
            return
        
        current_slots = [slot_idx for slot_idx, _ in current_powers]
        current_ids = [pid for _, pid in current_powers]
        
        # Buscar combos posibles entre los poderes actuales
        used_slots = set()
        
        for i, (slot1, pid1) in enumerate(current_powers):
            for j, (slot2, pid2) in enumerate(current_powers):
                if i >= j or slot1 in used_slots or slot2 in used_slots:
                    continue
                
                # Verificar si estos dos pueden combinarse
                can_combine, combo_key = self.power_manager.can_combine_powers(pid1, pid2)
                if can_combine:
                    # Agregar grupo de color
                    self.recommendation_groups.append([slot1, slot2])
                    used_slots.add(slot1)
                    used_slots.add(slot2)
                    break
    
    def _find_valuable_combo_path(self, current_powers, available_slots) -> Optional[Dict]:
        """
        Buscar el combo más valioso considerando TODOS los poderes actuales.
        Puede recomendar múltiples combos si no se puede alcanzar uno solo.
        """
        if not available_slots:
            return None
        
        # IDs de poderes actuales
        current_ids = [pid for _, pid in current_powers]
        
        # Buscar todos los combos alcanzables con los poderes actuales
        all_combos = self.power_manager.combo_powers_data
        
        best_path = None
        best_score = 0
        
        for combo_id, combo_info in all_combos.items():
            components = combo_info.get('components', [])
            
            # Calcular cuántos componentes ya tenemos (directos o indirectos)
            matching_count = 0
            for comp_id in components:
                if comp_id in current_ids:
                    matching_count += 1
                else:
                    # Verificar en sub-componentes
                    comp_info_detail = self.power_manager.get_power_info(comp_id)
                    if comp_info_detail and comp_info_detail.get('is_combo'):
                        sub_comps = comp_info_detail.get('components', [])
                        if any(sc in current_ids for sc in sub_comps):
                            matching_count += 0.5  # Match parcial
            
            if matching_count == 0:
                continue
            
            # Intentar construir el path hacia este combo
            path = self._build_path_to_combo(combo_id, combo_info, current_powers, available_slots)
            
            if path:
                # Scoring: componentes * 100 + matching * 50 + depth
                # Prioriza combos complejos que usen más poderes actuales
                score = (len(components) * 100 + 
                        int(matching_count * 50) + 
                        path.get('depth', 0))
                
                if score > best_score:
                    best_score = score
                    best_path = path
        
        return best_path
    
    def _build_path_to_combo(self, target_combo_id, target_combo_info, current_powers, available_slots) -> Optional[Dict]:
        """
        Construir el camino hacia un combo específico usando SOLO balls base.
        Descompone combos anidados y llena todos los slots disponibles.
        """
        components = target_combo_info.get('components', [])
        if not components:
            return None
        
        # Mapear qué componentes ya tenemos
        current_ids = [pid for _, pid in current_powers]
        current_slots_map = {pid: slot_idx for slot_idx, pid in current_powers}
        
        # Recolectar TODAS las balls base necesarias para todos los componentes
        all_base_components = []
        seen_bases = set()  # Solo para evitar duplicados exactos en la lista
        component_groups = []  # Para tracking de qué bases van juntas
        
        for comp_id in components:
            if comp_id in current_ids:
                # Ya lo tenemos, marcar su slot
                slot_idx = current_slots_map[comp_id]
                component_groups.append({
                    'component_id': comp_id,
                    'slots': [slot_idx],
                    'base_ids': []
                })
                continue
            
            comp_info = self.power_manager.get_power_info(comp_id)
            if not comp_info:
                continue
            
            group = {
                'component_id': comp_id,
                'slots': [],
                'base_ids': []
            }
            
            # Si es combo, descomponer en balls base
            if comp_info.get('is_combo'):
                sub_components = comp_info.get('components', [])
                
                for sub_comp_id in sub_components:
                    # Verificar si ya está en uso actualmente
                    if sub_comp_id in current_ids:
                        # Ya está en uso, agregar al grupo pero no a recomendaciones
                        group['base_ids'].append(sub_comp_id)
                        continue
                    
                    sub_info = self.power_manager.get_power_info(sub_comp_id)
                    if not sub_info or sub_info.get('is_combo'):
                        continue
                    
                    # SIEMPRE agregar al grupo (para tracking)
                    group['base_ids'].append(sub_comp_id)
                    
                    # Solo agregar a la lista de recomendaciones si no está
                    if sub_comp_id not in seen_bases:
                        all_base_components.append(sub_comp_id)
                        seen_bases.add(sub_comp_id)
            else:
                # Es ball base
                if comp_id not in current_ids and comp_id not in seen_bases:
                    all_base_components.append(comp_id)
                    seen_bases.add(comp_id)
                    group['base_ids'].append(comp_id)
            
            if group['base_ids']:
                component_groups.append(group)
        
        # Ahora asignar todas las balls base a los slots disponibles
        steps = []
        combo_groups = []
        all_slots_used = []
        
        for i, base_id in enumerate(all_base_components):
            if i >= len(available_slots):
                break  # No hay más slots
            
            slot = available_slots[i]
            steps.append({
                'slot': slot,
                'power_id': base_id,
                'is_recommendation': True
            })
            all_slots_used.append(slot)
        
        # Crear grupos de combinación
        # Agrupar por componente intermedio
        for group in component_groups:
            group_slots = []
            # Agregar slots con las bases de este grupo
            for base_id in group['base_ids']:
                try:
                    idx = all_base_components.index(base_id)
                    if idx < len(available_slots):
                        group_slots.append(available_slots[idx])
                except ValueError:
                    pass
            
            # Agregar slots actuales si aplica
            group_slots.extend(group['slots'])
            
            if group_slots:
                combo_groups.append(group_slots)
        
        # Si no hay pasos, retornar None
        if not steps:
            return None
        
        return {
            'steps': steps,
            'combo_groups': combo_groups,
            'depth': len(components),  # Profundidad = número de componentes
            'final_result': target_combo_id
        }
    
    def get_contextual_power_priority(self, power_id: str, current_slots: List[Optional[str]], 
                                      used_powers: set) -> Tuple[int, str, bool]:
        """
        Calcular prioridad de un poder según el contexto actual.
        
        Returns:
            Tuple[priority, prefix, can_combo_with_current]
            priority: 0 (máxima) a 3 (mínima)
            prefix: emoji para mostrar
            can_combo_with_current: si se combina con lo que tienes
        """
        if power_id in used_powers:
            return (999, "", False)  # No mostrar duplicados
        
        # Obtener IDs de poderes actuales para contexto
        current_ids = [pid for pid in current_slots if pid is not None]
        
        # Analizar utilidad para combos
        possible_combos = self.power_manager.get_possible_combos(power_id)
        
        # Verificar si puede combinarse con alguno de los poderes actuales
        can_combo_with_current = False
        for current_id in current_ids:
            can_combine, _ = self.power_manager.can_combine_powers(power_id, current_id)
            if can_combine:
                can_combo_with_current = True
                break
        
        # Contar combos anidados y totales
        nested_count = sum(1 for c in possible_combos if c.get('is_nested') or len(c.get('future_combos', [])) > 0)
        combo_count = len(possible_combos)
        
        # Asignar prioridad según contexto
        if can_combo_with_current:
            priority = 0  # MÁXIMA - Se combina con lo que tienes
            prefix = "⭐🔥"
        elif nested_count > 0:
            priority = 1  # Alta (combos anidados)
            prefix = "🔥🔥"
        elif combo_count > 0:
            priority = 2  # Media (combos simples)
            prefix = "🔥"
        else:
            priority = 3  # Baja (sin combos)
            prefix = "⚪"
        
        return (priority, prefix, can_combo_with_current)
    
    def get_sorted_powers_for_menu(self, current_slots: List[Optional[str]], 
                                   used_powers: set) -> List[Dict]:
        """
        Obtener lista de poderes ordenada por contexto para menú.
        
        Returns:
            Lista de dicts con 'id', 'info', 'priority', 'prefix'
        """
        all_powers = self.power_manager.powers_data
        power_list = []
        
        for pid, pinfo in all_powers.items():
            priority, prefix, can_combo = self.get_contextual_power_priority(
                pid, current_slots, used_powers
            )
            
            if priority == 999:  # Skip duplicados
                continue
            
            possible_combos = self.power_manager.get_possible_combos(pid)
            nested_count = sum(1 for c in possible_combos if c.get('is_nested') or len(c.get('future_combos', [])) > 0)
            combo_count = len(possible_combos)
            
            power_list.append({
                'id': pid,
                'info': pinfo,
                'priority': priority,
                'prefix': prefix,
                'nested_count': nested_count,
                'combo_count': combo_count,
                'combos_with_current': can_combo
            })
        
        # Ordenar: primero por prioridad, luego por nested_count, combo_count, nombre
        power_list.sort(key=lambda x: (x['priority'], -x['nested_count'], -x['combo_count'], x['info']['name']))
        
        return power_list
