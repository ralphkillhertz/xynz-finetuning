# === fix_macro_rotation_complete_v2.py ===
# 🔧 Fix definitivo de MacroRotation - versión corregida
# ⚡ Corrige el error del timestamp
# 🎯 Tiempo: 2 minutos

from pathlib import Path
import datetime

def fix_macro_rotation_complete():
    """Arregla MacroRotation encontrando TODOS los problemas"""
    
    print("🔍 Analizando MacroRotation completa...")
    
    # 1. Leer archivo
    file_path = Path("trajectory_hub/core/motion_components.py")
    content = file_path.read_text()
    
    # 2. Extraer clase MacroRotation completa
    class_start = content.find("class MacroRotation")
    if class_start == -1:
        print("❌ No se encontró MacroRotation")
        return False
        
    # Encontrar el final de la clase
    next_class = content.find("\nclass ", class_start + 1)
    if next_class == -1:
        next_class = len(content)
    
    print("📝 Reescribiendo MacroRotation con arrays seguros...")
    
    # 3. Reescribir MacroRotation completamente segura
    safe_macro_rotation = '''class MacroRotation(MotionComponent):
    """Rotación algorítmica para grupos de fuentes - Sistema de deltas"""
    
    def __init__(self):
        super().__init__()
        self.component_type = 'macro_rotation'
        self.enabled = False
        
        # Centro de rotación - siempre numpy array
        self.center = np.zeros(3, dtype=np.float32)
        
        # Velocidades de rotación (rad/s) - siempre escalares
        self._speed_x = 0.0
        self._speed_y = 0.0  
        self._speed_z = 0.0
        
        # Ángulos actuales - siempre escalares
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        
    @property
    def speed_x(self):
        return float(self._speed_x)
        
    @speed_x.setter
    def speed_x(self, value):
        self._speed_x = float(value) if not isinstance(value, (list, np.ndarray)) else float(value[0] if len(value) > 0 else 0)
        
    @property
    def speed_y(self):
        return float(self._speed_y)
        
    @speed_y.setter
    def speed_y(self, value):
        self._speed_y = float(value) if not isinstance(value, (list, np.ndarray)) else float(value[0] if len(value) > 0 else 0)
        
    @property
    def speed_z(self):
        return float(self._speed_z)
        
    @speed_z.setter
    def speed_z(self, value):
        self._speed_z = float(value) if not isinstance(value, (list, np.ndarray)) else float(value[0] if len(value) > 0 else 0)
        
    def set_rotation(self, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configura velocidades de rotación de forma segura"""
        # Usar setters que garantizan float
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed_z = speed_z
        
        if center is not None:
            # Garantizar que center es numpy array de 3 elementos
            if isinstance(center, (list, tuple)):
                self.center = np.array(center[:3], dtype=np.float32)
            elif isinstance(center, np.ndarray):
                self.center = center.flatten()[:3].astype(np.float32)
            else:
                self.center = np.zeros(3, dtype=np.float32)
        
        # Habilitar si alguna velocidad es significativa
        # Usar abs() con floats garantizados
        threshold = 0.001
        self.enabled = (
            abs(self.speed_x) > threshold or
            abs(self.speed_y) > threshold or
            abs(self.speed_z) > threshold
        )
        
    def calculate_delta(self, state, current_time, dt):
        """Calcula delta de rotación para sistema de deltas"""
        if not self.enabled:
            return MotionDelta()
            
        # Garantizar dt es float
        dt_float = float(dt) if not isinstance(dt, float) else dt
        
        # Actualizar ángulos (todos son floats)
        self.angle_x += self.speed_x * dt_float
        self.angle_y += self.speed_y * dt_float
        self.angle_z += self.speed_z * dt_float
        
        # Posición actual - garantizar numpy array
        current_pos = np.array(state.position, dtype=np.float32)
        
        # Posición relativa al centro
        rel_pos = current_pos - self.center
        
        # Precalcular senos y cosenos
        cx, sx = np.cos(self.angle_x), np.sin(self.angle_x)
        cy, sy = np.cos(self.angle_y), np.sin(self.angle_y)
        cz, sz = np.cos(self.angle_z), np.sin(self.angle_z)
        
        # Aplicar rotaciones (Z -> Y -> X)
        # Rotación Z
        x1 = rel_pos[0] * cz - rel_pos[1] * sz
        y1 = rel_pos[0] * sz + rel_pos[1] * cz
        z1 = rel_pos[2]
        
        # Rotación Y
        x2 = x1 * cy + z1 * sy
        y2 = y1
        z2 = -x1 * sy + z1 * cy
        
        # Rotación X
        x3 = x2
        y3 = y2 * cx - z2 * sx
        z3 = y2 * sx + z2 * cx
        
        # Nueva posición absoluta
        new_pos = np.array([x3, y3, z3], dtype=np.float32) + self.center
        
        # Crear delta
        delta = MotionDelta()
        delta.position = new_pos - current_pos
        
        return delta
        
    def update(self, current_time, dt, state):
        """Actualiza el estado con el delta calculado"""
        if not self.enabled:
            return state
            
        delta = self.calculate_delta(state, current_time, dt)
        state.position += delta.position
        
        return state
        
    def get_state(self):
        """Obtiene el estado actual del componente"""
        return {
            'type': self.component_type,
            'enabled': bool(self.enabled),
            'center': self.center.tolist(),
            'speed_x': float(self.speed_x),
            'speed_y': float(self.speed_y),
            'speed_z': float(self.speed_z),
            'angle_x': float(self.angle_x),
            'angle_y': float(self.angle_y),
            'angle_z': float(self.angle_z)
        }

'''
    
    # 4. Reemplazar la clase completa
    new_content = content[:class_start] + safe_macro_rotation + content[next_class:]
    
    # 5. Guardar con backup usando timestamp correcto
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f'.backup_{timestamp}')
    
    # Crear backup primero
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Guardar nueva versión
    file_path.write_text(new_content)
    
    print(f"✅ MacroRotation reescrita completamente")
    print(f"   Backup: {backup_path}")
    
    # 6. Crear test específico
    with open("test_macro_rotation_fixed.py", "w") as f:
        f.write('''#!/usr/bin/env python3
"""Test de MacroRotation arreglada"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test MacroRotation Arreglada")

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")

    # Crear 4 fuentes en cuadrado
    positions = [[2,0,0], [-2,0,0], [0,2,0], [0,-2,0]]
    for i, pos in enumerate(positions):
        engine.create_source(position=pos)
        
    # Crear macro
    engine.create_macro("rot_test", [0,1,2,3])
    print("✅ Macro creado")

    # Estado inicial
    print("\\n📍 Inicial:")
    for i in range(4):
        p = engine._positions[i]
        print(f"  F{i}: [{p[0]:5.2f}, {p[1]:5.2f}, {p[2]:5.2f}]")

    # Aplicar rotación
    print("\\n🔄 Aplicando rotación Y=1.0 rad/s...")
    success = engine.set_macro_rotation("rot_test", speed_y=1.0)
    print(f"   Resultado: {success}")

    # Verificar que se configuró
    if hasattr(engine, 'motion_states'):
        rot_count = 0
        for sid in range(4):
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if 'macro_rotation' in motion.active_components:
                    rot = motion.active_components['macro_rotation']
                    if rot.enabled:
                        rot_count += 1
        print(f"   Componentes activos: {rot_count}/4")

    # Simular 1 segundo
    print("\\n⏱️ Simulando...")
    for i in range(60):
        engine.update()
        if i % 20 == 0:
            print(f"  {i}/60 frames...")

    # Estado final
    print("\\n📍 Final:")
    moved = False
    for i in range(4):
        p = engine._positions[i]
        dist = np.linalg.norm(p - positions[i])
        print(f"  F{i}: [{p[0]:5.2f}, {p[1]:5.2f}, {p[2]:5.2f}] (movió {dist:.3f})")
        if dist > 0.1:
            moved = True

    print(f"\\n{'✅' if moved else '❌'} {'Rotación funciona!' if moved else 'Sin movimiento'}")
    
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
''')
    
    print("\n📝 Próximo paso: python test_macro_rotation_fixed.py")
    
    return True

if __name__ == "__main__":
    fix_macro_rotation_complete()