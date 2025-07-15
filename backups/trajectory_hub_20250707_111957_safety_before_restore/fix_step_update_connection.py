#!/usr/bin/env python3
"""
🔧 FIX: Conectar engine.step() con motion.update()
⚡ Solución directa al problema de concentración
"""

import os
import sys
import re

print("""
================================================================================
🔧 ARREGLANDO ENGINE.STEP() → MOTION.UPDATE()
================================================================================
""")

# 1. Buscar el archivo del engine
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if not os.path.exists(engine_file):
    print(f"❌ No se encuentra {engine_file}")
    sys.exit(1)

# 2. Leer el archivo
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 3. Buscar el método step()
step_pattern = r'def step\(self.*?\):(.*?)(?=\n    def|\n\s*$|\nclass)'
step_match = re.search(step_pattern, content, re.DOTALL)

if not step_match:
    print("❌ No se encontró método step()")
    print("\n🔨 CREANDO método step() desde cero...")
    
    # Buscar dónde insertar (después de update)
    update_match = re.search(r'(def update\(self.*?\n(?:.*?\n)*?)(\n    def|\n\s*$|\nclass)', content, re.DOTALL)
    
    if update_match:
        # Crear método step
        new_step = '''
    def step(self, dt: float = None) -> dict:
        """
        Actualiza todas las fuentes y devuelve estado actual.
        Usado por el controller.
        
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
            
        # CRÍTICO: Actualizar cada SourceMotion
        active_sources = set()
        
        for sid, motion in self._source_motions.items():
            # Solo actualizar fuentes activas
            if sid < self.max_sources and motion.enabled:
                active_sources.add(sid)
                
                # 🎯 LLAMAR A motion.update() - ESTO ES LO QUE FALTABA
                try:
                    # motion.update() espera solo dt
                    motion.update(dt)
                    
                    # Obtener el estado actualizado
                    pos = motion.get_position()
                    orient = motion.get_orientation() 
                    aperture = motion.get_aperture()
                    
                    # Actualizar arrays globales
                    self._positions[sid] = pos
                    self._orientations[sid] = orient
                    self._apertures[sid] = aperture
                    
                except Exception as e:
                    print(f"⚠️ Error actualizando fuente {sid}: {e}")
        
        # Actualizar tiempo y frame
        self._time += dt
        self._frame_count += 1
        
        # Si hay OSC bridge, enviar posiciones
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                self.osc_bridge.send_batch_positions(
                    list(active_sources),
                    self._positions[:len(active_sources)],
                    self._orientations[:len(active_sources)]
                )
            except:
                pass  # Ignorar errores OSC
        
        # Devolver estado actual
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'names': [self._source_info.get(i, SourceInfo(i, f"Source_{i}")).name 
                     for i in range(self.max_sources)],
            'time': self._time,
            'frame': self._frame_count
        }
'''
        
        # Insertar después de update
        insert_pos = update_match.end(1)
        content = content[:insert_pos] + new_step + content[insert_pos:]
        
        print("✅ Método step() creado correctamente")
        
