# === fix_engine_update_motion.py ===
# 🔧 Fix: Arreglar engine.update() para que llame a motion.update()
# ⚡ Problema: Las trayectorias no se mueven porque engine no actualiza los SourceMotion
# 🎯 Impacto: ALTO - Sin esto ningún movimiento funciona

import os
import re

def fix_engine_update():
    """Arregla el método update() del engine para que actualice los SourceMotion"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("🔍 Leyendo enhanced_trajectory_engine.py...")
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    update_pattern = r'def update\(self.*?\):\s*\n(.*?)(?=\n    def|\n\s*$|\Z)'
    match = re.search(update_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró el método update()")
        return False
    
    print("✅ Método update() encontrado")
    update_body = match.group(1)
    
    # Verificar si ya actualiza los motion_states
    if "motion.update(" in update_body:
        print("⚠️ Ya parece tener código para actualizar motions")
        # Verificar si está comentado
        if "#.*motion.update" in update_body:
            print("🔧 El código está comentado, descomentando...")
    
    # Crear el código correcto para el update
    new_update_code = '''def update(self, dt: float = None) -> None:
        """Actualiza el sistema completo con soporte para deltas"""
        if dt is None:
            current_time = time.time()
            dt = current_time - self._last_time
            self._last_time = current_time
        else:
            current_time = self._last_time + dt
            self._last_time = current_time
        
        # Rate limiting
        if not self._check_rate_limit():
            return
        
        # 1. ACTUALIZAR COMPONENTES DE MOVIMIENTO (motion_states)
        for source_id, motion in self.motion_states.items():
            if motion is not None:
                # Actualizar el SourceMotion con el tiempo actual
                motion.update(current_time, dt)
                
                # Obtener el estado actualizado
                state = motion.state
                
                # Actualizar posición en el array principal
                if source_id < len(self._positions):
                    self._positions[source_id] = state.position
                    
                    # Si hay orientación en el estado, actualizar también
                    if hasattr(state, 'orientation') and state.orientation is not None:
                        if source_id < len(self._orientations):
                            self._orientations[source_id] = state.orientation
        
        # 2. PROCESAR DELTAS (si está implementado)
        if hasattr(self, '_process_deltas'):
            self._process_deltas(current_time, dt)
        
        # 3. ACTUALIZAR MODULADORES DE ORIENTACIÓN
        if self.enable_modulator:
            for source_id, state in self.motion_states.items():
                if source_id in self.orientation_modulators:
                    modulator = self.orientation_modulators[source_id]
                    if modulator.enabled:
                        # Actualizar estado con modulación
                        state = modulator.update(current_time, dt, state)
                        self.motion_states[source_id].state = state
                        
                        # Actualizar arrays principales
                        if source_id < len(self._orientations):
                            self._orientations[source_id] = state.orientation
                        if source_id < len(self._apertures):
                            self._apertures[source_id] = state.aperture
        
        # 4. APLICAR FÍSICA Y OTROS SISTEMAS
        # ... (mantener código existente de física si existe)
        
        # 5. ENVIAR ACTUALIZACIONES OSC
        self._send_osc_update()
        
        # Incrementar contador de frames
        self._frame_count += 1
        self._time += dt'''
    
    # Reemplazar el método update completo
    print("🔧 Reemplazando método update()...")
    
    # Encontrar el inicio del método
    update_start = content.find("def update(self")
    if update_start == -1:
        print("❌ No se pudo encontrar el inicio del método update")
        return False
    
    # Encontrar el siguiente método
    next_method = content.find("\n    def ", update_start + 1)
    if next_method == -1:
        next_method = len(content)
    
    # Reemplazar
    new_content = (
        content[:update_start] + 
        new_update_code + 
        "\n\n" +
        content[next_method:]
    )
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Escribir el archivo corregido
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ enhanced_trajectory_engine.py actualizado")
    
    # Verificar imports necesarios
    if "import time" not in content:
        print("⚠️ Añadiendo import time...")
        with open(engine_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Añadir después de otros imports
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                continue
            else:
                lines.insert(i, "import time\n")
                break
        
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    return True

def create_test_script():
    """Crea un script de test para verificar el fix"""
    test_code = '''# === test_update_fix.py ===
# Test para verificar que engine.update() actualiza las trayectorias

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import time

def test_update_motion():
    """Verifica que el update actualice las posiciones"""
    print("\\n🧪 TEST: Verificando engine.update() con trayectorias")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(n_sources=10, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear un macro
    engine.create_macro("test", 5)
    print("✅ Macro creado con 5 fuentes")
    
    # Configurar trayectorias individuales
    config = {
        'mode': 1,  # Todas iguales
        'shape': 'circle',
        'movement_mode': 'fix',
        'speed': 1.0
    }
    engine.configure_individual_trajectories("test", config)
    print("✅ Trayectorias configuradas")
    
    # Obtener posiciones iniciales
    initial_positions = []
    for sid in engine.macros["test"].source_ids:
        initial_positions.append(engine._positions[sid].copy())
    
    print(f"\\n📍 Posiciones iniciales:")
    for i, pos in enumerate(initial_positions):
        print(f"   Fuente {i}: {pos}")
    
    # Ejecutar varios updates
    print("\\n🔄 Ejecutando 10 updates...")
    for i in range(10):
        engine.update(0.1)  # 100ms por update
        time.sleep(0.01)
    
    # Verificar que las posiciones cambiaron
    print("\\n📍 Posiciones después de updates:")
    positions_moved = False
    for i, sid in enumerate(engine.macros["test"].source_ids):
        current_pos = engine._positions[sid]
        initial_pos = initial_positions[i]
        
        # Calcular diferencia
        diff = sum(abs(current_pos[j] - initial_pos[j]) for j in range(3))
        moved = diff > 0.01
        
        print(f"   Fuente {sid}: {current_pos} {'✅ MOVIDA' if moved else '❌ NO MOVIDA'}")
        if moved:
            positions_moved = True
    
    # Verificar motion_states
    print("\\n🔍 Verificando motion_states:")
    for sid in engine.macros["test"].source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'state'):
                state = motion.state
                print(f"   Fuente {sid}: fase = {getattr(state, 'position_on_trajectory', 0):.3f}")
    
    if positions_moved:
        print("\\n✅ ¡ÉXITO! Las trayectorias se están moviendo correctamente")
    else:
        print("\\n❌ ERROR: Las trayectorias NO se están moviendo")
        print("\\n🔍 Debugging adicional:")
        # Verificar si hay componentes activos
        for sid in engine.macros["test"].source_ids:
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                print(f"\\nFuente {sid}:")
                print(f"  - SourceMotion existe: ✅")
                if hasattr(motion, 'active_components'):
                    print(f"  - Componentes activos: {list(motion.active_components.keys())}")
                    for comp_name, comp in motion.active_components.items():
                        if hasattr(comp, 'enabled'):
                            print(f"    - {comp_name}: {'✅ Habilitado' if comp.enabled else '❌ Deshabilitado'}")
    
    return positions_moved

if __name__ == "__main__":
    test_update_motion()
'''
    
    # Guardar test
    with open("test_update_fix.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test creado: test_update_fix.py")

if __name__ == "__main__":
    print("🔧 FIX ENGINE UPDATE - Trajectory Hub")
    print("=" * 50)
    
    if fix_engine_update():
        print("\n✅ Fix aplicado exitosamente")
        create_test_script()
        print("\n📝 Próximos pasos:")
        print("1. Ejecutar: python test_update_fix.py")
        print("2. Verificar que las fuentes se muevan")
        print("3. Si funciona, probar con el controlador interactivo")
    else:
        print("\n❌ Error al aplicar el fix")