# === implement_individual_rotation.py ===
# 🔧 Implementar rotaciones individuales (IS) con sistema de deltas
# ⚡ IndividualRotation (algorítmica) y ManualIndividualRotation

import os
import re
from datetime import datetime

def implement_individual_rotations():
    """Añade las clases de rotación individual a motion_components.py"""
    
    print("🔧 IMPLEMENTANDO ROTACIONES INDIVIDUALES (IS)")
    print("=" * 60)
    
    # Ruta del archivo
    file_path = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra {file_path}")
        return False
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Código de las nuevas clases
    individual_rotation_code = '''

class IndividualRotation(MotionComponent):
    """Rotación algorítmica continua para fuentes individuales"""
    
    def __init__(self, center: Optional[np.ndarray] = None,
                 speed_x: float = 0.0, speed_y: float = 0.0, speed_z: float = 0.0):
        """
        Args:
            center: Centro de rotación (default: origen de la fuente)
            speed_x: Velocidad de rotación en X (rad/s)
            speed_y: Velocidad de rotación en Y (rad/s)
            speed_z: Velocidad de rotación en Z (rad/s)
        """
        super().__init__()
        self.center = np.array(center if center is not None else [0.0, 0.0, 0.0])
        self.speed_x = float(speed_x)
        self.speed_y = float(speed_y)
        self.speed_z = float(speed_z)
        self.enabled = any(abs(s) > 0.001 for s in [speed_x, speed_y, speed_z])
        
        # Tiempo acumulado para la rotación
        self.accumulated_time = 0.0
        
    def update(self, current_time: float, dt: float):
        """Actualiza el tiempo acumulado"""
        if self.enabled:
            self.accumulated_time += dt
    
    def calculate_delta(self, state: 'MotionState', current_time: float, dt: float) -> Optional['MotionDelta']:
        """Calcula el cambio para rotación continua individual"""
        if not self.enabled:
            return None
            
        from trajectory_hub.core import MotionDelta
        delta = MotionDelta()
        
        # Posición relativa al centro
        current_position = np.array(state.position)
        relative_pos = current_position - self.center
        
        # Si está muy cerca del centro, mover ligeramente
        if np.linalg.norm(relative_pos) < 0.001:
            delta.position = np.array([0.1, 0.0, 0.0])
            return delta
        
        # Calcular rotaciones incrementales
        angle_x = self.speed_x * dt
        angle_y = self.speed_y * dt
        angle_z = self.speed_z * dt
        
        # Aplicar rotaciones en orden Y, X, Z (evita gimbal lock)
        new_pos = relative_pos.copy()
        
        # Rotación alrededor de Y (yaw)
        if abs(angle_y) > 0.00001:
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            x = new_pos[0]
            z = new_pos[2]
            new_pos[0] = x * cos_y - z * sin_y
            new_pos[2] = x * sin_y + z * cos_y
        
        # Rotación alrededor de X (pitch)
        if abs(angle_x) > 0.00001:
            cos_x = np.cos(angle_x)
            sin_x = np.sin(angle_x)
            y = new_pos[1]
            z = new_pos[2]
            new_pos[1] = y * cos_x - z * sin_x
            new_pos[2] = y * sin_x + z * cos_x
        
        # Rotación alrededor de Z (roll)
        if abs(angle_z) > 0.00001:
            cos_z = np.cos(angle_z)
            sin_z = np.sin(angle_z)
            x = new_pos[0]
            y = new_pos[1]
            new_pos[0] = x * cos_z - y * sin_z
            new_pos[1] = x * sin_z + y * cos_z
        
        # Trasladar de vuelta
        new_pos += self.center
        
        # Delta es la diferencia
        delta.position = new_pos - current_position
        
        return delta
    
    def set_rotation_speeds(self, speed_x: float = 0.0, speed_y: float = 0.0, speed_z: float = 0.0):
        """Actualiza las velocidades de rotación"""
        self.speed_x = float(speed_x)
        self.speed_y = float(speed_y)
        self.speed_z = float(speed_z)
        self.enabled = any(abs(s) > 0.001 for s in [speed_x, speed_y, speed_z])


class ManualIndividualRotation(MotionComponent):
    """Rotación manual con interpolación para fuentes individuales"""
    
    def __init__(self, center: Optional[np.ndarray] = None):
        """
        Args:
            center: Centro de rotación (default: origen de la fuente)
        """
        super().__init__()
        self.center = np.array(center if center is not None else [0.0, 0.0, 0.0])
        
        # Ángulos objetivo y actuales
        self.target_yaw = 0.0
        self.target_pitch = 0.0
        self.target_roll = 0.0
        
        self.current_yaw = 0.0
        self.current_pitch = 0.0
        self.current_roll = 0.0
        
        # Velocidad de interpolación
        self.interpolation_speed = 0.1
        
        self.enabled = False
    
    def set_target_rotation(self, yaw: float = 0.0, pitch: float = 0.0, roll: float = 0.0,
                          interpolation_speed: float = 0.1):
        """Establece la rotación objetivo"""
        self.target_yaw = float(yaw)
        self.target_pitch = float(pitch)
        self.target_roll = float(roll)
        self.interpolation_speed = max(0.01, min(1.0, float(interpolation_speed)))
        self.enabled = True
    
    def update(self, current_time: float, dt: float):
        """Actualiza los ángulos actuales interpolando hacia el objetivo"""
        if not self.enabled:
            return
        
        # Interpolación suave hacia los ángulos objetivo
        factor = self.interpolation_speed
        self.current_yaw += (self.target_yaw - self.current_yaw) * factor
        self.current_pitch += (self.target_pitch - self.current_pitch) * factor
        self.current_roll += (self.target_roll - self.current_roll) * factor
        
        # Verificar si llegamos al objetivo
        diff_yaw = abs(self.target_yaw - self.current_yaw)
        diff_pitch = abs(self.target_pitch - self.current_pitch)
        diff_roll = abs(self.target_roll - self.current_roll)
        
        if diff_yaw < 0.001 and diff_pitch < 0.001 and diff_roll < 0.001:
            self.current_yaw = self.target_yaw
            self.current_pitch = self.target_pitch
            self.current_roll = self.target_roll
            self.enabled = False
    
    def calculate_delta(self, state: 'MotionState', current_time: float, dt: float) -> Optional['MotionDelta']:
        """Calcula el cambio para rotación manual individual"""
        if not self.enabled:
            return None
            
        from trajectory_hub.core import MotionDelta
        delta = MotionDelta()
        
        # Posición actual y relativa
        current_position = np.array(state.position)
        relative_pos = current_position - self.center
        
        # Si está en el centro, no rotar
        if np.linalg.norm(relative_pos) < 0.001:
            return None
        
        # Para rotación individual, usamos un enfoque diferente:
        # Calculamos la posición objetivo basada en los ángulos actuales
        
        # Convertir a coordenadas esféricas
        r = np.linalg.norm(relative_pos)
        theta = np.arctan2(relative_pos[1], relative_pos[0])  # Ángulo en XY
        phi = np.arctan2(relative_pos[2], np.sqrt(relative_pos[0]**2 + relative_pos[1]**2))  # Elevación
        
        # Aplicar rotaciones (simplificado para yaw primero)
        new_theta = theta + (self.current_yaw - theta) * self.interpolation_speed
        
        # Convertir de vuelta a cartesianas
        xy_dist = r * np.cos(phi)
        new_x = xy_dist * np.cos(new_theta)
        new_y = xy_dist * np.sin(new_theta)
        new_z = r * np.sin(phi)  # Por ahora sin pitch/roll
        
        # Nueva posición absoluta
        new_position = self.center + np.array([new_x, new_y, new_z])
        
        # Delta
        delta.position = new_position - current_position
        
        # Limitar el delta para evitar saltos
        max_delta = 0.1
        delta_magnitude = np.linalg.norm(delta.position)
        if delta_magnitude > max_delta:
            delta.position = delta.position * (max_delta / delta_magnitude)
        
        return delta
    
    def _sync_with_state(self, state: 'MotionState'):
        """Sincroniza los ángulos actuales con la posición del estado"""
        relative_pos = np.array(state.position) - self.center
        if np.linalg.norm(relative_pos) > 0.001:
            self.current_yaw = np.arctan2(relative_pos[1], relative_pos[0])
            # Simplificado: solo sincronizamos yaw por ahora
'''
    
    # Buscar dónde insertar (después de ManualMacroRotation)
    print("\n🔍 Buscando lugar para insertar...")
    
    # Patrón para encontrar el final de ManualMacroRotation
    pattern = r'(class ManualMacroRotation.*?(?=\n\nclass|\n\n# |\Z))'
    
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        
        # Insertar el código
        content = content[:insert_pos] + individual_rotation_code + content[insert_pos:]
        
        print("✅ Clases de rotación individual añadidas")
    else:
        print("❌ No se pudo encontrar el lugar de inserción")
        return False
    
    # Escribir el archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ motion_components.py actualizado con:")
    print("   - IndividualRotation (algorítmica)")
    print("   - ManualIndividualRotation")
    
    print("\n📌 Siguiente paso: Actualizar enhanced_trajectory_engine.py")
    
    return True

if __name__ == "__main__":
    implement_individual_rotations()