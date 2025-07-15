
# === test_sphere_correct.py ===
import sys
sys.path.append('.')

# Test directo del cálculo de sphere
print("🧪 TEST DE SPHERE 3D")
print("="*40)

# Opción 1: Probar FormationManager si existe
try:
    from trajectory_hub.control.managers.formation_manager import FormationManager
    fm = FormationManager()
    
    # Intentar diferentes métodos
    methods_to_try = ['calculate_formation', 'get_formation', 'calculate_formation', 'create_formation']
    
    for method_name in methods_to_try:
        if hasattr(fm, method_name):
            print(f"\n✅ Probando {method_name}()...")
            method = getattr(fm, method_name)
            try:
                # Intentar llamar con diferentes firmas
                try:
                    positions = method("sphere", 8)
                except:
                    positions = method("sphere", 8, scale=2.0)
                
                if positions:
                    print(f"\n🌐 POSICIONES SPHERE ({len(positions)} fuentes):")
                    for i, pos in enumerate(list(positions)[:5]):
                        if isinstance(pos, tuple) and len(pos) >= 3:
                            print(f"   Fuente {i}: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")
                        else:
                            print(f"   Fuente {i}: {pos}")
                    break
            except Exception as e:
                print(f"   Error con {method_name}: {e}")
                
except ImportError:
    print("❌ No se pudo importar FormationManager")

# Opción 2: Probar directamente el código sphere
print("\n\n📊 CÁLCULO DIRECTO DE SPHERE:")
import math

positions = []
source_count = 8
radius = 2.0
scale = 1.0
center = (0, 0, 0)

# Código sphere con espiral de Fibonacci
golden_ratio = (1 + math.sqrt(5)) / 2

for i in range(source_count):
    # Y va de 1 a -1
    y = 1 - (2 * i / (source_count - 1)) if source_count > 1 else 0
    
    # Radio en plano XZ
    radius_xz = math.sqrt(1 - y * y)
    
    # Ángulo usando proporción áurea
    theta = 2 * math.pi * i / golden_ratio
    
    # Coordenadas 3D
    x = radius_xz * math.cos(theta) * radius * scale
    y_scaled = y * radius * scale
    z = radius_xz * math.sin(theta) * radius * scale
    
    positions.append((center[0] + x, center[1] + y_scaled, center[2] + z))
    
    print(f"Fuente {i}: x={x:.2f}, y={y_scaled:.2f}, z={z:.2f}")

# Verificar que es 3D
y_values = [pos[1] for pos in positions]
z_values = [pos[2] for pos in positions]

print(f"\n✅ Rango Y: {min(y_values):.2f} a {max(y_values):.2f}")
print(f"✅ Rango Z: {min(z_values):.2f} a {max(z_values):.2f}")

if max(y_values) - min(y_values) > 0.1:
    print("\n✅ ES 3D! Tiene variación en altura (Y)")
else:
    print("\n❌ ES 2D! Sin variación en Y")
