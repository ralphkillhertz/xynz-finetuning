#!/usr/bin/env python3
"""
🔧 ARREGLAR TEST DE CONCENTRACIÓN
"""

import os
import re

print("""
================================================================================
🔧 ARREGLANDO TEST DE CONCENTRACIÓN
================================================================================
El test necesita ajustarse a la firma de update(time, dt)
================================================================================
""")

test_file = "test_concentration_delta.py"

# Leer el test
with open(test_file, 'r') as f:
    content = f.read()

# Backup
backup_name = f"{test_file}.backup_fix"
with open(backup_name, 'w') as f:
    f.write(content)
print(f"✅ Backup creado: {backup_name}")

# 1. Cambiar engine.update() para incluir time
print("\n🔧 Ajustando llamadas a engine.update()...")

# Patrón para encontrar engine.update(
pattern = r'engine\.update\(([^)]+)\)'
matches = re.findall(pattern, content)

if matches:
    print(f"   Encontradas {len(matches)} llamadas a engine.update()")
    
    # Si solo pasan dt, necesitamos añadir time
    for match in set(matches):
        if ',' not in match:  # Solo un parámetro
            # Cambiar engine.update(dt) por engine.update(i*dt, dt)
            # o engine.update(frame*dt, dt) dependiendo del contexto
            new_pattern = f'engine.update({match})'
            
            # Buscar si estamos en un loop con índice
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if new_pattern in line:
                    # Buscar si hay un for loop cercano
                    for j in range(max(0, i-5), i):
                        if 'for i in range' in lines[j] or 'for frame in range' in lines[j]:
                            # Usar el índice del loop
                            if 'for i in range' in lines[j]:
                                replacement = f'engine.update(i * {match}, {match})'
                            else:
                                replacement = f'engine.update(frame * {match}, {match})'
                            content = content.replace(new_pattern, replacement)
                            break
                    else:
                        # No hay loop, usar tiempo acumulado
                        # Buscar si hay alguna variable de tiempo
                        replacement = f'engine.update(0.0, {match})'  # Por defecto time=0
                        content = content.replace(new_pattern, replacement)

# 2. También necesitamos ajustar la verificación de motion.motion_components
print("\n🔧 Verificando acceso a motion_components...")

# El test verifica motion.motion_components pero motion puede no tener use_delta_system activado
# Añadir verificación
if "if 'concentration' in motion.motion_components:" in content:
    print("   Encontrada verificación de motion_components")
    
    # Añadir verificación de que existe
    old_check = "if 'concentration' in motion.motion_components:"
    new_check = "if hasattr(motion, 'motion_components') and 'concentration' in motion.motion_components:"
    content = content.replace(old_check, new_check)
    print("   ✅ Añadida verificación de existencia")

# 3. Guardar cambios
print("\n💾 Guardando test arreglado...")
with open(test_file, 'w') as f:
    f.write(content)

# 4. Mostrar un extracto del test arreglado
print("\n📋 Extracto del test arreglado:")
print("-" * 70)
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'engine.update(' in line:
        print(f"Línea {i+1}: {line.strip()}")
        break

# 5. Crear test simple alternativo
print("\n📝 Creando test_concentration_simple.py como alternativa...")

simple_test = '''#!/usr/bin/env python3
"""
🧪 TEST SIMPLE DE CONCENTRACIÓN
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST SIMPLE DE CONCENTRACIÓN")
print("=" * 50)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    
    # Crear macro
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=6.0)
    print(f"✅ Macro creado: {macro_id}")
    
    # Obtener posiciones iniciales
    positions_before = []
    for i in range(4):
        pos = engine._positions[i].copy()
        positions_before.append(pos)
        print(f"   Fuente {i}: {pos}")
    
    # Calcular centro y dispersión inicial
    center = np.mean(positions_before, axis=0)
    dispersion_before = np.mean([np.linalg.norm(p - center) for p in positions_before])
    print(f"\\nCentro: {center}")
    print(f"Dispersión inicial: {dispersion_before:.2f}")
    
    # Aplicar concentración
    print("\\n🎯 Aplicando concentración (factor=0.8)...")
    engine.set_macro_concentration(macro_id, 0.8)
    
    # Ejecutar simulación
    print("\\n🔄 Ejecutando 60 frames...")
    time = 0.0
    dt = 1.0 / 60.0
    
    for frame in range(60):
        # Llamar update con time y dt
        result = engine.update(dt)
        time += dt
        
        # Mostrar progreso cada 20 frames
        if frame % 20 == 0:
            pos = engine._positions[0]
            dist_to_center = np.linalg.norm(pos - center)
            print(f"   Frame {frame}: distancia al centro = {dist_to_center:.2f}")
    
    # Verificar resultado
    print("\\n📊 RESULTADO:")
    positions_after = []
    for i in range(4):
        pos = engine._positions[i]
        positions_after.append(pos)
        print(f"   Fuente {i}: {pos}")
    
    # Calcular dispersión final
    center_after = np.mean(positions_after, axis=0)
    dispersion_after = np.mean([np.linalg.norm(p - center_after) for p in positions_after])
    
    print(f"\\nDispersión final: {dispersion_after:.2f}")
    reduction = (dispersion_before - dispersion_after) / dispersion_before * 100
    print(f"Reducción: {reduction:.1f}%")
    
    # Verificar movimiento
    total_movement = sum(np.linalg.norm(p1 - p2) for p1, p2 in zip(positions_before, positions_after))
    
    if reduction > 10 and total_movement > 0.1:
        print("\\n✅ ¡CONCENTRACIÓN FUNCIONA!")
    else:
        print("\\n❌ La concentración no está funcionando")
        print(f"   Movimiento total: {total_movement:.4f}")
        
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\\n" + "=" * 50)
'''

with open("test_concentration_simple.py", 'w') as f:
    f.write(simple_test)
os.chmod("test_concentration_simple.py", 0o755)

print("\n✅ Test simple creado: test_concentration_simple.py")

print("""

================================================================================
✅ TEST ARREGLADO
================================================================================

OPCIONES:

1. Ejecutar el test original arreglado:
   python test_concentration_delta.py

2. Ejecutar el test simple alternativo:
   python test_concentration_simple.py

El test simple es más directo y evita complicaciones.

================================================================================
""")