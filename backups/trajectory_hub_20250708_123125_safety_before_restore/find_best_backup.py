# === find_best_backup.py ===
# 🔧 Fix: Encontrar el mejor backup con MotionDelta
# ⚡ SMART RESTORE

import os
import glob
import re

# Buscar todos los backups
backups = []
backups.extend(glob.glob("motion_components.py.backup_*"))
backups.extend(glob.glob("trajectory_hub/core/motion_components.py.backup_*"))
backups.extend(glob.glob("**/motion_components.py.backup_*", recursive=True))

print(f"📦 Analizando {len(backups)} backups...")

# Buscar el mejor backup
best_backup = None
best_score = 0

for backup in backups:
    try:
        with open(backup, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Calcular score basado en contenido
        score = 0
        if 'class MotionDelta' in content: score += 10
        if 'class MotionState' in content: score += 10
        if 'class MotionComponent' in content: score += 10
        if 'class SourceMotion' in content: score += 10
        if 'class ConcentrationComponent' in content: score += 5
        if 'class IndividualTrajectory' in content: score += 5
        if 'class MacroTrajectory' in content: score += 5
        if 'calculate_delta' in content: score += 5
        if 'update_with_deltas' in content: score += 5
        
        # Penalizar si tiene MacroRotation (queremos añadirla limpia)
        if 'class MacroRotation' in content: score -= 2
        
        if score > best_score:
            best_score = score
            best_backup = backup
            
        if score > 50:
            print(f"  ✅ {os.path.basename(backup)}: score={score}")
    except:
        pass

if best_backup and best_score > 40:
    print(f"\n🏆 Mejor backup: {os.path.basename(best_backup)} (score={best_score})")
    
    # Restaurar
    import shutil
    shutil.copy(best_backup, "trajectory_hub/core/motion_components.py")
    
    # Ahora añadir MacroRotation si no existe
    with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'class MacroRotation' not in content:
        print("🔧 Añadiendo MacroRotation...")
        
        # Buscar donde insertar (después de MacroTrajectory)
        insert_pos = content.find('class MacroTrajectory')
        if insert_pos > 0:
            # Buscar el final de MacroTrajectory
            next_class = content.find('\n\nclass ', insert_pos)
            if next_class > 0:
                insert_pos = next_class
            else:
                insert_pos = len(content)
            
            macro_rotation_class = '''

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
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula el cambio de posición debido a la rotación"""
        if not self.enabled:
            return MotionDelta()
            
        # Obtener posición actual
        current_pos = state.position.copy()
        
        # Trasladar al origen
        translated = current_pos - self.center
        
        # Aplicar rotación en Y (más común)
        angle_y = self.speed_y * dt
        
        if abs(angle_y) > 0:
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            new_x = translated[0] * cos_y - translated[2] * sin_y
            new_z = translated[0] * sin_y + translated[2] * cos_y
            translated[0] = new_x
            translated[2] = new_z
        
        # Aplicar rotación en X si hay
        if abs(self.speed_x * dt) > 0:
            angle_x = self.speed_x * dt
            cos_x = np.cos(angle_x)
            sin_x = np.sin(angle_x)
            new_y = translated[1] * cos_x - translated[2] * sin_x
            new_z = translated[1] * sin_x + translated[2] * cos_x
            translated[1] = new_y
            translated[2] = new_z
        
        # Trasladar de vuelta
        new_pos = translated + self.center
        
        # Calcular delta
        delta = MotionDelta()
        delta.position = new_pos - current_pos
        delta.source_id = state.source_id
        
        return delta
'''
            
            content = content[:insert_pos] + macro_rotation_class + content[insert_pos:]
            
            # Guardar
            with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ MacroRotation añadida")
    
    print("\n✅ motion_components.py restaurado y actualizado")
else:
    print("❌ No se encontró un backup adecuado")
    print("🔧 Usando el más reciente con MotionDelta...")
    
    # Buscar cualquier backup con MotionDelta
    for backup in sorted(backups, reverse=True):
        try:
            with open(backup, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'class MotionDelta' in content:
                print(f"  Usando: {os.path.basename(backup)}")
                import shutil
                shutil.copy(backup, "trajectory_hub/core/motion_components.py")
                break
        except:
            pass

print("\n🚀 Ejecutando test...")
os.system("python test_rotation_ms_final.py")