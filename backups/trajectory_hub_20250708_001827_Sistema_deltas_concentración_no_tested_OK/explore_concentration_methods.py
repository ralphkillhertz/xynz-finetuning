# === explore_concentration_methods.py ===
# 🔧 Explora TODOS los métodos relacionados con concentración
# ⚡ Encuentra la forma correcta de usar concentración

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 EXPLORACIÓN DE MÉTODOS DE CONCENTRACIÓN")
print("="*60)

# 1. Setup
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("test", source_count=3)

# 2. Posiciones iniciales
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])

print("\n📋 Métodos relacionados con concentración:")
concentration_methods = []
for attr in dir(engine):
    if 'concentr' in attr.lower() or 'macro' in attr.lower():
        if callable(getattr(engine, attr)):
            concentration_methods.append(attr)
            print(f"   - {attr}")

# 3. Explorar cada método
print("\n🧪 Probando métodos:")

for method_name in concentration_methods:
    if method_name.startswith('_'):
        continue
        
    print(f"\n📌 {method_name}:")
    method = getattr(engine, method_name)
    
    # Ver firma del método
    import inspect
    try:
        sig = inspect.signature(method)
        print(f"   Firma: {method_name}{sig}")
        
        # Obtener docstring
        if method.__doc__:
            first_line = method.__doc__.strip().split('\n')[0]
            print(f"   Doc: {first_line}")
    except:
        print("   No se pudo obtener firma")
    
    # Probar diferentes combinaciones
    if 'concentration' in method_name:
        test_calls = [
            (f"{method_name}(macro_name)", lambda: method(macro_name)),
            (f"{method_name}(macro_name, 0.5)", lambda: method(macro_name, 0.5)),
            (f"{method_name}(macro_name, [0,0,0])", lambda: method(macro_name, np.array([0,0,0]))),
            (f"{method_name}(macro_name, 0.5, 2.0)", lambda: method(macro_name, 0.5, 2.0)),
        ]
        
        for desc, func in test_calls:
            try:
                result = func()
                print(f"   ✅ {desc} = {result}")
                break
            except Exception as e:
                error_msg = str(e).split('\n')[0]
                print(f"   ❌ {desc}: {error_msg}")

# 4. Ver estado del macro
print("\n📊 Estado del macro después de pruebas:")
macro = engine._macros[macro_name]
state_attrs = ['concentration_active', 'concentration_factor', 'concentration_duration',
               'concentration_target', 'concentration_progress', 'concentration_speed']
for attr in state_attrs:
    if hasattr(macro, attr):
        print(f"   {attr}: {getattr(macro, attr)}")

# 5. Si concentration_active es True, actualizar y ver
if hasattr(macro, 'concentration_active') and macro.concentration_active:
    print("\n🔄 Concentration está activa, actualizando...")
    pos_before = engine._positions[0].copy()
    
    for i in range(20):
        engine.update()
    
    pos_after = engine._positions[0]
    movement = np.linalg.norm(pos_after - pos_before)
    print(f"   Movimiento después de 20 frames: {movement:.4f}")
    
    if movement < 0.001:
        print("\n❌ No hay movimiento a pesar de concentration_active=True")
        print("\n🔍 Verificando si necesita algún trigger adicional...")
        
        # Buscar métodos de procesamiento
        process_methods = ['process_macro_concentration', 'update_macro_concentration', 
                          '_apply_concentration', '_update_concentration']
        for pm in process_methods:
            if hasattr(engine, pm):
                print(f"   ✅ Encontrado: {pm}")