# === test_rotation_correct.py ===
# 🔧 Test correcto de rotación MS
# ⚡ Con nombres de métodos correctos
# 🎯 Impacto: DEBUG

import numpy as np
import sys

print("🔍 Test correcto de rotación MS")
print("=" * 50)

# Capturar errores array ambiguous
def monitor_arrays():
    """Monkey patch para detectar comparaciones problemáticas"""
    original_bool = np.ndarray.__bool__
    
    def debug_bool(self):
        if self.size > 1:
            print(f"\n🚨 ARRAY AMBIGUOUS DETECTADO!")
            print(f"   Array: {self}")
            print(f"   Shape: {self.shape}")
            print(f"   Stack trace:")
            import traceback
            traceback.print_stack()
        return original_bool(self)
    
    np.ndarray.__bool__ = debug_bool

# Activar monitoreo
monitor_arrays()

try:
    from trajectory_hub.core.motion_components import MacroRotation, MotionState, MotionDelta
    from trajectory_hub import EnhancedTrajectoryEngine
    
    print("✅ Imports exitosos")
    
    # Test 1: MacroRotation directamente
    print("\n📋 Test 1: MacroRotation aislada")
    rotation = MacroRotation()
    rotation.set_rotation(0.0, 1.0, 0.0)  # Nombre correcto del método
    print(f"✅ Rotación configurada - enabled: {rotation.enabled}")
    
    # Test 2: calculate_delta con parámetros correctos
    print("\n📋 Test 2: calculate_delta")
    state = MotionState()
    state.position = np.array([2.0, 2.0, 0.0])
    state.source_id = 0
    
    # Orden correcto: state, current_time, dt
    delta = rotation.calculate_delta(state, 0.0, 0.016)
    print(f"✅ Delta calculado: {delta.position if hasattr(delta, 'position') else 'No position'}")
    
    # Test 3: En el engine
    print("\n📋 Test 3: Test con engine completo")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    
    # Crear fuentes
    for i in range(4):
        engine.create_source(f"rot_test_{i}")
    
    # Crear macro
    engine.create_macro("test_rotation", [0, 1, 2, 3])
    
    # Aplicar rotación
    print("\n🔄 Aplicando rotación...")
    engine.set_macro_rotation("test_rotation", speed_x=0.0, speed_y=1.0, speed_z=0.0)
    
    # Un update para ver si hay error
    print("\n⏱️ Ejecutando update()...")
    try:
        engine.update()
        print("✅ Update exitoso!")
    except Exception as e:
        print(f"❌ Error en update: {e}")
        if "ambiguous" in str(e):
            print("🚨 ERROR ARRAY AMBIGUOUS EN UPDATE!")
    
    # Verificar posiciones
    print("\n📍 Posiciones después del update:")
    for i in range(4):
        pos = engine._positions[i]
        print(f"   Fuente {i}: {pos}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completado")