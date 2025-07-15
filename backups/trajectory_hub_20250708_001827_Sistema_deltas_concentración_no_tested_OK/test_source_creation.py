# === test_source_creation.py ===
# Test simple de creación de fuentes

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import SourceMotion, MotionState

print("🧪 TEST DE CREACIÓN DE FUENTES")
print("="*50)

# Test 1: Crear SourceMotion directamente
print("\n1️⃣ Test directo de SourceMotion:")
try:
    state = MotionState()
    
    # Intentar diferentes formas
    try:
        motion1 = SourceMotion()
        print("  ✅ SourceMotion() funciona")
    except:
        pass
    
    try:
        motion2 = SourceMotion(state)
        print("  ✅ SourceMotion(state) funciona")
    except:
        pass
    
    try:
        motion3 = SourceMotion(0, state)
        print("  ✅ SourceMotion(id, state) funciona")
    except:
        pass
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: Crear a través del engine
print("\n2️⃣ Test a través del engine:")
try:
    engine = EnhancedTrajectoryEngine(n_sources=5)
    engine.create_source(0, "test_0")
    print("  ✅ create_source funciona")
    
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
