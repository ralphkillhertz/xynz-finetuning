# === fix_individual_trajectory_deltas.py ===
# 🔧 Fix: Migrar IndividualTrajectory a sistema de deltas
# ⚡ Impacto: ALTO - Base para todos los movimientos individuales

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
    import_pos = content.find("class IndividualTrajectory:")
    if import_pos == -1:
        print("❌ No se encontró IndividualTrajectory")
        return
    
    # Encontrar el método update
    update_start = content.find("def update(", import_pos)
    update_end = content.find("\n    def ", update_start + 1)
    if update_end == -1:
        update_end = content.find("\nclass", update_start)
    
    # Añadir calculate_delta después del método update
    delta_method = '''
    def calculate_delta(self, state: MotionState, dt: float) -> MotionDelta:
        """Calcula el delta de movimiento para trayectoria individual."""
        delta = MotionDelta()
        
        if not self.enabled or self.movement_mode == 'stop':
            return delta
        
        # Actualizar fase según modo de movimiento
        if self.movement_mode == 'fix':
            self.position_on_trajectory += self.movement_speed * dt
        elif self.movement_mode == 'random':
            # Cambio aleatorio de velocidad cada cierto tiempo
            if hasattr(self, '_last_random_change'):
                if state.time - self._last_random_change > 2.0:  # Cada 2 segundos
                    self.movement_speed = np.random.uniform(-2.0, 2.0)
                    self._last_random_change = state.time
            else:
                self._last_random_change = state.time
            self.position_on_trajectory += self.movement_speed * dt
        elif self.movement_mode == 'vibration':
            # Vibración sinusoidal
            vibration = np.sin(state.time * 10.0) * 0.5
            self.position_on_trajectory += (self.movement_speed + vibration) * dt
        elif self.movement_mode == 'spin':
            # Giro muy rápido
            self.position_on_trajectory += self.movement_speed * 5.0 * dt
        
        # Normalizar fase
        self.position_on_trajectory = self.position_on_trajectory % 1.0
        
        # Calcular nueva posición en la trayectoria
        new_position = self._calculate_position_on_trajectory(self.position_on_trajectory)
        
        # El delta es la diferencia con la posición actual
        if hasattr(state, 'trajectory_offset'):
            current_trajectory_pos = state.trajectory_offset
        else:
            current_trajectory_pos = np.zeros(3)
            
        delta.position = new_position - current_trajectory_pos
        
        # Guardar la nueva posición para el próximo cálculo
        state.trajectory_offset = new_position
        
        return delta
'''
    
    # Insertar el método calculate_delta
    if "def calculate_delta" not in content[import_pos:update_end if update_end != -1 else len(content)]:
        insert_pos = update_end if update_end != -1 else content.find("\nclass", update_start)
        content = content[:insert_pos] + delta_method + content[insert_pos:]
        print("✅ Método calculate_delta añadido a IndividualTrajectory")
    
    # Actualizar SourceMotion para usar deltas de IndividualTrajectory
    source_motion_pos = content.find("class SourceMotion:")
    if source_motion_pos != -1:
        update_deltas_pos = content.find("def update_with_deltas(", source_motion_pos)
        if update_deltas_pos != -1:
            # Buscar el return de update_with_deltas
            return_pos = content.find("return deltas", update_deltas_pos)
            
            # Añadir código para procesar IndividualTrajectory
            individual_code = '''
        # Procesar trayectoria individual si existe
        if 'individual_trajectory' in self.components and self.components['individual_trajectory']:
            traj = self.components['individual_trajectory']
            if hasattr(traj, 'calculate_delta'):
                delta = traj.calculate_delta(self.state, dt)
                if delta:
                    deltas.append(delta)
        
        '''
            # Insertar antes del return
            content = content[:return_pos] + individual_code + content[return_pos:]
            print("✅ SourceMotion actualizado para procesar deltas de IndividualTrajectory")
    
    # Guardar cambios
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Backup creado: {backup_path}")
    print("✅ IndividualTrajectory migrado a sistema de deltas")
    
    # Test rápido
    test_code = '''
# === test_individual_trajectory_deltas.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test de IndividualTrajectory con deltas...")

engine = EnhancedTrajectoryEngine(n_sources=5)
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias individuales
engine.configure_individual_trajectories("test", mode=1)  # Todas círculos

# Activar movimiento
for sid in [0, 1, 2]:
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        if 'individual_trajectory' in motion.components:
            motion.components['individual_trajectory'].movement_mode = 'fix'
            motion.components['individual_trajectory'].movement_speed = 1.0

# Test de movimiento
print("\\nPosiciones iniciales:")
for sid in [0, 1, 2]:
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: {pos}")

# Simular 1 segundo
for _ in range(60):
    engine.update(1/60)

print("\\nPosiciones después de 1 segundo:")
for sid in [0, 1, 2]:
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: {pos}")
    
print("\\n✅ Si las posiciones cambiaron, IndividualTrajectory funciona con deltas!")
'''
    
    with open("test_individual_trajectory_deltas.py", "w") as f:
        f.write(test_code)
    
    print("\n📝 Test creado: test_individual_trajectory_deltas.py")
    print("Ejecuta: python test_individual_trajectory_deltas.py")

if __name__ == "__main__":
    migrate_individual_trajectory()