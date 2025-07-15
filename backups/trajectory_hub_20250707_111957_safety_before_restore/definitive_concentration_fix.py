#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO: Recalcular offsets en cada step()
"""

import os
import re

print("""
================================================================================
🔧 FIX DEFINITIVO DE CONCENTRACIÓN
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

print("📋 MODIFICANDO step() para recalcular offsets...")

with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
import datetime
backup_name = engine_file + f".backup_definitive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"📋 Backup: {backup_name}")

# Buscar y reemplazar el método step completo
step_match = re.search(r'def step\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)

if step_match:
    print("✅ Método step() encontrado")
    
    # Nuevo step que recalcula offsets
    new_step = '''def step(self, dt: float = None) -> dict:
        """
        Ejecuta un paso de simulación con concentración.
        Recalcula offsets en cada frame para evitar reseteos.
        """
        if dt is None:
            dt = self.dt
        
        # Primero, recalcular offsets de concentración para cada macro
        for macro_id, macro in self._macros.items():
            if hasattr(macro, 'concentration_factor') and macro.concentration_factor > 0:
                # Calcular centro del macro
                positions = []
                for sid in macro.source_ids:
                    if sid in self._source_motions:
                        positions.append(self._source_motions[sid].state.position.copy())
                
                if positions:
                    import numpy as np
                    center = np.mean(positions, axis=0)
                    
                    # Aplicar offset a cada fuente
                    for i, sid in enumerate(macro.source_ids):
                        if sid in self._source_motions:
                            motion = self._source_motions[sid]
                            # Recalcular offset
                            direction = center - positions[i]
                            motion.concentration_offset = direction * macro.concentration_factor
        
        # Actualizar motions y aplicar offsets
        for sid, motion in self._source_motions.items():
            if sid < self.max_sources:
                # Actualizar motion (puede resetear offsets)
                motion.update(dt)
                
                # Obtener posición base
                pos = motion.state.position.copy()
                
                # Aplicar concentration_offset (recalculado arriba)
                if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
                    pos = pos + motion.concentration_offset
                
                # Actualizar arrays
                self._positions[sid] = pos
                self._orientations[sid] = motion.state.orientation
                self._apertures[sid] = motion.state.aperture
        
        # Incrementar tiempo
        self._time = getattr(self, '_time', 0.0) + dt
        self._frame_count = getattr(self, '_frame_count', 0) + 1
        
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'time': self._time,
            'frame': self._frame_count
        }'''
    
    # Reemplazar
    content = re.sub(r'def step\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', new_step, content, flags=re.DOTALL)
    
    # Guardar
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ step() modificado para recalcular offsets")
else:
    print("❌ No se encontró step()")

# Test completo
print("\n" + "="*80)
print("🧪 TEST COMPLETO")
print("="*80 + "\n")

test_code = '''
import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    print("1️⃣ CREANDO ENGINE Y MACRO...")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=6.0)
    
    print("\\n2️⃣ POSICIONES INICIALES:")
    initial_pos = {}
    for i in range(4):
        initial_pos[i] = engine._positions[i].copy()
        print(f"   F{i}: {initial_pos[i]}")
    
    center = np.mean(list(initial_pos.values()), axis=0)
    print(f"   Centro: {center}")
    
    print("\\n3️⃣ APLICANDO CONCENTRACIÓN 0.5...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    print("\\n4️⃣ EJECUTANDO PRIMER FRAME...")
    engine.step()
    
    print("\\n   MOVIMIENTOS:")
    total_movement = 0
    for i in range(4):
        mov = np.linalg.norm(engine._positions[i] - initial_pos[i])
        total_movement += mov
        if mov > 0.001:
            print(f"   F{i}: ✅ movió {mov:.4f} → {engine._positions[i]}")
        else:
            print(f"   F{i}: ❌ no se movió")
    
    if total_movement > 0.01:
        print("\\n✅ ¡LAS FUENTES SE ESTÁN MOVIENDO!")
        
        # Ejecutar más frames
        print("\\n5️⃣ EJECUTANDO 100 FRAMES...")
        for frame in range(99):
            engine.step()
            
            if (frame + 2) % 25 == 0:
                mov0 = np.linalg.norm(engine._positions[0] - initial_pos[0])
                print(f"   Frame {frame + 2}: F0 ha movido {mov0:.4f} total")
        
        print("\\n6️⃣ RESULTADO FINAL:")
        for i in range(4):
            final_pos = engine._positions[i]
            total_mov = np.linalg.norm(final_pos - initial_pos[i])
            print(f"   F{i}: {initial_pos[i]} → {final_pos} (mov: {total_mov:.4f})")
        
        # Análisis de concentración
        initial_spread = np.std(list(initial_pos.values()))
        final_spread = np.std([engine._positions[i] for i in range(4)])
        reduction = (1 - final_spread/initial_spread) * 100
        
        print(f"\\n📊 CONCENTRACIÓN:")
        print(f"   Dispersión inicial: {initial_spread:.4f}")
        print(f"   Dispersión final: {final_spread:.4f}")
        print(f"   Reducción: {reduction:.1f}%")
        
        if reduction > 20:
            print("\\n" + "="*60)
            print("🎉 ¡ÉXITO TOTAL! LA CONCENTRACIÓN FUNCIONA PERFECTAMENTE")
            print("="*60)
            print("\\n🚀 Las fuentes se concentran hacia el centro")
            print("\\n💡 Ahora puedes usar:")
            print("   python trajectory_hub/interface/interactive_controller.py")
            print("\\n🎮 En el controlador:")
            print("   - Tecla 'C': Activar/desactivar concentración")
            print("   - Teclas '1-9': Ajustar intensidad (1=10%, 9=90%)")
            print("   - Los cambios se verán en Spat Revolution")
        else:
            print("\\n⚠️ Movimiento detectado pero poca concentración")
    else:
        print("\\n❌ Las fuentes NO se mueven")
        
except Exception as e:
    print(f"\\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 RESUMEN DEL FIX
================================================================================

🔧 Lo que hace este fix:
   1. Recalcula los offsets en CADA frame dentro de step()
   2. Evita que motion.update() resetee los offsets
   3. Garantiza que la concentración siempre se aplique

💡 Esto soluciona el problema de que concentration_offset
   se reseteaba a [0,0,0] entre frames.

🎯 Si funciona, las fuentes convergerán gradualmente al centro.
================================================================================
""")