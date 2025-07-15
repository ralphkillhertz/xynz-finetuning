# === fix_indent_auto.py ===
import os

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Corregir línea 265 (índice 264)
if lines[264].strip() == '"""':
    lines[264] = '        """\n'  # 8 espacios
    print("✅ Línea 265 corregida")

# Verificar que las siguientes líneas del docstring estén bien indentadas
for i in range(265, min(280, len(lines))):
    if lines[i].strip() and not lines[i].startswith('        '):
        # Si no está vacía y no tiene 8 espacios, corregir
        lines[i] = '        ' + lines[i].lstrip()

with open(file_path, 'w') as f:
    f.writelines(lines)

print("✅ Indentación corregida")

# Test
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Ejecutar test completo
    import subprocess
    result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                          capture_output=True, text=True)
    
    if "ÉXITO TOTAL" in result.stdout:
        print("\n🎉 ¡MacroTrajectory MIGRADO EXITOSAMENTE!")
    else:
        # Mostrar output
        print("\nResultado del test:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"  {line}")
                
except Exception as e:
    print(f"❌ Error: {e}")
