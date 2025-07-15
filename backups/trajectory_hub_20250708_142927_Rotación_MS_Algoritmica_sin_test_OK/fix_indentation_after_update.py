# === fix_indentation_after_update.py ===
# 🔧 Fix: Corregir indentación después de añadir update()
# ⚡ El método _check_rate_limit tiene mala indentación

import os
import shutil
from datetime import datetime

print("🔧 Corrigiendo indentación en enhanced_trajectory_engine.py...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    lines = f.readlines()

print(f"📄 Total líneas: {len(lines)}")

# Buscar la línea problemática (alrededor de 1906)
if len(lines) > 1905:
    print(f"\nLínea 1906: '{lines[1905].rstrip()}'")
    
    # Ver contexto
    print("\nContexto (líneas 1900-1910):")
    for i in range(max(0, 1899), min(len(lines), 1910)):
        indent = len(lines[i]) - len(lines[i].lstrip())
        print(f"  L{i+1} ({indent}sp): {lines[i].rstrip()[:60]}")

# Arreglar la indentación de _check_rate_limit
for i in range(max(0, 1900), min(len(lines), 1910)):
    if '_check_rate_limit' in lines[i] and 'def' in lines[i]:
        # Asegurar 4 espacios para método de clase
        lines[i] = '    def _check_rate_limit(self) -> bool:\n'
        print(f"\n✅ Línea {i+1} corregida")
        break

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"✅ Backup: {backup_path}")

# Verificar que funciona
print("\n🧪 Verificando import...")
try:
    import sys
    # Limpiar cache
    modules_to_reload = [k for k in sys.modules.keys() if k.startswith('trajectory_hub')]
    for module in modules_to_reload:
        del sys.modules[module]
    
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Ejecutar test
    print("\n🚀 Ejecutando test de engine.update()...")
    import subprocess
    result = subprocess.run(['python', 'test_engine_auto_deltas.py'], 
                          capture_output=True, text=True)
    
    # Mostrar resultados
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        print(lines[0])  # Título
        
        # Mostrar líneas importantes
        for line in lines:
            if any(word in line for word in ['Frame', '✅', '❌', 'ÉXITO', 'RESULTADOS', 'automáticamente']):
                print(line)
    
    if result.stderr and "No se puede crear modulador" not in result.stderr:
        print(f"\n❌ Error: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Intentando arreglo más agresivo...")
    
    # Recargar archivo
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar todos los métodos mal indentados después de update()
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Si es una definición de método con indentación incorrecta
        if stripped.startswith('def ') and i > 1800:
            # Verificar indentación actual
            current_indent = len(line) - len(line.lstrip())
            
            # Si no tiene 4 espacios, corregir
            if current_indent != 4:
                fixed_lines.append('    ' + stripped)
                print(f"  Corregido L{i+1}: {stripped[:50]}")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Guardar versión corregida
    with open(file_path, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("\n✅ Arreglo agresivo aplicado")