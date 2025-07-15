# === apply_rotation_fix.py ===
# 🔧 Fix: Aplicar corrección del algoritmo de rotación
# ⚡ Líneas modificadas: calculate_delta en ManualMacroRotation
# 🎯 Impacto: ALTO - Corrige rotación manual MS

import re
import shutil
from datetime import datetime

def apply_rotation_fix():
    """Aplica la corrección del algoritmo de rotación a ManualMacroRotation"""
    
    # Backup
    backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer el archivo
    with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # El método corregido completo
    fixed_method = '''    def calculate_delta(self, state: 'MotionState', current_time: float, dt: float) -> Optional['MotionDelta']:
        """Calcula el cambio necesario para la rotación manual usando ángulos polares"""
        if not self.enabled:
            return None
            
        from trajectory_hub.core import MotionDelta
        delta = MotionDelta()
        
        current_position = np.array(state.position)
        relative_pos = current_position - self.center
        
        # Calcular ángulo actual usando atan2 (maneja todos los cuadrantes)
        current_angle = np.arctan2(relative_pos[1], relative_pos[0])
        
        # Calcular ángulo objetivo (solo YAW por ahora)
        target_angle = self.target_yaw
        
        # Calcular diferencia angular (ruta más corta)
        angle_diff = target_angle - current_angle
        # Normalizar a [-pi, pi]
        angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))
        
        # Interpolar
        angle_step = angle_diff * self.interpolation_speed * dt
        new_angle = current_angle + angle_step
        
        # Calcular nueva posición preservando la distancia
        distance = np.linalg.norm(relative_pos[:2])  # Solo distancia XY
        
        if distance > 0.001:  # Evitar división por cero
            new_x = distance * np.cos(new_angle)
            new_y = distance * np.sin(new_angle)
            new_z = relative_pos[2]  # Z sin cambios para rotación YAW
            
            new_position = self.center + np.array([new_x, new_y, new_z])
            delta.position = new_position - current_position
            
            # Aplicar los otros ejes si están configurados
            if abs(self.target_pitch) > 0.001 or abs(self.target_roll) > 0.001:
                # Por ahora solo implementamos YAW
                # TODO: Implementar rotaciones completas 3D
                pass
        else:
            # Si está en el centro, mover ligeramente para evitar singularidad
            delta.position = np.array([0.1, 0.0, 0.0])
        
        return delta'''
    
    # Buscar el método calculate_delta en ManualMacroRotation
    pattern = r'(class ManualMacroRotation.*?)(def calculate_delta\(self.*?\n(?:.*?\n)*?        return delta)'
    
    def replacer(match):
        class_part = match.group(1)
        # Buscar el final del método anterior para mantener la indentación
        lines = class_part.split('\n')
        # Encontrar la última línea con contenido para determinar la indentación
        for line in reversed(lines):
            if line.strip() and not line.strip().startswith('#'):
                if 'def ' in line or 'return' in line or 'pass' in line:
                    break
        
        return class_part + '\n' + fixed_method
    
    # Aplicar el reemplazo
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    # Verificar que se hizo el cambio
    if "usando ángulos polares" in new_content and "np.arctan2" in new_content:
        # Escribir el archivo
        with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Método calculate_delta corregido exitosamente")
        print("📐 Ahora usa ángulos polares (atan2) para rotación correcta")
        return True
    else:
        print("❌ No se pudo aplicar el parche automáticamente")
        print("📝 Por favor, revisa manual_rotation_fix.txt y aplícalo manualmente")
        return False

if __name__ == "__main__":
    print("🔧 Aplicando corrección del algoritmo de rotación...")
    if apply_rotation_fix():
        print("\n🎯 Próximo paso: Ejecutar test de rotación")
        print("$ python test_rotation_controlled.py")