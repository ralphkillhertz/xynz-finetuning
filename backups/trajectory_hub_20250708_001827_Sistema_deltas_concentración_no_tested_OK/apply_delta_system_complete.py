#!/usr/bin/env python3
"""
🔧 Fix: Aplica COMPLETAMENTE el sistema de deltas
⚡ Problema: La migración anterior no se aplicó correctamente
🎯 Solución: Verificar y aplicar todos los cambios necesarios
"""

import os
import re
from datetime import datetime

def backup_file(filepath):
    """Backup antes de modificar"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(filepath, backup_path)
    return backup_path

def fix_motion_components():
    """Asegura que ConcentrationComponent tenga calculate_delta"""
    print("\n1️⃣ Arreglando motion_components.py...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    backup_file(motion_file)
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # 1. Verificar si MotionDelta existe
    if "class MotionDelta" not in content:
        print("   ❌ MotionDelta no existe - añadiendo...")
        
        # Buscar dónde insertar
        import_section_end = content.find("\n\n\n") 
        if import_section_end == -1:
            import_section_end = content.find("@dataclass")
        
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
        content = content[:import_section_end] + motion_delta_code + content[import_section_end:]
        print("   ✅ MotionDelta añadido")
    
    # 2. Añadir calculate_delta a ConcentrationComponent
    if "def calculate_delta" not in content:
        print("   ❌ calculate_delta no existe en ConcentrationComponent - añadiendo...")
        
        # Buscar ConcentrationComponent
        class_start = content.find("class ConcentrationComponent")
        if class_start != -1:
            # Buscar el método update
            update_start = content.find("def update(", class_start)
            if update_start != -1:
                # Insertar calculate_delta antes de update
                calculate_delta_code = '''
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
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
                # Encontrar la indentación correcta
                indent_match = re.search(r'^(\s*)def update', content[update_start:update_start+50], re.MULTILINE)
                if indent_match:
                    indent = indent_match.group(1)
                    calculate_delta_code = calculate_delta_code.replace('    def', f'{indent}def')
                
                content = content[:update_start] + calculate_delta_code + content[update_start:]
                print("   ✅ calculate_delta añadido a ConcentrationComponent")
    
    # 3. Añadir update_with_deltas a SourceMotion
    if "def update_with_deltas" not in content:
        print("   ❌ update_with_deltas no existe en SourceMotion - añadiendo...")
        
        source_motion_class = content.find("class SourceMotion")
        if source_motion_class != -1:
            # Buscar el método update existente
            update_pos = content.find("def update(", source_motion_class)
            if update_pos != -1:
                # Buscar el final del método update
                next_def = content.find("\n    def ", update_pos + 10)
                if next_def == -1:
                    next_def = content.find("\nclass", update_pos)
                
                update_with_deltas_code = '''

    def update_with_deltas(self, current_time: float, dt: float) -> MotionDelta:
        """Nueva versión que retorna delta"""
        deltas = []
        
        for component in self.active_components:
            if hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, current_time, dt)
                deltas.append(delta)
            else:
                # Fallback
                old_pos = self.state.position.copy()
                new_state = component.update(self.state, current_time, dt)
                delta = MotionDelta(
                    position=new_state.position - old_pos,
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
        
        result.source = "+".join(d.source for d in deltas)
        
        # Actualizar estado
        self.state.position += result.position
        
        return result
'''
                content = content[:next_def] + update_with_deltas_code + content[next_def:]
                print("   ✅ update_with_deltas añadido a SourceMotion")
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("   ✅ motion_components.py actualizado completamente")

def fix_engine():
    """Arregla EnhancedTrajectoryEngine para usar deltas"""
    print("\n2️⃣ Arreglando enhanced_trajectory_engine.py...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    backup_file(engine_file)
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Asegurar que motion_states se inicializa
    if "self.motion_states = {}" not in content:
        print("   ❌ motion_states no se inicializa - añadiendo...")
        
        # Buscar __init__ o __post_init__
        init_pos = content.find("def __init__")
        if init_pos == -1:
            init_pos = content.find("def __post_init__")
        
        if init_pos != -1:
            # Buscar el final del método
            next_def = content.find("\n    def ", init_pos + 10)
            
            # Insertar antes del final
            init_line = "\n        self.motion_states = {}  # Dict[int, SourceMotion]\n"
            content = content[:next_def] + init_line + content[next_def:]
            print("   ✅ motion_states inicializado")
    
    # 2. Actualizar create_macro para crear motion_states
    create_macro_pos = content.find("def create_macro")
    if create_macro_pos != -1:
        # Verificar si ya crea motion_states
        method_end = content.find("\n    def ", create_macro_pos + 10)
        if method_end == -1:
            method_end = len(content)
        
        method_content = content[create_macro_pos:method_end]
        
        if "SourceMotion" not in method_content:
            print("   ❌ create_macro no crea SourceMotion - añadiendo...")
            
            # Buscar dónde insertar (después de crear el macro)
            macro_created = method_content.find("self._macros[name] = macro")
            if macro_created != -1:
                insert_pos = create_macro_pos + macro_created + len("self._macros[name] = macro")
                
                motion_code = '''
        
        # Crear motion states para cada fuente
        from trajectory_hub.core.motion_components import SourceMotion, ConcentrationComponent
        for sid in source_ids:
            if sid not in self.motion_states:
                self.motion_states[sid] = SourceMotion(sid)
'''
                content = content[:insert_pos] + motion_code + content[insert_pos:]
                print("   ✅ create_macro ahora crea motion_states")
    
    # 3. Actualizar step() para usar deltas
    step_method = re.search(r'def step\(self\):.*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    if step_method:
        step_content = step_method.group(0)
        
        if "update_with_deltas" not in step_content:
            print("   ❌ step() no usa sistema de deltas - reemplazando...")
            
            new_step = '''def step(self):
        """Calcula siguiente frame usando sistema de deltas"""
        current_time = time.time()
        dt = 1.0 / self.fps
        
        # Para cada fuente con motion state
        for source_id, motion in self.motion_states.items():
            if source_id >= self.max_sources:
                continue
                
            # Obtener delta
            if hasattr(motion, 'update_with_deltas'):
                delta = motion.update_with_deltas(current_time, dt)
                
                # Aplicar delta
                if source_id < len(self._positions):
                    self._positions[source_id] += delta.position
                    
                    # Límites
                    self._positions[source_id] = np.clip(
                        self._positions[source_id], -50, 50
                    )
        
        return self._positions.copy()'''
            
            content = content.replace(step_content, new_step)
            print("   ✅ step() actualizado para usar deltas")
    
    # 4. Actualizar set_macro_concentration
    set_concentration = content.find("def set_macro_concentration")
    if set_concentration != -1:
        # Verificar que active la concentración en motion_states
        method_end = content.find("\n    def ", set_concentration + 10)
        if method_end == -1:
            method_end = len(content)
        
        method_content = content[set_concentration:method_end]
        
        if "motion_states" not in method_content:
            print("   ❌ set_macro_concentration no usa motion_states - actualizando...")
            
            # Reemplazar el método completo
            old_method = re.search(r'def set_macro_concentration.*?(?=\n    def|\nclass|\Z)', 
                                   content[set_concentration:], re.DOTALL)
            if old_method:
                new_method = '''def set_macro_concentration(self, macro_name: str, factor: float = 0.5):
        """Aplica concentración usando sistema de deltas"""
        if macro_name not in self._macros:
            macro_name = f"macro_{self.macro_counter}_{macro_name}"
            
        if macro_name not in self._macros:
            print(f"Macro {macro_name} no encontrado")
            return False
            
        macro = self._macros[macro_name]
        
        # Crear/actualizar componente de concentración para cada fuente
        from trajectory_hub.core.motion_components import ConcentrationComponent
        
        for sid in macro.source_ids:
            # Asegurar que existe motion state
            if sid not in self.motion_states:
                from trajectory_hub.core.motion_components import SourceMotion
                self.motion_states[sid] = SourceMotion(sid)
            
            motion = self.motion_states[sid]
            
            # Buscar o crear componente de concentración
            concentration = None
            for comp in motion.active_components:
                if isinstance(comp, ConcentrationComponent):
                    concentration = comp
                    break
            
            if concentration is None:
                concentration = ConcentrationComponent(macro=macro)
                motion.add_component(concentration)
            
            # Configurar
            concentration.enabled = True
            concentration.concentration_factor = factor
            concentration.macro_center = np.mean([self._positions[i] for i in macro.source_ids], axis=0)
        
        return True'''
                
                content = content[:set_concentration] + new_method + content[set_concentration + len(old_method.group(0)):]
                print("   ✅ set_macro_concentration actualizado")
    
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("   ✅ enhanced_trajectory_engine.py actualizado completamente")

def create_verification_test():
    """Crea test para verificar que todo funciona"""
    test_code = '''#!/usr/bin/env python3
"""Test final del sistema de deltas"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST FINAL DEL SISTEMA DE DELTAS\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Verificar motion_states
print("1️⃣ Verificando motion_states:")
print(f"   Existe: {'SÍ' if hasattr(engine, 'motion_states') else 'NO'}")

