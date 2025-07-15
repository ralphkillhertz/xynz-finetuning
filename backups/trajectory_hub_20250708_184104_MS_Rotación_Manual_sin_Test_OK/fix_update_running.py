# === fix_update_running.py ===
# 🔧 Fix: Atributo 'running' no existe
# ⚡ Ajustar update() a la estructura real

import os
import re
from datetime import datetime

def fix_update_method():
    """Corrige el método update() para usar la estructura correcta"""
    
    print("🔧 FIX: Atributo 'running' no existe")
    print("=" * 60)
    
    # Ruta del archivo
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra {file_path}")
        return False
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar y reemplazar el método update
    print("\n🔍 Corrigiendo método update()...")
    
    # Nuevo método update sin 'running'
    new_update = '''def update(self):
        """Actualiza el sistema completo"""
        current_time = time.time()
        dt = 1.0 / self.fps
        
        # Actualizar estados de movimiento con sistema de deltas
        for source_id, motion in self.motion_states.items():
            if source_id >= self._active_sources:
                continue
                
            # IMPORTANTE: Sincronizar estado con posición actual
            motion.state.position = self._positions[source_id].copy()
            
            # Obtener deltas de TODOS los componentes activos
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                
                # Aplicar cada delta a la posición
                if deltas:
                    for delta in deltas:
                        if delta and delta.position is not None:
                            self._positions[source_id] += delta.position
                            
                            # Actualizar estado después del cambio
                            motion.state.position = self._positions[source_id].copy()
            
            # Actualizar el motion (para componentes sin deltas)
            if hasattr(motion, 'update'):
                motion.update(current_time, dt)
        
        # Actualizar moduladores de orientación si están habilitados
        if self.enable_modulator:
            for source_id, state in self.motion_states.items():
                if source_id in self.orientation_modulators:
                    modulator = self.orientation_modulators[source_id]
                    if modulator.enabled:
                        # Actualizar estado con modulación
                        state = modulator.update(current_time, dt, state)
                        self.motion_states[source_id] = state
        
        # Incrementar contador de frames y tiempo
        self._frame_count += 1
        self._time += dt
        
        # Enviar actualizaciones OSC con rate limiting
        self._send_osc_update()'''
    
    # Buscar el método update actual
    update_pattern = r'def update\(self\):\s*\n(?:.*\n)*?(?=\n    def |\n\S|\Z)'
    
    # Reemplazar
    if 'def update(self):' in content:
        content = re.sub(update_pattern, new_update, content, flags=re.MULTILINE | re.DOTALL)
        print("✅ Método update() reemplazado")
    else:
        print("❌ No se encontró el método update()")
        return False
    
    # Escribir el archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Cambios aplicados:")
    print("   - Eliminada verificación de 'running'")
    print("   - Mantenida lógica de deltas")
    print("   - Compatible con estructura actual")
    
    # Test simple inline
    print("\n🎯 TEST RÁPIDO:")
    test_code = '''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math

# Test rápido
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
engine.create_macro("test", 2)
macro_name = list(engine._macros.keys())[0]
macro = engine._macros[macro_name]

# Posiciones
engine._positions[0] = np.array([3.0, 0.0, 0.0])
engine._positions[1] = np.array([0.0, 3.0, 0.0])

# Rotación
engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, pitch=0, roll=0, interpolation_speed=0.1)

# Update
pos_before = engine._positions[0].copy()
engine.update()
pos_after = engine._positions[0].copy()

# Verificar
diff = np.linalg.norm(pos_after - pos_before)
if diff > 0.0001:
    print(f"✅ ¡FUNCIONA! Movimiento: {diff:.6f}")
    print(f"   {pos_before} → {pos_after}")
else:
    print("❌ Sin movimiento")
'''
    
    print("Ejecutando test...")
    exec(test_code)
    
    return True

if __name__ == "__main__":
    fix_update_method()