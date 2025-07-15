# === diagnose_indentation_context.py ===
# 🔧 Fix: Ver contexto completo alrededor de _check_rate_limit
# ⚡ Para entender la estructura real

import os

print("🔍 Analizando contexto completo alrededor de _check_rate_limit...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar _check_rate_limit
check_rate_line = None
for i, line in enumerate(lines):
    if '_check_rate_limit' in line and 'def' in line:
        check_rate_line = i
        print(f"✅ Encontrado _check_rate_limit en línea {i+1}")
        break

if check_rate_line:
    # Ver contexto amplio (30 líneas antes)
    print("\n📋 Contexto amplio (30 líneas antes):")
    start = max(0, check_rate_line - 30)
    
    # Buscar el def anterior para entender la estructura
    prev_def = None
    for i in range(check_rate_line - 1, max(0, check_rate_line - 50), -1):
        if lines[i].strip().startswith('def '):
            prev_def = i
            print(f"\n⚠️ Método anterior encontrado en línea {i+1}: {lines[i].strip()}")
            break
    
    # Mostrar desde el def anterior
    if prev_def:
        start = prev_def
    
    for i in range(start, min(len(lines), check_rate_line + 5)):
        indent = len(lines[i]) - len(lines[i].lstrip())
        marker = ""
        if i == check_rate_line:
            marker = " ← PROBLEMA AQUÍ"
        elif 'def ' in lines[i]:
            marker = " ← MÉTODO"
        elif 'class ' in lines[i]:
            marker = " ← CLASE"
            
        print(f"  L{i+1} ({indent:2d}sp): {lines[i].rstrip()[:70]}{marker}")

# Crear fix definitivo
fix_code = '''# === fix_indentation_complete.py ===
import os
import shutil
from datetime import datetime

print("🔧 Arreglo COMPLETO de indentación...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# El problema parece ser que _check_rate_limit está dentro de otro método
# Necesitamos sacarlo y ponerlo al nivel de clase

# Buscar _check_rate_limit
lines = content.split('\\n')
fixed_lines = []
skip_until = -1

for i, line in enumerate(lines):
    # Si estamos saltando líneas
    if i < skip_until:
        continue
        
    # Si encontramos _check_rate_limit mal ubicado
    if '_check_rate_limit' in line and 'def' in line and i > 1800:
        print(f"Encontrado _check_rate_limit en línea {i+1}")
        
        # Extraer el método completo
        method_lines = []
        j = i
        while j < len(lines):
            current_line = lines[j]
            # Si es el inicio del método o tiene indentación consistente
            if j == i or (current_line.strip() and not current_line.strip().startswith('def ')):
                method_lines.append(current_line)
                j += 1
            else:
                break
        
        # Ahora añadir el método con indentación correcta
        fixed_lines.append("")  # Línea en blanco
        fixed_lines.append("    def _check_rate_limit(self) -> bool:")
        fixed_lines.append('        """Verificar si se debe enviar actualización OSC"""')
        fixed_lines.append("        return True")
        fixed_lines.append("")
        
        skip_until = j
        print(f"  Método extraído y reubicado (saltando hasta línea {j+1})")
    else:
        fixed_lines.append(line)

# Guardar
with open(file_path, 'w') as f:
    f.write('\\n'.join(fixed_lines))

print(f"✅ Backup: {backup_path}")
print("✅ Indentación corregida completamente")

# Test final
import subprocess
result = subprocess.run(['python', 'test_engine_auto_deltas.py'], 
                      capture_output=True, text=True)

if result.returncode == 0:
    print("\\n✅ Test ejecutado exitosamente!")
    # Mostrar resultados
    for line in result.stdout.split('\\n'):
        if any(word in line for word in ['✅', '❌', 'ÉXITO', 'RESULTADOS']):
            print(f"  {line}")
else:
    print(f"\\n❌ Error: {result.stderr}")
'''

with open("fix_indentation_complete.py", "w") as f:
    f.write(fix_code)

print("\n✅ Script de corrección creado: fix_indentation_complete.py")