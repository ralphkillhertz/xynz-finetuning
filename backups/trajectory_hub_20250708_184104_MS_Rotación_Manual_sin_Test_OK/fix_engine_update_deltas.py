# === fix_engine_update_deltas.py ===
# 🔧 Fix: engine.update() no aplica deltas de rotación
# ⚡ Solución definitiva al delta mismatch

import os
import re
from datetime import datetime

def fix_engine_update():
    """Arregla el método update() para que aplique TODOS los deltas"""
    
    print("🔧 FIX: engine.update() no aplica deltas")
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
    
    # Buscar el método update()
    print("\n🔍 Buscando método update()...")
    
    # Patrón para encontrar el método update completo
    update_pattern = r'(def update\(self[^:]*\):\s*\n(?:.*\n)*?)(\s*)(# Enviar actualizaciones OSC|$)'
    
    match = re.search(update_pattern, content, re.MULTILINE)
    
    if not match:
        print("❌ No se encontró el método update()")
        return False
    
    print("✅ Método update() encontrado")
    
    # Nuevo código del método update
    new_update = '''def update(self):
        """Actualiza el sistema completo"""
        if not self.running:
            return
        
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
    
    # Reemplazar el método update
    content_new = re.sub(update_pattern, new_update + r'\n\2\3', content)
    
    # Agregar import de time si no existe
    if 'import time' not in content_new:
        content_new = re.sub(r'(import.*?\n)', r'\1import time\n', content_new, count=1)
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_new)
    
    print("\n✅ Método update() corregido:")
    print("   - Sincroniza estados antes de calcular deltas")
    print("   - Aplica TODOS los deltas a las posiciones")
    print("   - Actualiza estados después de aplicar deltas")
    print("   - Mantiene compatibilidad con componentes sin deltas")
    
    # Crear test de verificación
    print("\n📝 Creando test de verificación...")
    
    test_content = '''# === test_rotation_fixed.py ===
# Test para verificar que las rotaciones funcionan

import sys
import os
import numpy as np
import math

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)

# Crear macro
engine.create_macro("test", 4, formation="square")
macro_name = list(engine._macros.keys())[0]

# Posiciones iniciales
positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
macro = engine._macros[macro_name]

for i, (sid, pos) in enumerate(zip(macro.source_ids, positions)):
    engine._positions[sid] = np.array(pos, dtype=np.float32)

# Configurar rotación
engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, pitch=0, roll=0, interpolation_speed=0.1)

# Guardar posiciones iniciales
pos_before = {sid: engine._positions[sid].copy() for sid in macro.source_ids}

# Update
engine.update()

# Verificar cambios
print("🎯 TEST DE ROTACIÓN:")
print("-" * 40)
any_change = False
for sid in macro.source_ids:
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = np.linalg.norm(after - before)
    
    if diff > 0.0001:
        print(f"Fuente {sid}: {before} → {after} ✅")
        any_change = True
    else:
        print(f"Fuente {sid}: Sin cambios ❌")

if any_change:
    print("\\n✅ ¡ROTACIÓN FUNCIONA!")
else:
    print("\\n❌ Rotación sigue sin funcionar")
'''
    
    with open("test_rotation_fixed.py", "w") as f:
        f.write(test_content)
    
    print("✅ Test creado: test_rotation_fixed.py")
    
    print("\n🎯 FIX COMPLETADO")
    print("=" * 60)
    print("Ejecuta: python test_rotation_fixed.py")
    
    return True

if __name__ == "__main__":
    fix_engine_update()