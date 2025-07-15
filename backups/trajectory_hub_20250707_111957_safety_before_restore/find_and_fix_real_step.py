#!/usr/bin/env python3
"""
🔍 BUSCAR Y ARREGLAR EL VERDADERO step() o update()
"""

import os
import sys

print("""
================================================================================
🔍 BUSCANDO MÉTODO QUE ACTUALIZA POSICIONES
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# 1. Buscar todos los métodos que podrían actualizar posiciones
with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("📋 BUSCANDO MÉTODOS RELEVANTES...")

methods_found = []
for i, line in enumerate(lines):
    if 'def ' in line and ('step' in line or 'update' in line):
        # Extraer nombre del método
        method_name = line.strip().split('(')[0].replace('def ', '')
        methods_found.append((i, method_name, line.strip()))
        print(f"   Línea {i+1}: {method_name}")

# 2. Buscar dónde se actualiza _positions
print("\n📋 BUSCANDO DÓNDE SE ACTUALIZA _positions...")

positions_updates = []
for i, line in enumerate(lines):
    if '_positions[' in line and '=' in line:
        positions_updates.append((i, line.strip()))
        print(f"   Línea {i+1}: {line.strip()[:60]}...")

# 3. Buscar el método principal de actualización
update_method_line = -1
for i, line in enumerate(lines):
    if 'def update(' in line:
        update_method_line = i
        print(f"\n✅ Encontrado update() en línea {i+1}")
        break

if update_method_line >= 0:
    print("\n🔨 MODIFICANDO update() para aplicar offsets...")
    
    # Buscar el bloque donde se actualiza _positions
    in_update = False
    update_start = update_method_line
    update_end = len(lines)
    
    # Encontrar el final del método
    indent_level = len(lines[update_method_line]) - len(lines[update_method_line].lstrip())
    
    for i in range(update_method_line + 1, len(lines)):
        line = lines[i]
        if line.strip() and (len(line) - len(line.lstrip())) <= indent_level:
            if 'def ' in line or 'class ' in line:
                update_end = i
                break
    
    # Buscar dónde se actualiza _positions dentro de update
    positions_update_line = -1
    for i in range(update_start, update_end):
        if '_positions[sid] =' in lines[i]:
            positions_update_line = i
            print(f"   Encontrada actualización de _positions en línea {i+1}")
            break
    
    if positions_update_line >= 0:
        # Reemplazar esa línea para usar get_position
        old_line = lines[positions_update_line]
        indent = ' ' * (len(old_line) - len(old_line.lstrip()))
        
        new_lines = [
            f"{indent}# Obtener posición con offsets aplicados\n",
            f"{indent}if hasattr(motion, 'get_position'):\n",
            f"{indent}    pos = motion.get_position()\n",
            f"{indent}else:\n",
            f"{indent}    # Fallback: calcular manualmente\n",
            f"{indent}    pos = motion.state.position.copy()\n",
            f"{indent}    if hasattr(motion, 'concentration_offset'):\n",
            f"{indent}        pos = pos + motion.concentration_offset\n",
            f"{indent}    if hasattr(motion, 'distribution_offset'):\n",
            f"{indent}        pos = pos + motion.distribution_offset\n",
            f"{indent}    if hasattr(motion, 'trajectory_offset'):\n",
            f"{indent}        pos = pos + motion.trajectory_offset\n",
            f"{indent}self._positions[sid] = pos\n"
        ]
        
        # Reemplazar
        lines[positions_update_line] = ''.join(new_lines)
        
        # Guardar
        import datetime
        backup_name = engine_file + f".backup_update_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_name, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\n📋 Backup: {backup_name}")
        
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ update() modificado para aplicar offsets")

# 4. Si no hay update(), crear step()
else:
    print("\n❌ No se encontró update()")
    print("\n🔨 AÑADIENDO método step() al final de EnhancedTrajectoryEngine...")
    
    # Buscar el final de la clase
    class_end = -1
    for i in range(len(lines)-1, -1, -1):
        if lines[i].strip() and not lines[i].startswith(' '):
            class_end = i
            break
    
    if class_end > 0:
        # Insertar step() antes del final
        step_method = '''
    def step(self, dt: float = None) -> dict:
        """
        Actualiza todas las fuentes y devuelve estado actual.
        Este método es llamado por el controller.
        """
        if dt is None:
            dt = self.dt
            
        # Primero llamar a update si existe
        if hasattr(self, 'update'):
            self.update(dt)
        
        # Asegurar que los offsets se apliquen a _positions
        for sid, motion in self._source_motions.items():
            if sid < self.max_sources and motion.enabled:
                # Obtener posición con offsets
                if hasattr(motion, 'get_position'):
                    pos = motion.get_position()
                else:
                    pos = motion.state.position.copy()
                    if hasattr(motion, 'concentration_offset'):
                        pos = pos + motion.concentration_offset
                
                # Actualizar array global
                self._positions[sid] = pos
        
        # Incrementar tiempo
        self._time = getattr(self, '_time', 0.0) + dt
        self._frame_count = getattr(self, '_frame_count', 0) + 1
        
        # Devolver estado
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'time': self._time,
            'frame': self._frame_count
        }
'''
        
        lines.insert(class_end, step_method)
        
        # Guardar
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("✅ step() añadido")

# 5. Test simple
test_code = '''#!/usr/bin/env python3
"""
🧪 TEST DIRECTO: Offsets en posiciones
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

print("\\n🧪 TEST DIRECTO DE OFFSETS\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)

# Crear 2 fuentes
engine.create_source(0, "Test0", position=np.array([-2.0, 0.0, 0.0]))
engine.create_source(1, "Test1", position=np.array([2.0, 0.0, 0.0]))

# Crear macro
macro_id = engine.create_macro("test", source_count=0)
engine._macros[macro_id].source_ids = {0, 1}

print("📍 Posiciones iniciales:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")

# Aplicar concentración
print("\\n🎯 Aplicando concentración 0.5...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar offsets
if 0 in engine._source_motions:
    offset0 = engine._source_motions[0].concentration_offset
    offset1 = engine._source_motions[1].concentration_offset
    print(f"\\n🔍 Offsets calculados:")
    print(f"   Fuente 0: {offset0}")
    print(f"   Fuente 1: {offset1}")

# Llamar a step o update
print("\\n🔄 Actualizando...")
if hasattr(engine, 'step'):
    engine.step()
elif hasattr(engine, 'update'):
    engine.update(engine.dt)

print("\\n📍 Posiciones después:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")

# Verificar movimiento
mov0 = np.linalg.norm(engine._positions[0] - np.array([-2.0, 0.0, 0.0]))
mov1 = np.linalg.norm(engine._positions[1] - np.array([2.0, 0.0, 0.0]))

if mov0 > 0.01 or mov1 > 0.01:
    print(f"\\n✅ ¡ÉXITO! Las fuentes se movieron:")
    print(f"   Fuente 0: {mov0:.4f}")
    print(f"   Fuente 1: {mov1:.4f}")
    print("\\n🎉 LA CONCENTRACIÓN FUNCIONA!")
else:
    print(f"\\n❌ Las fuentes NO se movieron")
    
    # Aplicar offset manualmente para verificar
    print("\\n🔧 Aplicando offsets manualmente...")
    if 0 in engine._source_motions:
        motion0 = engine._source_motions[0]
        motion1 = engine._source_motions[1]
        
        engine._positions[0] = motion0.state.position + motion0.concentration_offset
        engine._positions[1] = motion1.state.position + motion1.concentration_offset
        
        print(f"   Fuente 0: {engine._positions[0]}")
        print(f"   Fuente 1: {engine._positions[1]}")
        
        print("\\n💡 Los offsets funcionan manualmente")
        print("   El problema está en update() o step()")

print("\\n" + "="*60)
'''

with open("test_direct_offsets.py", 'w', encoding='utf-8') as f:
    f.write(test_code)

print(f"\n✅ Test creado: test_direct_offsets.py")

print("""
================================================================================
✅ DIAGNÓSTICO Y FIX APLICADO
================================================================================

🔧 Lo que hicimos:
   1. Buscamos todos los métodos step/update
   2. Identificamos dónde se actualiza _positions
   3. Modificamos para usar get_position() con offsets
   4. Si no existe step(), lo añadimos

🚀 EJECUTA:
   python test_direct_offsets.py

💡 Este test es más simple y directo para verificar offsets

🎯 Si aún no funciona, aplicará los offsets manualmente para debug
================================================================================
""")