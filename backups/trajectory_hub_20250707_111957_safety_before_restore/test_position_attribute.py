#!/usr/bin/env python3
"""
🧪 Test rápido del atributo de posición
"""

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
    
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=1)
    
    # Obtener la primera fuente
    if hasattr(engine, '_source_motions') and engine._source_motions:
        motion = list(engine._source_motions.values())[0]
        
        print("✅ SourceMotion obtenido")
        print(f"   Tipo: {type(motion).__name__}")
        
        # Ver qué atributos de posición tiene
        print("\n📍 Atributos de posición:")
        for attr in ['macro_reference', 'position', '_position', 'pos', 'base_position']:
            if hasattr(motion, attr):
                value = getattr(motion, attr)
                print(f"   ✅ {attr}: {value}")
        
        # Test update
        print("\n🧪 Test update()...")
        try:
            motion.update(0.1)
            print("   ✅ update() ejecutado sin errores")
            
            # Ver offsets
            print("\n📊 Offsets después de update:")
            print(f"   concentration_offset: {motion.concentration_offset}")
            
        except Exception as e:
            print(f"   ❌ Error en update: {e}")
        
        # Test get_position
        try:
            pos = motion.get_position()
            print(f"\n✅ get_position(): {pos}")
        except Exception as e:
            print(f"\n❌ Error en get_position: {e}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
