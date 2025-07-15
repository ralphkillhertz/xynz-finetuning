#!/usr/bin/env python3
"""
🔧 Fix: Mover import FormationManager a posición correcta
⚡ El import se insertó dentro de otro import multi-línea
"""

import os

# Leer archivo
with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
    content = f.read()

# Quitar el import mal posicionado
content = content.replace("from trajectory_hub.control.managers.formation_manager import FormationManager\n    SourceMotion", "    SourceMotion")

# Buscar dónde insertar correctamente (después del bloque de imports motion_components)
pos = content.find("AdvancedOrientationModulation\n)")
if pos != -1:
    insert_pos = content.find("\n", pos + len("AdvancedOrientationModulation\n)")) + 1
    # Insertar el import
    content = content[:insert_pos] + "from trajectory_hub.control.managers.formation_manager import FormationManager\n" + content[insert_pos:]
    print("✅ Import movido a posición correcta")

# Guardar
with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'w') as f:
    f.write(content)

print("✅ Archivo corregido")