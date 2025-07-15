# === test_osc_debug.py ===
# Test con información de debug

import logging
logging.basicConfig(level=logging.DEBUG)

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import OSCTarget

print("🧪 TEST DEBUG OSC")
print("=" * 50)

try:
    # Crear engine
    print("1. Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
    print(f"   ✅ Engine creado")
    
    # Verificar osc_bridge
    print(f"2. Verificando osc_bridge...")
    print(f"   - osc_bridge existe: {hasattr(engine, 'osc_bridge')}")
    print(f"   - osc_bridge es None: {getattr(engine, 'osc_bridge', 'NO EXISTE') is None}")
    
    if hasattr(engine, 'osc_bridge') and engine.osc_bridge is not None:
        print(f"   ✅ osc_bridge inicializado correctamente")
        
        # Configurar OSC
        target = OSCTarget(host="127.0.0.1", port=9000, name="Spat_Test")
        engine.osc_bridge.add_target(target)
        print(f"3. ✅ Target OSC añadido")
        
        # Test básico
        engine.osc_bridge.send_position(1, 1.0, 2.0, 3.0)
        print(f"4. ✅ Mensaje de prueba enviado")
    else:
        print("   ❌ osc_bridge no está inicializado")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
