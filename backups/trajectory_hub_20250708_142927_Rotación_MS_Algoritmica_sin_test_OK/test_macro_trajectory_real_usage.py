# === test_macro_trajectory_real_usage.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import math

print("🧪 Test MacroTrajectory - Implementación REAL\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
print("1️⃣ Creando macro...")
engine.create_macro("orbita", [0, 1, 2, 3, 4])

# Definir función de trayectoria circular
def circular_trajectory(t):
    """Trayectoria circular en el plano XY"""
    radius = 5.0
    return np.array([
        radius * np.cos(t),
        radius * np.sin(t),
        0.0
    ])

def circular_orientation(t):
    """Orientación que sigue la tangente del círculo"""
    return np.array([
        t * 180 / math.pi,  # yaw
        0.0,                # pitch
        0.0                 # roll
    ])

# Configurar trayectoria usando funciones
print("\n2️⃣ Configurando trayectoria con funciones...")
try:
    # Basado en el análisis, parece que espera funciones directamente
    engine.set_macro_trajectory(
        "orbita",
        trajectory_func=circular_trajectory,
        orientation_func=circular_orientation
    )
    print("✅ Trayectoria configurada")
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Plan B: tal vez hay otro método
    print("\n🔄 Intentando método alternativo...")
    # Buscar si hay set_trajectory en el macro directamente
    macro = engine._macros.get("orbita")
    if macro and hasattr(macro, 'trajectory_component'):
        if macro.trajectory_component:
            macro.trajectory_component.set_trajectory(
                position_func=circular_trajectory,
                orientation_func=circular_orientation,
                speed=2.0
            )
            macro.trajectory_component.enabled = True
            print("✅ Configurado via trajectory_component")

# Guardar posiciones iniciales
print("\n3️⃣ Estado inicial:")
positions_start = {}
for i in range(5):
    positions_start[i] = engine._positions[i].copy()
    print(f"  Fuente {i}: {positions_start[i]}")

# Simular movimiento
print("\n4️⃣ Simulando 2 segundos...")
for frame in range(120):  # 2 segundos a 60 fps
    engine.update()
    
    if frame == 30:  # Medio segundo
        dist = np.linalg.norm(engine._positions[0] - positions_start[0])
        print(f"  0.5s: Fuente 0 movió {dist:.3f} unidades")

# Resultados finales
print("\n5️⃣ Resultados:")
total_moved = 0
for i in range(5):
    pos_final = engine._positions[i]
    distance = np.linalg.norm(pos_final - positions_start[i])
    
    if distance > 0.01:
        print(f"  ✅ Fuente {i}: {distance:.3f} unidades")
        total_moved += 1
    else:
        print(f"  ❌ Fuente {i}: Sin movimiento")

if total_moved == 5:
    print("\n🎉 ¡ÉXITO TOTAL! Todas las fuentes se movieron")
elif total_moved > 0:
    print(f"\n⚠️ Éxito parcial: {total_moved}/5 fuentes se movieron")
else:
    print("\n❌ FALLO: Ninguna fuente se movió")
    
    # Debug
    print("\n🔍 Debug:")
    if "orbita" in engine._macros:
        macro = engine._macros["orbita"]
        print(f"  Macro existe: ✓")
        if hasattr(macro, 'trajectory_component'):
            tc = macro.trajectory_component
            if tc:
                print(f"  trajectory_component: {tc}")
                print(f"  enabled: {tc.enabled}")
                print(f"  phase: {tc.phase}")
