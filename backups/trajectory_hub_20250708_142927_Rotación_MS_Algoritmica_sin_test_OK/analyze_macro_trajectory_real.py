# === analyze_macro_trajectory_real.py ===
# 🔍 Entender la implementación REAL de set_macro_trajectory
# ⚡ Ver toda la estructura para crear test correcto

import re

print("🔍 ANÁLISIS COMPLETO: set_macro_trajectory\n")

# 1. Ver la firma completa del método
engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_path, 'r') as f:
    content = f.read()

# Buscar el método completo
match = re.search(r'(def set_macro_trajectory\(.*?\):.*?)(?=\n    def|\n\nclass|\Z)', content, re.DOTALL)
if match:
    full_method = match.group(1)
    print("📝 MÉTODO COMPLETO:")
    print("="*60)
    # Mostrar solo las primeras 50 líneas
    lines = full_method.split('\n')[:50]
    for i, line in enumerate(lines):
        print(f"{i+1:3d}: {line}")
    print("="*60)

# 2. Buscar cómo se usa en otros archivos
print("\n\n🔍 USOS DE set_macro_trajectory EN EL PROYECTO:")

import os
for root, dirs, files in os.walk("trajectory_hub"):
    if "__pycache__" in root:
        continue
    
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    file_content = f.read()
                
                # Buscar llamadas a set_macro_trajectory
                calls = re.findall(r'\.set_macro_trajectory\((.*?)\)', file_content, re.DOTALL)
                if calls:
                    print(f"\n📄 {filepath}:")
                    for call in calls[:3]:  # Primeras 3 llamadas
                        # Limpiar y mostrar
                        call_clean = ' '.join(call.split())[:100]
                        print(f"  → {call_clean}...")
            except:
                pass

# 3. Ver si hay otra versión o wrapper
print("\n\n🔍 BUSCANDO MÉTODOS RELACIONADOS:")
methods = re.findall(r'def (\w*macro\w*trajectory\w*)\(', content, re.IGNORECASE)
for method in set(methods):
    print(f"  - {method}")

# 4. Ver la estructura de _macros
print("\n\n🔍 ESTRUCTURA DE MACROS:")
macro_refs = re.findall(r'self\._macros\[.*?\]\.(\w+)', content)
attrs = set(macro_refs)
print("Atributos de macro usados:")
for attr in sorted(attrs):
    print(f"  - macro.{attr}")

# 5. Crear test basado en el análisis
print("\n\n✅ CREANDO TEST CORRECTO...")

test_code = '''# === test_macro_trajectory_real_usage.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import math

print("🧪 Test MacroTrajectory - Implementación REAL\\n")

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
print("\\n2️⃣ Configurando trayectoria con funciones...")
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
    print("\\n🔄 Intentando método alternativo...")
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
print("\\n3️⃣ Estado inicial:")
positions_start = {}
for i in range(5):
    positions_start[i] = engine._positions[i].copy()
    print(f"  Fuente {i}: {positions_start[i]}")

# Simular movimiento
print("\\n4️⃣ Simulando 2 segundos...")
for frame in range(120):  # 2 segundos a 60 fps
    engine.update()
    
    if frame == 30:  # Medio segundo
        dist = np.linalg.norm(engine._positions[0] - positions_start[0])
        print(f"  0.5s: Fuente 0 movió {dist:.3f} unidades")

# Resultados finales
print("\\n5️⃣ Resultados:")
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
    print("\\n🎉 ¡ÉXITO TOTAL! Todas las fuentes se movieron")
elif total_moved > 0:
    print(f"\\n⚠️ Éxito parcial: {total_moved}/5 fuentes se movieron")
else:
    print("\\n❌ FALLO: Ninguna fuente se movió")
    
    # Debug
    print("\\n🔍 Debug:")
    if "orbita" in engine._macros:
        macro = engine._macros["orbita"]
        print(f"  Macro existe: ✓")
        if hasattr(macro, 'trajectory_component'):
            tc = macro.trajectory_component
            if tc:
                print(f"  trajectory_component: {tc}")
                print(f"  enabled: {tc.enabled}")
                print(f"  phase: {tc.phase}")
'''

with open("test_macro_trajectory_real_usage.py", "w") as f:
    f.write(test_code)

print("📝 Test creado: test_macro_trajectory_real_usage.py")
print("🚀 Ejecuta: python test_macro_trajectory_real_usage.py")