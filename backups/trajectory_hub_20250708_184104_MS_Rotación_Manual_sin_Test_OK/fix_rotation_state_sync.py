# === fix_rotation_state_sync.py ===
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
        """Actualiza el estado aplicando la rotación manual"""
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
    pattern = r'(class ManualMacroRotation.*?)(def update\(self.*?return state)(.*?(?=def|class|\Z))'
    
    def replacer(match):
        return match.group(1) + new_update + match.group(3)
    
    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    # Guardar
    with open("trajectory_hub/core/motion_components.py", 'w') as f:
        f.write(new_content)
    
    print("✅ Método update actualizado")
    
    # También necesitamos asegurar que engine.update() sincronice estados
    print("\n🔧 Verificando sincronización en engine.update()...")
    
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
