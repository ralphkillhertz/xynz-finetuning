#!/usr/bin/env python3
"""
🚀 INICIO RÁPIDO - Próxima sesión Trajectory Hub
⚡ Resumen del estado y siguiente acción directa
"""

print("""
================================================================================
📊 ESTADO ACTUAL - TRAJECTORY HUB
================================================================================

✅ LO QUE YA FUNCIONA:
   1. SourceMotion tiene offsets (concentration_offset, etc.)
   2. motion.update(dt) calcula correctamente la concentración
   3. Los cálculos están perfectos (probado manualmente)

❌ EL ÚNICO PROBLEMA:
   engine.step() NO llama a motion.update(dt)
   
   Por eso las fuentes no se mueven en Spat.

🎯 SOLUCIÓN REQUERIDA:
   Modificar engine.step() para que actualice las fuentes

================================================================================
🔧 DIAGNÓSTICO RÁPIDO
================================================================================
""")

import os
import subprocess

# 1. Verificar cuántos step() hay
print("1️⃣ BUSCANDO DEFINICIONES DE step()...\n")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    try:
        result = subprocess.run(
            ['grep', '-n', 'def step', engine_file],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print("   Definiciones encontradas:")
            print(result.stdout)
        else:
            print("   ❌ No se encontró 'def step'")
            
        # Buscar también referencias
        result2 = subprocess.run(
            ['grep', '-n', 'step()', engine_file],
            capture_output=True,
            text=True
        )
        
        if result2.stdout:
            print("\n   Referencias a step():")
            for line in result2.stdout.split('\n')[:5]:
                if line:
                    print(f"   {line}")
    except:
        print("   ⚠️  No se pudo ejecutar grep")

# 2. Verificar el test
print("\n\n2️⃣ EJECUTANDO TEST RÁPIDO...\n")

test_code = '''
import os
import sys

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=2)
    
    # Aplicar concentración
    engine.set_macro_concentration(macro_id, 0.1)
    
    # Posición antes
    if hasattr(engine, '_source_motions'):
        motion = list(engine._source_motions.values())[0]
        pos_before = motion.state.position.copy()
        
        # Llamar step
        engine.step()
        
        # Posición después
        pos_after = motion.state.position
        
        if (pos_before == pos_after).all():
            print("   ❌ step() NO mueve las fuentes")
        else:
            print("   ✅ step() SÍ mueve las fuentes")
            
except Exception as e:
    print(f"   Error: {e}")
'''

exec(test_code)

print("""

================================================================================
🚀 SIGUIENTE ACCIÓN DIRECTA
================================================================================

OPCIÓN A - Si step() existe pero no actualiza:
   python fix_existing_step_to_update_motions.py

OPCIÓN B - Si hay múltiples step():
   python identify_correct_step_method.py

OPCIÓN C - Si step() no se puede modificar:
   python intercept_at_different_point.py

💡 RECOMENDACIÓN:
   Empezar con OPCIÓN A - es lo más probable

================================================================================
""")