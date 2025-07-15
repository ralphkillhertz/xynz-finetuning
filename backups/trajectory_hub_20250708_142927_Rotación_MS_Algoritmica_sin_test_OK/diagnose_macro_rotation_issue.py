# === diagnose_macro_rotation_issue.py ===
# 🔧 Diagnóstico profundo del problema
# ⚡ Por qué MacroRotation no tiene set_rotation en el engine

from pathlib import Path
import importlib
import sys

print("🔍 DIAGNÓSTICO PROFUNDO: MacroRotation")
print("=" * 60)

# 1. Verificar qué MacroRotation se está importando
print("\n1️⃣ Verificando imports...")
try:
    from trajectory_hub.core.motion_components import MacroRotation
    print(f"✅ MacroRotation importada")
    print(f"   Ubicación: {MacroRotation.__module__}")
    print(f"   Métodos: {[m for m in dir(MacroRotation()) if not m.startswith('_')]}")
    
    # Verificar set_rotation
    mr = MacroRotation()
    if hasattr(mr, 'set_rotation'):
        print("   ✅ set_rotation existe en la importación directa")
    else:
        print("   ❌ set_rotation NO existe en la importación directa")
        
except Exception as e:
    print(f"❌ Error importando: {e}")

# 2. Verificar el archivo motion_components.py
print("\n2️⃣ Verificando archivo motion_components.py...")
file_path = Path("trajectory_hub/core/motion_components.py")
content = file_path.read_text()

# Buscar la clase MacroRotation
class_pos = content.find("class MacroRotation")
if class_pos > 0:
    print("✅ Clase MacroRotation encontrada")
    
    # Buscar set_rotation
    set_rot_pos = content.find("def set_rotation", class_pos)
    next_class = content.find("\nclass ", class_pos + 1)
    
    if set_rot_pos > 0 and (next_class == -1 or set_rot_pos < next_class):
        print("✅ Método set_rotation encontrado en el archivo")
        
        # Verificar indentación
        line_start = content.rfind('\n', 0, set_rot_pos) + 1
        indent = set_rot_pos - line_start
        print(f"   Indentación: {indent} espacios")
    else:
        print("❌ Método set_rotation NO encontrado en el archivo")

# 3. Verificar en set_macro_rotation del engine
print("\n3️⃣ Verificando uso en engine...")
engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
engine_content = engine_path.read_text()

set_macro_rot = engine_content.find("def set_macro_rotation")
if set_macro_rot > 0:
    # Buscar dónde se crea MacroRotation
    create_pos = engine_content.find("MacroRotation()", set_macro_rot)
    if create_pos > 0:
        print("✅ MacroRotation() se crea en set_macro_rotation")
        
        # Ver si hay un import local problemático
        local_import_start = engine_content.rfind("from", set_macro_rot, create_pos)
        local_import_end = engine_content.find("\n", local_import_start)
        if local_import_start > set_macro_rot:
            local_import = engine_content[local_import_start:local_import_end]
            print(f"⚠️ Import local encontrado: {local_import}")

# 4. Solución: Recargar el módulo
print("\n4️⃣ Recargando módulos...")
try:
    # Recargar motion_components
    if 'trajectory_hub.core.motion_components' in sys.modules:
        importlib.reload(sys.modules['trajectory_hub.core.motion_components'])
        print("✅ motion_components recargado")
    
    # Recargar engine
    if 'trajectory_hub.core.enhanced_trajectory_engine' in sys.modules:
        importlib.reload(sys.modules['trajectory_hub.core.enhanced_trajectory_engine'])
        print("✅ enhanced_trajectory_engine recargado")
        
except Exception as e:
    print(f"⚠️ Error recargando: {e}")

# 5. Crear script de corrección definitiva
with open("fix_macro_rotation_definitive.py", "w") as f:
    f.write('''#!/usr/bin/env python3
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
    next_def = content.find("\\n    def ", set_macro_pos + 1)
    if next_def == -1:
        next_def = len(content)
    
    method_content = content[set_macro_pos:next_def]
    
    # Buscar imports locales
    if "from trajectory_hub.core.motion_components import MacroRotation" in method_content:
        print("❌ Import local encontrado, eliminando...")
        # Eliminar la línea
        lines = method_content.split('\\n')
        new_lines = []
        for line in lines:
            if "from trajectory_hub.core.motion_components import MacroRotation" not in line:
                new_lines.append(line)
        
        new_method = '\\n'.join(new_lines)
        content = content[:set_macro_pos] + new_method + content[next_def:]
        
        # Guardar
        engine_path.write_text(content)
        print("✅ Import local eliminado")

print("\\n✅ Corrección aplicada")
print("\\n📝 IMPORTANTE: Reinicia el terminal de Python y ejecuta:")
print("   python test_rotation_final_working.py")
''')

print("\n✅ Diagnóstico completo")
print("\n📝 Próximos pasos:")
print("  1. python fix_macro_rotation_definitive.py")
print("  2. REINICIAR el terminal/kernel de Python")
print("  3. python test_rotation_final_working.py")