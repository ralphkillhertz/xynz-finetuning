#!/usr/bin/env python3
"""Corrección definitiva del problema de MacroRotation"""

from pathlib import Path

print("🔧 Aplicando corrección definitiva...")

# 1. Verificar que no haya imports locales problemáticos en el engine
engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

# Buscar y eliminar cualquier import local de MacroRotation dentro de set_macro_rotation
set_macro_pos = content.find("def set_macro_rotation")
if set_macro_pos > 0:
    # Buscar el final del método
    next_def = content.find("\n    def ", set_macro_pos + 1)
    if next_def == -1:
        next_def = len(content)
    
    method_content = content[set_macro_pos:next_def]
    
    # Buscar imports locales
    if "from trajectory_hub.core.motion_components import MacroRotation" in method_content:
        print("❌ Import local encontrado, eliminando...")
        # Eliminar la línea
        lines = method_content.split('\n')
        new_lines = []
        for line in lines:
            if "from trajectory_hub.core.motion_components import MacroRotation" not in line:
                new_lines.append(line)
        
        new_method = '\n'.join(new_lines)
        content = content[:set_macro_pos] + new_method + content[next_def:]
        
        # Guardar
        engine_path.write_text(content)
        print("✅ Import local eliminado")

print("\n✅ Corrección aplicada")
print("\n📝 IMPORTANTE: Reinicia el terminal de Python y ejecuta:")
print("   python test_rotation_final_working.py")
