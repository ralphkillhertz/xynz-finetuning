# === debug_calculate_delta_issue.py ===
# 🔍 Debug: Por qué calculate_delta retorna siempre lo mismo
# ⚡ Investiga el flujo de datos en detalle
# 🎯 Impacto: IDENTIFICAR BUG REAL

import numpy as np

def debug_calculate_delta():
    """Debug profundo del método calculate_delta"""
    print("🔍 DEBUG PROFUNDO: calculate_delta")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    from trajectory_hub.core.motion_components import ManualMacroRotation, MotionState
    
    # Crear un test manual primero
    print("1️⃣ TEST MANUAL de calculate_delta:")
    
    rotation = ManualMacroRotation()
    rotation.enabled = True
    rotation.target_yaw = np.pi/2
    rotation.interpolation_speed = 1.0
    rotation.center = np.array([0, 0, 0])
    
    # Simular 3 llamadas con estado CAMBIANTE
    positions = [[3.0, 0.0, 0.0], [3.0, 0.1, 0.0], [3.0, 0.2, 0.0]]
    
    for i, pos in enumerate(positions):
        state = MotionState()
        state.position = list(pos)
        
        delta = rotation.calculate_delta(state, i/60.0, 1/60.0)
        
        print(f"\n   Llamada {i+1}:")
        print(f"      state.position: {state.position}")
        print(f"      delta: {delta.position if delta else 'None'}")
    
    # Ahora en el engine
    print("\n\n2️⃣ DEBUG EN ENGINE:")
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Setup
    motion = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    engine.motion_states[0].position = [3.0, 0.0, 0.0]
    
    macro_name = engine.create_macro("test", source_count=1)
    
    # Desactivar otros
    state = engine.motion_states[0]
    for name, comp in state.active_components.items():
        if hasattr(comp, 'enabled') and name != 'manual_macro_rotation':
            comp.enabled = False
    
    engine.set_manual_macro_rotation(macro_name, yaw=np.pi/2, interpolation_speed=1.0)
    
    # Obtener el componente
    rotation_comp = state.active_components['manual_macro_rotation']
    
    print("\n🎯 Ejecutando 3 updates con debug detallado:")
    
    for i in range(3):
        print(f"\n--- Update {i+1} ---")
        
        # Estado ANTES
        print(f"   ANTES:")
        print(f"      engine._positions[0]: {engine._positions[0]}")
        print(f"      state.position: {state.position}")
        
        # Calcular delta manualmente ANTES del update
        manual_delta = rotation_comp.calculate_delta(state, i/60.0, 1/60.0)
        print(f"      Delta manual: {manual_delta.position if manual_delta else 'None'}")
        
        # Update
        engine.update()
        
        # Estado DESPUÉS
        print(f"   DESPUÉS:")
        print(f"      engine._positions[0]: {engine._positions[0]}")
        print(f"      state.position: {state.position}")
        
        # VERIFICACIÓN CRÍTICA
        if not np.array_equal(engine._positions[0], state.position):
            print("      ⚠️ DESINCRONIZACIÓN: _positions != state.position")
    
    # Verificar el código de update
    print("\n\n3️⃣ VERIFICANDO EL FLUJO DE UPDATE:")
    
    # El problema puede estar en cómo engine.update() maneja los estados
    print("   Posibles problemas:")
    print("   - state.position no se actualiza antes de calculate_delta")
    print("   - calculate_delta usa una copia vieja del estado")
    print("   - El update de SourceMotion no sincroniza correctamente")
    
    # Crear un fix específico
    print("\n4️⃣ SOLUCIÓN PROPUESTA:")
    print("   El problema es que calculate_delta siempre ve la posición [3,0,0]")
    print("   Necesitamos asegurar que state.position se actualice ANTES de calculate_delta")

def create_definitive_fix():
    """Crea el fix definitivo"""
    
    fix_code = '''# === fix_rotation_state_sync.py ===
# 🔧 Fix: Sincronizar estado antes de calculate_delta
# ⚡ Asegura que el estado tenga la posición actualizada
# 🎯 Impacto: CRÍTICO

import re
from datetime import datetime
import shutil

def fix_state_sync():
    """Arregla la sincronización del estado en ManualMacroRotation"""
    
    # Backup
    backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        content = f.read()
    
    # Buscar el método update en ManualMacroRotation
    print("🔧 Actualizando método update en ManualMacroRotation...")
    
    # El nuevo método update que sincroniza correctamente
    new_update = """    def update(self, current_time: float, dt: float, state: 'MotionState') -> 'MotionState':
        \"\"\"Actualiza el estado aplicando la rotación manual\"\"\"
        if not self.enabled:
            return state
            
        # CRÍTICO: Sincronizar la posición actual del estado
        # Esto asegura que calculate_delta vea la posición actualizada
        if hasattr(state, 'position'):
            # Forzar que sea una lista mutable
            if isinstance(state.position, (tuple, np.ndarray)):
                state.position = list(state.position)
        
        # Sincronizar con estado
        self._sync_with_state(state)
        
        # Calcular delta con el estado actualizado
        delta = self.calculate_delta(state, current_time, dt)
        
        if delta and delta.position is not None:
            # Aplicar el delta al estado
            state.position = [
                state.position[0] + delta.position[0],
                state.position[1] + delta.position[1],
                state.position[2] + delta.position[2]
            ]
            
        return state"""
    
    # Buscar y reemplazar el método update existente
    pattern = r'(class ManualMacroRotation.*?)(def update\\(self.*?return state)(.*?(?=def|class|\\Z))'
    
    def replacer(match):
        return match.group(1) + new_update + match.group(3)
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    # Guardar
    with open("trajectory_hub/core/motion_components.py", 'w') as f:
        f.write(new_content)
    
    print("✅ Método update actualizado")
    
    # También necesitamos asegurar que engine.update() sincronice estados
    print("\\n🔧 Verificando sincronización en engine.update()...")
    
    with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
        engine_content = f.read()
    
    # Buscar el método update del engine
    if "motion.update(" in engine_content:
        print("✅ engine.update() llama a motion.update()")
    else:
        print("⚠️ engine.update() puede no estar llamando a motion.update()")
    
    return True

if __name__ == "__main__":
    fix_state_sync()
'''
    
    with open("fix_rotation_state_sync.py", 'w') as f:
        f.write(fix_code)
    
    print("\n✅ Script de fix creado: fix_rotation_state_sync.py")

if __name__ == "__main__":
    debug_calculate_delta()
    create_definitive_fix()
    print("\n🎯 Ejecutar:")
    print("1. python fix_rotation_state_sync.py")
    print("2. python test_rotation_final.py")