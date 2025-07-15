# === fix_test_api.py ===
# 🔧 Diagnóstico de APIs correctas
# ⚡ Verificar métodos y parámetros

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import inspect

print("🔍 DIAGNÓSTICO DE APIs DEL SISTEMA")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)

# 1. Verificar create_macro
print("\n1️⃣ create_macro:")
sig = inspect.signature(engine.create_macro)
print(f"   Firma: {sig}")
print("   Uso correcto: create_macro(name, source_count, formation='grid')")

# 2. Verificar set_individual_trajectory  
print("\n2️⃣ set_individual_trajectory:")
if hasattr(engine, 'set_individual_trajectory'):
    sig = inspect.signature(engine.set_individual_trajectory)
    print(f"   Firma: {sig}")
else:
    print("   ❌ Método no existe")

# 3. Verificar set_macro_trajectory
print("\n3️⃣ set_macro_trajectory:")
if hasattr(engine, 'set_macro_trajectory'):
    sig = inspect.signature(engine.set_macro_trajectory)
    print(f"   Firma: {sig}")
else:
    print("   ❌ Método no existe")

# 4. Verificar set_macro_rotation
print("\n4️⃣ set_macro_rotation:")
if hasattr(engine, 'set_macro_rotation'):
    sig = inspect.signature(engine.set_macro_rotation)
    print(f"   Firma: {sig}")
else:
    print("   ❌ Método no existe")

# 5. Verificar estructuras
print("\n5️⃣ Verificar estructura de macro:")
# Crear macro de prueba
macro_name = engine.create_macro("test", 3)
print(f"   create_macro retorna: {type(macro_name)} = '{macro_name}'")

if macro_name in engine.macros:
    macro = engine.macros[macro_name]
    print(f"   Tipo de macro: {type(macro)}")
    print(f"   Atributos: {[attr for attr in dir(macro) if not attr.startswith('_')]}")
    if hasattr(macro, 'source_ids'):
        print(f"   source_ids tipo: {type(macro.source_ids)}")
        print(f"   source_ids contenido: {macro.source_ids}")

# 6. Verificar motion_states
print("\n6️⃣ motion_states:")
print(f"   Tipo: {type(engine.motion_states)}")
print(f"   IDs disponibles: {list(engine.motion_states.keys())}")

print("\n✅ Diagnóstico completado")