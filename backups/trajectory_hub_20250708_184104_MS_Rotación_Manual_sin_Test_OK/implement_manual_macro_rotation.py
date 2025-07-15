# === implement_manual_macro_rotation.py ===
# 🔧 Implementar ManualMacroRotation con sistema de deltas
# 🎯 Basado en MacroRotation pero con control manual directo
# ⚡ Más simple que la algorítmica

import os
import re
from datetime import datetime

def add_manual_macro_rotation_class():
    """Añade la clase ManualMacroRotation a motion_components.py"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔧 Añadiendo ManualMacroRotation...")
    
    # Clase completa para rotación manual
    manual_rotation_class = '''
class ManualMacroRotation(MotionComponent):
    """Rotación manual de macro con control directo de ángulos"""
    
    def __init__(self):
        super().__init__("manual_macro_rotation")
        
        # Ángulos objetivo en radianes
        self.target_pitch = 0.0
        self.target_yaw = 0.0
        self.target_roll = 0.0
        
        # Ángulos actuales
        self.current_pitch = 0.0
        self.current_yaw = 0.0
        self.current_roll = 0.0
        
        # Velocidad de interpolación (0-1, donde 1 es instantáneo)
        self.interpolation_speed = 0.1
        
        # Centro de rotación
        self.center = np.array([0.0, 0.0, 0.0])
        
        self.enabled = True
    
    def set_target_rotation(self, pitch: float = None, yaw: float = None, roll: float = None):
        """Establece los ángulos objetivo"""
        if pitch is not None:
            self.target_pitch = pitch
        if yaw is not None:
            self.target_yaw = yaw
        if roll is not None:
            self.target_roll = roll
    
    def set_interpolation_speed(self, speed: float):
        """Establece la velocidad de interpolación (0-1)"""
        self.interpolation_speed = max(0.0, min(1.0, speed))
    
    def calculate_delta(self, state, current_time, dt):
        """Calcula el delta de rotación manual"""
        if not self.enabled:
            return None
        
        # Interpolar hacia los ángulos objetivo
        factor = self.interpolation_speed
        
        # Suavizar la interpolación con dt
        smooth_factor = 1.0 - pow(1.0 - factor, dt * 60.0)  # Normalizado a 60 FPS
        
        self.current_pitch += (self.target_pitch - self.current_pitch) * smooth_factor
        self.current_yaw += (self.target_yaw - self.current_yaw) * smooth_factor
        self.current_roll += (self.target_roll - self.target_roll) * smooth_factor
        
        # Calcular matriz de rotación
        rotation_matrix = self._calculate_rotation_matrix(
            self.current_pitch, 
            self.current_yaw, 
            self.current_roll
        )
        
        # Aplicar rotación alrededor del centro
        relative_pos = state.position - self.center
        rotated_pos = rotation_matrix @ relative_pos
        new_position = rotated_pos + self.center
        
        # Crear delta
        delta = MotionDelta()
        delta.position = new_position - state.position
        
        return delta
    
    def _calculate_rotation_matrix(self, pitch, yaw, roll):
        """Calcula la matriz de rotación 3D"""
        # Rotación en X (pitch)
        rx = np.array([
            [1, 0, 0],
            [0, np.cos(pitch), -np.sin(pitch)],
            [0, np.sin(pitch), np.cos(pitch)]
        ])
        
        # Rotación en Y (yaw)
        ry = np.array([
            [np.cos(yaw), 0, np.sin(yaw)],
            [0, 1, 0],
            [-np.sin(yaw), 0, np.cos(yaw)]
        ])
        
        # Rotación en Z (roll)
        rz = np.array([
            [np.cos(roll), -np.sin(roll), 0],
            [np.sin(roll), np.cos(roll), 0],
            [0, 0, 1]
        ])
        
        # Combinar rotaciones: Roll -> Pitch -> Yaw
        return ry @ rx @ rz
'''
    
    # Leer el archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya existe
    if "class ManualMacroRotation" in content:
        print("⚠️ ManualMacroRotation ya existe")
        return True
    
    # Buscar dónde insertar (después de MacroRotation)
    insert_pos = content.find("class MacroRotation")
    if insert_pos == -1:
        print("❌ No se encontró MacroRotation")
        return False
    
    # Buscar el final de MacroRotation
    next_class = content.find("\nclass ", insert_pos + 1)
    if next_class == -1:
        next_class = len(content)
    
    # Hacer backup
    backup_name = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy(motion_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Insertar la nueva clase
    new_content = (
        content[:next_class] + 
        "\n\n" + manual_rotation_class + 
        content[next_class:]
    )
    
    # Escribir
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ ManualMacroRotation añadida")
    return True

def add_set_manual_macro_rotation():
    """Añade el método set_manual_macro_rotation al engine"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("\n🔧 Añadiendo set_manual_macro_rotation al engine...")
    
    # Método para el engine
    engine_method = '''
    def set_manual_macro_rotation(self, macro_id: str, pitch: float = None, 
                                 yaw: float = None, roll: float = None,
                                 interpolation_speed: float = 0.1,
                                 center: np.ndarray = None):
        """
        Configura rotación manual para un macro
        
        Args:
            macro_id: ID del macro
            pitch: Ángulo de pitch en radianes
            yaw: Ángulo de yaw en radianes
            roll: Ángulo de roll en radianes
            interpolation_speed: Velocidad de interpolación (0-1)
            center: Centro de rotación [x,y,z]
        """
        if macro_id not in self._macros:
            print(f"Macro '{macro_id}' no encontrado")
            return False
        
        macro = self._macros[macro_id]
        
        # Importar la clase
        from .motion_components import ManualMacroRotation
        
        # Configurar para cada fuente del macro
        for source_id in macro.source_ids:
            if source_id not in self.motion_states:
                continue
            
            motion = self.motion_states[source_id]
            
            # Crear o actualizar el componente
            if 'manual_macro_rotation' not in motion.active_components:
                rotation = ManualMacroRotation()
                motion.active_components['manual_macro_rotation'] = rotation
            else:
                rotation = motion.active_components['manual_macro_rotation']
            
            # Configurar parámetros
            rotation.set_target_rotation(pitch, yaw, roll)
            rotation.set_interpolation_speed(interpolation_speed)
            
            if center is not None:
                rotation.center = center.copy()
            else:
                # Usar el centro del macro
                positions = [self._positions[sid] for sid in macro.source_ids 
                           if sid < len(self._positions)]
                if positions:
                    rotation.center = np.mean(positions, axis=0)
            
            rotation.enabled = True
        
        print(f"✅ Rotación manual configurada para macro '{macro_id}'")
        return True
    
    def toggle_manual_macro_rotation(self, macro_id: str, enabled: bool = None):
        """Activa/desactiva la rotación manual de un macro"""
        if macro_id not in self._macros:
            return False
        
        macro = self._macros[macro_id]
        
        for source_id in macro.source_ids:
            if source_id in self.motion_states:
                motion = self.motion_states[source_id]
                if 'manual_macro_rotation' in motion.active_components:
                    comp = motion.active_components['manual_macro_rotation']
                    if enabled is None:
                        comp.enabled = not comp.enabled
                    else:
                        comp.enabled = enabled
        
        return True'''
    
    # Leer el archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya existe
    if "def set_manual_macro_rotation" in content:
        print("⚠️ set_manual_macro_rotation ya existe")
        return True
    
    # Buscar dónde insertar (después de set_macro_rotation)
    insert_pos = content.find("def set_macro_rotation")
    if insert_pos == -1:
        print("❌ No se encontró set_macro_rotation")
        return False
    
    # Buscar el siguiente método
    next_method = content.find("\n    def ", insert_pos + 1)
    if next_method == -1:
        next_method = len(content)
    
    # Insertar
    new_content = (
        content[:next_method] + 
        "\n" + engine_method + "\n" +
        content[next_method:]
    )
    
    # Escribir
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Métodos añadidos al engine")
    return True

