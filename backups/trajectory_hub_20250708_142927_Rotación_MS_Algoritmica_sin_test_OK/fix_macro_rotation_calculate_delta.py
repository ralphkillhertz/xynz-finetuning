# === fix_macro_rotation_calculate_delta.py ===
# 🔧 Fix: Añadir método calculate_delta a MacroRotation
# ⚡ Impacto: CRÍTICO - Sin esto no hay movimiento

import os
import re

def add_calculate_delta_to_macro_rotation():
    """Añadir método calculate_delta que falta en MacroRotation"""
    
    file_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar dónde insertar el método (después de __init__)
    pattern = r'(class MacroRotation[^:]+:.*?def __init__.*?\n(?:.*?\n)*?)((?:\s{4}|\t)def|\s*class|\s*$)'
    
    def replacement(match):
        class_content = match.group(1)
        next_section = match.group(2)
        
        # Si ya tiene calculate_delta, no hacer nada
        if 'def calculate_delta' in class_content:
            return match.group(0)
        
        # Añadir el método calculate_delta
        calculate_delta_method = '''
    def calculate_delta(self, state, current_time, dt):
        """Calcular delta de rotación para el sistema de deltas"""
        if not self.enabled:
            return MotionDelta()
        
        # Calcular ángulos de rotación basados en velocidad y tiempo
        angle_x = float(self.speed_x) * dt
        angle_y = float(self.speed_y) * dt  
        angle_z = float(self.speed_z) * dt
        
        # Si no hay rotación, retornar delta vacío
        if abs(angle_x) < 0.0001 and abs(angle_y) < 0.0001 and abs(angle_z) < 0.0001:
            return MotionDelta()
        
        # Obtener posición actual relativa al centro
        current_pos = state.position
        relative_pos = current_pos - self.center
        
        # Aplicar rotaciones (orden: Y -> X -> Z)
        rotated_pos = relative_pos.copy()
        
        # Rotación en Y (yaw)
        if abs(angle_y) > 0.0001:
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            new_x = rotated_pos[0] * cos_y - rotated_pos[2] * sin_y
            new_z = rotated_pos[0] * sin_y + rotated_pos[2] * cos_y
            rotated_pos[0] = new_x
            rotated_pos[2] = new_z
        
        # Rotación en X (pitch)
        if abs(angle_x) > 0.0001:
            cos_x = np.cos(angle_x)
            sin_x = np.sin(angle_x)
            new_y = rotated_pos[1] * cos_x - rotated_pos[2] * sin_x
            new_z = rotated_pos[1] * sin_x + rotated_pos[2] * cos_x
            rotated_pos[1] = new_y
            rotated_pos[2] = new_z
        
        # Rotación en Z (roll)
        if abs(angle_z) > 0.0001:
            cos_z = np.cos(angle_z)
            sin_z = np.sin(angle_z)
            new_x = rotated_pos[0] * cos_z - rotated_pos[1] * sin_z
            new_y = rotated_pos[0] * sin_z + rotated_pos[1] * cos_z
            rotated_pos[0] = new_x
            rotated_pos[1] = new_y
        
        # Calcular nueva posición absoluta
        new_position = rotated_pos + self.center
        
        # Crear delta
        delta = MotionDelta()
        delta.position = new_position - current_pos
        
        return delta
'''
        
        return class_content + calculate_delta_method + '\n' + next_section
    
    # Aplicar el reemplazo
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Verificar que se hizo el cambio
    if 'def calculate_delta' not in content and 'def calculate_delta' in new_content:
        # Hacer backup
        import shutil
        from datetime import datetime
        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        
        # Escribir archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Método calculate_delta añadido a MacroRotation")
        print(f"📦 Backup: {backup_name}")
        return True
    else:
        print("⚠️ No se pudo añadir calculate_delta o ya existe")
        return False

if __name__ == "__main__":
    print("🔧 Añadiendo calculate_delta a MacroRotation...")
    
    if add_calculate_delta_to_macro_rotation():
        print("\n✅ Fix aplicado exitosamente")
        print("\n📝 Ejecuta:")
        print("  python test_macro_rotation_working.py")
    else:
        print("\n❌ Error al aplicar fix")