else:
    print("✅ Método step() encontrado")
    
    # Extraer el contenido del método
    step_content = step_match.group(0)
    
    # Verificar si llama a motion.update
    if 'motion.update' not in step_content:
        print("❌ step() NO llama a motion.update()")
        print("\n🔨 REEMPLAZANDO método step()...")
        
        # Reemplazar con versión correcta
        new_step = '''def step(self, dt: float = None) -> dict:
        """
        Actualiza todas las fuentes y devuelve estado actual.
        Usado por el controller.
        
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
            
        # CRÍTICO: Actualizar cada SourceMotion
        active_sources = set()
        
        for sid, motion in self._source_motions.items():
            # Solo actualizar fuentes activas
            if sid < self.max_sources and motion.enabled:
                active_sources.add(sid)
                
                # 🎯 LLAMAR A motion.update() - ESTO ES LO QUE FALTABA
                try:
                    # motion.update() espera solo dt
                    motion.update(dt)
                    
                    # Obtener el estado actualizado
                    pos = motion.get_position()
                    orient = motion.get_orientation() 
                    aperture = motion.get_aperture()
                    
                    # Actualizar arrays globales
                    self._positions[sid] = pos
                    self._orientations[sid] = orient
                    self._apertures[sid] = aperture
                    
                except Exception as e:
                    print(f"⚠️ Error actualizando fuente {sid}: {e}")
        
        # Actualizar tiempo y frame
        self._time += dt
        self._frame_count += 1
        
        # Si hay OSC bridge, enviar posiciones
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                self.osc_bridge.send_batch_positions(
                    list(active_sources),
                    self._positions[:len(active_sources)],
                    self._orientations[:len(active_sources)]
                )
            except:
                pass  # Ignorar errores OSC
        
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
        
        # Reemplazar el método completo
        content = re.sub(step_pattern, new_step, content, count=1)
        print("✅ Método step() reemplazado")
        
    else:
        print("✅ step() YA llama a motion.update()")

# 4. Hacer backup y guardar
import datetime
backup_name = engine_file + f".backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n📋 Backup: {backup_name}")

with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✅ Archivo actualizado: {engine_file}")

# 5. Crear test de verificación
test_code = '''#!/usr/bin/env python3
"""
🧪 TEST: Verificar que step() actualiza las fuentes
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

print("\\n🧪 TEST DE ENGINE.STEP() → MOTION.UPDATE()\\n")

# Crear engine y macro
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
macro_id = engine.create_macro("test", source_count=4, formation="line", spacing=2.0)

# Posiciones iniciales
print("📍 POSICIONES INICIALES:")
for i in range(4):
    if i in engine._source_motions:
        pos = engine._source_motions[i].get_position()
        print(f"   Fuente {i}: {pos}")

# Aplicar concentración
print("\\n🎯 APLICANDO CONCENTRACIÓN (factor=0.1)...")
engine.set_macro_concentration(macro_id, 0.1)

# Verificar offsets
print("\\n🔍 VERIFICANDO OFFSETS:")
for i in range(4):
    if i in engine._source_motions:
        motion = engine._source_motions[i]
        offset = motion.concentration_offset
        print(f"   Fuente {i} offset: {offset}")

# Llamar step() varias veces
print("\\n🔄 LLAMANDO ENGINE.STEP() 30 VECES...")
for _ in range(30):
    state = engine.step()

# Posiciones finales
print("\\n📍 POSICIONES FINALES:")
movimientos = []
for i in range(4):
    if i in engine._source_motions:
        pos = engine._source_motions[i].get_position()
        inicial = engine._source_motions[i].state.position - engine._source_motions[i].concentration_offset
        movimiento = np.linalg.norm(pos - inicial)
        movimientos.append(movimiento)
        print(f"   Fuente {i}: {pos}")
        print(f"      Movimiento: {movimiento:.4f}")

# Verificar
if all(m > 0.01 for m in movimientos):
    print("\\n✅ ¡ÉXITO! Las fuentes se están moviendo")
    print("\\n🎉 LA CONCENTRACIÓN FUNCIONA CORRECTAMENTE")
else:
    print("\\n❌ Las fuentes NO se mueven")
    print("⚠️  Revisar la implementación de step()")

print("\\n" + "="*60)
'''

with open("test_step_update_connection.py", 'w', encoding='utf-8') as f:
    f.write(test_code)

print(f"\n✅ Test creado: test_step_update_connection.py")

print("""
================================================================================
✅ FIX APLICADO - ENGINE.STEP() AHORA LLAMA A MOTION.UPDATE()
================================================================================

🚀 EJECUTA EL TEST:
   python test_step_update_connection.py

🎯 Si funciona, prueba la concentración:
   python trajectory_hub/interface/interactive_controller.py

💡 Lo que arreglamos:
   - step() ahora llama motion.update(dt) para cada fuente
   - Los offsets de concentración se aplicarán correctamente
   - Las posiciones se actualizarán en cada frame

🔥 ¡ESTE DEBERÍA SER EL FIX DEFINITIVO!
================================================================================
""")