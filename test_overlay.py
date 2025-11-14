"""
Script de pruebas para verificar todas las funcionalidades del overlay
Prueba los managers, combos, análisis y lógica sin necesidad de UI
"""
import json
from pathlib import Path
from core import PowerManager, ItemManager, ComboEngine


class OverlayTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
        print("\n" + "="*60)
        print("INICIANDO PRUEBAS DEL OVERLAY")
        print("="*60 + "\n")
    
    def test(self, name, condition, error_msg=""):
        """Ejecutar una prueba y registrar resultado"""
        if condition:
            print(f"✓ {name}")
            self.passed += 1
        else:
            print(f"✗ {name}")
            if error_msg:
                print(f"  Error: {error_msg}")
            self.failed += 1
            self.errors.append(name)
    
    def test_data_loading(self):
        """Probar carga de archivos JSON"""
        print("\n[1] PRUEBAS DE CARGA DE DATOS")
        print("-" * 40)
        
        # Verificar archivos existen
        powers_file = Path('config/powers.json')
        items_file = Path('config/items.json')
        chars_file = Path('config/characters.json')
        
        self.test("Archivo powers.json existe", powers_file.exists())
        self.test("Archivo items.json existe", items_file.exists())
        self.test("Archivo characters.json existe", chars_file.exists())
        
        # Verificar estructura JSON
        try:
            with open(powers_file, 'r', encoding='utf-8') as f:
                powers_data = json.load(f)
            self.test("powers.json es JSON válido", True)
            self.test("powers.json tiene sección 'powers'", 'powers' in powers_data)
            self.test("powers.json tiene sección 'combos'", 'combos' in powers_data)
            self.test("powers.json tiene sección 'combo_powers'", 'combo_powers' in powers_data)
            
            powers_count = len(powers_data.get('powers', {}))
            combos_count = len(powers_data.get('combos', {}))
            self.test(f"Poderes básicos cargados ({powers_count})", powers_count > 0, 
                     f"Se esperaban poderes básicos, encontrados: {powers_count}")
            self.test(f"Combos de poderes cargados ({combos_count})", combos_count > 0,
                     f"Se esperaban combos, encontrados: {combos_count}")
        except Exception as e:
            self.test("powers.json es JSON válido", False, str(e))
        
        try:
            with open(items_file, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
            self.test("items.json es JSON válido", True)
            self.test("items.json tiene sección 'items'", 'items' in items_data)
            
            items_count = len(items_data.get('items', {}))
            self.test(f"Items cargados ({items_count})", items_count > 0,
                     f"Se esperaban items, encontrados: {items_count}")
        except Exception as e:
            self.test("items.json es JSON válido", False, str(e))
        
        try:
            with open(chars_file, 'r', encoding='utf-8') as f:
                chars_data = json.load(f)
            self.test("characters.json es JSON válido", True)
            
            if isinstance(chars_data, list):
                chars_count = len(chars_data)
                self.test(f"Personajes cargados ({chars_count})", chars_count > 0,
                         f"Se esperaban personajes, encontrados: {chars_count}")
            else:
                self.test("characters.json es lista", False, "Formato incorrecto")
        except Exception as e:
            self.test("characters.json es JSON válido", False, str(e))
    
    def test_power_manager(self):
        """Probar PowerManager"""
        print("\n[2] PRUEBAS DE POWER MANAGER")
        print("-" * 40)
        
        try:
            pm = PowerManager()
            self.test("PowerManager inicializado", True)
            
            # Probar slots
            self.test("PowerManager tiene 4 slots", len(pm.current_slots) == 4)
            self.test("Slots inicialmente vacíos", all(s is None for s in pm.current_slots))
            
            # Probar obtener poderes
            available = pm.get_available_powers()
            self.test("Obtener poderes disponibles", len(available) > 0,
                     f"Poderes disponibles: {len(available)}")
            
            # Probar agregar poder
            first_power_id = list(pm.powers_data.keys())[0]
            result = pm.add_power_to_slot(first_power_id, 0)
            self.test("Agregar poder a slot 0", result)
            self.test("Poder en slot 0", pm.current_slots[0] == first_power_id)
            
            # Probar información de poder
            power_info = pm.get_power_info(first_power_id)
            self.test("Obtener info de poder", power_info is not None)
            self.test("Info de poder tiene 'name'", 'name' in power_info if power_info else False)
            
            # Probar combos si existen
            if pm.combos_data:
                combo_key = list(pm.combos_data.keys())[0]
                powers = combo_key.split('+')
                
                pm.add_power_to_slot(powers[0], 0)
                pm.add_power_to_slot(powers[1], 1)
                
                can_combine, result_id = pm.can_combine_powers(powers[0], powers[1])
                self.test("Detectar combo válido", can_combine,
                         f"Combo {combo_key} debería ser válido")
                
                if can_combine:
                    result = pm.combine_powers(0, 1)
                    self.test("Ejecutar combo", result is not None)
            
            # Probar deshacer
            pm.undo_last_action()
            self.test("Deshacer acción", True)
            
        except Exception as e:
            self.test("PowerManager funcional", False, str(e))
    
    def test_item_manager(self):
        """Probar ItemManager"""
        print("\n[3] PRUEBAS DE ITEM MANAGER")
        print("-" * 40)
        
        try:
            im = ItemManager()
            self.test("ItemManager inicializado", True)
            
            # Probar slots
            self.test("ItemManager tiene 4 slots", len(im.current_slots) == 4)
            self.test("Slots inicialmente vacíos", all(s is None for s in im.current_slots))
            
            # Probar obtener items
            available = im.get_available_items()
            self.test("Obtener items disponibles", len(available) > 0,
                     f"Items disponibles: {len(available)}")
            
            # Probar agregar item
            first_item_id = list(im.items_data.keys())[0]
            result = im.add_item_to_slot(first_item_id, 0)
            self.test("Agregar item a slot 0", result)
            self.test("Item en slot 0", im.current_slots[0] == first_item_id)
            
            # Probar información de item
            item_info = im.get_item_info(first_item_id)
            self.test("Obtener info de item", item_info is not None)
            self.test("Info de item tiene 'name'", 'name' in item_info if item_info else False)
            
            # Probar deshacer
            im.undo_last_action()
            self.test("Deshacer acción", True)
            
        except Exception as e:
            self.test("ItemManager funcional", False, str(e))
    
    def test_combo_engine(self):
        """Probar ComboEngine"""
        print("\n[4] PRUEBAS DE COMBO ENGINE")
        print("-" * 40)
        
        try:
            pm = PowerManager()
            im = ItemManager()
            ce = ComboEngine(pm, im)
            self.test("ComboEngine inicializado", True)
            
            # Agregar algunos poderes
            power_ids = list(pm.powers_data.keys())[:2]
            for i, pid in enumerate(power_ids):
                pm.add_power_to_slot(pid, i)
            
            # Analizar estado
            analysis = ce.analyze_current_state()
            self.test("Análisis de estado", analysis is not None)
            self.test("Análisis tiene sección 'powers'", 'powers' in analysis)
            self.test("Análisis tiene sección 'items'", 'items' in analysis)
            
            power_analysis = analysis['powers']
            self.test("Análisis de poderes tiene 'filled_slots'", 'filled_slots' in power_analysis)
            self.test("Análisis de poderes tiene 'possible_combos'", 'possible_combos' in power_analysis)
            
        except Exception as e:
            self.test("ComboEngine funcional", False, str(e))
    
    def test_images(self):
        """Verificar imágenes descargadas"""
        print("\n[5] PRUEBAS DE IMÁGENES")
        print("-" * 40)
        
        powers_dir = Path('assets/powers')
        items_dir = Path('assets/items')
        chars_dir = Path('assets/characters')
        
        self.test("Directorio assets/powers existe", powers_dir.exists())
        self.test("Directorio assets/items existe", items_dir.exists())
        self.test("Directorio assets/characters existe", chars_dir.exists())
        
        if powers_dir.exists():
            power_images = list(powers_dir.glob('*.png'))
            self.test(f"Imágenes de poderes ({len(power_images)})", len(power_images) > 0)
        
        if items_dir.exists():
            item_images = list(items_dir.glob('*.png'))
            self.test(f"Imágenes de items ({len(item_images)})", len(item_images) > 0)
        
        if chars_dir.exists():
            char_images = list(chars_dir.glob('*.png'))
            self.test(f"Imágenes de personajes ({len(char_images)})", len(char_images) > 0)
    
    def test_integration(self):
        """Pruebas de integración completas"""
        print("\n[6] PRUEBAS DE INTEGRACIÓN")
        print("-" * 40)
        
        try:
            pm = PowerManager()
            im = ItemManager()
            ce = ComboEngine(pm, im)
            
            # Simular flujo completo: agregar poderes, hacer combo
            power_ids = list(pm.powers_data.keys())[:3]
            
            # Llenar 3 slots
            for i, pid in enumerate(power_ids):
                pm.add_power_to_slot(pid, i)
            
            # Analizar
            analysis = ce.analyze_current_state()
            filled_before = len(analysis['powers']['filled_slots'])
            self.test("Estado inicial con 3 poderes", filled_before == 3)
            
            # Intentar combo si existe
            possible_combos = [c for c in analysis['powers']['possible_combos'] 
                              if c['action_type'] == 'combo']
            
            if possible_combos:
                combo = possible_combos[0]
                # Los slots están en las claves power1 y power2, no power1_slot
                p1 = combo.get('power1')
                p2 = combo.get('power2')
                
                # Encontrar en qué slots están
                p1_slot = pm.current_slots.index(p1) if p1 in pm.current_slots else None
                p2_slot = pm.current_slots.index(p2) if p2 in pm.current_slots else None
                
                if p1_slot is not None and p2_slot is not None:
                    result = pm.combine_powers(p1_slot, p2_slot)
                    self.test("Combo ejecutado correctamente", result is not None)
                    
                    # Re-analizar
                    analysis2 = ce.analyze_current_state()
                    self.test("Análisis después de combo", analysis2 is not None)
                else:
                    print("  ℹ No se pudieron localizar slots para el combo")
            else:
                print("  ℹ No hay combos disponibles para probar integración completa")
            
            # Probar deshacer múltiple
            pm.undo_last_action()
            pm.undo_last_action()
            self.test("Múltiples deshacer", True)
            
            # Limpiar y verificar
            for i in range(len(pm.current_slots)):
                pm.remove_power_from_slot(i)
            
            empty = all(s is None for s in pm.current_slots)
            self.test("Limpiar todos los slots", empty)
            
        except Exception as e:
            self.test("Integración completa", False, str(e))
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        self.test_data_loading()
        self.test_power_manager()
        self.test_item_manager()
        self.test_combo_engine()
        self.test_images()
        self.test_integration()
        
        # Resumen
        print("\n" + "="*60)
        print("RESUMEN DE PRUEBAS")
        print("="*60)
        print(f"✓ Pasadas: {self.passed}")
        print(f"✗ Falladas: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        
        if self.failed > 0:
            print("\nPruebas fallidas:")
            for error in self.errors:
                print(f"  - {error}")
        
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"\nTasa de éxito: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El overlay está funcionando correctamente.")
        elif success_rate >= 80:
            print("\n⚠️  La mayoría de pruebas pasaron, pero hay algunos problemas menores.")
        else:
            print("\n❌ Múltiples pruebas fallaron. Revisa los errores arriba.")
        
        print("")
        return success_rate == 100


def main():
    tester = OverlayTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
