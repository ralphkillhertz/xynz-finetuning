
# === test_sphere_3d.py ===
from trajectory_hub.control.managers.formation_manager import FormationManager

# Test directo
fm = FormationManager()
positions = fm.get_formation("sphere", 8, scale=2.0)

print("\n🌐 POSICIONES SPHERE (8 fuentes):")
for i, pos in enumerate(positions):
    print(f"Fuente {i}: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")

# Verificar que es 3D
y_values = [pos[1] for pos in positions]
z_values = [pos[2] for pos in positions]

if len(set(y_values)) > 1:
    print("\n✅ Variación en Y (altura) - ES 3D!")
else:
    print("\n❌ Sin variación en Y - ES 2D!")

if len(set(z_values)) > 2:
    print("✅ Variación en Z (profundidad)")
else:
    print("❌ Sin variación en Z")
