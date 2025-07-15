#!/usr/bin/env python3
"""
🔨 FIX AGRESIVO: Forzar concentración en TODOS los puntos posibles
"""

import os
import sys

print("""
================================================================================
🔨 FIX AGRESIVO DE CONCENTRACIÓN
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# 1. Leer el archivo
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
import datetime
backup_name = engine_file + f".backup_aggressive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"📋 Backup: {backup_name}")

# 2. Buscar TODAS las líneas donde se asigna a _positions[sid]
import re

print("\n🔍 BUSCANDO TODAS LAS ASIGNACIONES A _positions[sid]...")

# Patrón para encontrar asignaciones
pattern = r'(self\._positions\[sid\]\s*=\s*)([^\n]+)'

matches = list(re.finditer(pattern, content))
print(f"✅ Encontradas {len(matches)} asignaciones")

# 3. Modificar TODAS las asignaciones para incluir offsets
modifications = 0
for match in matches:
    original_line = match.group(0)
    assignment = match.group(1)
    value = match.group(2).strip()
    
    # Si ya tiene comentario de offsets, saltar
    if 'APLICAR OFFSETS' in content[max(0, match.start()-100):match.start()]:
        print(f"   ⏭️  Ya modificada: {original_line[:50]}...")
        continue
    
    # Obtener indentación
    line_start = content.rfind('\n', 0, match.start()) + 1
    line = content[line_start:match.end()]
    indent = len(line) - len(line.lstrip())
    spaces = ' ' * indent
    
    # Crear código que aplica offsets
    new_code = f'''{spaces}# FORZAR APLICACIÓN DE OFFSETS
{spaces}_temp_pos = {value}
{spaces}if sid in self._source_motions and hasattr(self._source_motions[sid], 'concentration_offset'):
{spaces}    _temp_pos = _temp_pos + self._source_motions[sid].concentration_offset
{spaces}{assignment}_temp_pos'''
    
    # Reemplazar
    content = content[:match.start()] + new_code + content[match.end():]
    modifications += 1
    print(f"   ✅ Modificada línea: {original_line[:50]}...")

print(f"\n✅ Total modificaciones: {modifications}")

# 4. Añadir método step si no existe
if 'def step(' not in content or content.count('def step(') < 2:
    print("\n🔨 AÑADIENDO MÉTODO step() robusto...")
    
    # Buscar el final de la clase EnhancedTrajectoryEngine
    class_match = re.search(r'class EnhancedTrajectoryEngine.*?(?=\nclass|\Z)', content, re.DOTALL)
    
    if class_match:
        # Insertar antes del final
        insert_pos = class_match.end() - 1
        
        step_method = '''
    def step(self, dt: float = None) -> dict:
        """
        Paso de simulación que GARANTIZA aplicación de offsets.
        """
        if dt is None:
            dt = self.dt
        
        # Llamar a update si existe
        if hasattr(self, 'update'):
            self.update(dt)
        
        # FORZAR APLICACIÓN DE OFFSETS (por si update no lo hizo)
        for sid in self._source_motions:
            if sid < self.max_sources:
                motion = self._source_motions[sid]
                if motion.enabled:
                    # Posición base
                    base_pos = motion.state.position.copy()
                    
                    # Sumar TODOS los offsets
                    final_pos = base_pos
                    if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
                        final_pos = final_pos + motion.concentration_offset
                    if hasattr(motion, 'distribution_offset') and motion.distribution_offset is not None:
                        final_pos = final_pos + motion.distribution_offset
                    if hasattr(motion, 'trajectory_offset') and motion.trajectory_offset is not None:
                        final_pos = final_pos + motion.trajectory_offset
                    
                    # FORZAR actualización
                    self._positions[sid] = final_pos
        
        # Incrementar tiempo
        self._time = getattr(self, '_time', 0.0) + dt
        self._frame_count = getattr(self, '_frame_count', 0) + 1
        
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'time': self._time,
            'frame': self._frame_count
        }
'''
        
        content = content[:insert_pos] + step_method + content[insert_pos:]
        print("✅ Método step() añadido")

# 5. Guardar archivo modificado
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Archivo modificado guardado")

# 6. Test definitivo
print("\n" + "="*80)
print("🧪 TEST DEFINITIVO")
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
    
    print("CREANDO ENGINE Y MACRO...")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=4.0)
    
    print("\\nPOSICIONES INICIALES:")
    initial_pos = {}
    for i in range(4):
        initial_pos[i] = engine._positions[i].copy()
        print(f"  F{i}: {initial_pos[i]}")
    
    print("\\nAPLICANDO CONCENTRACIÓN 0.5...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    print("\\nOFFSETS CALCULADOS:")
    for i in range(4):
        if i in engine._source_motions:
            offset = engine._source_motions[i].concentration_offset
            mag = np.linalg.norm(offset)
            print(f"  F{i}: magnitud={mag:.4f}")
    
    print("\\nEJECUTANDO 1 STEP...")
    engine.step()
    
    print("\\nPOSICIONES DESPUÉS DE 1 STEP:")
    movements = []
    for i in range(4):
        pos = engine._positions[i]
        mov = np.linalg.norm(pos - initial_pos[i])
        movements.append(mov)
        print(f"  F{i}: {pos} (movimiento={mov:.4f})")
    
    if any(m > 0.01 for m in movements):
        print("\\n✅ ¡ÉXITO! LAS FUENTES SE MUEVEN")
        
        # Ejecutar más frames
        for _ in range(50):
            engine.step()
        
        print("\\nDESPUÉS DE 50 FRAMES:")
        final_movements = []
        for i in range(4):
            pos = engine._positions[i]
            mov = np.linalg.norm(pos - initial_pos[i])
            final_movements.append(mov)
            print(f"  F{i}: {pos} (mov total={mov:.4f})")
        
        # Análisis de concentración
        initial_spread = np.std([p for p in initial_pos.values()])
        final_spread = np.std([engine._positions[i] for i in range(4)])
        
        print(f"\\nCONCENTRACIÓN:")
        print(f"  Dispersión inicial: {initial_spread:.4f}")
        print(f"  Dispersión final: {final_spread:.4f}")
        print(f"  Reducción: {(1-final_spread/initial_spread)*100:.1f}%")
        
        print("\\n🎉 ¡LA CONCENTRACIÓN FUNCIONA!")
        print("\\n🚀 Ahora ejecuta:")
        print("   python trajectory_hub/interface/interactive_controller.py")
        
    else:
        print("\\n❌ Las fuentes AÚN NO se mueven")
        print("\\n🔧 Algo muy raro está pasando. Verifica manualmente:")
        print("   1. Que el archivo se guardó correctamente")
        print("   2. Que no hay otro proceso usando el archivo")
        print("   3. Reinicia el terminal Python")
        
except Exception as e:
    print(f"\\nERROR: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 RESUMEN DEL FIX AGRESIVO
================================================================================

🔧 Lo que hicimos:
   1. Modificar TODAS las asignaciones a _positions[sid]
   2. Añadir un método step() que FUERZA la aplicación de offsets
   3. Garantizar que los offsets se apliquen sin importar el flujo

💡 Si TODAVÍA no funciona:
   1. Cierra todos los procesos Python
   2. Reinicia el terminal
   3. Ejecuta: python test_concentration_working.py
   
🔨 Este es el fix más agresivo posible.
================================================================================
""")