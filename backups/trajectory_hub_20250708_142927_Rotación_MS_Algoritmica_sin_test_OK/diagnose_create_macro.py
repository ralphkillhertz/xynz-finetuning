# === diagnose_create_macro.py ===
# 🔍 Ver qué pasa en create_macro
# ⚡ Encontrar por qué no se guarda el macro

import re

print("🔍 DIAGNÓSTICO: create_macro no guarda el macro\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# Buscar create_macro completo
match = re.search(r'def create_macro\(.*?\):.*?(?=\n    def|\Z)', content, re.DOTALL)
if match:
    method = match.group(0)
    print("📝 Método create_macro actual:")
    print("="*60)
    lines = method.split('\n')
    
    # Mostrar líneas numeradas
    for i, line in enumerate(lines):
        print(f"{i+1:3d}: {line}")
        
        # Resaltar líneas importantes
        if '_macros[' in line:
            print("     ^^^ AQUÍ SE GUARDA EL MACRO")
        if 'return' in line:
            print("     ^^^ RETURN")
    print("="*60)

# Buscar la definición de la clase Macro
print("\n\n🔍 Buscando clase Macro:")
macro_class = re.search(r'class Macro.*?(?=\nclass|\Z)', content, re.DOTALL)
if macro_class:
    print("✅ Encontrada:")
    print(macro_class.group(0)[:500] + "...")

# Crear fix directo
print("\n\n✅ CREANDO FIX DIRECTO...")

fix_code = '''# === fix_create_macro_direct.py ===
# 🔧 Fix: Asegurar que create_macro guarde el macro correctamente
# ⚡ Solución directa al problema

import os
import re

print("🔧 Arreglando create_macro...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# Buscar el método create_macro
create_match = re.search(r'def create_macro\\(.*?\\):.*?(?=\\n    def|\\Z)', content, re.DOTALL)
if not create_match:
    print("❌ No se encontró create_macro")
    exit(1)

old_method = create_match.group(0)

# Verificar si ya tiene el código de guardar macro
if "self._macros[macro_id] = Macro(" in old_method or "self._macros[name] = Macro(" in old_method:
    print("✅ create_macro ya guarda el macro")
else:
    print("❌ create_macro NO guarda el macro - arreglando...")
    
    # Buscar dónde insertar el código
    lines = old_method.split('\\n')
    
    # Buscar el return
    return_line_idx = None
    for i, line in enumerate(lines):
        if 'return' in line and ('macro_id' in line or 'name' in line):
            return_line_idx = i
            break
    
    if return_line_idx:
        # Insertar antes del return
        indent = '        '
        
        # Código a insertar
        new_code = [
            '',
            f'{indent}# Crear y guardar el macro',
            f'{indent}from trajectory_hub.core.enhanced_trajectory_engine import Macro',
            f'{indent}macro = Macro(name, source_ids)',
            f'{indent}',
            f'{indent}# Configurar trajectory component',
            f'{indent}from trajectory_hub.core.motion_components import MacroTrajectory',
            f'{indent}trajectory_component = MacroTrajectory()',
            f'{indent}trajectory_component.enabled = False',
            f'{indent}macro.trajectory_component = trajectory_component',
            f'{indent}',
            f'{indent}# Añadir a motion_states de cada fuente',
            f'{indent}for sid in source_ids:',
            f'{indent}    if sid in self.motion_states:',
            f'{indent}        self.motion_states[sid].active_components["macro_trajectory"] = trajectory_component',
            f'{indent}',
            f'{indent}# Guardar el macro',
            f'{indent}if isinstance(source_count, list):',
            f'{indent}    # Si se pasó lista de IDs, usar el primer ID como parte del nombre',
            f'{indent}    macro_id = f"{name}_custom"',
            f'{indent}else:',
            f'{indent}    macro_id = name',
            f'{indent}',
            f'{indent}self._macros[macro_id] = macro',
            f'{indent}logger.info(f"Macro {macro_id} creado con {len(source_ids)} fuentes")',
            '',
        ]
        
        # Insertar
        lines = lines[:return_line_idx] + new_code + lines[return_line_idx:]
        new_method = '\\n'.join(lines)
        
        # Reemplazar en el contenido
        content = content.replace(old_method, new_method)
        
        # Guardar
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ create_macro arreglado")

# Ejecutar test
print("\\n🧪 Ejecutando test...")
import subprocess
result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                      capture_output=True, text=True)

# Mostrar resultados clave
for line in result.stdout.split('\\n'):
    if any(word in line for word in ['✅', '❌', 'ÉXITO', 'Macro', 'creado', 'distancia']):
        print(line)
'''

with open("fix_create_macro_direct.py", "w") as f:
    f.write(fix_code)

print("📝 Fix creado: fix_create_macro_direct.py")
print("🚀 Ejecuta: python fix_create_macro_direct.py")