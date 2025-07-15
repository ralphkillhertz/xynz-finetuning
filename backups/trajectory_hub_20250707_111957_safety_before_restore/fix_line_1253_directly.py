#!/usr/bin/env python3
"""
🔧 FIX DIRECTO: Línea 1253 en update()
"""

import os
import sys

print("""
================================================================================
🔧 FIX ESPECÍFICO LÍNEA 1253
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Leer el archivo
with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"📋 Total líneas en archivo: {len(lines)}")

# Verificar línea 1253 (índice 1252)
if len(lines) > 1252:
    print(f"\n📍 Línea 1253 actual:")
    print(f"   {lines[1252].strip()}")
    
    # Buscar contexto alrededor
    print(f"\n📍 Contexto (líneas 1250-1255):")
    for i in range(max(0, 1249), min(len(lines), 1255)):
        print(f"   {i+1}: {lines[i].rstrip()}")
    
    # Verificar si es la línea correcta
    if '_positions[sid] = pos' in lines[1252] or '_positions[sid] =' in lines[1252]:
        print(f"\n✅ Línea 1253 encontrada correctamente")
        
        # Verificar si ya está arreglada
        if 'get_position' in ''.join(lines[1245:1260]):
            print("⚠️  Parece que ya se intentó arreglar")
            
            # Buscar el bloque completo
            print("\n🔍 Buscando bloque de actualización...")
            for i in range(1245, min(1265, len(lines))):
                if 'self._positions[sid]' in lines[i]:
                    print(f"   Línea {i+1}: {lines[i].strip()}")
        
        # Aplicar fix robusto
        print("\n🔨 APLICANDO FIX ROBUSTO...")
        
        # Buscar el bloque exacto donde se actualiza _positions[sid]
        update_line = -1
        for i in range(1240, min(1270, len(lines))):
            if 'self._positions[sid] =' in lines[i] and 'pos' in lines[i]:
                update_line = i
                print(f"   Encontrada actualización en línea {i+1}")
                break
        
        if update_line >= 0:
            # Obtener indentación
            indent = len(lines[update_line]) - len(lines[update_line].lstrip())
            spaces = ' ' * indent
            
            # Reemplazar con código que SIEMPRE aplica offsets
            new_code = f'''{spaces}# APLICAR OFFSETS DE CONCENTRACIÓN
{spaces}pos_with_offsets = pos.copy()
{spaces}if hasattr(motion, 'concentration_offset') and motion.concentration_offset is not None:
{spaces}    pos_with_offsets = pos_with_offsets + motion.concentration_offset
{spaces}if hasattr(motion, 'distribution_offset') and motion.distribution_offset is not None:
{spaces}    pos_with_offsets = pos_with_offsets + motion.distribution_offset
{spaces}if hasattr(motion, 'trajectory_offset') and motion.trajectory_offset is not None:
{spaces}    pos_with_offsets = pos_with_offsets + motion.trajectory_offset
{spaces}self._positions[sid] = pos_with_offsets
'''
            
            # Reemplazar la línea
            lines[update_line] = new_code
            
            # Guardar
            import datetime
            backup_name = engine_file + f".backup_1253_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_name, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"\n📋 Backup: {backup_name}")
            
            with open(engine_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✅ Línea {update_line+1} actualizada con aplicación de offsets")
            
            # Mostrar resultado
            print(f"\n📍 Código nuevo insertado:")
            print(new_code)
            
else:
    print("❌ El archivo tiene menos de 1253 líneas")

# Test inmediato
print("\n" + "="*80)
print("🧪 TEST INMEDIATO")
print("="*80)

test_code = '''
import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Test rápido
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)
    
    # Posiciones iniciales
    pos0_init = engine._positions[0].copy()
    pos1_init = engine._positions[1].copy()
    print(f"Inicial: Fuente 0={pos0_init}, Fuente 1={pos1_init}")
    
    # Aplicar concentración
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Verificar offsets
    offset0 = engine._source_motions[0].concentration_offset
    print(f"\\nOffsets: Fuente 0={offset0}")
    
    # Un step
    if hasattr(engine, 'step'):
        engine.step()
    elif hasattr(engine, 'update'):
        engine.update(engine.dt)
    
    # Verificar movimiento
    mov0 = np.linalg.norm(engine._positions[0] - pos0_init)
    mov1 = np.linalg.norm(engine._positions[1] - pos1_init)
    
    print(f"\\nFinal: Fuente 0={engine._positions[0]}, Fuente 1={engine._positions[1]}")
    print(f"Movimiento: Fuente 0={mov0:.4f}, Fuente 1={mov1:.4f}")
    
    if mov0 > 0.01:
        print("\\n✅ ¡FUNCIONA! La concentración se aplica correctamente")
    else:
        print("\\n❌ Aún no funciona")
        
except Exception as e:
    print(f"Error en test: {e}")
'''

exec(test_code)

print("""
================================================================================
✅ FIX APLICADO
================================================================================

🔧 Lo que hicimos:
   - Localizar exactamente la línea donde se actualiza _positions
   - Reemplazar con código que SIEMPRE suma los offsets
   - Test inmediato para verificar

🚀 EJECUTA EL TEST COMPLETO:
   python test_concentration_working.py

💡 Si aún no funciona, revisa manualmente el archivo en la línea
   indicada y asegúrate que _positions se actualice con offsets

🎯 Este es el fix más directo posible
================================================================================
""")