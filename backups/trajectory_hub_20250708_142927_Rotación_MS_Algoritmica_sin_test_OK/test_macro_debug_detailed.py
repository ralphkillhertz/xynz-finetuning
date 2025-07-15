# === test_macro_debug_detailed.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import math

print("🔍 DEBUG DETALLADO: MacroTrajectory\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
print("1️⃣ Creando macro...")
engine.create_macro("test", [0, 1, 2])

# Verificar que el macro existe
print("\n2️⃣ Verificando macro:")
if hasattr(engine, 'None'):
    macros = getattr(engine, 'None')
    print(f"  Macros disponibles: {list(macros.keys())}")
    
    if "test" in macros:
        macro = macros["test"]
        print(f"  ✅ Macro 'test' existe")
        print(f"  source_ids: {macro.source_ids}")
        
        # Verificar trajectory_component
        if hasattr(macro, 'trajectory_component'):
            tc = macro.trajectory_component
            print(f"  trajectory_component: {tc}")
            if tc:
                print(f"    - Tipo: {type(tc).__name__}")
                print(f"    - enabled: {tc.enabled if hasattr(tc, 'enabled') else 'N/A'}")
        else:
            print("  ❌ NO tiene trajectory_component")
else:
    print("  ❌ No se encontró atributo de macros")

# Función de trayectoria simple
def simple_trajectory(t):
    return np.array([t, 0.0, 0.0])  # Movimiento lineal en X

# Configurar trayectoria
print("\n3️⃣ Configurando trayectoria...")
try:
    engine.set_macro_trajectory("test", simple_trajectory)
    print("  ✅ set_macro_trajectory ejecutado")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Verificar componentes en motion_states
print("\n4️⃣ Verificando motion_states:")
for sid in [0, 1, 2]:
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        components = list(motion.active_components.keys())
        print(f"  Fuente {sid}: {components}")
        
        # Verificar macro_trajectory
        if 'macro_trajectory' in motion.active_components:
            mt = motion.active_components['macro_trajectory']
            print(f"    - MacroTrajectory.enabled: {mt.enabled}")
            print(f"    - MacroTrajectory.trajectory_func: {mt.trajectory_func is not None}")
            
            # Test calculate_delta directamente
            if hasattr(mt, 'calculate_delta'):
                print("    - tiene calculate_delta ✅")
                
                # Llamar directamente
                delta = mt.calculate_delta(motion, 0.0, 1/60)
                if delta:
                    print(f"    - Delta calculado: {delta.position}")
                else:
                    print("    - Delta es None")
            else:
                print("    - NO tiene calculate_delta ❌")

# Test un solo frame
print("\n5️⃣ Test de un frame:")
pos_before = engine._positions[0].copy()
print(f"  Antes: {pos_before}")

engine.update()

pos_after = engine._positions[0].copy()
print(f"  Después: {pos_after}")
print(f"  Movimiento: {np.linalg.norm(pos_after - pos_before):.6f}")

# Debug adicional
print("\n6️⃣ Debug del engine:")
print(f"  motion_states keys: {list(engine.motion_states.keys())}")
print(f"  _positions shape: {engine._positions.shape}")
