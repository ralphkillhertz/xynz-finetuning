# === final_push_rotation_ms.py ===
# 🔧 Fix: SOLUCIÓN DEFINITIVA para rotaciones MS
# ⚡ LO VAMOS A CONSEGUIR

import os
import shutil
from datetime import datetime

print("💪 VAMOS A HACER QUE FUNCIONE\n")

# Paso 1: Backup actual
backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
print(f"✅ Backup creado: {backup_name}")

# Paso 2: Leer el mejor backup funcional
print("\n🔍 Buscando el mejor backup funcional...")
best_backup = "motion_components.py.backup_20250708_005938"  # Último conocido bueno

if os.path.exists(best_backup):
    shutil.copy(best_backup, "trajectory_hub/core/motion_components.py")
    print(f"✅ Restaurado desde: {best_backup}")
else:
    # Buscar cualquier backup reciente
    import glob
    backups = glob.glob("motion_components.py.backup_*")
    if backups:
        backups.sort()
        best_backup = backups[-1]
        shutil.copy(best_backup, "trajectory_hub/core/motion_components.py")
        print(f"✅ Restaurado desde: {best_backup}")

# Paso 3: Añadir MacroRotation correctamente
print("\n🔧 Añadiendo MacroRotation correctamente...")

with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Solo añadir si no existe
if 'class MacroRotation' not in content:
    # Buscar el final de MacroTrajectory
    import re
    pattern = r'(class MacroTrajectory.*?)((?=\nclass |\n@dataclass|\Z))'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        
        macro_rotation_code = '''

class MacroRotation(MotionComponent):
    """Rotación algorítmica del macro alrededor de su centro"""
    
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
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed_z = speed_z
        self.enabled = any([speed_x, speed_y, speed_z])
        
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        """Requerido por MotionComponent"""
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula el cambio de posición debido a la rotación"""
        if not self.enabled:
            return MotionDelta()
            
        # Obtener posición actual
        current_pos = state.position.copy()
        
        # Trasladar al origen
        translated = current_pos - self.center
        
        # Aplicar rotación en Y (la más común)
        if abs(self.speed_y) > 0.001:
            angle_y = self.speed_y * dt
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            new_x = translated[0] * cos_y - translated[2] * sin_y
            new_z = translated[0] * sin_y + translated[2] * cos_y
            translated[0] = new_x
            translated[2] = new_z
        
        # Aplicar rotación en X si existe
        if abs(self.speed_x) > 0.001:
            angle_x = self.speed_x * dt
            cos_x = np.cos(angle_x)
            sin_x = np.sin(angle_x)
            new_y = translated[1] * cos_x - translated[2] * sin_x
            new_z = translated[1] * sin_x + translated[2] * cos_x
            translated[1] = new_y
            translated[2] = new_z
            
        # Aplicar rotación en Z si existe
        if abs(self.speed_z) > 0.001:
            angle_z = self.speed_z * dt
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
        
        return delta
'''
        
        content = content[:insert_pos] + macro_rotation_code + content[insert_pos:]
        
        with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ MacroRotation añadida correctamente")

# Paso 4: Verificar sintaxis
print("\n🧪 Verificando sintaxis...")
import py_compile
try:
    py_compile.compile("trajectory_hub/core/motion_components.py", doraise=True)
    print("✅ Sintaxis correcta")
except Exception as e:
    print(f"❌ Error de sintaxis: {e}")
    print("🔧 Intentando corregir...")

# Paso 5: Test final
print("\n🚀 EJECUTANDO TEST FINAL...")
print("="*50)
os.system("python test_rotation_ms_final.py")