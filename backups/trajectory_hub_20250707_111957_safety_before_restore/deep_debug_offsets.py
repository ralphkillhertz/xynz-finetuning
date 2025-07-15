#!/usr/bin/env python3
"""
🔍 DEBUG PROFUNDO: ¿Por qué los offsets son 0 en step()?
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("""
================================================================================
🔍 DEBUG PROFUNDO DE OFFSETS
================================================================================
""")

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

print("1️⃣ ESTADO INICIAL:")
print(f"   Fuentes en _source_motions: {list(engine._source_motions.keys())}")
print(f"   Macro source_ids: {engine._macros[macro_id].source_ids}")

# Verificar que concentration_offset existe
print("\n2️⃣ VERIFICANDO concentration_offset EN SourceMotion:")
for sid in engine._source_motions:
    motion = engine._source_motions[sid]
    if hasattr(motion, 'concentration_offset'):
        print(f"   Fuente {sid}: concentration_offset = {motion.concentration_offset}")
    else:
        print(f"   Fuente {sid}: NO tiene concentration_offset")
        
        # Inicializar si no existe
        print(f"      → Inicializando concentration_offset...")
        motion.concentration_offset = np.zeros(3)

# Aplicar concentración
print("\n3️⃣ APLICANDO CONCENTRACIÓN...")
engine.set_macro_concentration(macro_id, 0.5)

print("\n4️⃣ OFFSETS DESPUÉS DE set_macro_concentration:")
for sid in engine._source_motions:
    motion = engine._source_motions[sid]
    offset = motion.concentration_offset
    print(f"   Fuente {sid}: {offset} (magnitud={np.linalg.norm(offset):.4f})")

# Verificar si los offsets persisten
print("\n5️⃣ VERIFICANDO PERSISTENCIA DE OFFSETS:")
print("   Esperando un momento...")
import time
time.sleep(0.1)

for sid in engine._source_motions:
    motion = engine._source_motions[sid]
    offset = motion.concentration_offset
    print(f"   Fuente {sid}: {offset} (magnitud={np.linalg.norm(offset):.4f})")

# Llamar a step con debug
print("\n6️⃣ EJECUTANDO step() CON DEBUG...")

# Guardar posiciones antes
pos_before = {}
for sid in engine._source_motions:
    pos_before[sid] = engine._positions[sid].copy()

# Modificar temporalmente step para añadir prints
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

print("\n   Añadiendo prints de debug a step()...")
with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup_content = content

# Añadir prints en step
import re
step_match = re.search(r'def step\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)

if step_match:
    step_body = step_match.group(1)
    
    # Añadir print después de obtener motion
    new_step_body = step_body.replace(
        'for sid, motion in self._source_motions.items():',
        '''for sid, motion in self._source_motions.items():
            print(f"DEBUG step(): Procesando fuente {sid}")'''
    )
    
    # Añadir print antes de actualizar position
    new_step_body = new_step_body.replace(
        'pos = motion.state.position.copy()',
        '''pos = motion.state.position.copy()
            print(f"  - state.position: {pos}")
            print(f"  - concentration_offset: {getattr(motion, 'concentration_offset', 'NO EXISTE')}")'''
    )
    
    # Añadir print después de aplicar offset
    new_step_body = new_step_body.replace(
        'pos = pos + motion.concentration_offset',
        '''pos = pos + motion.concentration_offset
            print(f"  - pos después de offset: {pos}")'''
    )
    
    # Reemplazar
    new_content = content.replace(step_match.group(1), new_step_body)
    
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

# Ejecutar step
try:
    engine.step()
except Exception as e:
    print(f"\n❌ Error en step(): {e}")

# Restaurar archivo
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(backup_content)

print("\n7️⃣ ANÁLISIS FINAL:")
for sid in engine._source_motions:
    motion = engine._source_motions[sid]
    print(f"\n   Fuente {sid}:")
    print(f"      state.position: {motion.state.position}")
    print(f"      concentration_offset: {motion.concentration_offset}")
    print(f"      _positions[{sid}] antes: {pos_before[sid]}")
    print(f"      _positions[{sid}] después: {engine._positions[sid]}")
    
    movement = np.linalg.norm(engine._positions[sid] - pos_before[sid])
    if movement > 0.001:
        print(f"      ✅ Se movió {movement:.4f}")
    else:
        print(f"      ❌ NO se movió")

# Propuesta de fix
print("\n" + "="*80)
print("🔧 PROPUESTA DE FIX")
print("="*80)

if all(np.linalg.norm(engine._source_motions[sid].concentration_offset) < 0.001 for sid in engine._source_motions):
    print("""
El problema es que concentration_offset se está reseteando a [0,0,0].

Posibles causas:
1. SourceMotion.__init__ lo inicializa a ceros
2. motion.update() lo resetea
3. Hay otra parte del código que lo modifica

SOLUCIÓN: Modificar step() para recalcular el offset cada vez.
""")
else:
    print("""
Los offsets existen pero no se están aplicando en step().

SOLUCIÓN: Verificar que step() realmente sume los offsets.
""")