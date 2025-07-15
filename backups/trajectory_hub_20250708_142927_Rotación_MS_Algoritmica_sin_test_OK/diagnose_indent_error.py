# === diagnose_indent_error.py ===
# 🔍 Ver exactamente qué está mal en línea 265
# ⚡ Diagnóstico completo de indentación

import os

print("🔍 DIAGNÓSTICO PROFUNDO: Error línea 265\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Ver más contexto (líneas 255-275)
print("📝 Contexto extendido:")
print("="*60)
for i in range(254, min(275, len(lines))):
    line = lines[i]
    # Mostrar espacios como puntos para ver indentación
    visible_line = line.replace(' ', '·')
    print(f"{i+1:3d}: {visible_line}", end='')
    
    # Marcar problemas potenciales
    if i == 264:  # línea 265 (índice 264)
        if line.strip() == '"""':
            spaces = len(line) - len(line.lstrip())
            print(f"     ^^^ DOCSTRING con {spaces} espacios (debe tener 8)")
print("="*60)

# Verificar estructura del método
print("\n🔍 Verificando estructura del método create_macro:")
in_create_macro = False
method_indent = None

for i in range(250, min(300, len(lines))):
    line = lines[i]
    
    if 'def create_macro(' in line:
        in_create_macro = True
        method_indent = len(line) - len(line.lstrip())
        print(f"✅ Método empieza en línea {i+1} con {method_indent} espacios de indentación")
    
    elif in_create_macro and line.strip() == '"""' and i == 264:
        docstring_indent = len(line) - len(line.lstrip())
        print(f"📝 Docstring en línea {i+1} con {docstring_indent} espacios")
        
        if docstring_indent != method_indent + 4:
            print(f"❌ ERROR: Docstring mal indentado!")
            print(f"   Esperado: {method_indent + 4} espacios")
            print(f"   Actual: {docstring_indent} espacios")

# Crear fix automático
print("\n✅ CREANDO FIX AUTOMÁTICO...")

fix_code = '''# === fix_indent_auto.py ===
import os

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Corregir línea 265 (índice 264)
if lines[264].strip() == '"""':
    lines[264] = '        """\\n'  # 8 espacios
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
        print("\\n🎉 ¡MacroTrajectory MIGRADO EXITOSAMENTE!")
    else:
        # Mostrar output
        print("\\nResultado del test:")
        for line in result.stdout.split('\\n'):
            if line.strip():
                print(f"  {line}")
                
except Exception as e:
    print(f"❌ Error: {e}")
'''

with open("fix_indent_auto.py", "w") as f:
    f.write(fix_code)

print("📝 Fix creado: fix_indent_auto.py")
print("🚀 Ejecuta: python fix_indent_auto.py")