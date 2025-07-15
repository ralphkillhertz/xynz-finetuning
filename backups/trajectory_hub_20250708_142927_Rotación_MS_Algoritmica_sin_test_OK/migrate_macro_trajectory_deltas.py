# === migrate_macro_trajectory_deltas.py ===
# 🔧 Fix: Migrar MacroTrajectory al sistema de deltas
# ⚡ Impacto: ALTO - Permite combinar trayectorias macro con otros componentes
# 🎯 Tiempo: ~5 minutos

import os
import shutil
from datetime import datetime

print("🚀 Migrando MacroTrajectory a sistema de deltas...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_macro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)
print(f"📦 Backup: {backup_path}")

with open(file_path, 'r') as f:
    content = f.read()

# Buscar la clase MacroTrajectory
class_start = content.find("class MacroTrajectory:")
if class_start == -1:
    print("❌ No se encontró MacroTrajectory")
    exit(1)

# Buscar el final de la clase
next_class = content.find("\nclass ", class_start + 1)
if next_class == -1:
    next_class = len(content)

# Buscar dónde insertar calculate_delta (antes del final de la clase)
# Buscar el último método de la clase
class_content = content[class_start:next_class]
last_method_pos = class_content.rfind("\n    def ")

# Crear el método calculate_delta
calculate_delta_method = '''
    def calculate_delta(self, state: 'MotionState', current_time: float, dt: float) -> Optional['MotionDelta']:
        """Calcular delta de posición para trayectoria macro"""
        if not self.enabled or self.trajectory_type == MacroTrajectoryType.STATIC:
            return None
        
        # Obtener la posición en la trayectoria
        trajectory_position = self._get_trajectory_position(current_time)
        if trajectory_position is None:
            return None
        
        # Calcular delta desde la posición actual del estado
        delta_position = trajectory_position - state.position
        
        # Aplicar factor de velocidad si es necesario
        if hasattr(self, 'speed_factor') and self.speed_factor != 1.0:
            delta_position *= self.speed_factor
        
        # Limitar el delta para evitar saltos bruscos
        max_delta = 5.0 * dt  # Máximo 5 unidades por segundo
        delta_magnitude = np.linalg.norm(delta_position)
        if delta_magnitude > max_delta:
            delta_position = delta_position * (max_delta / delta_magnitude)
        
        # Crear y retornar MotionDelta
        from trajectory_hub.core.motion_components import MotionDelta
        return MotionDelta(
            position=delta_position,
            orientation=np.zeros(3),  # MacroTrajectory no afecta orientación
            aperture=0.0
        )
    
    def _get_trajectory_position(self, current_time: float) -> Optional[np.ndarray]:
        """Obtener posición en la trayectoria según el tiempo"""
        if self.trajectory_type == MacroTrajectoryType.CIRCULAR:
            angle = current_time * self.angular_speed
            radius = self.trajectory_params.get('radius', 5.0)
            center = self.trajectory_params.get('center', np.zeros(3))
            return np.array([
                center[0] + radius * np.cos(angle),
                center[1] + radius * np.sin(angle),
                center[2]
            ])
        
        elif self.trajectory_type == MacroTrajectoryType.LINEAR:
            start = np.array(self.trajectory_params.get('start', [0, 0, 0]))
            end = np.array(self.trajectory_params.get('end', [10, 0, 0]))
            speed = self.trajectory_params.get('speed', 1.0)
            
            # Movimiento de ida y vuelta
            distance = np.linalg.norm(end - start)
            if distance > 0:
                cycle_time = 2 * distance / speed
                t = (current_time % cycle_time) / cycle_time
                if t > 0.5:
                    t = 1.0 - t
                t *= 2  # Normalizar a 0-1
                return start + t * (end - start)
            return start
        
        elif self.trajectory_type == MacroTrajectoryType.SPIRAL:
            angle = current_time * self.angular_speed
            radius_base = self.trajectory_params.get('radius', 5.0)
            expansion = self.trajectory_params.get('expansion', 0.1)
            height_rate = self.trajectory_params.get('height_rate', 0.5)
            
            radius = radius_base + expansion * angle
            return np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                height_rate * current_time
            ])
        
        elif self.trajectory_type == MacroTrajectoryType.RANDOM_WALK:
            # Para random walk, usar la posición almacenada
            if not hasattr(self, '_random_position'):
                self._random_position = np.zeros(3)
                self._last_random_update = current_time
            
            # Actualizar cada 0.5 segundos
            if current_time - self._last_random_update > 0.5:
                self._random_position += np.random.uniform(-1, 1, 3)
                self._random_position = np.clip(self._random_position, -10, 10)
                self._last_random_update = current_time
            
            return self._random_position
        
        elif self.trajectory_type == MacroTrajectoryType.FIGURE_EIGHT:
            angle = current_time * self.angular_speed
            scale = self.trajectory_params.get('scale', 5.0)
            return np.array([
                scale * np.sin(angle),
                scale * np.sin(angle) * np.cos(angle),
                0
            ])
        
        elif self.trajectory_type == MacroTrajectoryType.CUSTOM:
            # Para trayectorias custom, usar puntos definidos
            if hasattr(self, 'custom_points') and len(self.custom_points) > 0:
                # Interpolar entre puntos
                total_points = len(self.custom_points)
                speed = self.trajectory_params.get('speed', 1.0)
                index = (current_time * speed) % total_points
                
                idx1 = int(index)
                idx2 = (idx1 + 1) % total_points
                t = index - idx1
                
                p1 = np.array(self.custom_points[idx1])
                p2 = np.array(self.custom_points[idx2])
                
                return p1 + t * (p2 - p1)
        
        return None
'''

# Insertar el método
if last_method_pos != -1:
    insert_pos = class_start + last_method_pos
    # Buscar el final del último método
    method_end = content.find("\n\n    def ", insert_pos + 1)
    if method_end == -1:
        method_end = content.find("\n\nclass ", insert_pos + 1)
    if method_end == -1:
        method_end = next_class - 1
    
    # Insertar
    content = content[:method_end] + calculate_delta_method + content[method_end:]
    print("✅ Método calculate_delta añadido a MacroTrajectory")

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print("\n✅ MacroTrajectory migrado a deltas")
print("\n🧪 Creando test...")

# Test
test_code = '''# === test_macro_trajectory_deltas.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import MacroTrajectory, MacroTrajectoryType

print("🧪 Test de MacroTrajectory con deltas...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro con varias fuentes
print("\\n1️⃣ Creando macro con 5 fuentes...")
engine.create_macro("test_macro", [0, 1, 2, 3, 4])

# Configurar trayectoria circular para el macro
print("\\n2️⃣ Configurando trayectoria circular...")
engine.set_macro_trajectory("test_macro", "circular", speed=1.0)

# Verificar que las fuentes tienen el componente
macro = engine.macros["test_macro"]
for sid in macro.source_ids:
    motion = engine.motion_states[sid]
    if 'macro_trajectory' in motion.active_components:
        comp = motion.active_components['macro_trajectory']
        print(f"✅ Fuente {sid}: MacroTrajectory configurado (tipo: {comp.trajectory_type})")

# Test de movimiento
print("\\n3️⃣ Probando movimiento con deltas...")
positions_before = [engine._positions[sid].copy() for sid in macro.source_ids]

# Ejecutar varios frames
for i in range(60):  # 1 segundo a 60 fps
    engine.update()

positions_after = [engine._positions[sid].copy() for sid in macro.source_ids]

# Verificar movimiento
print("\\n4️⃣ Verificando movimiento:")
all_moved = True
for i, sid in enumerate(macro.source_ids):
    dist = np.linalg.norm(positions_after[i] - positions_before[i])
    if dist > 0.01:
        print(f"✅ Fuente {sid} se movió {dist:.3f} unidades")
    else:
        print(f"❌ Fuente {sid} NO se movió")
        all_moved = False

if all_moved:
    print("\\n🎉 ¡ÉXITO! MacroTrajectory funciona con deltas")
else:
    print("\\n❌ Error: Algunas fuentes no se movieron")
    
# Test de tipos de trayectoria
print("\\n5️⃣ Probando otros tipos de trayectoria...")
for traj_type in ["linear", "spiral", "figure_eight"]:
    engine.set_macro_trajectory("test_macro", traj_type)
    pos_before = engine._positions[0].copy()
    
    for _ in range(10):
        engine.update()
    
    pos_after = engine._positions[0].copy()
    moved = np.linalg.norm(pos_after - pos_before) > 0.01
    print(f"  {traj_type}: {'✅ Funciona' if moved else '❌ No funciona'}")
'''

with open("test_macro_trajectory_deltas.py", "w") as f:
    f.write(test_code)

print("📝 Test creado: test_macro_trajectory_deltas.py")
print("\n🚀 Ejecuta: python test_macro_trajectory_deltas.py")