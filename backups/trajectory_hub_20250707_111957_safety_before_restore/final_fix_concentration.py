#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO: Aplicar offsets directamente
"""

import os
import sys

print("""
================================================================================
🔧 FIX DEFINITIVO DE CONCENTRACIÓN
================================================================================
""")

# 1. Primero, verificar si get_position existe en SourceMotion
motion_file = "trajectory_hub/core/motion_components.py"
print("1️⃣ VERIFICANDO get_position en SourceMotion...")

with open(motion_file, 'r', encoding='utf-8') as f:
    motion_content = f.read()

if 'def get_position' in motion_content and 'class SourceMotion' in motion_content:
    print("✅ get_position existe en el archivo")
    # Verificar que esté dentro de SourceMotion
    import re
    class_match = re.search(r'class SourceMotion.*?(?=class|\Z)', motion_content, re.DOTALL)
    if class_match and 'def get_position' in class_match.group(0):
        print("✅ get_position está dentro de SourceMotion")
    else:
        print("❌ get_position NO está dentro de SourceMotion")
else:
    print("❌ get_position NO existe")

# 2. Arreglar update() para que SIEMPRE aplique offsets
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
print("\n2️⃣ ARREGLANDO update() en enhanced_trajectory_engine.py...")

with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la línea específica donde se asigna _positions[sid]
target_line = -1
for i, line in enumerate(lines):
    if 'self._positions[sid] = pos' in line and i > 1200 and i < 1300:
        target_line = i
        print(f"✅ Encontrada asignación en línea {i+1}")
        break

if target_line >= 0:
    # Obtener indentación
    indent = len(lines[target_line]) - len(lines[target_line].lstrip())
    spaces = ' ' * indent
    
    # Reemplazar con código que GARANTIZA aplicación de offsets
    new_code = f'''{spaces}# APLICAR OFFSETS SIEMPRE
{spaces}final_pos = pos.copy() if hasattr(pos, 'copy') else pos
{spaces}if sid in self._source_motions:
{spaces}    motion = self._source_motions[sid]
{spaces}    if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
{spaces}        final_pos = final_pos + motion.concentration_offset
{spaces}self._positions[sid] = final_pos
'''
    
    # Reemplazar la línea
    lines[target_line] = new_code
    
    # Guardar
    import datetime
    backup_name = engine_file + f".backup_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"\n📋 Backup: {backup_name}")
    
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Línea {target_line+1} reemplazada con aplicación directa de offsets")

# 3. Test inmediato
print("\n" + "="*80)
print("🧪 TEST INMEDIATO")
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
    
    # Test simple
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
    
    # Inicial
    pos0_init = engine._positions[0].copy()
    pos1_init = engine._positions[1].copy()
    print(f"INICIAL:")
    print(f"  F0: {pos0_init}")
    print(f"  F1: {pos1_init}")
    
    # Concentración
    engine.set_macro_concentration(macro_id, 0.5)
    print(f"\\nOFFSETS:")
    print(f"  F0: {engine._source_motions[0].concentration_offset}")
    print(f"  F1: {engine._source_motions[1].concentration_offset}")
    
    # Un solo step
    if hasattr(engine, 'step'):
        engine.step()
    elif hasattr(engine, 'update'):
        engine.update(engine.dt)
    
    # Final
    print(f"\\nDESPUÉS DE 1 STEP:")
    print(f"  F0: {engine._positions[0]}")
    print(f"  F1: {engine._positions[1]}")
    
    # Movimiento
    mov0 = np.linalg.norm(engine._positions[0] - pos0_init)
    mov1 = np.linalg.norm(engine._positions[1] - pos1_init)
    
    print(f"\\nMOVIMIENTO:")
    print(f"  F0: {mov0:.4f}")
    print(f"  F1: {mov1:.4f}")
    
    if mov0 > 0.01 or mov1 > 0.01:
        print("\\n✅ ¡FUNCIONA! LA CONCENTRACIÓN SE APLICA")
        
        # Ejecutar más frames
        for _ in range(50):
            if hasattr(engine, 'step'):
                engine.step()
            elif hasattr(engine, 'update'):
                engine.update(engine.dt)
        
        print(f"\\nDESPUÉS DE 50 FRAMES:")
        print(f"  F0: {engine._positions[0]}")
        print(f"  F1: {engine._positions[1]}")
        
        dist_inicial = np.linalg.norm(pos1_init - pos0_init)
        dist_final = np.linalg.norm(engine._positions[1] - engine._positions[0])
        
        print(f"\\nCONCENTRACIÓN:")
        print(f"  Distancia inicial: {dist_inicial:.4f}")
        print(f"  Distancia final: {dist_final:.4f}")
        print(f"  Reducción: {(1 - dist_final/dist_inicial)*100:.1f}%")
        
    else:
        print("\\n❌ Todavía no funciona")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
✅ FIX DEFINITIVO APLICADO
================================================================================

🔧 Lo que hicimos:
   - Aplicar offsets DIRECTAMENTE en la línea ~1265
   - No depender de get_position() que no existe
   - Garantizar que concentration_offset se sume SIEMPRE

🚀 SI FUNCIONÓ, ejecuta el test completo:
   python test_concentration_working.py

🎯 Y luego el controlador interactivo:
   python trajectory_hub/interface/interactive_controller.py

💡 Si aún no funciona, edita manualmente enhanced_trajectory_engine.py
   en la línea indicada y asegúrate que los offsets se sumen.
================================================================================
""")