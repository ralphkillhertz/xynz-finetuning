# === test_diagnostic_attributes.py ===
# Test para diagnosticar atributos del engine

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🔍 DIAGNÓSTICO DE ATRIBUTOS")
print("="*50)

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Verificar atributos relacionados con sources
    attrs_to_check = ['n_sources', 'max_sources', '_max_sources', 'n_max_sources', '_n_sources']
    
    print("\n📋 Atributos de sources:")
    for attr in attrs_to_check:
        if hasattr(engine, attr):
            value = getattr(engine, attr)
            print(f"  ✅ {attr}: {value}")
        else:
            print(f"  ❌ {attr}: NO EXISTE")
    
    # Verificar otros atributos importantes
    print("\n📋 Otros atributos importantes:")
    other_attrs = ['_active_sources', 'motion_states', '_positions']
    for attr in other_attrs:
        if hasattr(engine, attr):
            print(f"  ✅ {attr}: existe")
        else:
            print(f"  ❌ {attr}: NO EXISTE")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
