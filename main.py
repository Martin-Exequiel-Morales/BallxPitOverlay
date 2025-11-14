"""
Game Power Overlay - Aplicación principal

Un overlay para juegos que ayuda a gestionar combinaciones de poderes e items
con interfaz visual intuitiva, tooltips informativos y recomendaciones inteligentes.

Uso:
    python main.py              # Iniciar overlay gaming

Características:
- Sistema de poderes con combos y fusiones
- Sistema de items con recomendaciones de sets
- Interfaz overlay moderna con DearPyGui
- Tooltips con información detallada
- Análisis y recomendaciones automáticas
"""
import sys
from pathlib import Path

# Agregar path para importar módulos locales
sys.path.append(str(Path(__file__).parent))

from ui import create_overlay


def main():
    """Función principal"""
    # Ayuda
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print(__doc__)
        print("\nOpciones:")
        print("  -h, --help    Mostrar esta ayuda")
        return
    
    # Ejecutar gaming overlay
    print("Iniciando Game Power Overlay...")
    create_overlay()


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
