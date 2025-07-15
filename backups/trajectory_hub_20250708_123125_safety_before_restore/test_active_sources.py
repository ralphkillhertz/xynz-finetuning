# === test_active_sources.py ===
# 🧪 Test específico para _active_sources

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\n🔍 TEST: Verificación de _active_sources\n")

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Verificar atributo
    if hasattr(engine, '_active_sources'):
        print(f"✅ _active_sources existe: {engine._active_sources}")
    else:
        print("❌ _active_sources NO EXISTE")
        
        # Añadirlo manualmente para continuar
        engine._active_sources = set()
        print("⚠️ Añadido manualmente")
    
    # Crear macro
    macro_id = engine.create_macro("test", 2)
    print(f"✅ Macro creado: {macro_id}")
    
    # Verificar fuentes activas
    print(f"\n📊 Fuentes activas: {engine._active_sources}")
    
    # Test de rotación rápido
    positions = [[1,0,0], [-1,0,0]]
    macro = engine._macros[macro_id]
    
    for i, sid in enumerate(list(macro.source_ids)[:2]):
        if sid < len(engine._positions):
            engine._positions[sid] = np.array(positions[i])
    
    # Aplicar rotación
    engine.set_macro_rotation(macro_id, 0, 1.0, 0)
    
    # Simular
    for _ in range(30):
        engine.update()
    
    # Verificar movimiento
    if not np.allclose(engine._positions[0], [1,0,0]):
        print("\n✅ ¡ROTACIÓN FUNCIONANDO!")
    else:
        print("\n❌ Sin movimiento")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
