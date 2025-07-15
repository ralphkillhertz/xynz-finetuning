#!/usr/bin/env python3
"""
🔧 Fix: Restaura backup limpio y aplica migración de deltas CORRECTAMENTE
⚡ Estrategia: Empezar limpio y ser más cuidadoso
🎯 Objetivo: Sistema de deltas funcionando sin romper sintaxis
"""

import os
import shutil
import re
from datetime import datetime

def restore_clean_backup():
    """Restaura el backup más limpio"""
    backup_file = "trajectory_hub/core/motion_components.py.backup_20250707_164013"
    target_file = "trajectory_hub/core/motion_components.py"
    
    print("1️⃣ Restaurando backup limpio...")
    
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, target_file)
        print(f"   ✅ Restaurado desde: {backup_file}")
        return True
    else:
        print(f"   ❌ No se encuentra: {backup_file}")
        return False

def add_motion_delta_class():
    """Añade MotionDelta de forma segura"""
    print("\n2️⃣ Añadiendo clase MotionDelta...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    if "class MotionDelta" in content:
        print("   ⚠️ MotionDelta ya existe")
        return
    
    # Código de MotionDelta
    motion_delta_code = '''
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
    
    # Insertar después de las importaciones y antes de la primera clase
    # Buscar el primer @dataclass o class
    first_class = re.search(r'^(@dataclass|class)', content, re.MULTILINE)
    if first_class:
        insert_pos = first_class.start()
        content = content[:insert_pos] + motion_delta_code + '\n' + content[insert_pos:]
        
        with open(motion_file, 'w') as f:
            f.write(content)
        
        print("   ✅ MotionDelta añadido correctamente")

def add_concentration_delta_safely():
    """Añade calculate_delta a ConcentrationComponent de forma segura"""
    print("\n3️⃣ Añadiendo calculate_delta a ConcentrationComponent...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar ConcentrationComponent
    in_concentration = False
    class_line = -1
    update_line = -1
    
    for i, line in enumerate(lines):
        if 'class ConcentrationComponent' in line:
            in_concentration = True
            class_line = i
        elif in_concentration and 'def update(' in line:
            update_line = i
            break
        elif in_concentration and line.strip() and not line.startswith(' '):
            # Salimos de la clase
            break
    
    if update_line > 0:
        # Insertar calculate_delta antes de update
        calculate_delta = '''    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta para concentración"""
        if not hasattr(self, 'enabled'):
            self.enabled = True
            
        if not self.enabled or self.concentration_factor == 0:
            return MotionDelta(source="concentration")
        
        # Calcular centro
        center = self.macro_center if hasattr(self, 'macro_center') else np.zeros(3)
        
        # Vector hacia el centro
        to_center = center - state.position
        distance = np.linalg.norm(to_center)
        
        if distance > 0.001:
            direction = to_center / distance
            movement = direction * distance * self.concentration_factor * dt
            
            return MotionDelta(
                position=movement,
                weight=abs(self.concentration_factor),
                source="concentration"
            )
        
        return MotionDelta(source="concentration")
    
'''
        lines.insert(update_line, calculate_delta)
        
        with open(motion_file, 'w') as f:
            f.writelines(lines)
        
        print("   ✅ calculate_delta añadido correctamente")

def update_engine_safely():
    """Actualiza el engine de forma segura"""
    print("\n4️⃣ Actualizando EnhancedTrajectoryEngine...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup primero
    backup_path = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(engine_file, backup_path)
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Asegurar import de MotionDelta
    if 'MotionDelta' not in content:
        import_pattern = r'(from trajectory_hub\.core\.motion_components import \()'
        content = re.sub(import_pattern, r'\1\n    MotionDelta,', content)
        print("   ✅ Import de MotionDelta añadido")
    
    # 2. Inicializar motion_states en __init__ o __post_init__
    if 'self.motion_states = {}' not in content:
        # Buscar __init__ o __post_init__
        init_pattern = r'(def __(?:init|post_init)__\(.*?\):.*?)(\n\s+def|\n\nclass|\Z)'
        
        def add_motion_states(match):
            return match.group(1) + '\n        self.motion_states = {}  # Para sistema de deltas\n' + match.group(2)
        
        content = re.sub(init_pattern, add_motion_states, content, flags=re.DOTALL)
        print("   ✅ motion_states inicializado")
    
    # 3. Actualizar create_macro
    if 'SourceMotion(' not in content:
        create_macro_pattern = r'(self\._macros\[.*?\] = macro)(.*?)(\n\s+return|\n\s+def|\Z)'
        
        def add_source_motion(match):
            return match.group(1) + '''
        
        # Crear motion states para sistema de deltas
        from trajectory_hub.core.motion_components import SourceMotion, ConcentrationComponent
        for sid in source_ids:
            if sid not in self.motion_states:
                self.motion_states[sid] = SourceMotion(sid)''' + match.group(3)
        
        content = re.sub(create_macro_pattern, add_source_motion, content, flags=re.DOTALL)
        print("   ✅ create_macro actualizado")
    
    with open(engine_file, 'w') as f:
        f.write(content)

def create_simple_test():
    """Crea un test simple para verificar"""
    test_code = '''#!/usr/bin/env python3
"""Test simple del sistema de deltas"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST SISTEMA DE DELTAS\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
engine.create_macro("test", [0, 1, 2])

# Posiciones iniciales
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([np.cos(angle) * 10, np.sin(angle) * 10, 0])

print("Posiciones iniciales:")
for i in range(3):
    print(f"  Source {i}: {engine._positions[i]}")

# Verificar motion_states
if hasattr(engine, 'motion_states'):
    print(f"\\nMotion states: {list(engine.motion_states.keys())}")
else:
    print("\\n❌ No hay motion_states")

print("\\n✅ Test básico completado")
'''
    
    with open("test_delta_simple.py", 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test simple creado: test_delta_simple.py")

def main():
    print("🔧 RESTAURACIÓN Y MIGRACIÓN LIMPIA")
    print("=" * 60)
    
    # 1. Restaurar
    if not restore_clean_backup():
        print("\n❌ No se pudo restaurar. Abortando.")
        return
    
    # 2. Añadir MotionDelta
    add_motion_delta_class()
    
    # 3. Añadir calculate_delta
    add_concentration_delta_safely()
    
    # 4. Actualizar engine
    update_engine_safely()
    
    # 5. Crear test
    create_simple_test()
    
    print("\n✅ MIGRACIÓN COMPLETA")
    print("\n📋 Pasos siguientes:")
    print("1. python test_delta_simple.py  # Test básico")
    print("2. python test_delta_final.py   # Test completo")

if __name__ == "__main__":
    main()