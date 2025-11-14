"""
Test script para verificar que el scraper genera el formato correcto
"""
import json
from pathlib import Path

def validate_powers_format():
    """Validar formato de powers.json"""
    print("\n=== Validando powers.json ===")
    
    with open('config/powers.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verificar estructura
    assert 'powers' in data, "Falta clave 'powers'"
    assert 'combos' in data, "Falta clave 'combos'"
    assert 'combo_powers' in data, "Falta clave 'combo_powers'"
    
    # Verificar que powers es un dict con IDs como claves
    assert isinstance(data['powers'], dict), "powers debe ser dict"
    
    # Verificar estructura de un poder básico
    if data['powers']:
        first_power = next(iter(data['powers'].values()))
        assert 'name' in first_power
        assert 'description' in first_power
        assert 'image' in first_power
        assert 'traits' in first_power
        assert 'is_combo' not in first_power, "Poderes básicos no deben tener is_combo"
    
    # Verificar combo_powers
    if data['combo_powers']:
        first_combo = next(iter(data['combo_powers'].values()))
        assert 'name' in first_combo
        assert 'is_combo' in first_combo
        assert first_combo['is_combo'] == True
        assert 'components' in first_combo
    
    # Verificar combos (recetas)
    if data['combos']:
        first_recipe = next(iter(data['combos'].values()))
        assert 'result' in first_recipe
        assert 'type' in first_recipe
        assert first_recipe['type'] in ['COMBO', 'TRIPLE']
    
    print(f"✓ Poderes básicos: {len(data['powers'])}")
    print(f"✓ Poderes combo: {len(data['combo_powers'])}")
    print(f"✓ Recetas: {len(data['combos'])}")
    print("✓ Formato correcto!")

def validate_items_format():
    """Validar formato de items.json"""
    print("\n=== Validando items.json ===")
    
    with open('config/items.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verificar estructura
    assert 'items' in data, "Falta clave 'items'"
    assert 'combos' in data, "Falta clave 'combos'"
    assert 'combo_items' in data, "Falta clave 'combo_items'"
    assert 'recommendations' in data, "Falta clave 'recommendations'"
    
    # Verificar que items usa nombres como claves
    assert isinstance(data['items'], dict), "items debe ser dict"
    
    # Verificar estructura de un item
    if data['items']:
        first_item = next(iter(data['items'].values()))
        assert 'name' in first_item
        assert 'description' in first_item
        assert 'image' in first_item
        assert 'traits' in first_item
    
    print(f"✓ Items básicos: {len(data['items'])}")
    print(f"✓ Items combo: {len(data['combo_items'])}")
    print(f"✓ Recetas: {len(data['combos'])}")
    print("✓ Formato correcto!")

if __name__ == "__main__":
    try:
        validate_powers_format()
        validate_items_format()
        print("\n" + "="*60)
        print("✓ TODOS LOS FORMATOS VÁLIDOS")
        print("="*60)
    except AssertionError as e:
        print(f"\n✗ ERROR DE VALIDACIÓN: {e}")
    except FileNotFoundError as e:
        print(f"\n✗ ARCHIVO NO ENCONTRADO: {e}")
        print("Ejecuta primero: python scraper.py")
