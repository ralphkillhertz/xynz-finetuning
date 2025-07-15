# investigate_rotation_deeper.py
# Investigación más profunda del problema de rotación

import numpy as np
import math
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ManualMacroRotation, MotionState, MotionDelta

def test_calculate_delta_directly():
    print("🔬 TEST DIRECTO: ManualMacroRotation.calculate_delta")
    print("=" * 60)
    
    # Crear componente de rotación
    rotation = ManualMacroRotation()
    rotation.enabled = True
    rotation.target_yaw = math.pi/2  # 90 grados
    rotation.target_pitch = 0.0
    rotation.target_roll = 0.0
    rotation.center = np.array([0.0, 0.0, 0.0])
    rotation.interpolation_speed = 0.1
    
    # Probar con diferentes posiciones
    test_positions = [
        ([3.0, 0.0, 0.0], "Fuente 0 - Derecha (Y=0)"),
        ([0.0, 3.0, 0.0], "Fuente 1 - Arriba (X=0)"),
        ([-3.0, 0.0, 0.0], "Fuente 2 - Izquierda (Y=0)"),
        ([0.0, -3.0, 0.0], "Fuente 3 - Abajo (X=0)"),
        ([2.0, 2.0, 0.0], "Fuente diagonal (X=Y)")
    ]
    
    print("\n📊 Resultados de calculate_delta para cada posición:")
    
    for pos, desc in test_positions:
        # Crear estado
        state = MotionState()
        state.position = np.array(pos, dtype=np.float32)
        state.orientation = np.array([0.0, 0.0, 0.0])
        state.aperture = 0.5
        
        # Calcular delta
        print(f"\n   {desc}:")
        print(f"      Posición: {state.position}")
        
        try:
            delta = rotation.calculate_delta(state, 0.0, 1/60.0)
            
            if delta is None:
                print(f"      ❌ calculate_delta retornó None")
            else:
                print(f"      ✅ Delta: {delta.position}")
                print(f"      Magnitud: {np.linalg.norm(delta.position):.6f}")
                
                # Verificar si el delta tiene sentido para una rotación
                # En una rotación de 90°, [3,0,0] debería ir hacia [0,3,0]
                if desc.startswith("Fuente 0"):
                    expected_direction = np.array([0.0, 3.0, 0.0]) - pos
                    expected_direction = expected_direction / np.linalg.norm(expected_direction)
                    actual_direction = delta.position / (np.linalg.norm(delta.position) + 1e-10)
                    dot_product = np.dot(expected_direction, actual_direction)
                    print(f"      Dirección correcta: {'✅' if dot_product > 0.9 else '❌'} (dot={dot_product:.3f})")
                    
        except Exception as e:
            print(f"      ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Verificar el código actual
    print("\n\n🔍 Verificando el código de calculate_delta después del fix...")
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar alrededor de la línea 1150
    print("\n📋 Código alrededor de la línea del fix:")
    for i in range(1145, 1160):
        if i < len(lines):
            line = lines[i].rstrip()
            if 'return None' in line or 'np.linalg.norm(delta.position)' in line:
                print(f">>> {i+1:4d}: {line}")
            else:
                print(f"    {i+1:4d}: {line}")
    
    # Buscar si hay otra condición que retorna None
    print("\n🔍 Buscando TODAS las líneas que retornan None en calculate_delta:")
    in_calculate_delta = False
    method_start = 0
    
    for i, line in enumerate(lines):
        if 'def calculate_delta' in line and 'ManualMacroRotation' in lines[max(0, i-20):i]:
            in_calculate_delta = True
            method_start = i
            
        if in_calculate_delta:
            if line.strip() and not line[0].isspace():
                # Fin del método
                break
                
            if 'return None' in line:
                print(f"   Línea {i+1}: {line.strip()}")
                # Mostrar contexto
                for j in range(max(0, i-2), min(i+1, len(lines))):
                    print(f"      {j+1}: {lines[j].rstrip()}")

if __name__ == "__main__":
    test_calculate_delta_directly()
    
    print("\n\n💡 Conclusiones:")
    print("   1. Si algunas posiciones retornan None, hay más condiciones problemáticas")
    print("   2. Si los deltas son incorrectos, el cálculo de rotación está mal")
    print("   3. Necesitamos encontrar y arreglar TODOS los return None")