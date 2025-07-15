# === fix_macro_indent.py ===
# 🔧 Fix: Corregir indentación de _macros
# ⚡ Impacto: CRÍTICO - Bloquea todo

import os

print("🔧 Corrigiendo indentación de _macros...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar la línea problemática
for i, line in enumerate(lines):
    if 'self._macros = {}  # Almacén de macros' in line:
        print(f"✅ Encontrada línea mal indentada: {i+1}")
        
        # Ver líneas alrededor para determinar indentación correcta
        print("\nContexto:")
        for j in range(max(0, i-3), min(len(lines), i+3)):
            print(f"{j+1:4d}: {repr(lines[j])}")
        
        # Corregir indentación (debe ser 8 espacios como motion_states)
        lines[i] = '        self._macros = {}  # Almacén de macros\n'
        break

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print("\n✅ Indentación corregida")

# Test inmediato
print("\n🚀 Probando import...")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Ejecutar test
    import subprocess
    print("\n🧪 Ejecutando test...")
    result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Debug adicional
    print("\n🔍 Verificando estructura de __init__:")
    with open(file_path, 'r') as f:
        content = f.read()
    
    import re
    init_match = re.search(r'def __init__\(.*?\):.*?(?=\n    def)', content, re.DOTALL)
    if init_match:
        init_lines = init_match.group(0).split('\n')
        print("\nPrimeras líneas de __init__:")
        for i, line in enumerate(init_lines[:20]):
            if 'self.' in line:
                print(f"  {i}: {repr(line)}")