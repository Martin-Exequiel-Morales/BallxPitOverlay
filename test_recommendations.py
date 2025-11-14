"""
Test para debuggear el sistema de recomendaciones
"""
import json
from core.power_manager import PowerManager

# Cargar datos
pm = PowerManager()

# Simular: Vampire en slot 1
pm.current_slots[0] = "17"  # Vampire

print("=" * 60)
print("DATOS DE NOSFERATU")
print("=" * 60)

# Obtener info de Nosferatu
nosferatu_info = pm.get_power_info("41")
print(f"\nNosferatu (41):")
print(f"  Componentes: {nosferatu_info.get('components', [])}")

# Ver cada componente
components = nosferatu_info.get('components', [])
for comp_id in components:
    comp_info = pm.get_power_info(comp_id)
    print(f"\n  → {comp_info['name']} ({comp_id}):")
    print(f"      is_combo: {comp_info.get('is_combo')}")
    if comp_info.get('is_combo'):
        sub_comps = comp_info.get('components', [])
        print(f"      componentes: {sub_comps}")
        for sub_id in sub_comps:
            sub_info = pm.get_power_info(sub_id)
            print(f"        - {sub_info['name']} ({sub_id})")

print("\n" + "=" * 60)
print("SIMULACIÓN DEL ALGORITMO")
print("=" * 60)

# Simular el algoritmo
current_powers = [(0, "17")]  # Vampire en slot 0
current_ids = ["17"]
available_slots = [1, 2, 3]

all_base_components = []
seen_bases = set()
component_groups = []

print(f"\nPoderes actuales: {current_ids}")
print(f"Slots disponibles: {available_slots}")

for comp_id in components:
    print(f"\n--- Procesando componente: {comp_id} ---")
    
    if comp_id in current_ids:
        print(f"  ✓ Ya tenemos {comp_id}, skip")
        continue
    
    comp_info = pm.get_power_info(comp_id)
    print(f"  Nombre: {comp_info['name']}")
    print(f"  Is combo: {comp_info.get('is_combo')}")
    
    group = {
        'component_id': comp_id,
        'slots': [],
        'base_ids': []
    }
    
    if comp_info.get('is_combo'):
        sub_components = comp_info.get('components', [])
        print(f"  Sub-componentes: {sub_components}")
        
        for sub_comp_id in sub_components:
            print(f"\n    Procesando sub-componente: {sub_comp_id}")
            
            if sub_comp_id in current_ids:
                print(f"      ✓ Ya está en uso, agregar al grupo pero no recomendar")
                group['base_ids'].append(sub_comp_id)
                continue
            
            sub_info = pm.get_power_info(sub_comp_id)
            print(f"      Nombre: {sub_info['name']}")
            print(f"      Is combo: {sub_info.get('is_combo')}")
            
            if sub_info.get('is_combo'):
                print(f"      ✗ Es combo anidado, skip")
                continue
            
            # Agregar al grupo
            group['base_ids'].append(sub_comp_id)
            print(f"      ✓ Agregado al grupo: {sub_comp_id}")
            
            # Agregar a recomendaciones si no está
            if sub_comp_id not in seen_bases:
                all_base_components.append(sub_comp_id)
                seen_bases.add(sub_comp_id)
                print(f"      ✓ Agregado a recomendaciones: {sub_comp_id} ({sub_info['name']})")
            else:
                print(f"      ✗ Ya está en seen_bases, NO agregar a recomendaciones")
    
    else:
        print(f"  Es ball base directa")
        if comp_id not in current_ids and comp_id not in seen_bases:
            all_base_components.append(comp_id)
            seen_bases.add(comp_id)
            group['base_ids'].append(comp_id)
            print(f"  ✓ Agregado: {comp_id}")
    
    if group['base_ids']:
        component_groups.append(group)
        print(f"  Grupo creado con base_ids: {group['base_ids']}")

print("\n" + "=" * 60)
print("BÚSQUEDA DE COMBOS VALIOSOS")
print("=" * 60)

# Simular _find_valuable_combo_path
all_combos = pm.combo_powers_data
current_ids = ["17"]

best_combo_id = None
best_score = 0

for combo_id, combo_info in all_combos.items():
    components = combo_info.get('components', [])
    matching = [c for c in components if c in current_ids]
    
    if matching:
        score = len(components) * 100 + len(components)  # Aproximado
        combo_name = combo_info.get('name', combo_id)
        print(f"\n{combo_name} ({combo_id}): components={len(components)}, score={score}")
        print(f"  Componentes: {components}")
        print(f"  Matching con Vampire: {matching}")
        
        if score > best_score:
            best_score = score
            best_combo_id = combo_id

print(f"\n✓ MEJOR COMBO ENCONTRADO: {best_combo_id} (score={best_score})")

print("\n" + "=" * 60)
print("RESULTADO FINAL")
print("=" * 60)
print(f"\nRecomendaciones (all_base_components): {all_base_components}")
print(f"Cantidad: {len(all_base_components)}")

for i, base_id in enumerate(all_base_components):
    base_info = pm.get_power_info(base_id)
    print(f"  Slot {available_slots[i] if i < len(available_slots) else 'N/A'}: {base_info['name']} ({base_id})")

print(f"\nGrupos creados: {len(component_groups)}")
for i, group in enumerate(component_groups):
    comp_info = pm.get_power_info(group['component_id'])
    print(f"  Grupo {i}: {comp_info['name']} → base_ids: {group['base_ids']}")
