# === fix_indentation_update_deltas.py ===
# 🔧 Fix: Corregir indentación en update_with_deltas
# ⚡ Arreglo rápido del docstring

import os
import shutil
from datetime import datetime

print("🔧 Arreglando indentación en update_with_deltas...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar la línea problemática (línea 109)
if len(lines) >= 109:
    print(f"Línea 109: '{lines[108].rstrip()}'")
    
    # Verificar contexto
    print("\nContexto (líneas 105-115):")
    for i in range(max(0, 104), min(len(lines), 115)):
        print(f"  L{i+1}: '{lines[i].rstrip()}'")
    
    # Arreglar la indentación del docstring
    # El docstring debe tener 8 espacios (dentro del método)
    if lines[108].strip().startswith('"""'):
        lines[108] = '        """Actualiza componentes y retorna LISTA de deltas"""\n'
        print("\n✅ Docstring corregido con 8 espacios")

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"✅ Backup: {backup_path}")

# Verificar que funciona
print("\n🧪 Verificando import...")
try:
    import importlib
    import sys
    
    # Limpiar cache
    modules_to_reload = [k for k in sys.modules.keys() if k.startswith('trajectory_hub')]
    for module in modules_to_reload:
        del sys.modules[module]
    
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Ejecutar test
    print("\n🚀 Ejecutando test final...")
    import subprocess
    result = subprocess.run(['python', 'test_individual_trajectory_final.py'], 
                          capture_output=True, text=True)
    
    # Mostrar solo las partes importantes
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        # Mostrar título
        print(lines[0])
        # Mostrar últimas líneas con resultados
        print("\n".join(lines[-15:]))
    
    if result.stderr and "No se puede crear modulador" not in result.stderr:
        print("\nErrores:", result.stderr)
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Intentando arreglo más agresivo...")
    
    # Recargar y buscar el método completo
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar update_with_deltas y asegurar indentación correcta
    update_pos = content.find("def update_with_deltas(self, current_time: float, dt: float) -> list:")
    if update_pos != -1:
        # Encontrar el final del método
        next_def = content.find("\n    def ", update_pos + 1)
        if next_def == -1:
            next_def = len(content)
        
        # Extraer el método
        method_content = content[update_pos:next_def]
        
        # Corregir indentación línea por línea
        fixed_lines = []
        for line in method_content.split('\n'):
            if line.strip():  # No es línea vacía
                if line.strip().startswith('def '):
                    fixed_lines.append('    ' + line.strip())
                elif line.strip().startswith('"""'):
                    fixed_lines.append('        ' + line.strip())
                elif line.strip().startswith('deltas'):
                    fixed_lines.append('        ' + line.strip())
                elif line.strip().startswith('if '):
                    fixed_lines.append('        ' + line.strip())
                elif line.strip().startswith('for '):
                    fixed_lines.append('            ' + line.strip())
                elif line.strip().startswith('return'):
                    fixed_lines.append('        ' + line.strip())
                else:
                    # Contenido dentro de if/for
                    fixed_lines.append('                ' + line.strip())
            else:
                fixed_lines.append('')
        
        # Reemplazar en el contenido
        fixed_method = '\n'.join(fixed_lines)
        content = content[:update_pos] + fixed_method + content[next_def:]
        
        # Guardar
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ Método corregido completamente")