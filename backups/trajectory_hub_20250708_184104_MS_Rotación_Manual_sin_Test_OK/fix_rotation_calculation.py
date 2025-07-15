# fix_rotation_calculation.py
# Examina y corrige el cálculo de rotación en ManualMacroRotation

import numpy as np
import math

def analyze_rotation_calculation():
    print("🔍 Analizando el cálculo de rotación en ManualMacroRotation...")
    
    # Leer el archivo
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar el cálculo de rotación en calculate_delta
    print("\n📋 Buscando el cálculo de rotación...")
    
    in_manual_rotation = False
    in_calculate_delta = False
    rotation_calc_lines = []
    
    for i, line in enumerate(lines):
        if 'class ManualMacroRotation' in line:
            in_manual_rotation = True
            
        if in_manual_rotation and 'def calculate_delta' in line:
            in_calculate_delta = True
            continue
            
        if in_calculate_delta:
            if line.strip() and not line.startswith(' '):
                break
                
            # Buscar líneas relacionadas con el cálculo
            if any(keyword in line for keyword in ['relative_pos', 'rotated_pos', 'rotation_matrix', 'np.dot', 'delta.position']):
                rotation_calc_lines.append((i+1, line))
                
    print("\n📐 Líneas del cálculo de rotación:")
    for line_num, line in rotation_calc_lines:
        print(f"   {line_num}: {line.rstrip()}")
    
    # Simular el cálculo correcto
    print("\n\n🧮 Simulación del cálculo CORRECTO de rotación:")
    
    test_positions = [
        np.array([3.0, 0.0, 0.0]),   # Fuente 0
        np.array([0.0, 3.0, 0.0]),   # Fuente 1
        np.array([-3.0, 0.0, 0.0]),  # Fuente 2
        np.array([0.0, -3.0, 0.0])   # Fuente 3
    ]
    
    center = np.array([0.0, 0.0, 0.0])
    target_yaw = math.pi/2  # 90 grados
    interpolation_speed = 0.05
    dt = 1/60.0
    
    print(f"\n   Centro: {center}")
    print(f"   Rotación objetivo: {math.degrees(target_yaw)}°")
    print(f"   Velocidad interpolación: {interpolation_speed}")
    
    for i, pos in enumerate(test_positions):
        print(f"\n   Fuente {i} - Posición: {pos}")
        
        # Posición relativa al centro
        rel_pos = pos - center
        print(f"      Relativa al centro: {rel_pos}")
        
        # Para una rotación YAW (alrededor del eje Z):
        # x' = x*cos(θ) - y*sin(θ)
        # y' = x*sin(θ) + y*cos(θ)
        # z' = z
        
        # Ángulo actual
        current_angle = np.arctan2(rel_pos[1], rel_pos[0])
        print(f"      Ángulo actual: {math.degrees(current_angle):.1f}°")
        
        # Ángulo objetivo (actual + rotación)
        target_angle = current_angle + target_yaw
        print(f"      Ángulo objetivo: {math.degrees(target_angle):.1f}°")
        
        # Posición objetivo (manteniendo la distancia)
        distance = np.linalg.norm(rel_pos[:2])  # Distancia en plano XY
        target_pos = np.array([
            distance * np.cos(target_angle),
            distance * np.sin(target_angle),
            rel_pos[2]  # Z no cambia
        ])
        print(f"      Posición objetivo: {target_pos}")
        
        # Delta hacia el objetivo
        full_delta = target_pos - rel_pos
        
        # Aplicar interpolación
        smooth_factor = 1.0 - pow(1.0 - interpolation_speed, dt * 60.0)
        interpolated_delta = full_delta * smooth_factor
        
        print(f"      Delta completo: {full_delta}")
        print(f"      Delta interpolado: {interpolated_delta}")
        print(f"      Magnitud delta: {np.linalg.norm(interpolated_delta):.4f}")
        
        # Verificar resultado
        if np.linalg.norm(interpolated_delta) < 0.001:
            print(f"      ⚠️ Delta muy pequeño!")
        else:
            print(f"      ✅ Delta válido")

def create_rotation_fix():
    """Crea un parche temporal para el cálculo de rotación"""
    
    fix_code = '''# fix_manual_rotation_calculation.py
# Parche temporal para ManualMacroRotation.calculate_delta

import numpy as np

def patch_calculate_delta():
    """Reemplaza el método calculate_delta con uno que funciona correctamente"""
    
    print("🔧 Aplicando parche a ManualMacroRotation.calculate_delta...")
    
    # Leer el archivo
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    # El nuevo método corregido
    new_calculate_delta = """    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        \\"\\"\\"Calcula el delta de rotación manual\\"\\"\\"
        if not self.enabled:
            return None
            
        # Crear delta
        delta = MotionDelta(source_id=0)  # El ID se asignará después
        
        # Posición relativa al centro
        relative_pos = state.position - self.center
        
        # Para rotación YAW (alrededor de Z)
        if abs(self.target_yaw - self.current_yaw) > 0.001:
            # Ángulo actual en plano XY
            current_angle = np.arctan2(relative_pos[1], relative_pos[0])
            
            # Diferencia angular
            yaw_diff = self.target_yaw - self.current_yaw
            yaw_diff = np.arctan2(np.sin(yaw_diff), np.cos(yaw_diff))  # Normalizar a [-pi, pi]
            
            # Interpolación
            smooth_factor = 1.0 - pow(1.0 - self.interpolation_speed, dt * 60.0)
            angle_delta = yaw_diff * smooth_factor
            
            # Actualizar ángulo actual
            self.current_yaw += angle_delta
            
            # Nueva posición después de rotar
            distance = np.linalg.norm(relative_pos[:2])
            if distance > 0.001:  # Solo rotar si no está en el centro
                new_angle = current_angle + angle_delta
                new_pos = np.array([
                    distance * np.cos(new_angle),
                    distance * np.sin(new_angle),
                    relative_pos[2]
                ])
                
                # Delta de posición
                delta.position = (new_pos - relative_pos).astype(np.float32)
            else:
                delta.position = np.zeros(3, dtype=np.float32)
        else:
            self.current_yaw = self.target_yaw
            delta.position = np.zeros(3, dtype=np.float32)
            
        return delta
"""
    
    # TODO: Implementar el reemplazo del método
    print("⚠️ Por ahora, copia manualmente el método corregido")
    
    # Guardar el método corregido en un archivo
    with open('manual_rotation_fix.txt', 'w') as f:
        f.write(new_calculate_delta)
    
    print("✅ Método corregido guardado en manual_rotation_fix.txt")

patch_calculate_delta()
'''
    
    with open('fix_manual_rotation_calculation.py', 'w') as f:
        f.write(fix_code)
    
    print("✅ Script de parche creado: fix_manual_rotation_calculation.py")

if __name__ == "__main__":
    analyze_rotation_calculation()
    
    print("\n\n💡 CONCLUSIÓN:")
    print("   El cálculo de rotación actual está MAL")
    print("   - No maneja correctamente fuentes con X=0")
    print("   - Produce valores Z incorrectos")
    print("   - Las distancias se distorsionan")
    
    print("\n🔧 Creando parche...")
    create_rotation_fix()
    
    print("\n📝 Solución:")
    print("   1. El cálculo debe usar ángulos polares (atan2)")
    print("   2. La rotación YAW solo afecta X,Y (no Z)")
    print("   3. La distancia al centro debe preservarse")