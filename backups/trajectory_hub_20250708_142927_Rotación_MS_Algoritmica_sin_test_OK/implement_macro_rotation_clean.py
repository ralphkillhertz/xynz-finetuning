# === implement_macro_rotation_clean.py ===
# 🔧 Implementación limpia de MacroRotation desde backup
# ⚡ Basado en análisis de todos los intentos previos
# 🎯 Tiempo estimado: 10 minutos

import shutil
from pathlib import Path
import datetime

def implement_macro_rotation_from_scratch():
    """Implementa MacroRotation correctamente desde el principio"""
    
    print("🔄 Implementando MacroRotation desde backup limpio...")
    
    # 1. Restaurar backup
    backup_name = "trajectory_hub_20250708_101052_MS_Trayectorias_Delta_sin_Test_OK"
    if not Path(backup_name).exists():
        print(f"❌ Backup {backup_name} no encontrado")
        return False
    
    # 2. Crear backup del estado actual
    current_backup = f"trajectory_hub_backup_before_clean_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree("trajectory_hub", current_backup)
    print(f"✅ Backup actual guardado en: {current_backup}")
    
    # 3. Restaurar backup limpio
    shutil.rmtree("trajectory_hub")
    shutil.copytree(backup_name, "trajectory_hub")
    print("✅ Backup limpio restaurado")
    
    # 4. Añadir MacroRotation CORRECTAMENTE a motion_components.py
    motion_components_path = Path("trajectory_hub/core/motion_components.py")
    content = motion_components_path.read_text()
    
    # Insertar después de MacroTrajectory
    insert_pos = content.find("class MacroTrajectory")
    if insert_pos == -1:
        print("❌ No se encontró MacroTrajectory")
        return False
    
    # Encontrar el final de MacroTrajectory
    next_class = content.find("\nclass ", insert_pos + 1)
    if next_class == -1:
        next_class = len(content)
    
    # Código de MacroRotation CORRECTO
    macro_rotation_code = '''

class MacroRotation(MotionComponent):
    """Rotación algorítmica para grupos de fuentes - Sistema de deltas"""
    
    def __init__(self):
        super().__init__()
        self.component_type = 'macro_rotation'
        self.enabled = False
        
        # Centro de rotación
        self.center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        
        # Velocidades de rotación (rad/s)
        self.speed_x = 0.0
        self.speed_y = 0.0  
        self.speed_z = 0.0
        
        # Ángulos actuales
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        
    def set_rotation(self, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configura velocidades de rotación - SIEMPRE usa float()"""
        # Convertir a float SIEMPRE para evitar arrays
        self.speed_x = float(speed_x)
        self.speed_y = float(speed_y)
        self.speed_z = float(speed_z)
        
        if center is not None:
            self.center = np.array(center, dtype=np.float32)
        
        # Usar any() para arrays, pero aquí ya son floats
        speeds = [abs(self.speed_x) > 0.001, 
                  abs(self.speed_y) > 0.001,
                  abs(self.speed_z) > 0.001]
        self.enabled = any(speeds)
        
    def calculate_delta(self, state, current_time, dt):
        """Calcula delta de rotación"""
        if not self.enabled:
            return MotionDelta()
            
        # Actualizar ángulos
        self.angle_x += float(self.speed_x) * float(dt)
        self.angle_y += float(self.speed_y) * float(dt)
        self.angle_z += float(self.speed_z) * float(dt)
        
        # Posición relativa al centro
        pos = state.position - self.center
        
        # Matrices de rotación (orden: Z, Y, X)
        cx, sx = np.cos(self.angle_x), np.sin(self.angle_x)
        cy, sy = np.cos(self.angle_y), np.sin(self.angle_y)
        cz, sz = np.cos(self.angle_z), np.sin(self.angle_z)
        
        # Rotación combinada
        # Rz
        x1 = pos[0] * cz - pos[1] * sz
        y1 = pos[0] * sz + pos[1] * cz
        z1 = pos[2]
        
        # Ry
        x2 = x1 * cy + z1 * sy
        y2 = y1
        z2 = -x1 * sy + z1 * cy
        
        # Rx
        x3 = x2
        y3 = y2 * cx - z2 * sx
        z3 = y2 * sx + z2 * cx
        
        # Nueva posición
        new_pos = np.array([x3, y3, z3]) + self.center
        
        # Delta es la diferencia
        delta = MotionDelta()
        delta.position = new_pos - state.position
        
        return delta
'''
    
    # Insertar el código
    content = content[:next_class] + macro_rotation_code + content[next_class:]
    motion_components_path.write_text(content)
    print("✅ MacroRotation añadida correctamente")
    
    # 5. Añadir set_macro_rotation a enhanced_trajectory_engine.py
    engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
    engine_content = engine_path.read_text()
    
    # Buscar dónde insertar (después de set_macro_trajectory)
    insert_pos = engine_content.find("def set_macro_trajectory")
    if insert_pos == -1:
        print("❌ No se encontró set_macro_trajectory")
        return False
    
    # Encontrar el final del método
    next_def = engine_content.find("\n    def ", insert_pos + 1)
    
    set_rotation_code = '''
    
    def set_macro_rotation(self, macro_name, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configura rotación algorítmica para un macro"""
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return False
            
        macro = self._macros[macro_name]
        source_ids = list(macro.source_ids)
        
        # Centro por defecto es el centroide del macro
        if center is None:
            positions = []
            for sid in source_ids:
                if sid < len(self._positions):
                    positions.append(self._positions[sid])
            if positions:
                center = np.mean(positions, axis=0)
            else:
                center = np.array([0.0, 0.0, 0.0])
        
        # Configurar rotación para cada fuente del macro
        configured = 0
        for sid in source_ids:
            if sid in self.motion_states:
                motion = self.motion_states[sid]
                
                # Crear componente si no existe
                if 'macro_rotation' not in motion.active_components:
                    from trajectory_hub.core.motion_components import MacroRotation
                    rotation = MacroRotation()
                    motion.active_components['macro_rotation'] = rotation
                else:
                    rotation = motion.active_components['macro_rotation']
                
                # Configurar rotación
                rotation.set_rotation(
                    speed_x=float(speed_x),
                    speed_y=float(speed_y), 
                    speed_z=float(speed_z),
                    center=center
                )
                configured += 1
        
        if configured > 0:
            print(f"✅ Rotación configurada para '{macro_name}'")
            print(f"   Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
            print(f"   Velocidades: X={speed_x}, Y={speed_y}, Z={speed_z} rad/s")
            print(f"   Fuentes: {configured}/{len(source_ids)}")
            return True
        
        return False
'''
    
    # Insertar el método
    engine_content = engine_content[:next_def] + set_rotation_code + engine_content[next_def:]
    engine_path.write_text(engine_content)
    print("✅ set_macro_rotation añadido correctamente")
    
    # 6. Crear test específico
    test_code = '''#!/usr/bin/env python3
"""Test de rotación MS con sistema de deltas - Implementación limpia"""

import numpy as np
import time
from trajectory_hub import EnhancedTrajectoryEngine

def test_macro_rotation_clean():
    """Test limpio de rotación algorítmica MS"""
    print("🧪 TEST LIMPIO: Rotación MS Algorítmica con Deltas")
    print("=" * 50)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(n_sources=4, update_rate=60)
    print("✅ Engine creado")
    
    # Crear fuentes formando un cuadrado
    positions = [
        [2.0, 2.0, 0.0],   # Superior derecha
        [-2.0, 2.0, 0.0],  # Superior izquierda
        [-2.0, -2.0, 0.0], # Inferior izquierda
        [2.0, -2.0, 0.0]   # Inferior derecha
    ]
    
    for i, pos in enumerate(positions):
        name = engine.create_source(position=pos)
        print(f"✅ Fuente {i} creada: {name} en {pos}")
    
    # Crear macro
    source_ids = list(range(4))
    macro_name = engine.create_macro("test_rotation", source_ids)
    print(f"\\n✅ Macro creado: {macro_name}")
    
    # Aplicar rotación
    success = engine.set_macro_rotation(
        macro_name,
        speed_x=0.0,
        speed_y=1.0,  # 1 rad/s en Y
        speed_z=0.0
    )
    
    if not success:
        print("❌ Error al configurar rotación")
        return
    
    # Verificar estado inicial
    print("\\n📍 Posiciones iniciales:")
    for i in range(4):
        pos = engine._positions[i]
        print(f"   Fuente {i}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # Simular movimiento
    print("\\n⏱️ Simulando 1 segundo (60 frames)...")
    for frame in range(60):
        engine.update()
        
        # Mostrar progreso cada 20 frames
        if frame % 20 == 0:
            print(f"   Frame {frame}/60...")
    
    # Verificar estado final
    print("\\n📍 Posiciones finales:")
    total_movement = 0.0
    for i in range(4):
        initial = np.array(positions[i])
        final = engine._positions[i]
        distance = np.linalg.norm(final - initial)
        
        # Calcular ángulo de rotación
        angle = np.arctan2(final[2] - initial[2], final[0] - initial[0])
        
        print(f"   Fuente {i}: [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
        print(f"            Movió: {distance:.2f} unidades, Rotó: {np.degrees(angle):.1f}°")
        
        total_movement += distance
    
    avg_movement = total_movement / 4
    print(f"\\n📊 Movimiento promedio: {avg_movement:.2f} unidades")
    
    # Verificar que hubo movimiento
    if avg_movement > 0.1:
        print("\\n✅ TEST EXITOSO: Las fuentes rotaron correctamente")
    else:
        print("\\n❌ TEST FALLIDO: No hubo movimiento suficiente")

if __name__ == "__main__":
    test_macro_rotation_clean()
'''
    
    test_path = Path("test_rotation_clean.py")
    test_path.write_text(test_code)
    print("✅ Test creado: test_rotation_clean.py")
    
    print("\n✅ Implementación completa desde backup limpio")
    print("\n📝 Próximos pasos:")
    print("1. python test_rotation_clean.py")
    print("2. Si funciona, guardar estado")
    print("3. Si no, el problema está en otra parte del sistema")
    
    return True

if __name__ == "__main__":
    implement_macro_rotation_from_scratch()