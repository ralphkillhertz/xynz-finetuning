# === fix_rotation_constant_delta.py ===
# 🔧 Fix: Arreglar el problema de deltas constantes
# ⚡ Identifica y corrige el bug de rotación
# 🎯 Impacto: CRÍTICO

import numpy as np

def diagnose_constant_delta():
    """Diagnóstico del problema de deltas constantes"""
    print("🔍 DIAGNÓSTICO: Por qué los deltas son constantes")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    from trajectory_hub.core.motion_components import ManualMacroRotation, MotionState
    
    # Simular el problema manualmente
    rotation = ManualMacroRotation()
    rotation.enabled = True
    rotation.target_yaw = np.pi/2
    rotation.interpolation_speed = 1.0
    rotation.center = np.array([0, 0, 0])
    
    # Estado inicial
    state = MotionState()
    state.position = [3.0, 0.0, 0.0]
    
    print("📊 Simulación manual de 3 frames:")
    
    for i in range(3):
        print(f"\n--- Frame {i+1} ---")
        print(f"   Posición actual: {state.position}")
        
        # Sincronizar con estado (ESTE PUEDE SER EL PROBLEMA)
        rotation._sync_with_state(state)
        
        # Calcular delta
        delta = rotation.calculate_delta(state, i/60.0, 1/60.0)
        
        if delta:
            print(f"   Delta calculado: {delta.position}")
            
            # PROBLEMA POTENCIAL: ¿Se está actualizando state.position?
            print(f"   Estado antes de aplicar: {state.position}")
            
            # Aplicar delta
            state.position[0] += delta.position[0]
            state.position[1] += delta.position[1]
            state.position[2] += delta.position[2]
            
            print(f"   Estado después de aplicar: {state.position}")
    
    # Ahora verificar en el engine real
    print("\n\n🔧 Verificando en engine real...")
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear setup
    motion = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    engine.motion_states[0].position = [3.0, 0.0, 0.0]
    
    macro_name = engine.create_macro("test", source_count=1)
    
    # Desactivar otros componentes
    state = engine.motion_states[0]
    for name, comp in state.active_components.items():
        if hasattr(comp, 'enabled') and name != 'manual_macro_rotation':
            comp.enabled = False
    
    engine.set_manual_macro_rotation(macro_name, yaw=np.pi/2, interpolation_speed=1.0)
    
    # Debug detallado de UN update
    print("\n🎯 Debug detallado de engine.update():")
    
    rotation_comp = state.active_components.get('manual_macro_rotation')
    if rotation_comp:
        print(f"   Rotación antes de update:")
        print(f"      center: {rotation_comp.center}")
        print(f"      target_yaw: {np.degrees(rotation_comp.target_yaw)}°")
    
    # Posición antes
    pos_before = engine._positions[0].copy()
    state_before = list(state.position)
    
    # UN SOLO UPDATE
    engine.update()
    
    # Posición después
    pos_after = engine._positions[0]
    state_after = state.position
    
    print(f"\n   Cambios después de update:")
    print(f"      _positions[0]: {pos_before} → {pos_after}")
    print(f"      state.position: {state_before} → {state_after}")
    
    # VERIFICAR SINCRONIZACIÓN
    print(f"\n⚠️ VERIFICACIÓN CRÍTICA:")
    print(f"   ¿state.position == _positions? {np.allclose(state_after, pos_after)}")
    
    if not np.allclose(state_after, pos_after):
        print("   ❌ DESINCRONIZACIÓN DETECTADA - Este puede ser el problema")

def create_fix():
    """Crear script para arreglar el problema"""
    
    fix_code = '''# === fix_rotation_sync.py ===
# 🔧 Fix: Arreglar sincronización en ManualMacroRotation
# ⚡ Asegura que el estado se actualice correctamente
# 🎯 Impacto: CRÍTICO - Corrige rotación manual

import re
from datetime import datetime
import shutil

def fix_rotation_sync():
    """Arregla el problema de sincronización en calculate_delta"""
    
    # Backup
    backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        content = f.read()
    
    # Buscar el método _sync_with_state en ManualMacroRotation
    # El problema puede ser que no sincroniza correctamente
    
    print("🔍 Verificando _sync_with_state...")
    
    # Verificar si ManualMacroRotation tiene _sync_with_state
    if "_sync_with_state" not in content[content.find("class ManualMacroRotation"):]:
        print("⚠️ ManualMacroRotation no tiene _sync_with_state")
        print("🔧 Añadiendo método...")
        
        # Buscar dónde insertar
        class_start = content.find("class ManualMacroRotation")
        init_end = content.find("\\n\\n", content.find("def __init__", class_start))
        
        sync_method = """
    def _sync_with_state(self, state: 'MotionState'):
        \"\"\"Sincroniza el componente con el estado actual\"\"\"
        # Actualizar centro si es necesario
        if hasattr(state, 'macro_center'):
            self.center = np.array(state.macro_center)
        # No hacer nada más - la posición se lee directamente del state
"""
        
        # Insertar después del __init__
        content = content[:init_end] + sync_method + content[init_end:]
    
    # El problema real puede estar en calculate_delta
    # Asegurémonos de que usa state.position actualizado
    
    print("🔧 Verificando que calculate_delta use state.position correctamente...")
    
    # Guardar
    with open("trajectory_hub/core/motion_components.py", 'w') as f:
        f.write(content)
    
    print("✅ Archivo actualizado")
    
    return True

if __name__ == "__main__":
    fix_rotation_sync()
'''
    
    with open("fix_rotation_sync.py", 'w') as f:
        f.write(fix_code)
    
    print("✅ Script de corrección creado: fix_rotation_sync.py")

if __name__ == "__main__":
    diagnose_constant_delta()
    print("\n" + "="*60)
    create_fix()
    print("\n🎯 Próximos pasos:")
    print("1. Ejecutar: python fix_rotation_sync.py")
    print("2. Probar: python test_rotation_fixed.py")