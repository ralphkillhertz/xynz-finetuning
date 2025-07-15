# === test_rotation_simple.py ===
# 🔧 Test minimalista de rotación MS
# ⚡ Verifica funcionamiento básico

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test Simple de Rotación MS")

# Crear engine con pocas fuentes
engine = EnhancedTrajectoryEngine(n_sources=4, update_rate=30)

# Crear fuentes en cuadrado
for i in range(4):
    angle = i * np.pi / 2
    x = 2 * np.cos(angle)
    y = 2 * np.sin(angle)
    engine.create_source(position=[x, y, 0])

# Crear macro
engine.create_macro("test", [0, 1, 2, 3])

# Posiciones iniciales
print("\n📍 Inicial:")
for i in range(4):
    pos = engine._positions[i]
    print(f"  Fuente {i}: [{pos[0]:5.2f}, {pos[1]:5.2f}, {pos[2]:5.2f}]")

# Aplicar rotación
success = engine.set_macro_rotation("test", speed_y=1.0)  # 1 rad/s en Y
print(f"\n🔄 Rotación aplicada: {success}")

# Simular
print("\n⏱️ Simulando...")
for _ in range(30):  # 1 segundo
    engine.update()

# Posiciones finales
print("\n📍 Final:")
for i in range(4):
    pos = engine._positions[i]
    print(f"  Fuente {i}: [{pos[0]:5.2f}, {pos[1]:5.2f}, {pos[2]:5.2f}]")

# Verificar movimiento
initial = np.array([2.0, 0.0, 0.0])
final = engine._positions[0]
moved = np.linalg.norm(final - initial) > 0.1

print(f"\n{'✅' if moved else '❌'} Movimiento: {'Sí' if moved else 'No'}")