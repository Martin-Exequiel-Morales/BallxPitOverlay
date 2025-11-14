# Análisis de Lógica Core - Optimizaciones Necesarias

## 📊 Estado Actual

### Archivos en `/core`:

1. **power_manager.py** - Gestión de poderes, combos, slots, historial
2. **item_manager.py** - Gestión de items (similar a power_manager)
3. **combo_engine.py** - Motor de análisis y recomendaciones (LEGACY)
4. **recommendation_engine.py** - Motor de recomendaciones contextual (NUEVO)
5. ****init**.py** - Exports

---

## 🔍 Problemas Detectados

### 1. **DUPLICACIÓN**: combo_engine.py vs recommendation_engine.py

**Problema**: Dos sistemas de recomendaciones:

- `combo_engine.py`: Sistema antiguo con `analyze_powers()`, `get_power_suggestions_for_slot()`
- `recommendation_engine.py`: Sistema nuevo con `calculate_recommendations()`, `_find_valuable_combo_path()`

**Impacto**:

- Confusión sobre qué usar
- Código duplicado
- Mantenimiento doble

**Solución**: Eliminar `combo_engine.py` y consolidar en `recommendation_engine.py`

---

### 2. **VIOLACIÓN SRP**: power_manager.py hace demasiado

**Problema**: PowerManager gestiona:

- ✅ Datos de poderes (correcto)
- ✅ Configuración (correcto)
- ❌ Estado de slots (debería estar en UI o state manager)
- ❌ Historial de deshacer (debería estar en state manager)
- ❌ Combinación de poderes (debería estar en recommendation_engine)

**Código problemático**:

```python
# PowerManager NO debería gestionar estado de slots
self.current_slots = [None] * num_slots
self.history = []

def add_power_to_slot(self, power_id: str, slot_index: int)
def remove_power_from_slot(self, slot_index: int)
def save_state(self)
def undo_last_action(self)
def combine_powers(self, *slots: int)  # ❌ Mezcla lógica con estado
```

**Solución**:

- PowerManager → Solo datos y validación
- StateManager → Gestionar slots e historial
- RecommendationEngine → Lógica de combos

---

### 3. **MÉTODOS NO USADOS**: Muchos métodos legacy

**Métodos que NO se usan en la nueva UI**:

- `power_manager.combine_powers()` - La UI no llama esto (hace combos directamente)
- `power_manager.fuse_powers()` - Funcionalidad no implementada
- `power_manager.get_current_loadout()` - No se usa
- `power_manager.set_default_power()` - No se usa (usa otro sistema)
- `combo_engine.analyze_current_state()` - No se usa (usa recommendation_engine)
- `combo_engine.get_hover_info()` - No se usa

---

### 4. **INCONSISTENCIAS**: Diferentes formatos

**Problema**:

- PowerManager usa `num_slots` configurable (4 o 5)
- RecommendationEngine hardcodea `[None, None, None, None]` (siempre 4)
- ComboEngine también hardcodea cosas

**Solución**: Centralizar configuración

---

## ✅ Arquitectura Propuesta

```
core/
├── power_manager.py      # SOLO datos, config, validación
│   ├── load_config()
│   ├── get_power_info()
│   ├── get_possible_combos()
│   ├── can_combine_powers()
│   └── _get_future_combos()
│
├── item_manager.py       # SOLO datos, config, validación
│   ├── load_config()
│   ├── get_item_info()
│   └── get_recommendations_for_item()
│
├── recommendation_engine.py  # TODA la lógica de recomendaciones
│   ├── calculate_recommendations()
│   ├── _find_valuable_combo_path()
│   ├── _build_path_to_combo()
│   ├── get_contextual_power_priority()
│   └── get_sorted_powers_for_menu()
│
└── state_manager.py      # NUEVO - Gestionar estado
    ├── current_slots
    ├── current_items
    ├── history
    ├── add_power_to_slot()
    ├── remove_power()
    ├── save_state()
    └── undo()
```

---

## 🎯 Acciones Recomendadas

### FASE 1: Limpieza (Sin romper nada)

1. ✅ Marcar `combo_engine.py` como deprecated
2. ✅ Documentar qué métodos de `power_manager` están obsoletos
3. ✅ Crear `state_manager.py` pero mantener compatibilidad

### FASE 2: Migración

4. ✅ Mover lógica de slots/history a `state_manager.py`
5. ✅ Actualizar `recommendation_engine.py` para usar state_manager
6. ✅ Limpiar `power_manager.py` eliminando métodos de estado

### FASE 3: Refactor Final

7. ✅ Eliminar `combo_engine.py`
8. ✅ Eliminar métodos no usados de `power_manager.py`
9. ✅ Consolidar configuración (num_slots centralizado)

---

## 📋 Métodos a ELIMINAR

### En power_manager.py:

```python
# Estado (mover a state_manager)
- current_slots
- history
- save_state()
- undo_last_action()
- add_power_to_slot()
- remove_power_from_slot()
- combine_powers()      # UI lo hace directamente
- fuse_powers()         # No implementado
- get_current_loadout() # No usado
- set_default_power()   # No usado
- get_empty_slots()     # state_manager
- get_filled_slots()    # state_manager
```

### En combo_engine.py (ELIMINAR ARCHIVO):

```python
- TODOS (usar recommendation_engine)
```

---

## 📋 Métodos a MANTENER

### power_manager.py (CORE DATA):

```python
✅ load_config()
✅ get_power_info()
✅ get_possible_combos()
✅ can_combine_powers()
✅ _get_future_combos()
✅ _is_combo_power()
✅ _is_nested_combo()
✅ _get_base_powers_needed()
✅ _get_base_powers_recursive()
✅ get_available_powers()
```

### recommendation_engine.py (LOGIC):

```python
✅ calculate_recommendations()
✅ _find_valuable_combo_path()
✅ _build_path_to_combo()
✅ _calculate_color_groups()
✅ _has_complete_combo_no_future()
✅ get_contextual_power_priority()
✅ get_sorted_powers_for_menu()
```

---

## 🚀 Beneficios

1. **Claridad**: Cada archivo tiene una responsabilidad única
2. **Mantenibilidad**: Menos duplicación, código más limpio
3. **Testabilidad**: Lógica separada de estado
4. **Escalabilidad**: Fácil agregar nuevas features
5. **Performance**: Menos código innecesario ejecutándose

---

## ⚠️ Riesgos

- **Bajo riesgo**: La UI actual solo usa recommendation_engine
- **Compatibilidad**: main.py aún importa combo_engine (pero no lo usa)
- **Testing**: Necesario probar después de cada fase