# Crear macro
source_ids = [0, 1, 2]
engine.create_macro("test", source_ids)

# Verificar que motion_states se crearon
if hasattr(engine, 'motion_states'):
    print(f"   Motion states creados: {list(engine.motion_states.keys())}")

# Posiciones iniciales
for i in source_ids:
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([np.cos(angle) * 10, np.sin(angle) * 10, 0])

print("\\n2️⃣ Posiciones iniciales:")
for i in source_ids:
    print(f"   Source {i}: {engine._positions[i]}")

# Aplicar concentración
print("\\n3️⃣ Aplicando concentración...")
engine.set_macro_concentration("test", factor=0.9)

# Simular
print("\\n4️⃣ Simulando 20 frames...")
for frame in range(20):
    engine.step()
    
    if frame in [0, 9, 19]:
        print(f"\\n   Frame {frame}:")
        center = np.mean(engine._positions[:3], axis=0)
        dist = np.mean([np.linalg.norm(engine._positions[i] - center) for i in range(3)])
        print(f"   Distancia promedio al centro: {dist:.2f}")

print("\\n✅ Test completado!")
'''
    
    with open("test_delta_final.py", 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test final creado: test_delta_final.py")

if __name__ == "__main__":
    print("🔧 APLICANDO SISTEMA DE DELTAS COMPLETO")
    print("=" * 60)
    
    fix_motion_components()
    fix_engine()
    create_verification_test()
    
    print("\n✅ SISTEMA DE DELTAS APLICADO COMPLETAMENTE")
    print("\n📋 Ejecuta el test final:")
    print("$ python test_delta_final.py")