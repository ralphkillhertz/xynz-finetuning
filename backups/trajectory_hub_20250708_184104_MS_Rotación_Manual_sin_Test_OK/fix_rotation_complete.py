# === fix_rotation_complete.py ===
# 🔧 Fix: Solución completa para rotación manual MS
# ⚡ Añade _sync_with_state y verifica el flujo
# 🎯 Impacto: CRÍTICO

import re
from datetime import datetime
import shutil
import numpy as np

def add_sync_method():
    """Añade el método _sync_with_state que falta"""
    print("🔧 Añadiendo _sync_with_state a ManualMacroRotation...")
    
    # Backup
    backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        content = f.read()
    
    # Buscar ManualMacroRotation
    class_match = re.search(r'(class ManualMacroRotation.*?)(def update\()', content, re.DOTALL)
    
    if class_match:
        class_part = class_match.group(1)
        update_part = class_match.group(2)
        
        # Añadir _sync_with_state antes de update
        sync_method = '''
    def _sync_with_state(self, state: 'MotionState'):
        """Sincroniza el componente con el estado actual"""
        # No hacer nada - la posición se lee directamente del state en calculate_delta
        pass
'''
        
        # Reemplazar
        new_content = content.replace(
            class_part + update_part,
            class_part + sync_method + '\n    ' + update_part
        )
        
        with open("trajectory_hub/core/motion_components.py", 'w') as f:
            f.write(new_content)
            
        print("✅ Método _sync_with_state añadido")
        return True
    else:
        print("❌ No se pudo encontrar la estructura de la clase")
        return False

def test_rotation_after_fix():
    """Test para verificar si la rotación funciona después del fix"""
    print("\n🎯 TEST: Verificando rotación después del fix")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Setup simple
    motion = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    engine.motion_states[0].position = [3.0, 0.0, 0.0]
    
    macro_name = engine.create_macro("test", source_count=1)
    
    # Desactivar otros componentes
    state = engine.motion_states[0]
    for name, comp in state.active_components.items():
        if hasattr(comp, 'enabled') and name != 'manual_macro_rotation':
            comp.enabled = False
    
    # Configurar rotación
    engine.set_manual_macro_rotation(macro_name, yaw=np.pi/2, interpolation_speed=1.0)
    
    print("📍 Posición inicial: [3.0, 0.0, 0.0]")
    print("🎯 Objetivo: rotar 90° (debería terminar cerca de [0.0, 3.0, 0.0])")
    print("\n⚙️ Ejecutando 60 frames (1 segundo)...")
    
    # Para debug detallado
    positions_history = []
    deltas_history = []
    
    for i in range(60):
        pos_before = engine._positions[0].copy()
        
        # Update
        engine.update()
        
        pos_after = engine._positions[0]
        delta = pos_after - pos_before
        
        positions_history.append(pos_after.copy())
        deltas_history.append(delta)
        
        # Mostrar cada 10 frames
        if i % 10 == 9:
            angle = np.degrees(np.arctan2(pos_after[1], pos_after[0]))
            distance = np.sqrt(pos_after[0]**2 + pos_after[1]**2)
            print(f"   Frame {i+1}: pos=[{pos_after[0]:.3f}, {pos_after[1]:.3f}] | ángulo={angle:.1f}° | dist={distance:.3f}")
    
    # Análisis final
    print("\n📊 Análisis de deltas:")
    
    # Ver si los deltas cambian
    unique_deltas = []
    for d in deltas_history:
        is_unique = True
        for ud in unique_deltas:
            if np.allclose(d, ud, atol=1e-6):
                is_unique = False
                break
        if is_unique:
            unique_deltas.append(d)
    
    print(f"   Deltas únicos encontrados: {len(unique_deltas)}")
    if len(unique_deltas) <= 3:
        print("   ❌ Deltas casi constantes - PROBLEMA PERSISTE")
        for i, d in enumerate(unique_deltas[:3]):
            print(f"      Delta {i+1}: [{d[0]:.6f}, {d[1]:.6f}, {d[2]:.6f}]")
    else:
        print("   ✅ Deltas varían correctamente")
    
    # Verificar resultado final
    final_pos = positions_history[-1]
    final_angle = np.degrees(np.arctan2(final_pos[1], final_pos[0]))
    final_distance = np.sqrt(final_pos[0]**2 + final_pos[1]**2)
    
    print(f"\n📊 Resultado final:")
    print(f"   Posición: [{final_pos[0]:.3f}, {final_pos[1]:.3f}, {final_pos[2]:.3f}]")
    print(f"   Ángulo: {final_angle:.1f}° (objetivo: 90°)")
    print(f"   Distancia: {final_distance:.3f} (debería ser ~3.0)")
    
    if abs(final_angle - 90) < 10 and abs(final_distance - 3.0) < 0.1:
        print("\n✅ ¡ROTACIÓN FUNCIONA CORRECTAMENTE!")
    else:
        print("\n❌ La rotación aún no funciona correctamente")

if __name__ == "__main__":
    if add_sync_method():
        print("\n⏳ Esperando un momento para que los cambios se carguen...")
        import time
        time.sleep(1)
        
        test_rotation_after_fix()
    else:
        print("\n❌ No se pudo aplicar el fix")