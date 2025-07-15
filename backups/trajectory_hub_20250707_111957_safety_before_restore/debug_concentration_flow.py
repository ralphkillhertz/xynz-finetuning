#!/usr/bin/env python3
"""
🔍 DEBUG: Seguir el flujo completo de concentración
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

print("""
================================================================================
🔍 DEBUG COMPLETO DE CONCENTRACIÓN
================================================================================
""")

# Modificar temporalmente el código para añadir prints
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

print("🔧 AÑADIENDO PRINTS DE DEBUG...")

with open(engine_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
import datetime
backup_name = engine_file + f".backup_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w', encoding='utf-8') as f:
    f.write(content)

# Añadir prints en puntos clave
import re

# 1. En get_position()
content = re.sub(
    r'(def get_position\(self\).*?:)',
    r'\1\n        print(f"DEBUG get_position() llamado para fuente {self.source_id}")',
    content,
    flags=re.DOTALL
)

# 2. En la parte de update donde se llama get_position
content = re.sub(
    r'(if hasattr\(motion, \'get_position\'\):)',
    r'print(f"DEBUG: Fuente {sid} - hasattr(get_position) = True")\n            \1',
    content
)

# 3. Antes de asignar a _positions
content = re.sub(
    r'(self\._positions\[sid\] = pos\s*$)',
    r'print(f"DEBUG: Asignando a _positions[{sid}] = {pos}")\n            \1',
    content,
    flags=re.MULTILINE
)

# Guardar con debug
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Prints de debug añadidos")

# Ejecutar test con debug
print("\n" + "="*80)
print("🧪 EJECUTANDO TEST CON DEBUG")
print("="*80 + "\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Test simple
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    
    print("1️⃣ CREANDO MACRO...")
    macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
    
    print(f"\n2️⃣ POSICIONES INICIALES:")
    print(f"   F0: {engine._positions[0]}")
    print(f"   F1: {engine._positions[1]}")
    
    print(f"\n3️⃣ APLICANDO CONCENTRACIÓN...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    print(f"\n4️⃣ VERIFICANDO OFFSETS:")
    for sid in range(2):
        if sid in engine._source_motions:
            motion = engine._source_motions[sid]
            print(f"   F{sid}:")
            print(f"      - concentration_offset: {motion.concentration_offset}")
            print(f"      - hasattr(get_position): {hasattr(motion, 'get_position')}")
    
    print(f"\n5️⃣ EJECUTANDO STEP()...")
    if hasattr(engine, 'step'):
        engine.step()
    elif hasattr(engine, 'update'):
        engine.update(engine.dt)
    
    print(f"\n6️⃣ POSICIONES FINALES:")
    print(f"   F0: {engine._positions[0]}")
    print(f"   F1: {engine._positions[1]}")
    
    # Análisis
    mov0 = np.linalg.norm(engine._positions[0] - np.array([-4., 0., 0.]))
    mov1 = np.linalg.norm(engine._positions[1] - np.array([0., 0., 0.]))
    
    print(f"\n📊 MOVIMIENTO:")
    print(f"   F0: {mov0:.6f}")
    print(f"   F1: {mov1:.6f}")
    
    if mov0 > 0.001:
        print("\n✅ ¡FUNCIONA!")
    else:
        print("\n❌ NO FUNCIONA")
        
        # Debug manual
        print("\n🔍 DEBUG MANUAL:")
        motion0 = engine._source_motions[0]
        print(f"   motion0.state.position: {motion0.state.position}")
        print(f"   motion0.concentration_offset: {motion0.concentration_offset}")
        print(f"   Suma manual: {motion0.state.position + motion0.concentration_offset}")
        
        if hasattr(motion0, 'get_position'):
            print(f"   motion0.get_position(): {motion0.get_position()}")
            
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Restaurar archivo sin debug
print("\n\n🔧 RESTAURANDO ARCHIVO SIN DEBUG...")
with open(backup_name, 'r', encoding='utf-8') as f:
    original_content = f.read()

with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(original_content)

print("✅ Archivo restaurado")

print("""
================================================================================
📋 ANÁLISIS DEL DEBUG
================================================================================

Si ves que:
- get_position() NO se llama → El problema está en la condición hasattr
- get_position() SÍ se llama pero devuelve posición sin offset → Problema en get_position()
- La asignación muestra el valor correcto pero no se refleja → Problema después

🔧 SOLUCIÓN DIRECTA:
Edita enhanced_trajectory_engine.py, busca la línea ~1265 donde está:
   self._positions[sid] = pos

Y cámbiala por:
   # APLICAR OFFSETS DIRECTAMENTE
   final_pos = pos
   if sid in self._source_motions:
       motion = self._source_motions[sid]
       if hasattr(motion, 'concentration_offset'):
           final_pos = final_pos + motion.concentration_offset
   self._positions[sid] = final_pos

Esto garantiza que SIEMPRE se apliquen los offsets.
================================================================================
""")