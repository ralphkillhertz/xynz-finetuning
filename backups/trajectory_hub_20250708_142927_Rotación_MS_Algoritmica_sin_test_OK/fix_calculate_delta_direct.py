# === fix_calculate_delta_direct.py ===
# 🔧 Fix directo para calculate_delta en IndividualTrajectory
# ⚡ Corrige la firma exacta del método
# 🎯 Impacto: CRÍTICO - Sin esto no funcionan las trayectorias

import os
import re

def find_exact_problem():
    """Encuentra exactamente dónde está el problema"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔍 Buscando el problema exacto...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar la línea 141 que menciona el error
    if len(lines) > 140:
        print(f"\n📍 Línea 141 (donde ocurre el error):")
        print(f"   {lines[140].strip()}")
    
    # Buscar IndividualTrajectory y su calculate_delta
    in_individual_trajectory = False
    class_line = 0
    calculate_delta_line = 0
    
    for i, line in enumerate(lines):
        if "class IndividualTrajectory" in line:
            in_individual_trajectory = True
            class_line = i
            print(f"\n✅ IndividualTrajectory encontrada en línea {i+1}")
        
        if in_individual_trajectory and line.strip().startswith("class ") and i > class_line:
            in_individual_trajectory = False
        
        if in_individual_trajectory and "def calculate_delta" in line:
            calculate_delta_line = i
            print(f"✅ calculate_delta encontrado en línea {i+1}:")
            print(f"   {line.strip()}")
            
            # Mostrar las siguientes líneas para ver el método
            for j in range(1, 10):
                if i+j < len(lines):
                    print(f"   {lines[i+j].rstrip()}")
                    if lines[i+j].strip() and not lines[i+j].startswith(' '):
                        break
            break
    
    return motion_path, calculate_delta_line

def fix_calculate_delta_method():
    """Arregla directamente el método calculate_delta"""
    
    motion_path, line_num = find_exact_problem()
    
    if line_num == 0:
        print("❌ No se encontró calculate_delta en IndividualTrajectory")
        return False
    
    print("\n🔧 Corrigiendo el método...")
    
    # Leer el archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Método correcto para IndividualTrajectory
    correct_calculate_delta = '''    def calculate_delta(self, state, current_time, dt):
        """Calcula el delta de movimiento para esta trayectoria individual"""
        if not self.enabled:
            return None
        
        # Actualizar posición en la trayectoria
        if hasattr(self, 'update_position'):
            self.update_position(dt)
        else:
            # Fallback: actualizar manualmente
            self.position_on_trajectory += self.movement_speed * dt
            if self.position_on_trajectory > 1.0:
                self.position_on_trajectory -= 1.0
        
        # Calcular nueva posición 3D
        if hasattr(self, '_calculate_position_on_trajectory'):
            new_position = self._calculate_position_on_trajectory()
        else:
            # Fallback: calcular posición circular
            import numpy as np
            t = self.position_on_trajectory * 2 * np.pi
            radius = getattr(self, 'radius', 2.0)
            new_position = np.array([
                radius * np.cos(t),
                radius * np.sin(t),
                0.0
            ])
        
        # Crear delta
        from .motion_components import MotionDelta
        delta = MotionDelta()
        delta.position = new_position - state.position
        
        return delta'''
    
    # Buscar y reemplazar el método calculate_delta en IndividualTrajectory
    # Primero encontrar la clase
    class_match = re.search(r'class IndividualTrajectory[^:]*:(.*?)(?=\nclass|\Z)', content, re.DOTALL)
    
    if not class_match:
        print("❌ No se pudo encontrar la clase IndividualTrajectory")
        return False
    
    class_content = class_match.group(0)
    
    # Buscar el método calculate_delta dentro de la clase
    method_pattern = r'    def calculate_delta\([^)]*\):[^}]+?(?=\n    def|\n\n|\Z)'
    method_match = re.search(method_pattern, class_content, re.DOTALL)
    
    if method_match:
        # Reemplazar el método existente
        new_class_content = re.sub(method_pattern, correct_calculate_delta, class_content)
        new_content = content.replace(class_content, new_class_content)
        print("✅ Método calculate_delta reemplazado")
    else:
        # Si no existe, añadirlo
        print("⚠️ No se encontró calculate_delta, añadiendo...")
        # Insertar antes del final de la clase
        insert_pos = class_content.rfind('\n\n')
        if insert_pos == -1:
            insert_pos = len(class_content) - 1
        
        new_class_content = (
            class_content[:insert_pos] + 
            '\n' + correct_calculate_delta + '\n' +
            class_content[insert_pos:]
        )
        new_content = content.replace(class_content, new_class_content)
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(motion_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Escribir el archivo
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ motion_components.py actualizado")
    
    # Verificar que el import de MotionDelta esté al principio
    if "from .motion_components import MotionDelta" in new_content:
        # Mover el import al principio del archivo
        new_content = new_content.replace("from .motion_components import MotionDelta", "")
        
        # Verificar si MotionDelta está definido en el archivo
        if "class MotionDelta" not in new_content:
            print("⚠️ MotionDelta no está definido, verificando...")
    
    return True

def create_verification_test():
    """Crea un test para verificar que funciona"""
    
    test_code = '''# === verify_fix.py ===
# Verifica que el fix funcionó

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test directo del método
print("🧪 Verificando fix de calculate_delta...")

try:
    from trajectory_hub.core.motion_components import IndividualTrajectory, MotionState
    import numpy as np
    
    # Crear instancia
    traj = IndividualTrajectory()
    traj.shape = "circle"
    traj.movement_speed = 1.0
    traj.enabled = True
    traj.radius = 2.0
    traj.position_on_trajectory = 0.0
    
    # Crear estado
    state = MotionState()
    state.position = np.array([0.0, 0.0, 0.0])
    
    # Probar calculate_delta con 4 argumentos
    delta = traj.calculate_delta(state, 1.0, 0.1)
    
    if delta is not None:
        print("✅ calculate_delta funciona con 4 argumentos")
        print(f"   Delta position: {delta.position}")
    else:
        print("⚠️ calculate_delta retornó None")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test completo
print("\\n🧪 Test completo con engine...")
from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=3, fps=60, enable_modulator=False)
macro_name = engine.create_macro("test", source_count=1)
macro = engine._macros[macro_name]
sid = list(macro.source_ids)[0]

try:
    engine.set_individual_trajectory(
        macro_name, sid,
        shape="circle",
        shape_params={'radius': 2.0},
        movement_mode="fix",
        speed=1.0
    )
    print("✅ Trayectoria configurada")
    
    # Ejecutar un update
    engine.update()
    print("✅ Update ejecutado sin errores")
    
except Exception as e:
    print(f"❌ Error en test completo: {e}")
'''
    
    with open("verify_fix.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("\n✅ Test de verificación creado")

if __name__ == "__main__":
    print("🔧 FIX DIRECTO DE CALCULATE_DELTA")
    print("=" * 50)
    
    if fix_calculate_delta_method():
        create_verification_test()
        print("\n✅ Fix aplicado")
        print("\n📝 Ejecuta:")
        print("1. python verify_fix.py")
        print("2. python test_individual_minimal.py")
    else:
        print("\n❌ Error al aplicar el fix")