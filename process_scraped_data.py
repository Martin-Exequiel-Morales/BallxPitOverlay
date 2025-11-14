"""
Procesador de datos scrapeados para convertirlos al formato del overlay
Convierte powers.json, items.json y characters.json scrapeados al formato compatible
"""
import json
from pathlib import Path
from typing import Dict, List, Set


class DataProcessor:
    def __init__(self):
        self.scraped_dir = Path('config')
        self.backup_dir = Path('config/scraped_backup')
        self.backup_dir.mkdir(exist_ok=True)
    
    def backup_file(self, filename: str):
        """Hacer backup del archivo scrapeado original"""
        source = self.scraped_dir / filename
        if source.exists():
            # Solo hacer backup si no existe o si el archivo fuente es lista (formato scrapeado)
            dest = self.backup_dir / f"{filename}.original"
            if not dest.exists():
                import shutil
                shutil.copy(source, dest)
                print(f"  ✓ Backup: {filename} -> scraped_backup/{filename}.original")
    
    def process_powers(self):
        """
        Procesar powers.json scrapeado y convertir al formato del overlay
        
        Estructura esperada por overlay:
        {
          "powers": { "power_id": {...} },
          "combos": { "power1+power2": {"result": "combo_id"} },
          "combo_powers": { "combo_id": {"components": [...], ...} }
        }
        """
        print("\n=== Procesando Powers ===")
        
        # Cargar datos scrapeados
        scraped_path = self.scraped_dir / 'powers.json'
        if not scraped_path.exists():
            print("✗ powers.json no encontrado")
            return
        
        with open(scraped_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        # Si ya está procesado, usar backup original
        if isinstance(file_data, dict) and 'powers' in file_data:
            print("  ℹ powers.json ya procesado, usando backup original")
            backup_path = self.backup_dir / 'powers.json.original'
            if not backup_path.exists():
                print("  ✗ No hay backup original, abortando")
                return
            with open(backup_path, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
        else:
            scraped_data = file_data
        
        # Hacer backup
        self.backup_file('powers.json')
        
        # Estructuras para el overlay
        powers = {}
        combos = {}
        combo_powers = {}
        
        # Primera pasada: identificar poderes básicos y combos
        for power in scraped_data:
            power_id = power['id']
            power_name = power['name']
            evolution_recipe = power.get('evolution_recipe')
            
            power_data = {
                'name': power_name,
                'description': power['description'],
                'image': power.get('icon', ''),
                'traits': power.get('traits', [])
            }
            
            # Si no tiene receta, es un poder básico
            if not evolution_recipe:
                powers[power_id] = power_data
            else:
                # Es un combo - parsear la receta
                components = self._parse_recipe(evolution_recipe, scraped_data)
                
                if components:
                    # Guardar como combo power
                    power_data['is_combo'] = True
                    power_data['components'] = components
                    combo_powers[power_id] = power_data
                    
                    # Crear entrada en combos
                    combo_key = '+'.join(components)
                    combos[combo_key] = {
                        'result': power_id,
                        'type': 'TRIPLE' if len(components) == 3 else 'COMBO'
                    }
                    
                    print(f"  ✓ Combo: {combo_key} -> {power_name}")
                else:
                    # No se pudo parsear, guardar como poder básico
                    powers[power_id] = power_data
                    print(f"  ⚠ No se pudo parsear receta de '{power_name}': {evolution_recipe}")
        
        # Guardar resultado
        result = {
            'powers': powers,
            'combos': combos,
            'combo_powers': combo_powers
        }
        
        output_path = self.scraped_dir / 'powers.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Procesado completo:")
        print(f"  - Poderes básicos: {len(powers)}")
        print(f"  - Combos: {len(combos)}")
        print(f"  - Combo powers: {len(combo_powers)}")
    
    def _parse_recipe(self, recipe: str, all_powers: List[Dict]) -> List[str]:
        """
        Parsear receta de evolución y obtener IDs de componentes
        
        Ejemplos:
        - "Poison + Earthquake" -> ["123", "456"]
        - "Vampire + Burn + Bleed" -> ["234", "3", "1"]
        - "Iron+Ghost/Iron+Dark" -> ["iron_id", "ghost_id"] (usa primera opción)
        """
        # Si hay múltiples recetas (separadas por /), usar la primera
        if '/' in recipe:
            recipes = recipe.split('/')
            print(f"    ℹ Receta múltiple detectada, usando: {recipes[0].strip()}")
            recipe = recipes[0].strip()
        
        # Dividir por + y limpiar espacios
        component_names = [c.strip() for c in recipe.split('+')]
        
        # Crear mapeo nombre -> id
        name_to_id = {p['name']: p['id'] for p in all_powers}
        
        # Convertir nombres a IDs
        component_ids = []
        for name in component_names:
            if name in name_to_id:
                component_ids.append(name_to_id[name])
            else:
                print(f"    ⚠ Componente no encontrado: {name}")
                return []
        
        return component_ids
    
    def process_items(self):
        """
        Procesar items.json scrapeado y convertir al formato del overlay
        
        Estructura esperada:
        {
          "items": { "item_name": {...} },
          "combos": { "item1+item2": {"result": "combo_name"} },
          "combo_items": { "combo_name": {"components": [...], ...} }
        }
        """
        print("\n=== Procesando Items ===")
        
        scraped_path = self.scraped_dir / 'items.json'
        if not scraped_path.exists():
            print("✗ items.json no encontrado")
            return
        
        with open(scraped_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        # Si ya está procesado, usar backup original
        if isinstance(file_data, dict) and 'items' in file_data:
            print("  ℹ items.json ya procesado, usando backup original")
            backup_path = self.backup_dir / 'items.json.original'
            if not backup_path.exists():
                print("  ✗ No hay backup original, abortando")
                return
            with open(backup_path, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
        else:
            scraped_data = file_data
        
        self.backup_file('items.json')
        
        items = {}
        combos = {}
        combo_items = {}
        
        for item in scraped_data:
            item_name = item['name']
            item_type = item.get('type', 'Basic')
            recipe = item.get('recipe')
            
            item_data = {
                'name': item_name,
                'description': item['description'],
                'image': item.get('icon', ''),
                'traits': item.get('traits', [])
            }
            
            # Si es básico o no tiene receta
            if item_type == 'Basic' or not recipe:
                items[item_name] = item_data
            else:
                # Es un combo evolucionado
                components = recipe  # Ya viene como lista de nombres
                
                if components and len(components) >= 2:
                    # Guardar como combo item
                    item_data['is_combo'] = True
                    item_data['components'] = components
                    combo_items[item_name] = item_data
                    
                    # Crear entrada en combos
                    combo_key = '+'.join(components)
                    combo_type = 'QUAD' if len(components) == 4 else 'TRIPLE' if len(components) == 3 else 'COMBO'
                    
                    combos[combo_key] = {
                        'result': item_name,
                        'type': combo_type
                    }
                    
                    print(f"  ✓ {combo_type}: {combo_key} -> {item_name}")
                else:
                    items[item_name] = item_data
        
        # Guardar resultado
        result = {
            'items': items,
            'combos': combos,
            'combo_items': combo_items,
            'recommendations': {}  # Vacío por ahora, se puede llenar manualmente
        }
        
        output_path = self.scraped_dir / 'items.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Procesado completo:")
        print(f"  - Items básicos: {len(items)}")
        print(f"  - Combos: {len(combos)}")
        print(f"  - Combo items: {len(combo_items)}")
    
    def process_characters(self):
        """
        Procesar characters.json (ya está en buen formato, solo verificar)
        """
        print("\n=== Verificando Characters ===")
        
        scraped_path = self.scraped_dir / 'characters.json'
        if not scraped_path.exists():
            print("✗ characters.json no encontrado")
            return
        
        with open(scraped_path, 'r', encoding='utf-8') as f:
            characters = json.load(f)
        
        print(f"✓ {len(characters)} personajes cargados")
        print(f"  - Ejemplo: {characters[0]['name']} ({characters[0]['difficulty']})")
        
        # Characters ya está en buen formato (lista), no requiere procesamiento
        print("  ✓ Formato correcto para characters.json")
    
    def process_all(self):
        """Procesar todos los archivos"""
        print("\n" + "="*60)
        print("PROCESANDO DATOS SCRAPEADOS")
        print("="*60)
        
        self.process_powers()
        self.process_items()
        self.process_characters()
        
        print("\n" + "="*60)
        print("PROCESAMIENTO COMPLETO")
        print("="*60)
        print("\n✓ Los archivos JSON ahora son compatibles con el overlay")
        print("✓ Backups guardados en config/scraped_backup/")
        print("\nPróximos pasos:")
        print("1. Revisar config/powers.json y config/items.json")
        print("2. Ejecutar main.py para probar el overlay con datos reales")


def main():
    processor = DataProcessor()
    processor.process_all()


if __name__ == "__main__":
    main()
