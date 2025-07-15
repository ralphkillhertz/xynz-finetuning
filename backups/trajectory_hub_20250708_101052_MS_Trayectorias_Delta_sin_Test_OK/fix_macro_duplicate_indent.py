# === fix_macro_duplicate_indent.py ===
# 🔧 Fix: Eliminar duplicado y corregir indentación
# ⚡ Impacto: CRÍTICO - Arregla sintaxis

import os

print("🔧 Corrigiendo líneas duplicadas y mal indentadas...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar y eliminar duplicados
fixed_lines = []
macro_line_found = False

for i, line in enumerate(lines):
    if 'self._macros = {}  # Almacén de macros' in line:
        if not macro_line_found:
            # Primera vez: corregir indentación
            fixed_lines.append('        self._macros = {}  # Almacén de macros\n')
            macro_line_found = True
            print(f"✅ Línea {i+1}: Corregida indentación")
        else:
            # Duplicado: saltar
            print(f"❌ Línea {i+1}: Eliminada (duplicada)")
    else:
        fixed_lines.append(line)

# Guardar
with open(file_path, 'w') as f:
    f.writelines(fixed_lines)

print("\n✅ Archivo corregido")

# Test final
print("\n🧪 Ejecutando test completo...")
import subprocess
result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                      capture_output=True, text=True)

# Mostrar solo líneas importantes
for line in result.stdout.split('\n'):
    if any(word in line for word in ['TEST', '✅', '❌', 'ÉXITO', 'Verificando', 'Creando', 'Frame', 'distancia']):
        print(line)

if "ÉXITO TOTAL" in result.stdout:
    print("\n🎉 ¡MacroTrajectory MIGRADO EXITOSAMENTE!")
elif result.stderr:
    print(f"\n❌ Error: {result.stderr}")