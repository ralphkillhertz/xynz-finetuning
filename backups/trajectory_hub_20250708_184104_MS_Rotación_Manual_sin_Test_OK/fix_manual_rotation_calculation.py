# fix_manual_rotation_calculation.py
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
        \"\"\"Calcula el delta de rotación manual\"\"\"
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
