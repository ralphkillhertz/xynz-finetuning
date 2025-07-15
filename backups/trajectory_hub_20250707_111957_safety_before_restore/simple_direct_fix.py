#!/usr/bin/env python3
"""
🔧 FIX SIMPLE Y DIRECTO: Concentración sin complicaciones
"""

import os
import re

print("""
================================================================================
🔧 FIX SIMPLE Y DIRECTO
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Backup
import datetime
backup_name = engine_file + f".backup_simple_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()
with open(backup_name, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"📋 Backup: {backup_name}")

# 1. Asegurar que concentration_factor se guarda en el macro
print("\n1️⃣ VERIFICANDO set_macro_concentration...")

if 'macro.concentration_factor = concentration_factor' not in content:
    print("   ❌ No se guarda concentration_factor, arreglando...")
    
    # Buscar set_macro_concentration
    set_conc_match = re.search(r'def set_macro_concentration\(.*?\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    
    if set_conc_match:
        method_body = set_conc_match.group(1)
        # Añadir línea para guardar factor
        if 'macro.concentration_factor' not in method_body:
            new_body = method_body.replace(
                'macro = self._macros[macro_id]',
                '''macro = self._macros[macro_id]
        macro.concentration_factor = concentration_factor'''
            )
            content = content.replace(method_body, new_body)
            print("   ✅ Añadido macro.concentration_factor = concentration_factor")
else:
    print("   ✅ concentration_factor ya se guarda")

# 2. Crear un step() muy simple que funcione
print("\n2️⃣ CREANDO step() SIMPLE...")

# Buscar step existente
step_match = re.search(r'def step\(.*?\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)

# Nuevo step simple
simple_step = '''def step(self, dt: float = None) -> dict:
        """
        Step simple que aplica concentración directamente.
        """
        if dt is None:
            dt = self.dt
        
        # Para cada macro con concentración
        for macro_id, macro in self._macros.items():
            factor = getattr(macro, 'concentration_factor', 0)
            if factor > 0 and hasattr(macro, 'source_ids'):
                # Obtener posiciones actuales
                positions = []
                source_list = list(macro.source_ids)
                
                for sid in source_list:
                    if sid < self.max_sources:
                        # Usar la posición del motion si existe
                        if sid in self._source_motions:
                            pos = self._source_motions[sid].state.position.copy()
                        else:
                            pos = self._positions[sid].copy()
                        positions.append(pos)
                
                if len(positions) > 1:
                    # Calcular centro
                    import numpy as np
                    center = np.mean(positions, axis=0)
                    
                    # Mover cada fuente hacia el centro
                    for i, sid in enumerate(source_list):
                        if sid < self.max_sources:
                            # Calcular nueva posición
                            current_pos = positions[i]
                            direction = center - current_pos
                            new_pos = current_pos + (direction * factor * dt * 10.0)  # *10 para velocidad visible
                            
                            # Actualizar
                            self._positions[sid] = new_pos
                            
                            # También actualizar el motion si existe
                            if sid in self._source_motions:
                                self._source_motions[sid].state.position = new_pos.copy()
        
        # Para fuentes sin macro, mantener sincronizado
        for sid in self._source_motions:
            if sid < self.max_sources:
                motion = self._source_motions[sid]
                # Si el motion no se actualizó arriba, usar su posición
                in_macro = any(sid in macro.source_ids for macro in self._macros.values() 
                              if hasattr(macro, 'source_ids'))
                if not in_macro:
                    self._positions[sid] = motion.state.position.copy()
                
                # Actualizar orientación y apertura
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

# Reemplazar step
if step_match:
    content = re.sub(r'def step\(.*?\):(.*?)(?=\n    def|\nclass|\Z)', simple_step, content, flags=re.DOTALL)
    print("   ✅ step() reemplazado con versión simple")
else:
    # Añadir al final de la clase
    print("   ⚠️ No se encontró step(), añadiendo al final...")
    # Buscar el final de la clase
    class_end = content.rfind('\n\nclass')
    if class_end == -1:
        class_end = content.rfind('\n\n# ')
    if class_end == -1:
        class_end = len(content)
    
    content = content[:class_end] + '\n' + simple_step + content[class_end:]

# Guardar
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Archivo modificado")

# Test
print("\n" + "="*80)
print("🧪 TEST FINAL")
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
    
    print("CREANDO ENGINE...")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    
    print("CREANDO MACRO...")
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=6.0)
    
    print("\\nPOSICIONES INICIALES:")
    initial_pos = {}
    for i in range(4):
        initial_pos[i] = engine._positions[i].copy()
        print(f"  F{i}: {initial_pos[i]}")
    
    print("\\nAPLICANDO CONCENTRACIÓN...")
    engine.set_macro_concentration(macro_id, 0.8)  # Alta para ver efecto rápido
    
    # Verificar que se guardó
    macro = engine._macros[macro_id]
    print(f"  concentration_factor = {getattr(macro, 'concentration_factor', 'NO EXISTE')}")
    
    print("\\nEJECUTANDO SIMULACIÓN...")
    
    # Ejecutar varios frames
    for frame in range(50):
        engine.step()
        
        if frame == 0:
            print("\\nDESPUÉS DE 1 FRAME:")
            for i in range(4):
                mov = np.linalg.norm(engine._positions[i] - initial_pos[i])
                if mov > 0.001:
                    print(f"  F{i}: ✅ movió {mov:.4f}")
                else:
                    print(f"  F{i}: ❌ no movió")
        
        if (frame + 1) % 10 == 0:
            mov0 = np.linalg.norm(engine._positions[0] - initial_pos[0])
            print(f"  Frame {frame + 1}: F0 movió {mov0:.4f} total")
    
    print("\\nRESULTADO FINAL:")
    for i in range(4):
        final_pos = engine._positions[i]
        total_mov = np.linalg.norm(final_pos - initial_pos[i])
        print(f"  F{i}: {initial_pos[i]} → {final_pos}")
        print(f"       Movimiento total: {total_mov:.4f}")
    
    # Verificar concentración
    initial_spread = np.std(list(initial_pos.values()))
    final_spread = np.std([engine._positions[i] for i in range(4)])
    reduction = (1 - final_spread/initial_spread) * 100
    
    print(f"\\nCONCENTRACIÓN:")
    print(f"  Dispersión inicial: {initial_spread:.4f}")
    print(f"  Dispersión final: {final_spread:.4f}")
    print(f"  Reducción: {reduction:.1f}%")
    
    if reduction > 20:
        print("\\n" + "="*60)
        print("🎉 ¡ÉXITO! LA CONCENTRACIÓN FUNCIONA")
        print("="*60)
        print("\\n🚀 Usa ahora:")
        print("   python trajectory_hub/interface/interactive_controller.py")
    
except Exception as e:
    print(f"\\nERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 RESUMEN
================================================================================

Este fix implementa la versión más simple posible:
1. Calcula el centro del macro
2. Mueve cada fuente hacia el centro
3. No depende de concentration_offset ni motion.update()
4. Actualiza directamente _positions

Si funciona, las fuentes convergerán visiblemente al centro.
================================================================================
""")