# === fix_macro_rotation_import_engine.py ===
# 🔧 Verificar y corregir el import de MacroRotation
# ⚡ El problema está en el engine, no en la clase

from pathlib import Path

print("🔍 Verificando imports en enhanced_trajectory_engine.py...")

engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

# Buscar imports de motion_components
import_line = content.find("from trajectory_hub.core.motion_components import")
if import_line == -1:
    import_line = content.find("from .motion_components import")

if import_line > 0:
    # Encontrar el final de la línea
    line_end = content.find("\n", import_line)
    current_imports = content[import_line:line_end]
    print(f"Imports actuales: {current_imports}")
    
    if "MacroRotation" not in current_imports:
        print("❌ MacroRotation no está en los imports")
        print("🔧 Añadiendo MacroRotation...")
        
        # Añadir MacroRotation
        new_imports = current_imports.rstrip() + ", MacroRotation"
        content = content[:import_line] + new_imports + content[line_end:]
        
        # Guardar
        engine_path.write_text(content)
        print("✅ Import añadido")
    else:
        print("✅ MacroRotation ya está importada")

# Verificar también en set_macro_rotation
set_macro_pos = content.find("def set_macro_rotation")
if set_macro_pos > 0:
    print("\n🔍 Verificando set_macro_rotation...")
    
    # Buscar dónde se crea MacroRotation
    create_pos = content.find("MacroRotation()", set_macro_pos)
    if create_pos > 0:
        print("✅ MacroRotation() se usa correctamente")
        
        # Ver si hay un import local
        local_import = content.find("from trajectory_hub.core.motion_components import MacroRotation", set_macro_pos)
        if local_import > 0 and local_import < create_pos:
            print("⚠️ Hay un import local duplicado, esto puede causar problemas")

# Test final completo
with open("test_rotation_final_working.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Test final que debería funcionar"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎯 TEST FINAL MacroRotation")
print("=" * 50)

# Crear engine y macro
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("test", source_count=4, formation="square", spacing=4.0)
print(f"✅ Macro creado: {macro_name}")

# Establecer posiciones
positions = [[4,0,0], [0,4,0], [-4,0,0], [0,-4,0]]
for i, pos in enumerate(positions):
    engine._positions[i] = np.array(pos, dtype=np.float32)

print("\\n📍 Posiciones iniciales:")
for i in range(4):
    p = engine._positions[i]
    print(f"  F{i}: [{p[0]:5.1f}, {p[1]:5.1f}, {p[2]:5.1f}]")

# Aplicar rotación
print("\\n🔄 Aplicando rotación...")
try:
    success = engine.set_macro_rotation(macro_name, speed_y=1.0)
    print(f"  Resultado: {success}")
    
    # Simular
    if success:
        print("\\n⏱️ Simulando 30 frames...")
        for i in range(30):
            engine.update()
            
        print("\\n📍 Posiciones finales:")
        for i in range(4):
            p = engine._positions[i]
            print(f"  F{i}: [{p[0]:5.1f}, {p[1]:5.1f}, {p[2]:5.1f}]")
            
        # Verificar movimiento
        moved = any(abs(engine._positions[i][2]) > 0.1 for i in range(4))
        print(f"\\n{'✅ ÉXITO' if moved else '❌ Sin movimiento'}")
        
except Exception as e:
    print(f"\\n❌ Error: {e}")
    
    # Debug del error
    if "set_rotation" in str(e):
        print("\\n🔍 Debug: El problema está en set_macro_rotation del engine")
        print("   Verificar que MacroRotation esté importada correctamente")
''')

print("\n✅ Próximos pasos:")
print("  1. python fix_macro_rotation_import_engine.py")
print("  2. python test_rotation_final_working.py")