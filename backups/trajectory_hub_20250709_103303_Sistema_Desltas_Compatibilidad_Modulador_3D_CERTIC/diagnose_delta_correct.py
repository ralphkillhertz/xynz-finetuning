# === diagnose_delta_correct.py ===
# 🔍 Diagnóstico correcto de calculate_delta
# ⚡ Usando la API correcta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import math
from trajectory_hub.core.motion_components import ManualIndividualRotation, MotionState, MotionDelta

print("🔍 DIAGNÓSTICO CORRECTO DE calculate_delta")
print("=" * 60)

# Crear componente correctamente
component = ManualIndividualRotation(center=np.array([0.0, 0.0, 0.0]))

# Configurar manualmente los parámetros
component.target_yaw = math.pi/2  # 90 grados
component.target_pitch = 0.0
component.target_roll = 0.0
component.interpolation_speed = 0.1
component.enabled = True

# Crear estado
state = MotionState()
state.position = np.array([3.0, 0.0, 0.0])
state.velocity = np.array([0.0, 0.0, 0.0])
state.orientation = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}

print("1️⃣ Configuración inicial:")
print(f"   Posición: {state.position}")
print(f"   current_yaw: {math.degrees(component.current_yaw):.1f}°")
print(f"   target_yaw: {math.degrees(component.target_yaw):.1f}°")
print(f"   center: {component.center}")

# Simular varios frames
print("\n2️⃣ Simulando rotación...")
print("-" * 60)
print("Frame | current_yaw | Delta | Pos esperada")
print("-" * 60)

for i in range(5):
    # Update
    state = component.update(i*0.05, 0.05, state)
    
    # Calculate delta
    try:
        delta = component.calculate_delta(state, i*0.05, 0.05)
        
        # Calcular posición esperada manualmente
        angle = component.current_yaw
        expected_x = 3.0 * np.cos(angle)
        expected_y = 3.0 * np.sin(angle)
        
        if delta:
            print(f"  {i}   | {math.degrees(component.current_yaw):6.1f}° | {delta.position} | [{expected_x:.3f}, {expected_y:.3f}, 0.000]")
        else:
            print(f"  {i}   | {math.degrees(component.current_yaw):6.1f}° | None | -")
            
    except Exception as e:
        print(f"  {i}   | ERROR: {e}")

# Buscar el método calculate_delta completo
print("\n3️⃣ Analizando calculate_delta...")
try:
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar ManualIndividualRotation
    for i, line in enumerate(lines):
        if 'class ManualIndividualRotation' in line:
            start_idx = i
            break
    
    # Buscar calculate_delta
    in_method = False
    indent_level = None
    
    for i in range(start_idx, len(lines)):
        line = lines[i]
        
        if 'def calculate_delta' in line:
            in_method = True
            indent_level = len(line) - len(line.lstrip())
            print("\n📄 Método calculate_delta:")
            print("-" * 60)
            
        if in_method:
            current_indent = len(line) - len(line.lstrip())
            
            # Si encontramos otro método al mismo nivel, terminamos
            if line.strip().startswith('def ') and current_indent == indent_level and i > start_idx + 1:
                break
                
            # Imprimir línea
            print(f"{i+1:4d}: {line.rstrip()}")
            
            # Buscar problemas específicos
            if 'return None' in line:
                print("      ⚠️ AQUÍ SE RETORNA None")
            if 'if ' in line and 'None' not in line:
                print("      ⚡ Condición encontrada")
                
except Exception as e:
    print(f"Error: {e}")

print("\n🎯 RESUMEN DEL DIAGNÓSTICO")