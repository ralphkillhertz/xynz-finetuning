# === diagnose_calculate_delta.py ===
# 🔍 Diagnóstico de calculate_delta en ManualIndividualRotation
# ⚡ Debug profundo del cálculo de deltas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import math
from trajectory_hub.core.motion_components import ManualIndividualRotation, MotionState, MotionDelta

print("🔍 DIAGNÓSTICO DE calculate_delta")
print("=" * 60)

# Crear estado de prueba
state = MotionState()
state.position = np.array([3.0, 0.0, 0.0])
state.velocity = np.array([0.0, 0.0, 0.0])
state.orientation = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}

# Crear componente
component = ManualIndividualRotation(
    yaw=math.pi/2,  # 90 grados
    pitch=0.0,
    roll=0.0,
    interpolation_speed=0.1
)

print("1️⃣ Estado inicial:")
print(f"   Posición: {state.position}")
print(f"   current_yaw: {math.degrees(component.current_yaw):.1f}°")
print(f"   target_yaw: {math.degrees(component.target_yaw):.1f}°")

# Llamar update primero
print("\n2️⃣ Llamando update()...")
state_after_update = component.update(0.0, 0.05, state)
print(f"   current_yaw después: {math.degrees(component.current_yaw):.1f}°")
print(f"   ¿Retornó state?: {state_after_update is not None}")

# Ahora calculate_delta
print("\n3️⃣ Llamando calculate_delta()...")
try:
    delta = component.calculate_delta(state, 0.05, 0.05)
    if delta is None:
        print("   ⚠️ calculate_delta retornó None")
    else:
        print(f"   ✅ Delta calculado: {delta.position}")
        print(f"   Magnitude: {np.linalg.norm(delta.position):.6f}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Buscar el método calculate_delta
print("\n4️⃣ Buscando calculate_delta en el archivo...")
try:
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    in_manual_individual = False
    in_calculate_delta = False
    method_lines = []
    
    for i, line in enumerate(lines):
        if 'class ManualIndividualRotation' in line:
            in_manual_individual = True
        elif in_manual_individual and line.strip().startswith('class '):
            in_manual_individual = False
            
        if in_manual_individual and 'def calculate_delta' in line:
            in_calculate_delta = True
            
        if in_calculate_delta:
            method_lines.append((i+1, line.rstrip()))
            if line.strip() and not line[0].isspace() and i > 0:
                break
                
    if method_lines:
        print("📄 Método calculate_delta actual:")
        print("-" * 60)
        for num, line in method_lines[:30]:  # Primeras 30 líneas
            print(f"{num:4d}: {line}")
        print("-" * 60)
    else:
        print("❌ No se encontró calculate_delta")
        
except Exception as e:
    print(f"Error leyendo archivo: {e}")

print("\n🎯 DIAGNÓSTICO COMPLETO")