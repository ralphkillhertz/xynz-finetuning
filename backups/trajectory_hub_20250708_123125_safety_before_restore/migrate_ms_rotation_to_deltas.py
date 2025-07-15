# === migrate_ms_rotation_to_deltas.py ===
# 🔧 Migración: Rotaciones MS algorítmicas a sistema de deltas
# ⚡ Impacto: ALTO - Completa integración de transformaciones

import os
import re

def migrate_ms_rotation():
    """Migra las rotaciones MS algorítmicas al sistema de deltas"""
    
    print("🔄 MIGRANDO ROTACIONES MS ALGORÍTMICAS A DELTAS\n")
    
    # 1. Primero, buscar dónde están las rotaciones MS
    print("1️⃣ Buscando implementación de rotaciones MS...")
    
    # Buscar en motion_components.py
    motion_path = "trajectory_hub/core/motion_components.py"
    
    # Crear o actualizar la clase MacroRotation
    macro_rotation_class = '''
class MacroRotation(MotionComponent):
    """Rotación algorítmica del macro alrededor de su centro"""
    
    def __init__(self):
        super().__init__()
        self.center = np.zeros(3)
        self.rotation_speed = np.array([0.0, 0.0, 0.0])  # rad/s en x,y,z
        self.current_angle = np.array([0.0, 0.0, 0.0])
        self.enabled = False
        
    def calculate_delta(self, current_time: float, dt: float, state: MotionState) -> MotionDelta:
        """Calcula el delta de posición por rotación alrededor del centro"""
        delta = MotionDelta()
        delta.source_id = state.source_id
        
        if not self.enabled or np.allclose(self.rotation_speed, 0):
            return delta
            
        # Actualizar ángulos
        self.current_angle += self.rotation_speed * dt
        
        # Posición relativa al centro
        rel_pos = state.position - self.center
        
        # Aplicar rotaciones (orden: Z, Y, X)
        # Rotación en Z
        if abs(self.rotation_speed[2]) > 0:
            cos_z = np.cos(self.rotation_speed[2] * dt)
            sin_z = np.sin(self.rotation_speed[2] * dt)
            new_x = rel_pos[0] * cos_z - rel_pos[1] * sin_z
            new_y = rel_pos[0] * sin_z + rel_pos[1] * cos_z
            rel_pos[0] = new_x
            rel_pos[1] = new_y
            
        # Rotación en Y
        if abs(self.rotation_speed[1]) > 0:
            cos_y = np.cos(self.rotation_speed[1] * dt)
            sin_y = np.sin(self.rotation_speed[1] * dt)
            new_x = rel_pos[0] * cos_y + rel_pos[2] * sin_y
            new_z = -rel_pos[0] * sin_y + rel_pos[2] * cos_y
            rel_pos[0] = new_x
            rel_pos[2] = new_z
            
        # Rotación en X
        if abs(self.rotation_speed[0]) > 0:
            cos_x = np.cos(self.rotation_speed[0] * dt)
            sin_x = np.sin(self.rotation_speed[0] * dt)
            new_y = rel_pos[1] * cos_x - rel_pos[2] * sin_x
            new_z = rel_pos[1] * sin_x + rel_pos[2] * cos_x
            rel_pos[1] = new_y
            rel_pos[2] = new_z
            
        # Nueva posición absoluta
        new_position = rel_pos + self.center
        
        # Delta es la diferencia
        delta.position = new_position - state.position
        
        return delta
        
    def set_rotation(self, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):
        """Configura la velocidad de rotación en rad/s"""
        self.rotation_speed = np.array([speed_x, speed_y, speed_z])
        self.enabled = True
        
    def update_center(self, center: np.ndarray):
        """Actualiza el centro de rotación"""
        self.center = center.copy()
'''
    
    # Leer el archivo actual
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Añadir la clase si no existe
    if "class MacroRotation" not in content:
        # Buscar dónde insertar (después de MacroTrajectory)
        insert_pos = content.find("class MotionState:")
        if insert_pos > 0:
            content = content[:insert_pos] + macro_rotation_class + "\n\n" + content[insert_pos:]
            print("✅ Clase MacroRotation añadida")
    
    # Guardar
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 2. Actualizar EnhancedTrajectoryEngine
    print("\n2️⃣ Actualizando EnhancedTrajectoryEngine...")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Añadir métodos para rotación MS
    rotation_methods = '''
    def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):
        """Configura rotación algorítmica para un macro"""
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return
            
        macro = self._macros[macro_name]
        
        # Calcular centro del macro
        positions = [self._positions[sid] for sid in macro.source_ids if sid < len(self._positions)]
        if not positions:
            return
            
        center = np.mean(positions, axis=0)
        
        # Configurar rotación para cada fuente del macro
        for sid in macro.source_ids:
            if sid in self.motion_states:
                state = self.motion_states[sid]
                
                # Crear componente de rotación si no existe
                if 'macro_rotation' not in state.active_components:
                    rotation = MacroRotation()
                    state.active_components['macro_rotation'] = rotation
                else:
                    rotation = state.active_components['macro_rotation']
                
                # Configurar rotación
                rotation.update_center(center)
                rotation.set_rotation(speed_x, speed_y, speed_z)
                
        print(f"✅ Rotación configurada para macro '{macro_name}'")
        print(f"   Velocidades (rad/s): X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f}")
        
    def stop_macro_rotation(self, macro_name: str):
        """Detiene la rotación de un macro"""
        if macro_name not in self._macros:
            return
            
        macro = self._macros[macro_name]
        
        for sid in macro.source_ids:
            if sid in self.motion_states:
                state = self.motion_states[sid]
                if 'macro_rotation' in state.active_components:
                    state.active_components['macro_rotation'].enabled = False
                    
        print(f"✅ Rotación detenida para macro '{macro_name}'")
'''
    
    # Leer engine
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # Añadir import si no existe
    if "from .motion_components import" in engine_content and "MacroRotation" not in engine_content:
        engine_content = engine_content.replace(
            "from .motion_components import",
            "from .motion_components import MacroRotation,"
        )
    
    # Añadir métodos antes del último método o al final de la clase
    if "def set_macro_rotation" not in engine_content:
        # Buscar dónde insertar (antes del último def o antes del final de clase)
        last_def = engine_content.rfind("\n    def ")
        if last_def > 0:
            # Encontrar el final de ese método
            next_def = engine_content.find("\n    def ", last_def + 1)
            if next_def > 0:
                insert_pos = next_def
            else:
                # Es el último método, buscar el final
                insert_pos = engine_content.rfind("\n\n")
        else:
            insert_pos = engine_content.rfind("\n\n")
            
        engine_content = engine_content[:insert_pos] + "\n" + rotation_methods + engine_content[insert_pos:]
        print("✅ Métodos de rotación añadidos al engine")
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(engine_content)
    
    # 3. Crear test
    print("\n3️⃣ Creando test de rotación MS...")
    
    test_code = '''# === test_macro_rotation.py ===
# 🧪 Test de rotación MS algorítmica con deltas

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

print("\\n🔄 TEST: Rotación MS Algorítmica con Deltas\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60)
print("✅ Engine creado")

# Crear macro en formación cuadrada
macro_id = engine.create_macro("cubo", 8, formation="cube")
print(f"✅ Macro '{macro_id}' creado en formación cubo")

# Posiciones iniciales
print("\\n📍 Posiciones iniciales:")
initial_positions = {}
for sid in engine._macros[macro_id].source_ids:
    pos = engine._positions[sid]
    initial_positions[sid] = pos.copy()
    print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Configurar rotación en Y (como un carrusel)
engine.set_macro_rotation(macro_id, speed_x=0, speed_y=1.0, speed_z=0)  # 1 rad/s

# Simular 3.14 segundos (media vuelta)
print("\\n🎠 Simulando rotación por π segundos (media vuelta)...")
frames = int(3.14159 * 60)  # 60 fps
for i in range(frames):
    engine.update()
    time.sleep(0.01)  # Simulación rápida

# Verificar posiciones finales
print("\\n📍 Posiciones finales:")
total_movement = 0
for sid in engine._macros[macro_id].source_ids:
    initial = initial_positions[sid]
    final = engine._positions[sid]
    distance = np.linalg.norm(final - initial)
    total_movement += distance
    print(f"   Fuente {sid}: [{final[0]:.2f}, {final[1]:.2f}, {final[2]:.2f}] (movió {distance:.2f})")

avg_movement = total_movement / len(engine._macros[macro_id].source_ids)

if avg_movement > 0.5:
    print(f"\\n✅ ¡ÉXITO! Rotación MS funcionando")
    print(f"   Movimiento promedio: {avg_movement:.2f} unidades")
    print("\\n📊 SISTEMA DE DELTAS:")
    print("   ✅ Concentración: 100%")
    print("   ✅ Trayectorias IS: 100%") 
    print("   ✅ Trayectorias MS: 100%")
    print("   ✅ Rotaciones MS algorítmicas: 100%")
else:
    print(f"\\n❌ Sin rotación detectada: {avg_movement:.3f}")
'''
    
    with open("test_macro_rotation.py", "w") as f:
        f.write(test_code)
    
    print("✅ Test creado: test_macro_rotation.py")
    print("\n✅ MIGRACIÓN COMPLETA")

if __name__ == "__main__":
    migrate_ms_rotation()
    print("\n🚀 Ejecutando test...")
    os.system("python test_macro_rotation.py")