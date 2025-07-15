# === fix_all_indentation.py ===
# 🔧 Fix: Buscar y corregir TODOS los errores de indentación
# ⚡ Solución línea por línea

import os
import shutil
from datetime import datetime

print("🔧 Corrigiendo TODOS los errores de indentación...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

# Leer el archivo
with open(file_path, 'r') as f:
    lines = f.readlines()

print(f"📄 Total líneas: {len(lines)}")

# Verificar líneas problemáticas específicas
problem_lines = [416, 721]
print("\n🔍 Verificando líneas problemáticas:")

for line_num in problem_lines:
    if line_num <= len(lines):
        idx = line_num - 1
        line = lines[idx]
        spaces = len(line) - len(line.lstrip())
        print(f"\nLínea {line_num} ({spaces} espacios):")
        print(f"  '{line.rstrip()}'")
        
        # Buscar contexto
        print("  Contexto:")
        for i in range(max(0, idx-3), min(len(lines), idx+2)):
            spaces_ctx = len(lines[i]) - len(lines[i].lstrip())
            print(f"    L{i+1} ({spaces_ctx}sp): {lines[i].rstrip()[:60]}")

# Aplicar correcciones específicas
corrections = {
    415: 4,  # Si línea 416 tiene problema, puede ser que 415 esté mal
    416: 8,  # Contenido de método debe tener 8 espacios
    720: 4,  # def debe tener 4 espacios
    721: 4   # def debe tener 4 espacios
}

for line_num, correct_spaces in corrections.items():
    if line_num <= len(lines):
        idx = line_num - 1
        old_line = lines[idx]
        stripped = old_line.strip()
        if stripped:  # No modificar líneas vacías
            lines[idx] = ' ' * correct_spaces + stripped + '\n'
            print(f"\n✅ Línea {line_num} corregida a {correct_spaces} espacios")

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"\n✅ Archivo corregido")
print(f"📁 Backup: {backup_path}")

# Test rápido de import
print("\n🧪 Probando import...")
try:
    # Limpiar cache de Python
    import sys
    if 'trajectory_hub' in sys.modules:
        del sys.modules['trajectory_hub']
    if 'trajectory_hub.core' in sys.modules:
        del sys.modules['trajectory_hub.core']
    if 'trajectory_hub.core.motion_components' in sys.modules:
        del sys.modules['trajectory_hub.core.motion_components']
    
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ ¡Import exitoso!")
    
except IndentationError as e:
    print(f"❌ Error de indentación: {e}")
    print(f"   En línea: {e.lineno}")
    
    # Intentar arreglo más específico
    print("\n🔧 Aplicando corrección específica...")
    
    # Recargar líneas
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Corregir la línea específica
    if e.lineno and e.lineno <= len(lines):
        idx = e.lineno - 1
        print(f"   Línea {e.lineno}: '{lines[idx].rstrip()}'")
        
        # Determinar indentación correcta basada en el contenido
        stripped = lines[idx].strip()
        if stripped.startswith('def '):
            # Método de clase: 4 espacios
            lines[idx] = '    ' + stripped + '\n'
        elif stripped.startswith('class '):
            # Clase: 0 espacios
            lines[idx] = stripped + '\n'
        else:
            # Contenido de método: 8 espacios mínimo
            lines[idx] = '        ' + stripped + '\n'
        
        # Guardar
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        print("✅ Línea corregida")

# Test final
print("\n🏃 Ejecutando test...")
import subprocess
result = subprocess.run(['python', 'test_individual_fixed.py'], 
                      capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Test ejecutado")
    # Mostrar solo las últimas líneas relevantes
    output_lines = result.stdout.strip().split('\n')
    for line in output_lines[-10:]:
        print(f"  {line}")
else:
    print(f"❌ Error en test: {result.stderr}")
    
    # Si sigue fallando, usar el script de restauración simple
    restore_code = '''# === restore_simple.py ===
import shutil
shutil.copy2("trajectory_hub/core/motion_components.py.backup_20250708_003129", 
             "trajectory_hub/core/motion_components.py")
print("✅ Restaurado a versión con calculate_delta")
'''
    
    with open("restore_simple.py", "w") as f:
        f.write(restore_code)
    
    print("\n⚠️ Si sigue fallando, ejecuta: python restore_simple.py")
    print("   Esto restaurará a la versión anterior con calculate_delta")