#!/usr/bin/env python3
"""
🧪 TEST FINAL - Verificar que la concentración funciona
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST FINAL DE CONCENTRACIÓN\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=3, formation="line", spacing=2.0)
    
    print("✅ Macro creado con 3 fuentes en línea")
    
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        # Mostrar posiciones iniciales
        print("\n📍 POSICIONES INICIALES:")
        positions_before = {}
        for source_id, motion in motions.items():
            pos = motion.state.position.copy()
            positions_before[source_id] = pos
            print(f"   Fuente {source_id}: {pos}")
        
        # Aplicar concentración
        print("\n🎯 APLICANDO CONCENTRACIÓN (factor 0.1)...")
        engine.set_macro_concentration(macro_id, 0.1)
        
        # Verificar que se creó el componente
        first_motion = list(motions.values())[0]
        if 'concentration' in first_motion.components:
            conc = first_motion.components['concentration']
            print(f"   ✅ Componente creado - factor: {conc.factor}")
        
        # Update manual de cada motion
        print("\n🔄 UPDATE MANUAL DE CADA FUENTE:")
        for source_id, motion in motions.items():
            print(f"\n   Fuente {source_id}:")
            print(f"   Antes: {motion.state.position}")
            
            # Update
            motion.update(0.1)
            
            print(f"   Después: {motion.state.position}")
            print(f"   concentration_offset: {motion.concentration_offset}")
            
            # Verificar si cambió
            if not np.allclose(positions_before[source_id], motion.state.position):
                print("   ✅ ¡POSICIÓN CAMBIÓ!")
            else:
                print("   ❌ Posición sin cambios")
        
        # Test con engine.update()
        print("\n🔄 TEST CON ENGINE.UPDATE():")
        
        # Reset y probar de nuevo
        for motion in motions.values():
            motion.state.position = positions_before[list(motions.keys())[0]].copy()
        
        # Update del engine
        engine.update()
        
        print("\n📍 POSICIONES DESPUÉS DE ENGINE.UPDATE():")
        for source_id, motion in motions.items():
            print(f"   Fuente {source_id}: {motion.state.position}")
    
    print("\n✅ Test completado")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("💡 Si las posiciones cambiaron con la concentración,")
print("   entonces el sistema está funcionando correctamente.")
print("   Prueba ahora en el controller interactivo.")
