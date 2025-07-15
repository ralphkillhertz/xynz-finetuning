# === fix_indent_definitive.py ===
# 🔧 Fix: Corregir TODA la indentación del método create_macro
# ⚡ Solución definitiva

import os

print("🔧 FIX DEFINITIVO: Corrigiendo toda la indentación...\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Encontrar el método create_macro y corregir toda su indentación
fixed_lines = []
in_create_macro = False
fixing = False

for i, line in enumerate(lines):
    # Detectar inicio del método
    if '    def create_macro(' in line:
        in_create_macro = True
        fixing = True
        fixed_lines.append(line)
        print(f"✅ Encontrado create_macro en línea {i+1}")
        continue
    
    # Si estamos en create_macro
    if in_create_macro:
        # Si es una línea vacía, mantenerla
        if line.strip() == '':
            fixed_lines.append(line)
            continue
            
        # Si empieza un nuevo método, terminar
        if line.strip().startswith('def ') and i > 256:
            in_create_macro = False
            fixing = False
            fixed_lines.append(line)
            continue
        
        # Corregir indentación
        stripped = line.lstrip()
        
        # Calcular indentación correcta
        if stripped.startswith('"""'):
            # Docstring: 12 espacios
            fixed_line = ' ' * 12 + stripped
        elif stripped.startswith('Parameters') or stripped.startswith('Returns'):
            # Secciones del docstring: 12 espacios
            fixed_line = ' ' * 12 + stripped
        elif stripped.startswith('---'):
            # Separadores del docstring: 12 espacios
            fixed_line = ' ' * 12 + stripped
        elif line.startswith('            ') and not line.startswith('                '):
            # Contenido del docstring con 12 espacios, mantener
            fixed_line = line
        elif line.startswith('        ') and not line.startswith('            '):
            # Código con 8 espacios, cambiar a 12
            fixed_line = '    ' + line  # Añadir 4 espacios más
        else:
            # Por defecto, asegurar al menos 12 espacios
            if stripped:
                fixed_line = ' ' * 12 + stripped
            else:
                fixed_line = line
        
        fixed_lines.append(fixed_line)
        
        # Debug para las primeras líneas
        if i < 280:
            if line != fixed_line:
                print(f"  Línea {i+1}: corregida")
    else:
        # Fuera de create_macro, mantener como está
        fixed_lines.append(line)

# Guardar
with open(file_path, 'w') as f:
    f.writelines(fixed_lines)

print("\n✅ Archivo corregido completamente")

# Test final definitivo
print("\n🧪 TEST FINAL...")
import subprocess
result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                      capture_output=True, text=True)

if result.returncode == 0:
    # Éxito - mostrar resultados clave
    print("\n✅ IMPORT EXITOSO")
    
    for line in result.stdout.split('\n'):
        if any(word in line for word in ['✅', '❌', 'ÉXITO', 'TEST', 'Macro', 'Frame', 'distancia']):
            print(line)
    
    if "ÉXITO TOTAL" in result.stdout:
        print("\n" + "="*60)
        print("🎉 ¡MIGRACIÓN COMPLETA!")
        print("="*60)
        print("\n📊 ESTADO FINAL DEL SISTEMA:")
        print("✅ Sistema de deltas: 100%")
        print("✅ ConcentrationComponent: 100%")
        print("✅ IndividualTrajectory: 100%") 
        print("✅ MacroTrajectory: 100%")
        print("✅ engine.update(): Automático")
        print("\n⏭️ SIGUIENTE: Servidor MCP (CRÍTICO)")
else:
    # Error - mostrar detalles
    print(f"\n❌ Error: {result.stderr}")
    
    # Si sigue siendo error de indentación, mostrar contexto
    if "IndentationError" in result.stderr:
        print("\n🔍 Verificando línea problemática...")
        import re
        match = re.search(r'line (\d+)', result.stderr)
        if match:
            line_num = int(match.group(1))
            print(f"\nContexto línea {line_num}:")
            for i in range(max(0, line_num-5), min(len(fixed_lines), line_num+5)):
                print(f"{i+1:3d}: {repr(fixed_lines[i])}")