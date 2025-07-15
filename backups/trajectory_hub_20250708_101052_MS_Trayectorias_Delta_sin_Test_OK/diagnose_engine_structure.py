# === diagnose_engine_structure.py ===
# 🔧 Fix: Entender la estructura real del engine
# ⚡ Diagnóstico completo de motion_states

from trajectory_hub import EnhancedTrajectoryEngine
import pprint

print("🔍 Diagnóstico completo de la estructura del engine...\n")

# Crear engine y macro
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
engine.create_macro("test", [0, 1, 2])

# 1. Examinar motion_states
print("📋 MOTION_STATES:")
print(f"  Tipo: {type(engine.motion_states)}")
print(f"  Keys: {list(engine.motion_states.keys())}")

# 2. Examinar cada motion state
for key, motion in engine.motion_states.items():
    print(f"\n🔸 Motion State '{key}':")
    print(f"  Tipo: {type(motion)}")
    
    # Si es SourceMotion
    if hasattr(motion, 'active_components'):
        print(f"  active_components tipo: {type(motion.active_components)}")
        if isinstance(motion.active_components, dict):
            print(f"  active_components keys: {list(motion.active_components.keys())}")
        elif isinstance(motion.active_components, list):
            print(f"  active_components length: {len(motion.active_components)}")
    
    # Atributos importantes
    attrs = ['source_id', 'state', 'components']
    for attr in attrs:
        if hasattr(motion, attr):
            print(f"  {attr}: {getattr(motion, attr)}")

# 3. Intentar configurar trayectoria con el nombre correcto
print("\n🧪 Intentando configurar trayectoria...")
try:
    # Probar con el primer key encontrado
    if engine.motion_states:
        first_key = list(engine.motion_states.keys())[0]
        print(f"  Usando key: '{first_key}'")
        engine.set_individual_trajectory(first_key, "circle", "fix", radius=2.0)
        print("  ✅ Configuración exitosa!")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 4. Examinar _positions
print("\n📍 POSITIONS:")
print(f"  Tipo: {type(engine._positions)}")
print(f"  Shape: {engine._positions.shape}")
print(f"  Primeras 3 posiciones:")
for i in range(min(3, len(engine._positions))):
    print(f"    [{i}]: {engine._positions[i]}")

# 5. Buscar el mapeo source_id -> motion_state
print("\n🔗 MAPEOS:")
if hasattr(engine, '_source_to_name'):
    print(f"  _source_to_name: {engine._source_to_name}")
if hasattr(engine, '_name_to_source'):
    print(f"  _name_to_source: {engine._name_to_source}")
if hasattr(engine, 'macros'):
    print(f"  macros keys: {list(engine.macros.keys())}")
    for macro_name, macro in engine.macros.items():
        print(f"    {macro_name}.source_ids: {macro.source_ids}")

# Crear test corregido basado en lo encontrado
print("\n📝 Creando test corregido...")

test_code = '''# === test_individual_corrected.py ===
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 Test corregido de IndividualTrajectory...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro - esto crea fuentes con nombres como "test_0", "test_1", etc.
engine.create_macro("test", [0, 1, 2])

# Los motion_states usan nombres, no IDs numéricos
source_names = ["test_0", "test_1", "test_2"]

# Configurar trayectorias usando los NOMBRES correctos
print("\\nConfigurando trayectorias...")
for i, name in enumerate(source_names):
    try:
        engine.set_individual_trajectory(name, "circle", "fix", 
                                       radius=1.0 + i*0.5, speed=0.5)
        print(f"  ✅ {name} configurada")
    except Exception as e:
        print(f"  ❌ Error con {name}: {e}")

# Guardar posiciones iniciales
initial_pos = {}
for i in range(3):
    initial_pos[i] = engine._positions[i].copy()

print("\\nPosiciones iniciales:")
for i in range(3):
    print(f"  Fuente {i}: {initial_pos[i]}")

# Simular
print("\\nSimulando...")
for frame in range(60):
    engine.update(1/60)

# Verificar movimiento
print("\\nResultados:")
for i in range(3):
    dist = np.linalg.norm(engine._positions[i] - initial_pos[i])
    status = "✅ MOVIDA" if dist > 0.01 else "❌ ESTÁTICA"
    print(f"  Fuente {i}: {status} (dist: {dist:.3f})")
'''

with open("test_individual_corrected.py", "w") as f:
    f.write(test_code)

print("✅ Test creado: test_individual_corrected.py")