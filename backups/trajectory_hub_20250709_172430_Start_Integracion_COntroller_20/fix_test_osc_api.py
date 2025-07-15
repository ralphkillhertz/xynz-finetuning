def create_fixed_test():
    test_content = '''#!/usr/bin/env python3
"""Test debug OSC - API corregida"""

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST DEBUG OSC")
print("="*50)

try:
    # 1. Crear engine
    print("1. Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
    print("   ✅ Engine creado")
    
    # 2. Verificar osc_bridge
    print("2. Verificando osc_bridge...")
    print(f"   - osc_bridge existe: {hasattr(engine, 'osc_bridge')}")
    print(f"   - osc_bridge es None: {engine.osc_bridge is None}")
    
    if engine.osc_bridge is None:
        print("   ❌ osc_bridge no está inicializado")
    else:
        print("   ✅ osc_bridge inicializado correctamente")
        
        # 3. Test OSC target
        engine.osc_bridge.add_target("Spat_Test", "127.0.0.1", 9000)
        print("3. ✅ Target OSC añadido")
        
        # 4. Enviar posición (API correcta)
        position = np.array([1.0, 2.0, 3.0])
        engine.osc_bridge.send_position(1, position)
        print("4. ✅ Posición enviada")
        
        # 5. Stats
        stats = engine.osc_bridge.get_stats()
        print(f"5. Stats OSC: {stats}")
        
        print("\\n✅ TEST COMPLETADO - OSC funcionando")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("test_osc_fixed.py", "w") as f:
        f.write(test_content)
    
    print("✅ Test corregido creado: test_osc_fixed.py")
    print("🚀 Ejecuta: python test_osc_fixed.py")

if __name__ == "__main__":
    create_fixed_test()