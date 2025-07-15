#!/usr/bin/env python3
"""
🔧 Fix: Migra concentración al sistema de deltas
⚡ Componente: ConcentrationComponent → ConcentrationDelta
🎯 Resultado: Concentración funcionará con otros componentes
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Crea backup antes de modificar"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path

def add_delta_imports():
    """Añade imports necesarios a motion_components.py"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_file(motion_file)
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Añadir imports si no existen
    if "MotionDelta" not in content:
        imports = '''
# Sistema de deltas
@dataclass
class MotionDelta:
    """Representa un cambio incremental en posición/orientación"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    aperture: float = 0.0
    weight: float = 1.0
    source: str = ""
    
    def scale(self, factor: float) -> 'MotionDelta':
        return MotionDelta(
            position=self.position * factor,
            orientation=self.orientation * factor,
            aperture=self.aperture * factor,
            weight=self.weight * factor,
            source=self.source
        )
'''
        # Insertar después de MotionState
        content = content.replace("@dataclass\nclass MotionState:", 
                                  f"{imports}\n\n@dataclass\nclass MotionState:")
    
    # Añadir método calculate_delta a ConcentrationComponent
    concentration_delta = '''
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta para concentración"""
        if not self.enabled or self.concentration_factor == 0:
            return MotionDelta(source="concentration")
        
        # Calcular centro actual del grupo
        if self.mode == ConcentrationMode.CENTER:
            center = self.calculate_center()
        elif self.mode == ConcentrationMode.CUSTOM:
            center = self.custom_center
        else:  # ORIGIN
            center = np.zeros(3)
        
        # Vector hacia el centro
        to_center = center - state.position
        distance = np.linalg.norm(to_center)
        
        if distance > 0.001:
            direction = to_center / distance
            
            # Aplicar curva si está definida
            if self.curve == ConcentrationCurve.SMOOTH:
                factor = self._smooth_curve(self.concentration_factor)
            elif self.curve == ConcentrationCurve.SHARP:
                factor = self._sharp_curve(self.concentration_factor)
            else:
                factor = self.concentration_factor
            
            # Movimiento hacia el centro
            movement = direction * distance * factor * dt
            
            return MotionDelta(
                position=movement,
                weight=abs(factor),
                source="concentration"
            )
        
        return MotionDelta(source="concentration")
    
    def _smooth_curve(self, t: float) -> float:
        """Curva suave (ease-in-out)"""
        return t * t * (3.0 - 2.0 * t)
    
    def _sharp_curve(self, t: float) -> float:
        """Curva abrupta"""
        return t * t * t
'''
    
    # Buscar ConcentrationComponent y añadir método
    if "def calculate_delta" not in content:
        # Insertar antes del cierre de la clase
        marker = "class ConcentrationComponent(MotionComponent):"
        if marker in content:
            # Encontrar el final de la clase
            lines = content.split('\n')
            in_class = False
            indent_level = 0
            insert_line = -1
            
            for i, line in enumerate(lines):
                if marker in line:
                    in_class = True
                    indent_level = len(line) - len(line.lstrip())
                elif in_class and line.strip() and not line.startswith(' '):
                    # Fin de la clase
                    insert_line = i - 1
                    break
            
            if insert_line > 0:
                lines.insert(insert_line, concentration_delta)
                content = '\n'.join(lines)
    
    # Guardar cambios
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print(f"✅ motion_components.py actualizado con sistema de deltas")

