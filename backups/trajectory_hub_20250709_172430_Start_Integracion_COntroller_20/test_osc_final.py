#!/usr/bin/env python3
"""Test OSC funcional con API correcta"""

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np
import time

print("🧪 TEST OSC FINAL")
print("="*60)

try:
    # 1. Crear engine
    print("1. Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
    print("   ✅ Engine creado")
    
    # 2. Verificar OSC
    print("\n2. Estado OSC:")
    print(f"   - Bridge existe: {engine.osc_bridge is not None}")
    print(f"   - Targets: {engine.osc_bridge.targets}")
    print(f"   - FPS: {engine.osc_bridge.fps}")
    
    # 3. Añadir target adicional (tupla)
    print("\n3. Añadiendo target adicional...")
    engine.osc_bridge.add_target(("192.168.1.100", 9001))
    print(f"   ✅ Targets ahora: {len(engine.osc_bridge.targets)}")
    
    # 4. Crear macro y enviar posiciones
    print("\n4. Creando macro y enviando posiciones...")
    macro = engine.create_macro("test_osc", 5)
    print(f"   ✅ Macro creado: {macro.name}")
    
    # 5. Mover fuentes
    print("\n5. Moviendo fuentes...")
    for i in range(10):
        # Actualizar posiciones
        for sid in range(5):
            pos = np.array([
                np.cos(i * 0.1 + sid) * 2,
                np.sin(i * 0.1 + sid) * 2,
                0.0
            ])
            engine.osc_bridge.send_position(sid, pos)
        
        # Stats cada 5 frames
        if i % 5 == 0:
            stats = engine.osc_bridge.get_stats()
            print(f"   Frame {i}: {stats['messages_sent']} mensajes enviados")
        
        time.sleep(0.1)
    
    # 6. Stats finales
    print("\n6. Estadísticas finales:")
    stats = engine.osc_bridge.get_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n✅ TEST COMPLETADO - OSC funcionando correctamente")
    print("💡 Verifica en Spat que las fuentes 1-5 se muevan en círculo")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()