# === explore_engine_structure.py ===
# 🔧 Explora la estructura real del engine
# ⚡ Sin asumir nada sobre atributos

from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 EXPLORACIÓN DE ESTRUCTURA DEL ENGINE")
print("="*60)

# 1. Crear engine
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# 2. Explorar atributos
print("\n📋 Atributos del engine:")
attrs = [attr for attr in dir(engine) if not attr.startswith('_')]
for attr in sorted(attrs)[:20]:  # Primeros 20
    print(f"   - {attr}")

# 3. Crear macro y ver qué retorna
print("\n🎯 Creando macro...")
result = engine.create_macro("test", source_count=3)
print(f"   Tipo retornado: {type(result)}")
print(f"   Valor: {result}")

# 4. Buscar dónde están los macros
print("\n🔍 Buscando estructuras de datos:")
possible_attrs = ['macros', 'macro_sources', 'groups', '_macros', 'motion_states']
for attr in possible_attrs:
    if hasattr(engine, attr):
        val = getattr(engine, attr)
        print(f"   ✅ {attr}: {type(val)}")
        if isinstance(val, dict) and len(val) > 0:
            print(f"      Keys: {list(val.keys())}")

# 5. Si result es string, buscar los IDs
if isinstance(result, str):
    print(f"\n🔍 Buscando IDs para macro '{result}':")
    
    # En motion_states?
    if hasattr(engine, 'motion_states'):
        states = engine.motion_states
        print(f"   motion_states tiene {len(states)} entradas")
        if len(states) > 0:
            print(f"   Keys: {list(states.keys())[:5]}")
            
    # En _positions?
    if hasattr(engine, '_positions'):
        print(f"   _positions shape: {engine._positions.shape}")
        
    # Buscar source_ids
    for i in range(3):
        test_names = [f"{result}_{i}", f"test_{i}", str(i)]
        for name in test_names:
            if hasattr(engine, 'motion_states') and name in engine.motion_states:
                print(f"   ✅ Encontrado: '{name}' en motion_states")
                break

# 6. Test apply_concentration
print("\n🧪 Test apply_concentration:")
try:
    engine.apply_concentration(result, factor=0.8)
    print("   ✅ apply_concentration funcionó")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 7. Buscar método de update
print("\n🔍 Métodos de actualización:")
update_methods = ['update', 'step', 'tick', 'process', 'advance']
for method in update_methods:
    if hasattr(engine, method):
        print(f"   ✅ {method}")