#!/usr/bin/env python3
"""
🧪 Test directo - Llamar update() del engine
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST DIRECTO DE ENGINE.UPDATE()\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=3, formation="line", spacing=2.0)
    
    print("✅ Macro creado")
    
    # Verificar qué métodos tiene
    print("\n📊 Métodos de actualización disponibles:")
    for method in ['update', 'step', 'tick', 'process']:
        if hasattr(engine, method):
            print(f"   ✅ engine.{method}() existe")
    
    # Posiciones iniciales
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        print(f"\n📍 Posiciones iniciales ({len(motions)} fuentes):")
        pos_before = {}
        for sid, motion in motions.items():
            pos = motion.state.position.copy()
            pos_before[sid] = pos
            print(f"   Fuente {sid}: {pos}")
        
        # Aplicar concentración
        print("\n🎯 Aplicando concentración 0.1...")
        engine.set_macro_concentration(macro_id, 0.1)
        
        # Probar update()
        print("\n🔄 Llamando engine.update()...")
        result = engine.update()
        
        if isinstance(result, dict):
            print(f"   update() devolvió: {type(result).__name__} con {len(result)} claves")
        
        # Ver si cambió algo
        print("\n📍 Posiciones después de update():")
        any_moved = False
        for sid, motion in motions.items():
            pos = motion.state.position
            if not np.allclose(pos, pos_before[sid]):
                print(f"   Fuente {sid}: {pos} ✅ CAMBIÓ")
                any_moved = True
            else:
                print(f"   Fuente {sid}: {pos} ❌ igual")
        
        if not any_moved:
            print("\n⚠️  update() no movió las fuentes")
            print("\n🔄 Intentando actualización manual...")
            
            # Update manual
            for motion in motions.values():
                motion.update(0.1)
            
            print("\n📍 Después de update manual:")
            for sid, motion in motions.items():
                pos = motion.state.position
                if not np.allclose(pos, pos_before[sid]):
                    print(f"   Fuente {sid}: {pos} ✅ CAMBIÓ")
                    any_moved = True
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
