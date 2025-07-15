# === fix_set_individual_trajectory.py ===
# 🔧 Fix: Arreglar el método set_individual_trajectory
# ⚡ Error: "Source X not found" - está buscando en lugar equivocado
# 🎯 Impacto: ALTO - Sin esto no hay trayectorias individuales

import os
import re

def fix_set_individual_trajectory():
    """Arregla el método para que funcione correctamente"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("🔍 Analizando set_individual_trajectory...")
    
    # Leer el archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método actual
    pattern = r'def set_individual_trajectory\(self[^)]*\):[^\n]*\n((?:    .*\n)*)'
    match = re.search(pattern, content)
    
    if not match:
        print("❌ No se encontró el método")
        return False
    
    print("✅ Método encontrado, analizando problema...")
    
    # Nuevo método corregido
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
        
        # Preparar parámetros
        if shape_params is None:
            shape_params = {}
        
        # Valores por defecto según la forma
        if shape == "circle" and "radius" not in shape_params:
            shape_params["radius"] = 2.0
        elif shape == "spiral" and "scale" not in shape_params:
            shape_params["scale"] = 1.0
        elif shape == "figure8" and "scale" not in shape_params:
            shape_params["scale"] = 1.0
        
        # Crear el componente
        trajectory = IndividualTrajectory(
            shape=shape,
            shape_params=shape_params,
            movement_mode=movement_mode
        )
        
        # Configurar velocidad
        trajectory.movement_speed = speed
        trajectory.enabled = True
        
        # Añadir a los componentes activos
        if hasattr(motion, 'active_components'):
            motion.active_components['individual_trajectory'] = trajectory
        else:
            # Si no tiene active_components, crear el diccionario
            motion.active_components = {'individual_trajectory': trajectory}
        
        print(f"✅ Trayectoria individual configurada para fuente {source_id} en macro '{macro_id}'")
        return True'''
    
    # Encontrar el método completo para reemplazarlo
    method_start = content.find("def set_individual_trajectory")
    if method_start == -1:
        print("❌ No se pudo encontrar el inicio del método")
        return False
    
    # Encontrar el siguiente método
    next_method_pattern = r'\n    def \w+'
    next_match = re.search(next_method_pattern, content[method_start + 50:])
    
    if next_match:
        method_end = method_start + 50 + next_match.start()
    else:
        # Si no hay siguiente método, buscar el final de la clase
        method_end = content.find("\n\nclass", method_start)
        if method_end == -1:
            method_end = len(content)
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Reemplazar el método
    new_content = (
        content[:method_start] + 
        new_method + 
        content[method_end:]
    )
    
    # Escribir el archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Método set_individual_trajectory corregido")
    
    return True

def create_test_individual():
    """Crea un test específico para trayectorias individuales"""
    
    test_code = '''# === test_individual_trajectories.py ===
# 🧪 Test específico para trayectorias individuales

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test_individual_trajectories():
    """Test de trayectorias individuales con el fix aplicado"""
    print("\\n🧪 TEST: Trayectorias Individuales")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=4)
    print(f"✅ Macro creado: '{macro_name}'")
    
    # Obtener source_ids
    macro = engine._macros[macro_name]
    source_ids = list(macro.source_ids)
    print(f"📍 Source IDs: {source_ids}")
    
    # Configurar diferentes trayectorias para cada fuente
    shapes = ["circle", "spiral", "figure8", "circle"]
    speeds = [1.0, 0.5, 2.0, 1.5]
    
    print("\\n🔧 Configurando trayectorias individuales:")
    for i, (sid, shape, speed) in enumerate(zip(source_ids, shapes, speeds)):
        try:
            engine.set_individual_trajectory(
                macro_name,
                sid,
                shape=shape,
                shape_params={'radius': 2.0} if shape == "circle" else {'scale': 1.0},
                movement_mode="fix",
                speed=speed
            )
            print(f"   ✅ Fuente {sid}: {shape} a velocidad {speed}")
        except Exception as e:
            print(f"   ❌ Error en fuente {sid}: {e}")
    
    # Verificar componentes
    print("\\n🔍 Verificando componentes activos:")
    for sid in source_ids:
        motion = engine.motion_states[sid]
        components = list(motion.active_components.keys())
        print(f"   Fuente {sid}: {components}")
        
        if 'individual_trajectory' in motion.active_components:
            traj = motion.active_components['individual_trajectory']
            print(f"      - Forma: {traj.shape}, Velocidad: {traj.movement_speed}")
    
    # Capturar posiciones iniciales
    initial_positions = {sid: engine._positions[sid].copy() for sid in source_ids}
    
    # Ejecutar simulación
    print("\\n🔄 Ejecutando 40 updates (4 segundos)...")
    for i in range(40):
        engine.update()
        time.sleep(0.025)
        
        if i % 10 == 0:
            # Mostrar progreso
            distances = []
            for sid in source_ids:
                dist = np.linalg.norm(engine._positions[sid] - initial_positions[sid])
                distances.append(dist)
            print(f"   Update {i}: distancias = {[f'{d:.2f}' for d in distances]}")
    
    # Resultados finales
    print("\\n📊 RESULTADOS FINALES:")
    print("-" * 40)
    
    all_moved = True
    for sid, shape, speed in zip(source_ids, shapes, speeds):
        current_pos = engine._positions[sid]
        initial_pos = initial_positions[sid]
        distance = np.linalg.norm(current_pos - initial_pos)
        moved = distance > 0.01
        
        print(f"Fuente {sid} ({shape}, v={speed}):")
        print(f"  Distancia recorrida: {distance:.3f} {'✅' if moved else '❌'}")
        
        if not moved:
            all_moved = False
    
    print("\\n" + "=" * 60)
    if all_moved:
        print("✅ ¡ÉXITO! Todas las trayectorias individuales funcionan")
        print("\\n🎯 Características verificadas:")
        print("   - Diferentes formas (circle, spiral, figure8)")
        print("   - Diferentes velocidades")
        print("   - Movimiento independiente por fuente")
    else:
        print("❌ Algunas trayectorias no se movieron")
    
    return all_moved

if __name__ == "__main__":
    test_individual_trajectories()
'''
    
    with open("test_individual_trajectories.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test creado: test_individual_trajectories.py")

if __name__ == "__main__":
    print("🔧 FIX SET_INDIVIDUAL_TRAJECTORY")
    print("=" * 50)
    
    if fix_set_individual_trajectory():
        create_test_individual()
        print("\n✅ Fix aplicado exitosamente")
        print("\n📝 Próximos pasos:")
        print("1. python test_individual_trajectories.py")
        print("2. Si funciona, usar el controlador interactivo")
        print("3. ¡Celebrar! 🎉")
    else:
        print("\n❌ Error al aplicar el fix")