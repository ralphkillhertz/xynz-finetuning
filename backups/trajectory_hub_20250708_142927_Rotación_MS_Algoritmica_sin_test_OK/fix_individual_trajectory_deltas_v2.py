# === fix_individual_trajectory_deltas_v2.py ===
# 🔧 Fix: Migrar IndividualTrajectory a sistema de deltas
# ⚡ Actualizado con la ubicación correcta

import os
import shutil
from datetime import datetime

def migrate_individual_trajectory():
    print("🔄 Migrando IndividualTrajectory a sistema de deltas...")
    
    # Backup
    file_path = "trajectory_hub/core/motion_components.py"
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar la clase IndividualTrajectory
    class_pos = content.find("class IndividualTrajectory(MotionComponent, MovementModeMixin):")
    if class_pos == -1:
        print("❌ No se encontró IndividualTrajectory")
        return
    
    # Buscar el final de la clase (siguiente class o final del archivo)
    next_class = content.find("\nclass ", class_pos + 1)
    if next_class == -1:
        next_class = len(content)
    
    # Verificar si ya tiene calculate_delta
    if "def calculate_delta" in content[class_pos:next_class]:
        print("⚠️ IndividualTrajectory ya tiene calculate_delta")
        return
    
    # Buscar dónde insertar el método (antes del final de la clase)
    # Buscar el último método de la clase
    last_method = class_pos
    for method in ["def update", "def set_trajectory", "def get_state", "def set_state"]:
        pos = content.rfind(method, class_pos, next_class)
        if pos > last_method:
            last_method = pos
    
    # Encontrar el final del último método
    indent_count = 0
    pos = last_method
    while pos < next_class:
        if content[pos] == '\n':
            # Contar espacios de la siguiente línea
            spaces = 0
            next_pos = pos + 1
            while next_pos < len(content) and content[next_pos] == ' ':
                spaces += 1
                next_pos += 1
            # Si la indentación vuelve al nivel de clase, insertamos aquí
            if spaces <= 4 and next_pos < len(content) and content[next_pos] != ' ':
                break
        pos += 1
    
    # Método calculate_delta
    delta_method = '''
    def calculate_delta(self, state: MotionState, dt: float) -> MotionDelta:
        """Calcula el delta de movimiento para trayectoria individual."""
        delta = MotionDelta()
        
        if not self.enabled or self.movement_mode == TrajectoryMovementMode.STOP:
            return delta
        
        # Actualizar posición en la trayectoria según el modo
        old_position = self.position_on_trajectory
        self.update_position(dt)
        
        # Calcular nueva posición 3D
        new_position = self._calculate_position_on_trajectory(self.position_on_trajectory)
        
        # Aplicar desplazamiento si existe
        if hasattr(self, 'trajectory_offset'):
            new_position = new_position + self.trajectory_offset
        
        # El delta es el cambio desde la última posición conocida
        if hasattr(state, 'individual_trajectory_position'):
            delta.position = new_position - state.individual_trajectory_position
        else:
            # Primera vez, usamos la posición inicial
            delta.position = new_position
        
        # Guardar la posición actual para el próximo frame
        state.individual_trajectory_position = new_position.copy()
        
        return delta
'''
    
    # Insertar el método
    content = content[:pos] + delta_method + content[pos:]
    print("✅ Método calculate_delta añadido a IndividualTrajectory")
    
    # Ahora actualizar SourceMotion para procesar los deltas
    source_motion_pos = content.find("def update_with_deltas(self, dt: float)")
    if source_motion_pos != -1:
        # Buscar donde añadir el código
        deltas_append = content.find("deltas = []", source_motion_pos)
        if deltas_append != -1:
            # Buscar el return
            return_pos = content.find("return deltas", deltas_append)
            
            # Código para procesar IndividualTrajectory
            individual_code = '''
        # Procesar trayectoria individual
        if 'individual_trajectory' in self.active_components:
            component = self.active_components['individual_trajectory']
            if component and hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, dt)
                if delta and (delta.position is not None and np.any(delta.position != 0)):
                    deltas.append(delta)
        
'''
            # Insertar antes del return
            content = content[:return_pos] + individual_code + content[return_pos:]
            print("✅ SourceMotion.update_with_deltas actualizado")
    
    # Guardar
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Backup creado: {backup_path}")
    print("✅ Migración completada!")
    
    # Crear test
    create_test()

def create_test():
    test_code = '''# === test_individual_deltas.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import time

print("🧪 Test de IndividualTrajectory con sistema de deltas...")

# Crear engine
engine = EnhancedTrajectoryEngine(n_sources=5, update_rate=60)

# Crear macro con 3 fuentes
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias individuales (círculos)
engine.set_individual_trajectories("test", 
    trajectories={
        0: {"shape": "circle", "params": {"radius": 2.0}},
        1: {"shape": "circle", "params": {"radius": 1.5}},
        2: {"shape": "circle", "params": {"radius": 1.0}}
    }
)

# Activar movimiento
for sid in [0, 1, 2]:
    engine.set_individual_trajectory("test", sid, 
        mode="fix", 
        speed=0.5,
        shape="circle"
    )

print("\\nPosiciones iniciales:")
for sid in [0, 1, 2]:
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Simular 2 segundos
print("\\nSimulando movimiento...")
for i in range(120):  # 2 segundos a 60 fps
    engine.update(1/60)
    if i % 30 == 0:  # Cada 0.5 segundos
        print(f"\\nT={i/60:.1f}s:")
        for sid in [0, 1, 2]:
            pos = engine._positions[sid]
            print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

print("\\n✅ Si las posiciones cambiaron, las trayectorias individuales funcionan con deltas!")
'''
    
    with open("test_individual_deltas.py", "w") as f:
        f.write(test_code)
    
    print("\n📝 Test creado: test_individual_deltas.py")

if __name__ == "__main__":
    migrate_individual_trajectory()