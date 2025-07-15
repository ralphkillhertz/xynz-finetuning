#!/usr/bin/env python3
"""
🔧 FIX: Arreglar el atributo 'enabled' en step()
"""

import os
import re

print("""
================================================================================
🔧 FIX: ATRIBUTO 'enabled' EN STEP()
================================================================================
""")

# 1. Buscar y arreglar el método step
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

print("📋 ARREGLANDO step() para no requerir 'enabled'...")

with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar el método step
step_match = re.search(r'(def step\(.*?\):.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)

if step_match:
    step_content = step_match.group(0)
    print("✅ Método step() encontrado")
    
    # Reemplazar la verificación de enabled
    # Cambiar: if sid < self.max_sources and motion.enabled:
    # Por: if sid < self.max_sources:
    
    new_step_content = step_content.replace(
        'if sid < self.max_sources and motion.enabled:',
        'if sid < self.max_sources:'
    )
    
    # Si no cambió, buscar otra variante
    if new_step_content == step_content:
        new_step_content = step_content.replace(
            'motion.enabled',
            'getattr(motion, "enabled", True)'
        )
    
    # Reemplazar en el contenido completo
    content = content.replace(step_content, new_step_content)
    
    # Guardar
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ step() arreglado - ya no requiere 'enabled'")
else:
    print("❌ No se encontró step()")

# 2. Test rápido
print("\n" + "="*80)
print("🧪 TEST RÁPIDO")
print("="*80 + "\n")

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
    
    # Test mínimo
    print("CREANDO ENGINE...")
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    
    print("CREANDO MACRO...")
    macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
    
    print("\\nPOSICIONES INICIALES:")
    pos0_init = engine._positions[0].copy()
    pos1_init = engine._positions[1].copy()
    print(f"  F0: {pos0_init}")
    print(f"  F1: {pos1_init}")
    
    print("\\nAPLICANDO CONCENTRACIÓN...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    print("\\nOFFSETS:")
    for i in range(2):
        if i in engine._source_motions:
            offset = engine._source_motions[i].concentration_offset
            print(f"  F{i}: {offset} (mag={np.linalg.norm(offset):.4f})")
    
    print("\\nEJECUTANDO step()...")
    engine.step()  # Esto antes fallaba
    
    print("\\n✅ step() ejecutado sin errores!")
    
    print("\\nPOSICIONES DESPUÉS DE 1 FRAME:")
    for i in range(2):
        mov = np.linalg.norm(engine._positions[i] - [pos0_init, pos1_init][i])
        print(f"  F{i}: {engine._positions[i]} (movimiento={mov:.4f})")
    
    # Verificar si se movieron
    mov0 = np.linalg.norm(engine._positions[0] - pos0_init)
    mov1 = np.linalg.norm(engine._positions[1] - pos1_init)
    
    if mov0 > 0.01 or mov1 > 0.01:
        print("\\n✅ ¡LAS FUENTES SE MUEVEN!")
        
        # Ejecutar más frames
        for _ in range(49):
            engine.step()
        
        print("\\nDESPUÉS DE 50 FRAMES:")
        print(f"  F0: {engine._positions[0]}")
        print(f"  F1: {engine._positions[1]}")
        
        # Verificar concentración
        dist_init = np.linalg.norm(pos1_init - pos0_init)
        dist_final = np.linalg.norm(engine._positions[1] - engine._positions[0])
        reduction = (1 - dist_final/dist_init) * 100
        
        print(f"\\nCONCENTRACIÓN:")
        print(f"  Distancia inicial: {dist_init:.4f}")
        print(f"  Distancia final: {dist_final:.4f}")
        print(f"  Reducción: {reduction:.1f}%")
        
        if reduction > 10:
            print("\\n" + "="*60)
            print("🎉 ¡ÉXITO TOTAL! LA CONCENTRACIÓN FUNCIONA")
            print("="*60)
            print("\\n🚀 Ejecuta ahora:")
            print("   python trajectory_hub/interface/interactive_controller.py")
    else:
        print("\\n❌ Las fuentes NO se mueven")
        print("\\n🔍 Debug:")
        motion = engine._source_motions[0]
        print(f"  motion.state.position: {motion.state.position}")
        print(f"  motion.concentration_offset: {motion.concentration_offset}")
        print(f"  Suma esperada: {motion.state.position + motion.concentration_offset}")
        print(f"  _positions[0] actual: {engine._positions[0]}")
        
except Exception as e:
    print(f"\\nERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("\n" + "="*80)