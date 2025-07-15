#!/usr/bin/env python3
"""
🔍 INSPECCIONAR SOURCEMOTION ACTUAL
"""

import os

print("""
================================================================================
🔍 INSPECCIONANDO SOURCEMOTION
================================================================================
""")

motion_file = "trajectory_hub/core/motion_components.py"

with open(motion_file, 'r') as f:
    lines = f.readlines()

# Buscar SourceMotion
found = False
in_init = False
in_update = False
line_count = 0

print("📋 Contenido relevante de SourceMotion:")
print("=" * 70)

for i, line in enumerate(lines):
    # Buscar clase
    if 'class SourceMotion' in line and not line.strip().startswith('#'):
        found = True
        line_count = 0
        print(f"\n{i+1:4d}: {line}", end='')
        continue
    
    if found:
        line_count += 1
        
        # Mostrar primeras líneas de la clase
        if line_count < 5:
            print(f"{i+1:4d}: {line}", end='')
        
        # Buscar __init__
        if 'def __init__(self' in line:
            in_init = True
            print(f"\n{i+1:4d}: {line}", end='')
            continue
        
        # Mostrar contenido de __init__
        if in_init:
            print(f"{i+1:4d}: {line}", end='')
            
            # Buscar atributos importantes
            if 'motion_components' in line:
                print("      ^^^^^ ✅ TIENE motion_components")
            
            # Detectar fin de __init__
            if line.strip() and not line.startswith('        '):
                in_init = False
                
        # Buscar update
        if 'def update(self' in line and not in_init:
            in_update = True
            print(f"\n{i+1:4d}: {line}", end='')
            
            # Ver si acepta dt
            if ', dt' in line or 'dt:' in line:
                print("      ^^^^^ ✅ ACEPTA dt")
            else:
                print("      ^^^^^ ❌ NO ACEPTA dt")
            
            # Mostrar siguientes 5 líneas
            for j in range(1, 6):
                if i+j < len(lines):
                    print(f"{i+j+1:4d}: {lines[i+j]}", end='')
            break

print("\n" + "=" * 70)

# Crear un mini test inline
print("\n🧪 TEST RÁPIDO:")
print("-" * 50)

test = '''
try:
    from trajectory_hub.core.motion_components import SourceMotion
    # Ver qué requiere __init__
    import inspect
    sig = inspect.signature(SourceMotion.__init__)
    print(f"SourceMotion.__init__ requiere: {sig}")
    
    # Intentar crear con source_id
    m = SourceMotion(source_id=0)
    print(f"✅ Creada instancia con source_id=0")
    
    # Verificar atributos
    if hasattr(m, 'motion_components'):
        print(f"✅ Tiene motion_components: {type(m.motion_components)}")
    else:
        print("❌ NO tiene motion_components")
        
except Exception as e:
    print(f"❌ Error: {e}")
'''

exec(test)

print("""

================================================================================
📋 DIAGNÓSTICO
================================================================================

Si NO tiene motion_components, ejecuta:
python direct_sourcemotion_fix.py

Si el __init__ requiere source_id, el test debe usar:
SourceMotion(source_id=0)

================================================================================
""")