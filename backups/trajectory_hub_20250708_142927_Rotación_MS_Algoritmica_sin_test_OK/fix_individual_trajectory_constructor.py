# === fix_individual_trajectory_constructor.py ===
# 🔧 Fix: Verificar y corregir el constructor de IndividualTrajectory
# ⚡ Error: __init__() got an unexpected keyword argument 'shape'
# 🎯 Impacto: ALTO - Sin esto no se pueden crear trayectorias individuales

import os
import re
import inspect

def check_individual_trajectory_class():
    """Verifica la implementación actual de IndividualTrajectory"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔍 Analizando IndividualTrajectory en motion_components.py...")
    
    # Importar para inspeccionar
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from trajectory_hub.core.motion_components import IndividualTrajectory
        
        # Ver la firma del constructor
        sig = inspect.signature(IndividualTrajectory.__init__)
        print(f"✅ Constructor actual: {sig}")
        
        # Ver métodos disponibles
        methods = [m for m in dir(IndividualTrajectory) if not m.startswith('_')]
        print(f"\n📋 Métodos públicos: {methods}")
        
    except Exception as e:
        print(f"❌ Error importando: {e}")
    
    # Leer el archivo para ver la implementación
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la clase
    class_pattern = r'class IndividualTrajectory.*?(?=\nclass|\Z)'
    match = re.search(class_pattern, content, re.DOTALL)
    
    if match:
        class_content = match.group(0)
        
        # Buscar el __init__
        init_pattern = r'def __init__\(self[^)]*\):'
        init_match = re.search(init_pattern, class_content)
        
        if init_match:
            print(f"\n📝 __init__ encontrado: {init_match.group(0)}")
            
            # Ver si tiene set_shape o configure
            if "set_shape" in class_content:
                print("✅ Tiene método set_shape")
            if "configure" in class_content:
                print("✅ Tiene método configure")

def fix_set_individual_trajectory_v2():
    """Arregla el método para usar la API correcta de IndividualTrajectory"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("\n🔧 Corrigiendo set_individual_trajectory con API correcta...")
    
    # Leer el archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Nuevo método que usa la API correcta
    new_method = '''def set_individual_trajectory(self, macro_id: str, source_id: int, 
                                     shape: str, shape_params: dict = None,
                                     movement_mode: str = "fix", speed: float = 1.0):
        """Configura la trayectoria individual de una fuente dentro de un macro"""
        # Verificar que el macro existe
        if macro_id not in self._macros:
            raise ValueError(f"Macro '{macro_id}' not found")
        
        macro = self._macros[macro_id]
        
        # Verificar que la fuente pertenece al macro
        if source_id not in macro.source_ids:
            raise ValueError(f"Source {source_id} not in macro '{macro_id}'")
        
        # Verificar que el motion_state existe
        if source_id not in self.motion_states:
            raise ValueError(f"Motion state for source {source_id} not found")
        
        motion = self.motion_states[source_id]
        
        # Crear el componente de trayectoria individual
        from .motion_components import IndividualTrajectory
        
        # Crear el componente sin parámetros (constructor vacío)
        trajectory = IndividualTrajectory()
        
        # Configurar usando los métodos/atributos disponibles
        trajectory.shape = shape
        trajectory.movement_mode = movement_mode
        trajectory.movement_speed = speed
        trajectory.enabled = True
        
        # Configurar parámetros de forma
        if shape_params is None:
            shape_params = {}
        
        # Aplicar parámetros según la forma
        if shape == "circle":
            trajectory.radius = shape_params.get('radius', 2.0)
        elif shape == "spiral":
            trajectory.scale = shape_params.get('scale', 1.0)
            trajectory.turns = shape_params.get('turns', 3)
        elif shape == "figure8":
            trajectory.scale = shape_params.get('scale', 1.0)
        elif shape == "lissajous":
            trajectory.freq_x = shape_params.get('freq_x', 2)
            trajectory.freq_y = shape_params.get('freq_y', 3)
            trajectory.scale = shape_params.get('scale', 1.0)
        
        # Si tiene método configure, usarlo
        if hasattr(trajectory, 'configure'):
            trajectory.configure(shape, shape_params, movement_mode)
        
        # Si tiene método set_shape, usarlo
        if hasattr(trajectory, 'set_shape'):
            trajectory.set_shape(shape, **shape_params)
        
        # Añadir a los componentes activos
        if hasattr(motion, 'active_components'):
            motion.active_components['individual_trajectory'] = trajectory
        else:
            motion.active_components = {'individual_trajectory': trajectory}
        
        print(f"✅ Trayectoria individual configurada para fuente {source_id} en macro '{macro_id}'")
        return True'''
    
    # Buscar y reemplazar el método
    method_start = content.find("def set_individual_trajectory")
    if method_start == -1:
        print("❌ No se encontró el método")
        return False
    
    # Encontrar el final del método
    next_method = re.search(r'\n    def \w+', content[method_start + 50:])
    if next_method:
        method_end = method_start + 50 + next_method.start()
    else:
        method_end = len(content)
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Reemplazar
    new_content = content[:method_start] + new_method + content[method_end:]
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Método corregido con API apropiada")
    return True

def create_minimal_test():
    """Test minimal para verificar la corrección"""
    
    test_code = '''# === test_individual_minimal.py ===
# Test minimal de trayectorias individuales

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60, enable_modulator=False)
print("✅ Engine creado")

# Crear macro
macro_name = engine.create_macro("test", source_count=2)
macro = engine._macros[macro_name]
sid = list(macro.source_ids)[0]
print(f"✅ Macro '{macro_name}' con fuente {sid}")

# Configurar trayectoria individual
try:
    engine.set_individual_trajectory(
        macro_name, 
        sid,
        shape="circle",
        shape_params={'radius': 3.0},
        movement_mode="fix",
        speed=1.0
    )
    print("✅ Trayectoria configurada")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Verificar componente
motion = engine.motion_states[sid]
if 'individual_trajectory' in motion.active_components:
    traj = motion.active_components['individual_trajectory']
    print(f"✅ Componente creado: {type(traj).__name__}")
    print(f"   - shape: {getattr(traj, 'shape', 'N/A')}")
    print(f"   - enabled: {getattr(traj, 'enabled', False)}")
    print(f"   - speed: {getattr(traj, 'movement_speed', 0)}")

# Test rápido de movimiento
initial_pos = engine._positions[sid].copy()
for _ in range(20):
    engine.update()

final_pos = engine._positions[sid]
distance = np.linalg.norm(final_pos - initial_pos)
print(f"\\n{'✅' if distance > 0.01 else '❌'} Distancia recorrida: {distance:.3f}")
'''
    
    with open("test_individual_minimal.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test minimal creado")

if __name__ == "__main__":
    print("🔧 FIX INDIVIDUAL TRAJECTORY CONSTRUCTOR")
    print("=" * 50)
    
    # Primero verificar la clase
    check_individual_trajectory_class()
    
    # Luego aplicar el fix
    if fix_set_individual_trajectory_v2():
        create_minimal_test()
        print("\n📝 Ejecuta:")
        print("1. python test_individual_minimal.py")
        print("2. Si funciona, python test_individual_trajectories.py")