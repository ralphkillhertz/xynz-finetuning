# === test_corrected.py ===
# Test con parámetros correctos

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST CORREGIDO")
print("="*50)

try:
    # Crear engine con parámetros correctos
    engine = EnhancedTrajectoryEngine(max_sources=5)
    print("✅ Engine creado")
    
    # Crear una fuente
    engine.create_source(0, "test_0")
    print("✅ Fuente creada")
    
    # Crear un macro
    engine.create_macro("test", [0, 1, 2])
    print("✅ Macro creado")
    
    print("\n✅ SISTEMA FUNCIONANDO")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
