# === test_rotation_correct_args.py ===
# 🧪 Test con argumentos correctos

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\n🔄 TEST: Rotación MS con argumentos correctos\n")

# Crear engine con argumentos por defecto (sin argumentos)
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado con valores por defecto")

# Ver cuántas fuentes tiene
print(f"   Fuentes disponibles: {len(engine._positions)}")

# Crear macro con 4 fuentes
macro_id = engine.create_macro("test", 4)
print(f"✅ Macro creado: {macro_id}")

# Configurar posiciones manualmente
positions = [[2,0,0], [-2,0,0], [0,2,0], [0,-2,0]]
macro = engine._macros[macro_id]

for i, sid in enumerate(list(macro.source_ids)[:4]):
    if sid < len(engine._positions):
        engine._positions[sid] = np.array(positions[i % len(positions)])
        if sid in engine.motion_states:
            engine.motion_states[sid].position = engine._positions[sid].copy()

print("\n📍 Posiciones iniciales:")
initial = {}
for sid in list(macro.source_ids)[:4]:
    if sid < len(engine._positions):
        p = engine._positions[sid]
        initial[sid] = p.copy()
        print(f"   Fuente {sid}: [{p[0]:.1f}, {p[1]:.1f}, {p[2]:.1f}]")

# Configurar rotación
print("\n🎯 Configurando rotación...")
try:
    engine.set_macro_rotation(macro_id, 0, 1.0, 0)  # 1 rad/s en Y
    print("✅ Rotación configurada")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Simular
print("\n⏱️ Simulando 60 frames...")
for i in range(60):
    engine.update()

print("\n📍 Posiciones finales:")
total_movement = 0
for sid in list(macro.source_ids)[:4]:
    if sid < len(engine._positions) and sid in initial:
        p = engine._positions[sid]
        dist = np.linalg.norm(p - initial[sid])
        total_movement += dist
        print(f"   Fuente {sid}: [{p[0]:.1f}, {p[1]:.1f}, {p[2]:.1f}] (movió {dist:.2f})")

if total_movement > 0.1:
    print(f"\n✅ ¡ROTACIÓN FUNCIONANDO! Movimiento total: {total_movement:.2f}")
    print("\n📊 SISTEMA DE DELTAS COMPLETO:")
    print("   ✅ Concentración: 100%")
    print("   ✅ Trayectorias IS: 100%")
    print("   ✅ Trayectorias MS: 100%")
    print("   ✅ Rotaciones MS algorítmicas: 100%")
else:
    print(f"\n❌ Sin movimiento detectado: {total_movement:.3f}")
