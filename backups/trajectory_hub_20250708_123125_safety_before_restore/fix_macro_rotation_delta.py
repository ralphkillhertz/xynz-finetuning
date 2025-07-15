# === fix_macro_rotation_delta.py ===
# 🔧 Fix: Corregir calculate_delta en MacroRotation
# ⚡ ULTRA FAST FIX

import os
import re

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar la clase MacroRotation y reemplazar calculate_delta
pattern = r'(class MacroRotation.*?def calculate_delta.*?)(?=def |class |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Encontrar el inicio y fin del método
    start = content.find('def calculate_delta', match.start())
    
    # Buscar el siguiente def o class
    next_def = content.find('\n    def ', start + 1)
    next_class = content.find('\nclass ', start + 1)
    end = min(x for x in [next_def, next_class, len(content)] if x > start)
    
    # Método corregido
    new_method = '''    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula el cambio de posición debido a la rotación"""
        if not self.enabled or not hasattr(state, 'source_id'):
            return MotionDelta()
            
        # Obtener posición actual
        current_pos = state.position.copy()
        
        # Trasladar al origen (restar centro)
        translated = current_pos - self.center
        
        # Aplicar rotaciones
        angle_x = self.speed_x * dt
        angle_y = self.speed_y * dt  
        angle_z = self.speed_z * dt
        
        # Rotación en Y (más común)
        if abs(angle_y) > 0:
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            new_x = translated[0] * cos_y - translated[2] * sin_y
            new_z = translated[0] * sin_y + translated[2] * cos_y
            translated[0] = new_x
            translated[2] = new_z
            
        # Rotación en X
        if abs(angle_x) > 0:
            cos_x = np.cos(angle_x)
            sin_x = np.sin(angle_x)
            new_y = translated[1] * cos_x - translated[2] * sin_x
            new_z = translated[1] * sin_x + translated[2] * cos_x
            translated[1] = new_y
            translated[2] = new_z
            
        # Rotación en Z
        if abs(angle_z) > 0:
            cos_z = np.cos(angle_z)
            sin_z = np.sin(angle_z)
            new_x = translated[0] * cos_z - translated[1] * sin_z
            new_y = translated[0] * sin_z + translated[1] * cos_z
            translated[0] = new_x
            translated[1] = new_y
        
        # Trasladar de vuelta
        new_pos = translated + self.center
        
        # Calcular delta
        delta = MotionDelta()
        delta.position = new_pos - current_pos
        delta.source_id = state.source_id
        
        return delta
'''
    
    # Reemplazar
    content = content[:start] + new_method + '\n' + content[end:]

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ MacroRotation.calculate_delta corregido")
os.system("python test_rotation_ms_final.py")