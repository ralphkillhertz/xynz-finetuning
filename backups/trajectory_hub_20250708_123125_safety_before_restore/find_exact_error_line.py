# === find_exact_error_line.py ===
# 🔍 Localizar la línea exacta del error array ambiguous
# ⚡ Usando la estructura correcta del proyecto

import numpy as np
import sys
import os

# Verificar estructura de archivos
print("📁 Verificando estructura del proyecto...")
print(f"Directorio actual: {os.getcwd()}")
print("\nArchivos Python en el directorio:")
for file in os.listdir('.'):
    if file.endswith('.py'):
        print(f"  - {file}")

# Buscar en subdirectorios
if os.path.exists('core'):
    print("\nArchivos en core/:")
    for file in os.listdir('core'):
        if file.endswith('.py'):
            print(f"  - core/{file}")

print("\n" + "="*50 + "\n")

# Intentar diferentes imports según la estructura
try:
    # Opción 1: archivos en raíz
    from enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from motion_components import SourceMotion, MacroRotation
    print("✅ Imports desde raíz funcionaron")
except:
    try:
        # Opción 2: archivos en core/
        sys.path.append('core')
        from enhanced_trajectory_engine import EnhancedTrajectoryEngine
        from motion_components import SourceMotion, MacroRotation
        print("✅ Imports desde core/ funcionaron")
    except:
        # Opción 3: con prefijo core
        from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        from core.motion_components import SourceMotion, MacroRotation
        print("✅ Imports con core. funcionaron")

# Ahora buscar el error específicamente en el código
print("\n🔍 Buscando comparaciones problemáticas en motion_components.py...")

# Leer el archivo y buscar patrones problemáticos
try:
    # Determinar la ruta correcta
    if os.path.exists('motion_components.py'):
        filepath = 'motion_components.py'
    elif os.path.exists('core/motion_components.py'):
        filepath = 'core/motion_components.py'
    else:
        print("❌ No se encuentra motion_components.py")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    print(f"\n📄 Analizando {filepath} ({len(lines)} líneas)...")
    
    # Buscar patrones problemáticos
    problematic_patterns = [
        'if component.enabled',
        'if self.enabled',
        'if enabled',
        'component.enabled and',
        'self.enabled and',
        'if comp.enabled',
        'if getattr(component, "enabled"',
        'if hasattr(component, "enabled") and component.enabled'
    ]
    
    print("\n🔍 Buscando comparaciones de 'enabled':\n")
    
    found_issues = []
    for i, line in enumerate(lines):
        for pattern in problematic_patterns:
            if pattern in line and 'isinstance' not in line and 'float(' not in line:
                found_issues.append((i+1, line.strip()))
                print(f"Línea {i+1}: {line.strip()}")
    
    # Buscar específicamente en update_with_deltas
    print("\n🔍 Buscando en update_with_deltas:\n")
    in_update_method = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'def update_with_deltas' in line:
            in_update_method = True
            indent_level = len(line) - len(line.lstrip())
            print(f"Encontrado update_with_deltas en línea {i+1}")
            continue
            
        if in_update_method:
            current_indent = len(line) - len(line.lstrip())
            
            # Si volvemos al nivel de indentación original, salimos del método
            if current_indent <= indent_level and line.strip() and not line.strip().startswith('#'):
                break
                
            # Buscar comparaciones problemáticas
            if any(pattern in line for pattern in problematic_patterns):
                print(f"  Línea {i+1}: {line.rstrip()}")
                if 'component.enabled' in line or 'comp.enabled' in line:
                    print(f"    ⚠️ POSIBLE PROBLEMA AQUÍ")
    
    # Buscar en MacroRotation
    print("\n🔍 Buscando en clase MacroRotation:\n")
    in_macro_rotation = False
    
    for i, line in enumerate(lines):
        if 'class MacroRotation' in line:
            in_macro_rotation = True
            print(f"Encontrada clase MacroRotation en línea {i+1}")
            continue
            
        if in_macro_rotation and line.strip().startswith('class '):
            break
            
        if in_macro_rotation:
            if 'self.enabled' in line and '=' in line:
                print(f"  Línea {i+1}: {line.strip()}")
                if 'np.' in line or 'array' in line:
                    print(f"    🔴 PROBLEMA: asignando array a enabled!")
                    
except Exception as e:
    print(f"❌ Error leyendo archivo: {e}")

print("\n" + "="*50)
print("\n💡 Resumen: Buscar líneas donde se compara 'enabled' directamente")
print("   El problema es que 'enabled' es un array en lugar de un bool/float")