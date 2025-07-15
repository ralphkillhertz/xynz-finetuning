# === test_diagnostic.py ===
# 🔍 Diagnóstico de la estructura del engine

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print("🔍 DIAGNÓSTICO DEL ENGINE")
print("=" * 60)

# Listar atributos
print("\nAtributos del engine que contienen 'macro':")
attrs = [attr for attr in dir(engine) if 'macro' in attr.lower()]
for attr in sorted(attrs):
    try:
        value = getattr(engine, attr)
        print(f"  {attr}: {type(value)}")
        if isinstance(value, dict) and len(value) == 0:
            print(f"    → Diccionario vacío (posible almacén de macros)")
    except:
        print(f"  {attr}: (no accesible)")

# Buscar específicamente _macros
print("\nBuscando atributos privados:")
private_attrs = [attr for attr in dir(engine) if attr.startswith('_') and 'macro' in attr.lower()]
for attr in private_attrs:
    try:
        value = getattr(engine, attr)
        print(f"  {attr}: {type(value)}")
    except:
        pass

# Crear un macro y ver dónde se guarda
print("\nCreando macro de prueba...")
result = engine.create_macro("test", 2)
print(f"create_macro retornó: {type(result)} = {result}")

# Buscar dónde se guardó
print("\nBuscando el macro creado:")
for attr in dir(engine):
    try:
        value = getattr(engine, attr)
        if isinstance(value, dict) and "test" in value:
            print(f"  ✅ Encontrado en: engine.{attr}")
            print(f"     Tipo del valor: {type(value['test'])}")
            if hasattr(value['test'], 'source_ids'):
                print(f"     source_ids: {value['test'].source_ids}")
    except:
        pass
