# Guía de Uso del Scraper

## 📦 Scraper Mejorado

El scraper ahora genera **directamente** el formato que usa la aplicación, sin necesidad de procesamiento adicional.

## 🚀 Uso

### Ejecutar el scraper:

```bash
python scraper.py
```

Esto hará:

1. ✅ Scrapear datos de https://www.ballxpitguide.com
2. ✅ Descargar todas las imágenes
3. ✅ Generar archivos JSON en formato correcto
4. ✅ Guardar en `config/` directamente

## 📊 Formato de Salida

### `powers.json`

```json
{
	"powers": {
		"1": {
			"name": "Bleed",
			"description": "...",
			"image": "power_1.png",
			"traits": []
		}
	},
	"combos": {
		"1+2": {
			"result": "34",
			"type": "COMBO"
		}
	},
	"combo_powers": {
		"34": {
			"name": "Leech",
			"description": "...",
			"image": "power_36.png",
			"traits": [],
			"is_combo": true,
			"components": ["1", "2"]
		}
	}
}
```

### `items.json`

```json
{
	"items": {
		"Baby Rattle": {
			"name": "Baby Rattle",
			"description": "...",
			"image": "item_3.png",
			"traits": []
		}
	},
	"combos": {},
	"combo_items": {},
	"recommendations": {}
}
```

### `characters.json`

Lista de personajes (formato existente)

## 🔄 Ya NO necesitas `process_scraped_data.py`

El scraper ahora genera directamente el formato correcto. Los pasos son:

1. `python scraper.py` → Genera JSON + descarga imágenes
2. Listo! Los archivos están en `config/` y las imágenes en `assets/`

## ✅ Validar Formato

Puedes validar que el formato sea correcto con:

```bash
python test_scraper_format.py
```

Esto verifica que los JSON tengan la estructura correcta que espera la app.

## 📝 Notas

- **Powers**: Usa IDs numéricos como claves
- **Items**: Usa nombres como claves
- **Combos**: Se generan automáticamente parseando las recetas
- **Imágenes**: Se descargan con nombres secuenciales (`power_1.png`, `item_1.png`, etc.)