def create_test_manual_rotation():
    """Crea test para rotación manual"""
    
    test_code = '''# === test_manual_rotation.py ===
# 🧪 Test de rotación manual de macros con deltas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time
import math

def test_manual_rotation():
    """Test de rotación manual con sistema de deltas"""
    print("\\n🧪 TEST: Rotación Manual de Macros")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear macro en formación cuadrada
    macro_name = engine.create_macro("rotating_square", source_count=4, 
                                   formation="square", spacing=2.0)
    print(f"✅ Macro '{macro_name}' creado en formación cuadrada")
    
    # Obtener posiciones iniciales
    macro = engine._macros[macro_name]
    source_ids = list(macro.source_ids)
    
    initial_positions = {}
    for sid in source_ids:
        initial_positions[sid] = engine._positions[sid].copy()
        print(f"   Fuente {sid}: posición inicial = {initial_positions[sid]}")
    
    # Configurar rotación manual
    print("\\n🔧 Configurando rotación manual...")
    success = engine.set_manual_macro_rotation(
        macro_name,
        pitch=0.0,
        yaw=0.0,
        roll=0.0,
        interpolation_speed=0.05  # Suave
    )
    
    if not success:
        print("❌ Error configurando rotación manual")
        return False
    
    print("✅ Rotación manual configurada")
    
    # Test 1: Rotación en Yaw (giro horizontal)
    print("\\n🔄 Test 1: Rotación en Yaw (90 grados)")
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2)  # 90 grados
    
    for i in range(30):
        engine.update()
        time.sleep(0.03)
    
    print("\\nPosiciones después de rotar 90° en Yaw:")
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: {pos}")
    
    # Test 2: Rotación en Pitch
    print("\\n🔄 Test 2: Añadiendo rotación en Pitch (45 grados)")
    engine.set_manual_macro_rotation(macro_name, pitch=math.pi/4)  # 45 grados
    
    for i in range(30):
        engine.update()
        time.sleep(0.03)
    
    # Test 3: Rotación completa
    print("\\n🔄 Test 3: Rotación completa (roll + cambio de velocidad)")
    engine.set_manual_macro_rotation(
        macro_name, 
        pitch=math.pi/6,    # 30 grados
        yaw=math.pi,        # 180 grados
        roll=math.pi/4,     # 45 grados
        interpolation_speed=0.1  # Más rápido
    )
    
    for i in range(50):
        engine.update()
        time.sleep(0.02)
        
        if i % 10 == 0:
            sid = source_ids[0]
            pos = engine._positions[sid]
            print(f"   Update {i}: Fuente {sid} en {pos}")
    
    # Verificar que las posiciones cambiaron
    print("\\n📊 RESULTADOS:")
    print("-" * 40)
    
    all_moved = True
    for sid in source_ids:
        initial = initial_positions[sid]
        current = engine._positions[sid]
        distance = np.linalg.norm(current - initial)
        
        print(f"Fuente {sid}:")
        print(f"  Inicial: {initial}")
        print(f"  Final:   {current}")
        print(f"  Distancia: {distance:.3f} {'✅' if distance > 0.1 else '❌'}")
        
        if distance < 0.1:
            all_moved = False
    
    # Test de toggle
    print("\\n🔧 Test de toggle on/off:")
    engine.toggle_manual_macro_rotation(macro_name, False)
    print("   Rotación desactivada")
    
    initial_pos = engine._positions[source_ids[0]].copy()
    for _ in range(10):
        engine.update()
    
    final_pos = engine._positions[source_ids[0]]
    if np.allclose(initial_pos, final_pos):
        print("   ✅ Las fuentes no se mueven cuando está desactivado")
    else:
        print("   ❌ Las fuentes se siguen moviendo")
    
    return all_moved

if __name__ == "__main__":
    if test_manual_rotation():
        print("\\n✅ ¡ÉXITO! La rotación manual funciona con deltas")
    else:
        print("\\n❌ La rotación manual no funciona correctamente")
'''
    
    with open("test_manual_rotation.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test creado: test_manual_rotation.py")

if __name__ == "__main__":
    print("🔧 IMPLEMENTACIÓN DE MANUAL MACRO ROTATION")
    print("=" * 50)
    
    success = True
    
    # Paso 1: Añadir la clase
    if not add_manual_macro_rotation_class():
        success = False
    
    # Paso 2: Añadir métodos al engine
    if not add_set_manual_macro_rotation():
        success = False
    
    if success:
        create_test_manual_rotation()
        print("\n✅ Implementación completada")
        print("\n📝 Ejecuta:")
        print("python test_manual_rotation.py")
        print("\n💡 La rotación manual es más simple que la algorítmica:")
        print("   - Control directo de ángulos")
        print("   - Interpolación suave configurable")
        print("   - Sin cálculos complejos de velocidad")
    else:
        print("\n❌ Hubo errores en la implementación")