def update_source_motion():
    """Actualiza SourceMotion para usar deltas"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Añadir DeltaComposer a SourceMotion
    delta_update = '''
    def update_with_deltas(self, current_time: float, dt: float) -> MotionDelta:
        """Nueva versión que retorna delta en lugar de estado"""
        from collections import defaultdict
        deltas = []
        
        # Recolectar deltas de cada componente
        for component in self.active_components:
            if hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, current_time, dt)
                deltas.append(delta)
            else:
                # Fallback para componentes sin calculate_delta
                old_pos = self.state.position.copy()
                old_ori = self.state.orientation.copy()
                old_aper = self.state.aperture
                
                new_state = component.update(self.state, current_time, dt)
                
                delta = MotionDelta(
                    position=new_state.position - old_pos,
                    orientation=new_state.orientation - old_ori,
                    aperture=new_state.aperture - old_aper,
                    source=component.__class__.__name__
                )
                deltas.append(delta)
                self.state = new_state
        
        # Componer deltas
        if not deltas:
            return MotionDelta()
        
        total_weight = sum(d.weight for d in deltas)
        if total_weight == 0:
            total_weight = 1.0
        
        result = MotionDelta()
        for delta in deltas:
            w = delta.weight / total_weight
            result.position += delta.position * w
            result.orientation += delta.orientation * w
            result.aperture += delta.aperture * w
        
        result.weight = 1.0
        result.source = "+".join(d.source for d in deltas)
        
        # Aplicar delta al estado interno
        self.state.position += result.position
        self.state.orientation += result.orientation
        self.state.aperture += result.aperture
        
        return result
'''
    
    # Insertar en SourceMotion
    if "update_with_deltas" not in content:
        marker = "class SourceMotion:"
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if marker in line:
                # Buscar el final del método update
                for j in range(i, len(lines)):
                    if "def update(" in lines[j]:
                        # Buscar el final del método
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        for k in range(j+1, len(lines)):
                            if lines[k].strip() and not lines[k].startswith(' ' * (indent + 1)):
                                lines.insert(k, delta_update)
                                break
                        break
                break
        content = '\n'.join(lines)
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ SourceMotion actualizado con update_with_deltas")

def update_engine_step():
    """Actualiza engine para usar deltas"""
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    backup_file(engine_file)
    
    # Crear nuevo step() que use deltas
    new_step = '''def step(self):
    """Calcula siguiente frame usando sistema de deltas"""
    current_time = time.time()
    dt = 1.0 / self.update_rate
    
    # Actualizar macros primero (pueden afectar comportamientos)
    for macro_name, macro in self._macros.items():
        if hasattr(macro, 'update'):
            macro.update(current_time, dt)
    
    # Para cada fuente con motion
    for source_id, motion in self.motion_states.items():
        if source_id >= self.n_sources:
            continue
            
        # Obtener delta compuesto
        if hasattr(motion, 'update_with_deltas'):
            delta = motion.update_with_deltas(current_time, dt)
        else:
            # Fallback
            old_state = motion.state
            motion.update(current_time, dt)
            delta = MotionDelta(
                position=motion.state.position - old_state.position,
                orientation=motion.state.orientation - old_state.orientation
            )
        
        # Aplicar delta
        self._positions[source_id] += delta.position
        if hasattr(self, '_orientations'):
            self._orientations[source_id] += delta.orientation
        
        # Límites
        self._positions[source_id] = np.clip(
            self._positions[source_id], -50, 50
        )
    
    self._frame_count += 1
    return self._positions.copy()
'''
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Reemplazar step() existente
    import re
    pattern = r'def step\(self\):.*?(?=\n    def|\n\nclass|\Z)'
    content = re.sub(pattern, new_step.strip(), content, flags=re.DOTALL)
    
    # Añadir import de MotionDelta
    if "from trajectory_hub.core.motion_components import" in content:
        content = content.replace(
            "from trajectory_hub.core.motion_components import",
            "from trajectory_hub.core.motion_components import MotionDelta,"
        )
    
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ EnhancedTrajectoryEngine.step() actualizado para usar deltas")

def test_concentration_with_deltas():
    """Test para verificar que concentración funciona"""
    test_code = '''#!/usr/bin/env python3
"""Test de concentración con sistema de deltas"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test():
    print("🧪 Test de concentración con deltas\\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(n_sources=5)
    
    # Crear macro
    engine.create_macro("test", list(range(5)))
    
    # Posiciones iniciales dispersas
    for i in range(5):
        angle = i * 2 * np.pi / 5
        engine._positions[i] = np.array([
            np.cos(angle) * 10,
            np.sin(angle) * 10,
            0
        ])
    
    print("Posiciones iniciales:")
    for i in range(5):
        print(f"  Source {i}: {engine._positions[i]}")
    
    # Aplicar concentración
    print("\\n✨ Aplicando concentración...")
    engine.apply_concentration("test", factor=0.5)
    
    # Simular algunos frames
    for frame in range(30):
        engine.step()
        if frame % 10 == 0:
            print(f"\\nFrame {frame}:")
            center = np.mean(engine._positions[:5], axis=0)
            spread = np.std(engine._positions[:5])
            print(f"  Centro: {center}")
            print(f"  Dispersión: {spread:.2f}")
    
    print("\\n✅ Test completado!")

if __name__ == "__main__":
    test()
'''
    
    with open("test_concentration_delta.py", 'w') as f:
        f.write(test_code)
    
    print("✅ Test creado: test_concentration_delta.py")

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 MIGRANDO CONCENTRACIÓN A SISTEMA DE DELTAS")
    print("=" * 60)
    
    print("\n1️⃣ Actualizando motion_components.py...")
    add_delta_imports()
    update_source_motion()
    
    print("\n2️⃣ Actualizando enhanced_trajectory_engine.py...")
    update_engine_step()
    
    print("\n3️⃣ Creando test...")
    test_concentration_with_deltas()
    
    print("\n✅ Migración completada!")
    print("\n📋 Para probar:")
    print("$ python test_concentration_delta.py")