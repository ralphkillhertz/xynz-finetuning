# === fix_rotation_nuclear.py ===
# 🔧 Fix: OPCIÓN NUCLEAR - Reescribir MacroRotation completamente
# ⚡ ÚLTIMO INTENTO - TODO O NADA

import os
import shutil
from datetime import datetime

print("💣 FIX NUCLEAR - REESCRIBIR MacroRotation")
print("="*50)

# Backup
backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
print(f"✅ Backup: {backup_name}")

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar y reemplazar la clase MacroRotation completa
import re

# Nueva implementación LIMPIA de MacroRotation
new_macro_rotation = '''
class MacroRotation(MotionComponent):
    """Rotación algorítmica del macro alrededor de su centro - VERSIÓN CORREGIDA"""
    
    def __init__(self):
        self.center = np.zeros(3)
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_z = 0.0
        self.enabled = False
        
    def update_center(self, center: np.ndarray):
        """Actualiza el centro de rotación"""
        self.center = center.copy()
        
    def set_rotation(self, speed_x: float, speed_y: float, speed_z: float):
        """Configura velocidades de rotación"""
        self.speed_x = float(speed_x)  # Asegurar que sea float
        self.speed_y = float(speed_y)
        self.speed_z = float(speed_z)
        # Usar bool() para evitar problemas con arrays
        self.enabled = bool(abs(speed_x) > 0.001 or abs(speed_y) > 0.001 or abs(speed_z) > 0.001)
        
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        """Requerido por MotionComponent"""
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula el cambio de posición debido a la rotación"""
        delta = MotionDelta()
        
        # Check simple sin comparación de arrays
        if not self.enabled:
            return delta
            
        # Obtener posición actual
        current_pos = state.position.copy()
        
        # Trasladar al origen
        translated = current_pos - self.center
        
        # Variables para la nueva posición
        new_x = translated[0]
        new_y = translated[1]
        new_z = translated[2]
        
        # Aplicar rotación en Y (la más común)
        speed_y_float = float(self.speed_y)
        if abs(speed_y_float) > 0.001:
            angle_y = speed_y_float * dt
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            temp_x = new_x * cos_y - new_z * sin_y
            temp_z = new_x * sin_y + new_z * cos_y
            new_x = temp_x
            new_z = temp_z
        
        # Aplicar rotación en X si existe
        speed_x_float = float(self.speed_x)
        if abs(speed_x_float) > 0.001:
            angle_x = speed_x_float * dt
            cos_x = np.cos(angle_x)
            sin_x = np.sin(angle_x)
            temp_y = new_y * cos_x - new_z * sin_x
            temp_z = new_y * sin_x + new_z * cos_x
            new_y = temp_y
            new_z = temp_z
            
        # Aplicar rotación en Z si existe
        speed_z_float = float(self.speed_z)
        if abs(speed_z_float) > 0.001:
            angle_z = speed_z_float * dt
            cos_z = np.cos(angle_z)
            sin_z = np.sin(angle_z)
            temp_x = new_x * cos_z - new_y * sin_z
            temp_y = new_x * sin_z + new_y * cos_z
            new_x = temp_x
            new_y = temp_y
        
        # Trasladar de vuelta
        translated[0] = new_x
        translated[1] = new_y
        translated[2] = new_z
        new_pos = translated + self.center
        
        # Calcular delta
        delta.position = new_pos - current_pos
        
        return delta
'''

# Buscar la clase MacroRotation existente
pattern = r'class MacroRotation.*?(?=\nclass|\n@|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Reemplazar con la nueva versión
    content = content[:match.start()] + new_macro_rotation + content[match.end():]
    print("✅ MacroRotation reemplazada completamente")
else:
    print("⚠️ No se encontró MacroRotation, añadiendo al final...")
    content += "\n\n" + new_macro_rotation

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo actualizado")

# Test inmediato
print("\n" + "="*50)
print("🚀 TEST FINAL - MOMENTO DE LA VERDAD")
print("="*50)
os.system("python test_rotation_ms_final.py")