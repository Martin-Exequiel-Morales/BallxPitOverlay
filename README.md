# Game Power Overlay

Overlay para juegos que ayuda a gestionar combinaciones de poderes e items con interfaz gaming moderna usando DearPyGui.

## 🎮 Características

### Sistema de Poderes

- **4 slots de poderes** configurables por personaje
- **Poder por defecto** según el personaje seleccionado
- **Combos anidados**: Soporta combo+poder y combo+combo
- **Recomendaciones inteligentes**:
  - Detecta el mejor path hacia combos complejos
  - Muestra combos futuros posibles
  - Calcula poderes base necesarios
- **Grupos de color** para visualizar qué poderes se pueden combinar
- **Menú contextual** con prioridades:
  - ⭐🔥 Poderes que se combinan con los actuales
  - 🔥🔥 Combos anidados
  - 🔥 Combos simples
  - ⚪ Sin combos

### Sistema de Items

- **4 slots de items** independientes
- **Recomendaciones de sets**
- Sistema extensible para combos futuros

### Interfaz Gaming

- **DearPyGui** - UI moderna estilo gaming
- **Always-on-top** overlay
- **Tema oscuro** optimizado
- **Tooltips informativos** (próximamente)
- **Carga de imágenes** (próximamente)

## 📦 Instalación

1. **Python 3.14+** requerido

2. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

3. **Ejecutar overlay**:

```bash
python main.py
```

## 🚀 Uso

1. Selecciona tu personaje del dropdown
2. Click en slots para ver poderes disponibles
3. Los poderes recomendados aparecen con 💡
4. Los poderes que se combinan tienen el mismo color de borde
5. El menú muestra primero los poderes más útiles (⭐🔥)

## 🛠️ Actualizar Datos

Para actualizar poderes e items desde una fuente externa:

```bash
python scraper.py
python process_scraped_data.py
```

## 📁 Estructura del Proyecto

```
├── main.py                      # Punto de entrada
├── requirements.txt             # Dependencias
│
├── core/                        # Lógica de negocio
│   ├── power_manager.py         # Datos y validación de poderes
│   ├── item_manager.py          # Datos de items
│   ├── state_manager.py         # Estado de slots e historial
│   └── recommendation_engine.py # Motor de recomendaciones
│
├── ui/                          # Interfaz
│   └── gaming_overlay.py        # Gaming UI (DearPyGui)
│
├── config/                      # Configuración JSON
│   ├── powers.json              # Poderes y combos
│   ├── items.json               # Items
│   └── characters.json          # Personajes
│
├── assets/                      # Recursos visuales
│   ├── powers/                  # Imágenes de poderes
│   ├── items/                   # Imágenes de items
│   └── characters/              # Imágenes de personajes
│
└── utils/                       # Utilidades
    ├── scraper.py               # Scraper de datos
    └── process_scraped_data.py  # Procesador
```

## 🏗️ Arquitectura

### Separación de Responsabilidades (SOLID)

**PowerManager** → Solo datos y validación

- Carga configuración
- Valida combos
- Provee información de poderes

**StateManager** → Solo estado

- Gestiona slots de poderes/items
- Historial con undo (20 estados)
- API limpia para UI

**RecommendationEngine** → Solo lógica

- Calcula recomendaciones
- Encuentra paths óptimos
- Menús contextuales con prioridades

**GamingOverlay** → Solo UI

- Renderizado con DearPyGui
- Eventos de usuario
- Actualización de vistas

## 📝 Configuración JSON

### Powers (`config/powers.json`)

```json
{
	"powers": {
		"1": { "name": "Fire", "description": "..." }
	},
	"combo_powers": {
		"10": { "name": "Fireball", "components": ["1", "2"] }
	},
	"combos": {
		"1+2": { "result": "10" }
	}
}
```

### Characters (`config/characters.json`)

```json
[
	{
		"name": "The Warrior",
		"starting_power": "Bleed"
	}
]
```

## 🎯 Roadmap

- [x] Sistema de recomendaciones inteligente
- [x] Grupos de color para combos
- [x] Menú contextual priorizado
- [x] Refactorización SOLID
- [x] UI gaming con DearPyGui
- [ ] Tooltips informativos
- [ ] Carga de imágenes
- [ ] Animaciones y efectos
- [ ] Sistema de items completo
- [ ] Guardado de builds

## 📚 Documentación

- `REFACTORIZACION_COMPLETADA.md` - Detalles de arquitectura
- `LIMPIEZA_PROYECTO.md` - Cambios recientes
- `ANALISIS_LOGICA_CORE.md` - Análisis técnico
- `GUIA_SCRAPER_NUEVO.md` - Uso del scraper

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch
3. Commit tus cambios
4. Push al branch
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto.
