#!/usr/bin/env python3
"""
🔍 BUSCAR EXACTAMENTE DÓNDE SE ACTUALIZA _positions
"""

import os
import re

print("""
================================================================================
🔍 BUSCANDO ACTUALIZACIÓN DE _positions
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"📋 Total líneas: {len(lines)}")

# Buscar todas las líneas donde se asigna a _positions[sid]
print("\n📍 TODAS LAS ASIGNACIONES A _positions[sid]:")
positions_updates = []

for i, line in enumerate(lines):
    if 'self._positions[sid] =' in line and not line.strip().startswith('#'):
        positions_updates.append(i)
        print(f"\n   Línea {i+1}: {line.strip()}")
        # Mostrar contexto
        print("   Contexto:")
        for j in range(max(0, i-3), min(len(lines), i+3)):
            marker = ">>>" if j == i else "   "
            print(f"   {marker} {j+1}: {lines[j].rstrip()}")

# Buscar específicamente en el método update
print("\n\n🔍 BUSCANDO EN MÉTODO update():")
in_update = False
update_start = -1

for i, line in enumerate(lines):
    if 'def update(' in line and 'self' in line:
        in_update = True
        update_start = i
        print(f"✅ Método update() encontrado en línea {i+1}")
        break

if in_update:
    # Buscar todas las actualizaciones dentro de update()
    indent = len(lines[update_start]) - len(lines[update_start].lstrip())
    
    print("\n📍 Asignaciones a _positions dentro de update():")
    for i in range(update_start, len(lines)):
        line = lines[i]
        
        # Si salimos del método, parar
        if line.strip() and (len(line) - len(line.lstrip())) <= indent and i > update_start:
            if 'def ' in line or 'class ' in line:
                break
        
        # Si encontramos asignación a _positions
        if 'self._positions[sid] =' in line and not line.strip().startswith('#'):
            print(f"\n   Línea {i+1}: {line.strip()}")
            
            # Verificar si está después de get_position
            found_get_position = False
            for j in range(max(update_start, i-10), i):
                if 'get_position' in lines[j]:
                    found_get_position = True
                    break
            
            if found_get_position:
                print("   ⚠️ Esta asignación está DESPUÉS de get_position()")
                print("   🔧 ESTA ES LA LÍNEA QUE NECESITA ARREGLARSE")
                
                # Mostrar más contexto
                print("\n   Contexto ampliado:")
                for j in range(max(0, i-10), min(len(lines), i+3)):
                    marker = ">>>" if j == i else "   "
                    print(f"   {marker} {j+1}: {lines[j].rstrip()}")
                
                # Crear fix específico
                print(f"\n🔨 CREANDO FIX PARA LÍNEA {i+1}...")
                
                # Reemplazar esta línea específica
                old_line = lines[i]
                
                # Si la línea asigna 'pos' a _positions[sid]
                if '= pos' in old_line:
                    # Cambiar a pos_with_offsets si existe, o usar el valor de get_position
                    indent_spaces = ' ' * (len(old_line) - len(old_line.lstrip()))
                    
                    # Opción 1: Si ya calculamos pos con get_position, debería funcionar
                    # Opción 2: Forzar el uso del valor actual de pos (que debería tener offsets)
                    new_line = f"{indent_spaces}self._positions[sid] = pos  # pos ya incluye offsets de get_position()\n"
                    
                    lines[i] = new_line
                    
                    # Guardar
                    import datetime
                    backup_name = engine_file + f".backup_exact_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    with open(backup_name, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print(f"\n📋 Backup: {backup_name}")
                    
                    with open(engine_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print(f"✅ Línea {i+1} actualizada")
                    
                    # Pero mejor, vamos a verificar si pos realmente tiene los offsets
                    print("\n⚠️ IMPORTANTE: El problema puede ser que 'pos' no contiene los offsets")
                    print("   Vamos a forzar la suma de offsets justo antes de la asignación...")
                    
                    # Insertar código antes de la asignación
                    insert_code = f'''{indent_spaces}# FORZAR APLICACIÓN DE OFFSETS
{indent_spaces}if sid in self._source_motions:
{indent_spaces}    motion = self._source_motions[sid]
{indent_spaces}    if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
{indent_spaces}        pos = pos + motion.concentration_offset
'''
                    
                    # Recargar y aplicar inserción
                    with open(engine_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    lines.insert(i, insert_code)
                    
                    with open(engine_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    print("\n✅ Código de forzado de offsets insertado")
                    break

# Test final simple
print("\n\n" + "="*80)
print("🧪 TEST SIMPLE")
print("="*80)

test_code = '''
import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
    
    # Inicial
    print(f"Inicial: F0={engine._positions[0]}, F1={engine._positions[1]}")
    
    # Concentración
    engine.set_macro_concentration(macro_id, 0.5)
    print(f"Offset F0: {engine._source_motions[0].concentration_offset}")
    
    # Step
    if hasattr(engine, 'step'):
        engine.step()
    
    # Final
    print(f"Final: F0={engine._positions[0]}, F1={engine._positions[1]}")
    
    mov = np.linalg.norm(engine._positions[0] - np.array([-4., 0., 0.]))
    print(f"\\nMovimiento: {mov:.4f}")
    
    if mov > 0.01:
        print("✅ ¡FUNCIONA!")
    else:
        print("❌ No funciona aún")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 RESUMEN
================================================================================

Si el test aún falla, el problema es que get_position() no se está 
ejecutando o su resultado no se usa.

🔧 SOLUCIÓN MANUAL DEFINITIVA:
1. Abre enhanced_trajectory_engine.py
2. Busca "self._positions[sid] = pos" dentro de update()
3. Justo ANTES de esa línea, añade:
   
   # Forzar offsets
   if hasattr(motion, 'concentration_offset'):
       pos = pos + motion.concentration_offset

Esto garantiza que los offsets se apliquen sin importar qué.
================================================================================
""")