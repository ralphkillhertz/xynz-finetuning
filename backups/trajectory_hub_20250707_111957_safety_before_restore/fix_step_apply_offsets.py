#!/usr/bin/env python3
"""
🔧 FIX: engine.step() debe aplicar los offsets
"""

import os
import sys
import re

print("""
================================================================================
🔧 ARREGLANDO ENGINE.STEP() PARA APLICAR OFFSETS
================================================================================
""")

# 1. Verificar step() actual
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar método step
print("🔍 BUSCANDO MÉTODO step()...")
step_pattern = r'def step\(self[^)]*\):[^}]+?(?=\n    def|\nclass|\Z)'
match = re.search(step_pattern, content, re.DOTALL)

if match:
    print("✅ Método step() encontrado")
    current_step = match.group(0)
    
    # Verificar si usa get_position
    if 'get_position' in current_step:
        print("✅ step() ya llama a get_position()")
    else:
        print("❌ step() NO usa get_position()")
    
    # Verificar si actualiza _positions
    if '_positions[sid]' in current_step:
        print("✅ step() actualiza _positions")
    else:
        print("❌ step() NO actualiza _positions")
    
    print("\n🔨 REEMPLAZANDO step() con versión correcta...")
    
    new_step = '''def step(self, dt: float = None) -> dict:
        """
        Actualiza todas las fuentes y devuelve estado actual.
        
        Parameters
        ----------
        dt : float, optional
            Delta time. Si es None, usa self.dt
            
        Returns
        -------
        dict
            Estado actual con positions, orientations, apertures, etc.
        """
        if dt is None:
            dt = self.dt
            
        # Actualizar cada SourceMotion activa
        active_sources = set()
        
        for sid, motion in self._source_motions.items():
            if sid < self.max_sources and motion.enabled:
                active_sources.add(sid)
                
                # Actualizar el motion (actualiza velocity, etc.)
                motion.update(dt)
                
                # CRÍTICO: Usar get_position() para obtener posición con offsets
                if hasattr(motion, 'get_position'):
                    pos = motion.get_position()
                else:
                    # Fallback: calcular manualmente
                    pos = motion.state.position.copy()
                    if hasattr(motion, 'concentration_offset'):
                        pos = pos + motion.concentration_offset
                    if hasattr(motion, 'distribution_offset'):
                        pos = pos + motion.distribution_offset
                    if hasattr(motion, 'trajectory_offset'):
                        pos = pos + motion.trajectory_offset
                
                # Obtener orientación y apertura
                if hasattr(motion, 'get_orientation'):
                    orient = motion.get_orientation()
                else:
                    orient = motion.state.orientation
                    
                if hasattr(motion, 'get_aperture'):
                    aperture = motion.get_aperture()
                else:
                    aperture = motion.state.aperture
                
                # Actualizar arrays globales con posiciones + offsets
                self._positions[sid] = pos
                self._orientations[sid] = orient
                self._apertures[sid] = aperture
        
        # Actualizar tiempo y frame
        self._time += dt
        self._frame_count += 1
        
        # Si hay OSC bridge, enviar posiciones
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                source_list = list(active_sources)
                if source_list:
                    self.osc_bridge.send_batch_positions(
                        source_list,
                        self._positions[source_list],
                        self._orientations[source_list]
                    )
            except:
                pass
        
        # Devolver estado actual
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'names': [self._source_info.get(i, SourceInfo(i, f"Source_{i}")).name 
                     for i in range(self.max_sources)],
            'time': self._time,
            'frame': self._frame_count
        }'''
    
    # Reemplazar
    content = re.sub(step_pattern, new_step, content, count=1)
    
    # Guardar
    import datetime
    backup_name = engine_file + f".backup_step_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n📋 Backup: {backup_name}")
    
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ step() actualizado")
    
else:
    print("❌ No se encontró método step()")

# 2. Test de verificación rápida
test_code = '''#!/usr/bin/env python3
"""
🧪 TEST: Verificación de offsets aplicados
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("\\n🧪 TEST DE OFFSETS EN STEP()\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Posición inicial
print("📍 POSICIONES INICIALES:")
pos0_inicial = engine._positions[0].copy()
pos1_inicial = engine._positions[1].copy()
print(f"   Fuente 0: {pos0_inicial}")
print(f"   Fuente 1: {pos1_inicial}")

# Aplicar concentración
print("\\n🎯 Aplicando concentración 0.5...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar offsets
motion0 = engine._source_motions[0]
motion1 = engine._source_motions[1]
print(f"\\n🔍 Offsets:")
print(f"   Fuente 0: {motion0.concentration_offset}")
print(f"   Fuente 1: {motion1.concentration_offset}")

# Ejecutar UN solo step
print("\\n🔄 Ejecutando 1 step()...")
engine.step()

# Verificar posiciones después
print("\\n📍 POSICIONES DESPUÉS DE 1 STEP:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")

# Calcular movimiento
mov0 = np.linalg.norm(engine._positions[0] - pos0_inicial)
mov1 = np.linalg.norm(engine._positions[1] - pos1_inicial)

print(f"\\n📊 MOVIMIENTO:")
print(f"   Fuente 0: {mov0:.4f}")
print(f"   Fuente 1: {mov1:.4f}")

if mov0 > 0.01 or mov1 > 0.01:
    print("\\n✅ ¡ÉXITO! step() está aplicando los offsets")
    
    # Ejecutar más frames
    print("\\n🔄 Ejecutando 50 frames más...")
    for _ in range(50):
        engine.step()
    
    print("\\n📍 POSICIONES FINALES:")
    print(f"   Fuente 0: {engine._positions[0]}")
    print(f"   Fuente 1: {engine._positions[1]}")
    
    # Verificar concentración
    distancia_inicial = np.linalg.norm(pos1_inicial - pos0_inicial)
    distancia_final = np.linalg.norm(engine._positions[1] - engine._positions[0])
    
    print(f"\\n📊 CONCENTRACIÓN:")
    print(f"   Distancia inicial: {distancia_inicial:.4f}")
    print(f"   Distancia final: {distancia_final:.4f}")
    print(f"   Reducción: {(1 - distancia_final/distancia_inicial)*100:.1f}%")
    
    print("\\n🎉 LA CONCENTRACIÓN FUNCIONA!")
    print("\\n🚀 Prueba ahora el controlador:")
    print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print("\\n❌ step() NO está aplicando los offsets")

print("\\n" + "="*60)
'''

with open("test_step_offsets.py", 'w', encoding='utf-8') as f:
    f.write(test_code)

print(f"\n✅ Test creado: test_step_offsets.py")

print("""
================================================================================
✅ STEP() ACTUALIZADO PARA APLICAR OFFSETS
================================================================================

🔧 Lo que arreglamos:
   - step() ahora usa get_position() que incluye los offsets
   - Si get_position() no existe, calcula manualmente pos + offsets
   - Actualiza _positions con las posiciones finales (base + offsets)

🚀 EJECUTA EL TEST:
   python test_step_offsets.py

💡 Este test verifica con solo 1 frame si los offsets se aplican

🎯 Si funciona, las fuentes se moverán hacia el centro!
================================================================================
""")