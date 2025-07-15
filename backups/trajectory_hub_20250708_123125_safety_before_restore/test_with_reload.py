# === test_with_reload.py ===
# Test con recarga forzada del módulo

import importlib
import sys

# Eliminar módulos del cache
modules_to_remove = []
for module_name in sys.modules:
    if 'trajectory_hub' in module_name:
        modules_to_remove.append(module_name)

for module_name in modules_to_remove:
    del sys.modules[module_name]

print("✅ Cache limpiado")

# Importar fresh
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("✅ Import fresh completado")

# Verificar métodos
print("\n🔍 Métodos que contienen 'rotation':")
for attr in dir(EnhancedTrajectoryEngine):
    if 'rotation' in attr.lower():
        print(f"   - {attr}")

# Verificar específicamente
if hasattr(EnhancedTrajectoryEngine, 'set_macro_rotation'):
    print("\n✅ set_macro_rotation EXISTE")
else:
    print("\n❌ set_macro_rotation NO EXISTE")
    
    # Listar todos los métodos set_
    print("\n📋 Métodos set_* disponibles:")
    for attr in dir(EnhancedTrajectoryEngine):
        if attr.startswith('set_'):
            print(f"   - {attr}")

# Intentar crear instancia y usar
try:
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)
    print("\n✅ Engine creado")
    
    # Crear macro
    macro_id = engine.create_macro("test", 2)
    print(f"✅ Macro creado: {macro_id}")
    
    # Intentar rotación
    if hasattr(engine, 'set_macro_rotation'):
        engine.set_macro_rotation(macro_id, 0, 1.0, 0)
        print("✅ Rotación aplicada!")
    else:
        print("❌ El método no existe en la instancia")
        
        # Debug: ver qué tiene la instancia
        print("\n🔍 Métodos de la instancia con 'macro':")
        for attr in dir(engine):
            if 'macro' in attr.lower() and not attr.startswith('_'):
                print(f"   - {attr}")
                
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
