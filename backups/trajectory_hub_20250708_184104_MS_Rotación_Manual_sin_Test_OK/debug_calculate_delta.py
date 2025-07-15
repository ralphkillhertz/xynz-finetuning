# debug_calculate_delta.py
# Debug específico de por qué calculate_delta retorna None

import numpy as np
import math

def debug_calculate_delta():
    print("🔍 DEBUG: Por qué calculate_delta retorna None")
    print("=" * 60)
    
    # Buscar el código de ManualMacroRotation.calculate_delta
    print("1️⃣ Buscando código de calculate_delta en ManualMacroRotation...")
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar ManualMacroRotation
    in_manual_rotation = False
    in_calculate_delta = False
    method_lines = []
    
    for i, line in enumerate(lines):
        if 'class ManualMacroRotation' in line:
            in_manual_rotation = True
            print(f"✅ Encontrada clase ManualMacroRotation en línea {i+1}")
            continue
            
        if in_manual_rotation and 'def calculate_delta' in line:
            in_calculate_delta = True
            method_start = i
            continue
            
        if in_calculate_delta:
            if line.strip() and not line.startswith(' '):
                # Fin del método
                break
            method_lines.append((i+1, line))
            
            # Buscar returns
            if 'return None' in line or 'return' in line and 'None' in line:
                print(f"\n⚠️ ENCONTRADO return None en línea {i+1}: {line.strip()}")
            
    print(f"\n2️⃣ Método calculate_delta (líneas {method_start+1}-{method_start+len(method_lines)+1}):")
    for line_num, line in method_lines[:30]:  # Primeras 30 líneas
        print(f"{line_num:4d}: {line.rstrip()}")
        
    # Análisis del problema
    print("\n3️⃣ Análisis del problema:")
    print("   Las fuentes que NO se mueven:")
    print("   - Fuente 1: posición [0, 2, 0]")
    print("   - Fuente 3: posición [0, -2, 0]")
    print("\n   Las fuentes que SÍ se mueven:")
    print("   - Fuente 0: posición [2, 0, 0]")
    print("   - Fuente 2: posición [-2, 0, 0]")
    
    print("\n💡 Patrón detectado:")
    print("   - Las fuentes con X=0 NO se mueven (retornan None)")
    print("   - Las fuentes con Y=0 SÍ se mueven")
    
    # Simular el cálculo
    print("\n4️⃣ Simulación del cálculo:")
    
    positions = [
        ([2, 0, 0], "Fuente 0 (derecha)"),
        ([0, 2, 0], "Fuente 1 (arriba)"),
        ([-2, 0, 0], "Fuente 2 (izquierda)"),
        ([0, -2, 0], "Fuente 3 (abajo)")
    ]
    
    center = np.array([0, 0, 0])
    
    for pos, name in positions:
        pos = np.array(pos, dtype=float)
        rel_pos = pos - center
        
        print(f"\n   {name}:")
        print(f"      Posición: {pos}")
        print(f"      Relativa al centro: {rel_pos}")
        
        # Si X es 0, probablemente hay división por cero o similar
        if abs(rel_pos[0]) < 0.001:
            print(f"      ⚠️ X es casi 0 - posible problema")
        
        # Calcular ángulo actual
        if abs(rel_pos[0]) > 0.001 or abs(rel_pos[1]) > 0.001:
            current_angle = np.arctan2(rel_pos[1], rel_pos[0])
            print(f"      Ángulo actual: {np.degrees(current_angle):.1f}°")
        else:
            print(f"      ❌ No se puede calcular ángulo (posición en centro)")

if __name__ == "__main__":
    debug_calculate_delta()
    
    print("\n💡 Solución probable:")
    print("   El código tiene una condición que retorna None cuando X=0")
    print("   Esto es un BUG en ManualMacroRotation.calculate_delta")