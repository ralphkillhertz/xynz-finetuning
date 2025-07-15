#!/usr/bin/env python3
"""
🔬 DIAGNÓSTICO PROFUNDO: ¿Por qué no funciona la concentración?
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("""
================================================================================
🔬 DIAGNÓSTICO PROFUNDO DE CONCENTRACIÓN
================================================================================
""")

# 1. Importar y verificar estructura
try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from trajectory_hub.core.motion_components import SourceMotion
    
    print("✅ Imports exitosos")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # 2. Verificar que set_macro_concentration existe
    if hasattr(engine, 'set_macro_concentration'):
        print("✅ set_macro_concentration existe")
    else:
        print("❌ set_macro_concentration NO existe")
        sys.exit(1)
    
    # 3. Crear macro y verificar estructura
    print("\n📊 CREANDO MACRO...")
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)
    
    print(f"\n🔍 VERIFICANDO ESTRUCTURA DEL MACRO:")
    if macro_id in engine._macros:
        macro = engine._macros[macro_id]
        print(f"   ✅ Macro creado: {macro_id}")
        print(f"   - source_ids: {macro.source_ids}")
        print(f"   - Tiene {len(macro.source_ids)} fuentes")
    else:
        print("   ❌ Macro no se creó")
        sys.exit(1)
    
    # 4. Verificar source_motions
    print(f"\n🔍 VERIFICANDO SOURCE_MOTIONS:")
    for sid in range(4):
        if sid in engine._source_motions:
            motion = engine._source_motions[sid]
            print(f"   ✅ Fuente {sid} existe")
            print(f"      - state.position: {motion.state.position}")
            print(f"      - concentration_offset: {getattr(motion, 'concentration_offset', 'NO EXISTE')}")
        else:
            print(f"   ❌ Fuente {sid} NO existe en _source_motions")
    
    # 5. Llamar a set_macro_concentration con debug
    print(f"\n🎯 LLAMANDO set_macro_concentration({macro_id}, 0.5)...")
    
    # Interceptar la llamada
    original_method = engine.set_macro_concentration
    
    def debug_concentration(macro_id, factor):
        print(f"   → Entrando a set_macro_concentration")
        print(f"   → macro_id: {macro_id}")
        print(f"   → factor: {factor}")
        
        # Llamar al método original
        result = original_method(macro_id, factor)
        
        print(f"   → Saliendo de set_macro_concentration")
        return result
    
    # Temporalmente reemplazar
    engine.set_macro_concentration = debug_concentration
    
    # Llamar
    engine.set_macro_concentration(macro_id, 0.5)
    
    # 6. Verificar offsets después
    print(f"\n🔍 VERIFICANDO OFFSETS DESPUÉS:")
    for sid in range(4):
        if sid in engine._source_motions:
            motion = engine._source_motions[sid]
            offset = getattr(motion, 'concentration_offset', None)
            if offset is not None:
                mag = np.linalg.norm(offset)
                print(f"   Fuente {sid}: offset={offset}, magnitud={mag:.4f}")
            else:
                print(f"   Fuente {sid}: concentration_offset NO EXISTE")
    
    # 7. Calcular manualmente para verificar
    print(f"\n🧮 CÁLCULO MANUAL DE CONCENTRACIÓN:")
    positions = []
    for sid in range(4):
        if sid in engine._source_motions:
            pos = engine._source_motions[sid].state.position.copy()
            positions.append(pos)
            print(f"   Posición {sid}: {pos}")
    
    if positions:
        center = np.mean(positions, axis=0)
        print(f"   Centro calculado: {center}")
        
        print(f"\n   Offsets esperados (factor 0.5):")
        for i, pos in enumerate(positions):
            direction = center - pos
            distance = np.linalg.norm(direction)
            if distance > 0.001:
                expected_offset = direction * 0.5
                expected_mag = np.linalg.norm(expected_offset)
                print(f"   Fuente {i}: debería moverse {expected_mag:.4f} hacia {expected_offset}")
    
    # 8. Probar aplicar offset manualmente
    print(f"\n🔧 APLICANDO OFFSET MANUALMENTE A FUENTE 0:")
    if 0 in engine._source_motions:
        motion = engine._source_motions[0]
        motion.concentration_offset = np.array([1.0, 1.0, 0.0])
        print(f"   Offset manual establecido: {motion.concentration_offset}")
        
        # Probar get_position
        if hasattr(motion, 'get_position'):
            pos = motion.get_position()
            print(f"   get_position() retorna: {pos}")
        else:
            print(f"   ❌ get_position() no existe")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)

# 9. Crear fix directo
print("\n🔨 CREANDO FIX DIRECTO...")

fix_code = '''#!/usr/bin/env python3
"""
🔧 FIX DIRECTO: Implementación manual de concentración
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("\\n🔧 APLICANDO CONCENTRACIÓN MANUALMENTE\\n")

# Crear engine y macro
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)

# Obtener macro
macro = engine._macros[macro_id]

# Calcular centro
positions = []
for sid in macro.source_ids:
    if sid in engine._source_motions:
        pos = engine._source_motions[sid].state.position.copy()
        positions.append(pos)
        print(f"Fuente {sid}: {pos}")

center = np.mean(positions, axis=0)
print(f"\\nCentro: {center}")

# Aplicar offsets manualmente
concentration_factor = 0.5
print(f"\\nAplicando factor {concentration_factor}...")

for i, sid in enumerate(macro.source_ids):
    if sid in engine._source_motions:
        motion = engine._source_motions[sid]
        
        # Calcular offset
        direction = center - positions[i]
        offset = direction * concentration_factor
        
        # Establecer offset
        motion.concentration_offset = offset
        mag = np.linalg.norm(offset)
        print(f"Fuente {sid}: offset magnitud = {mag:.4f}")

# Simular
print("\\n🔄 Ejecutando simulación...")
for i in range(60):
    engine.step()
    
    if (i + 1) % 20 == 0:
        pos0 = engine._positions[0]
        print(f"Frame {i+1}: Fuente 0 en {pos0}")

# Verificar movimiento
print("\\n📊 RESULTADO:")
for sid in macro.source_ids:
    if sid in engine._source_motions:
        final_pos = engine._positions[sid]
        initial_pos = positions[sid]
        movement = np.linalg.norm(final_pos - initial_pos)
        print(f"Fuente {sid}: movió {movement:.4f} unidades")

print("\\n" + "="*60)
'''

with open("fix_concentration_manual.py", 'w', encoding='utf-8') as f:
    f.write(fix_code)

print("✅ Creado: fix_concentration_manual.py")

print("""
================================================================================
📋 RESUMEN DEL DIAGNÓSTICO
================================================================================

Este diagnóstico verifica:
1. Si el método set_macro_concentration existe
2. Si se está llamando correctamente
3. Si los offsets se están calculando
4. El cálculo manual de los offsets esperados
5. Si get_position() funciona

🚀 SIGUIENTE PASO:
   python fix_concentration_manual.py

Este script aplica la concentración manualmente para verificar
que el resto del sistema funciona.

💡 Si el fix manual funciona, el problema está en set_macro_concentration
================================================================================
""")