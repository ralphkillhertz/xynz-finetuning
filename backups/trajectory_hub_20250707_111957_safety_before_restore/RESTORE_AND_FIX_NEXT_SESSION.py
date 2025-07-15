#!/usr/bin/env python3
"""
🚀 INICIO RÁPIDO - Restaurar y aplicar fix de concentración
📅 Para usar en la próxima sesión
"""

import os
import shutil
import sys

print("""
================================================================================
🚀 RESTAURACIÓN Y FIX DE CONCENTRACIÓN
================================================================================
""")

# 1. Restaurar archivo desde backup
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_file = "trajectory_hub/core/enhanced_trajectory_engine.py.backup_final_20250707_030559"

if os.path.exists(backup_file):
    print(f"✅ Backup encontrado: {backup_file}")
    shutil.copy(backup_file, engine_file)
    print(f"✅ Archivo restaurado")
else:
    print(f"❌ Backup no encontrado")
    # Buscar otro backup
    import glob
    backups = glob.glob("trajectory_hub/core/enhanced_trajectory_engine.py.backup_*")
    if backups:
        backups.sort()
        print(f"   Usando backup alternativo: {backups[-1]}")
        shutil.copy(backups[-1], engine_file)
    else:
        print("❌ No hay backups disponibles")
        sys.exit(1)

# 2. Aplicar fix simple y directo
print("\n🔧 APLICANDO FIX SIMPLE...")

with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la línea donde se asigna _positions[sid] en update()
fix_applied = False
for i in range(1200, min(1400, len(lines))):
    if 'self._positions[sid] = ' in lines[i] and 'pos' in lines[i]:
        print(f"✅ Encontrada asignación en línea {i+1}")
        
        # Obtener indentación
        indent = len(lines[i]) - len(lines[i].lstrip())
        spaces = ' ' * indent
        
        # Reemplazar con aplicación directa de offsets
        new_code = f'''{spaces}# APLICACIÓN DIRECTA DE OFFSETS
{spaces}if sid in self._source_motions:
{spaces}    motion = self._source_motions[sid]
{spaces}    base_pos = pos if 'pos' in locals() else motion.state.position
{spaces}    if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
{spaces}        self._positions[sid] = base_pos + motion.concentration_offset
{spaces}    else:
{spaces}        self._positions[sid] = base_pos
{spaces}else:
{spaces}    self._positions[sid] = pos
'''
        
        lines[i] = new_code
        fix_applied = True
        break

if fix_applied:
    # Guardar
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Fix aplicado")
else:
    print("❌ No se encontró la línea a modificar")

# 3. Test rápido
print("\n🧪 TEST RÁPIDO...")

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
    
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
    
    print("Posiciones iniciales:", engine._positions[0], engine._positions[1])
    
    engine.set_macro_concentration(macro_id, 0.5)
    print("Offsets:", engine._source_motions[0].concentration_offset)
    
    if hasattr(engine, 'step'):
        engine.step()
    
    mov = np.linalg.norm(engine._positions[0] - np.array([-4., 0., 0.]))
    print(f"Movimiento: {mov:.4f}")
    
    if mov > 0.01:
        print("\\n✅ ¡FUNCIONA! La concentración se aplica")
    else:
        print("\\n❌ Aún no funciona")
        
except Exception as e:
    print(f"Error: {e}")
'''

exec(test_code)

print("""

================================================================================
📋 PRÓXIMOS PASOS
================================================================================

1. Si el test muestra movimiento > 0:
   ✅ La concentración funciona
   → Ejecuta: python trajectory_hub/interface/interactive_controller.py

2. Si NO hay movimiento:
   → Edita manualmente enhanced_trajectory_engine.py
   → Busca "self._positions[sid] =" cerca de la línea 1270
   → Asegúrate que sume motion.concentration_offset

3. Alternativa - Override completo:
   → Crea un nuevo step() que fuerce la aplicación
   → Ver código en SESSION_SUMMARY.md

💡 Recuerda: Los offsets se calculan bien, solo falta aplicarlos
================================================================================
""")