"""
EJEMPLO DE TOOLTIPS CON RECOMENDACIONES EN CADENA
================================================

Este archivo muestra cómo se verían los tooltips en la interfaz
cuando haces hover sobre los poderes.

ESCENARIO 1: Hover sobre "Fuego" (poder básico)
-----------------------------------------------
╔══════════════════════════════════════════════════════════╗
║ === Fuego ===                                            ║
║ Descripción: Poder básico de fuego que causa daño       ║
║                                                          ║
║ --- Combos Posibles ---                                 ║
║ • Con Agua → Vapor                                       ║
║   ⚡ COMBO EN CADENA:                                    ║
║     → Agregar poder 'Rayo' = Nube Eléctrica            ║
║     → Agregar poder 'Viento' = Niebla Densa            ║
║   Poderes base: fuego, agua, rayo                       ║
║                                                          ║
║ • Con Rayo → Plasma                                      ║
║   ⚡ COMBO EN CADENA:                                    ║
║     → Agregar poder 'Agua' = Explosión Térmica         ║
║   Poderes base: fuego, rayo, agua                       ║
╚══════════════════════════════════════════════════════════╝


ESCENARIO 2: Ya tienes Fuego + Agua (creaste Vapor)
---------------------------------------------------
Ahora haces hover sobre "Vapor":

╔══════════════════════════════════════════════════════════╗
║ === Vapor === [COMBO ANIDADO]                           ║
║ Descripción: Niebla caliente que oscurece la visión     ║
║                                                          ║
║ --- Combos Posibles ---                                 ║
║ • Con Rayo → Nube Eléctrica [COMBO ANIDADO]            ║
║   Poderes base: fuego, agua, rayo                       ║
║   ⚡ COMBO EN CADENA:                                    ║
║     → Agregar combo 'Tormenta' = Apocalipsis Eléctrico ║
║                                                          ║
║ • Con Viento → Niebla Densa [COMBO ANIDADO]            ║
║   Poderes base: fuego, agua, viento                     ║
╚══════════════════════════════════════════════════════════╝


ESCENARIO 3: Tienes Fuego, Agua, Rayo
-------------------------------------
Ya creaste Vapor, ahora haces hover sobre "Rayo":

╔══════════════════════════════════════════════════════════╗
║ === Rayo ===                                             ║
║ Descripción: Poder básico de electricidad que paraliza  ║
║                                                          ║
║ --- Combos Posibles ---                                 ║
║ • Con Vapor → Nube Eléctrica [COMBO ANIDADO]           ║
║   Poderes base: fuego, agua, rayo                       ║
║   ⚡ COMBO EN CADENA:                                    ║
║     → Agregar combo 'Tormenta' = Apocalipsis Eléctrico ║
║                                                          ║
║ • Con Fuego → Plasma                                     ║
║   ⚡ COMBO EN CADENA:                                    ║
║     → Agregar poder 'Agua' = Explosión Térmica         ║
║   Poderes base: fuego, rayo, agua                       ║
║                                                          ║
║ • Con Agua → Tormenta                                    ║
║   ⚡ COMBO EN CADENA:                                    ║
║     → Agregar combo 'Nube Eléctrica' = Apocalipsis...  ║
║   Poderes base: agua, rayo                              ║
╚══════════════════════════════════════════════════════════╝


ESCENARIO 4: Tienes Nube Eléctrica y Tormenta
--------------------------------------------
Haces hover sobre "Nube Eléctrica":

╔══════════════════════════════════════════════════════════╗
║ === Nube Eléctrica === [COMBO ANIDADO]                  ║
║ Descripción: Vapor cargado eléctricamente                ║
║                                                          ║
║ --- Combos Posibles ---                                 ║
║ • Con Tormenta → Apocalipsis Eléctrico [COMBO ANIDADO] ║
║   Poderes base: fuego, agua, rayo                       ║
║   🏆 ¡SUPER COMBO FINAL!                                ║
╚══════════════════════════════════════════════════════════╝


CÓMO USAR ESTA INFORMACIÓN:
============================

1. PLANIFICACIÓN TEMPRANA:
   - Al inicio del juego, eliges "Fuego"
   - El tooltip te dice: "Con Agua → Vapor, luego puedes agregar Rayo"
   - Sabes que debes buscar: Agua y Rayo

2. CONSTRUCCIÓN PASO A PASO:
   - Encuentras Agua → Combinas Fuego+Agua = Vapor
   - El tooltip de Vapor te dice: "Agregar Rayo = Nube Eléctrica"
   - Buscas Rayo

3. COMBOS COMPLEJOS:
   - Cuando tienes Nube Eléctrica, el tooltip te dice:
     "Necesitas combo 'Tormenta' (Agua+Rayo)"
   - Ya sabes exactamente qué hacer para el combo final

4. PODERES BASE:
   - El tooltip siempre muestra los poderes base necesarios
   - Ejemplo: "Poderes base: fuego, agua, rayo"
   - Así sabes qué poderes básicos necesitas guardar

VENTAJAS DEL SISTEMA:
=====================

✅ No necesitas memorizar combos
✅ El juego te guía paso a paso
✅ Sabes qué poderes buscar antes de encontrarlos
✅ Puedes planificar builds complejos desde el inicio
✅ Evitas desperdiciar poderes en combos sin salida
"""

print(__doc__)
