#!/usr/bin/env python3
"""
🔧 FIX SIMPLE Y DIRECTO - Aplicar deltas
"""

import os
import shutil
from datetime import datetime

print("=" * 80)
print("🔧 APLICANDO FIX SIMPLE PARA DELTAS")
print("=" * 80)

# Archivo a modificar
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Backup
backup_name = f"engine_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(engine_file, backup_name)
print(f"✅ Backup creado: {backup_name}")

# Leer archivo
with open(engine_file, 'r') as f:
    lines = f.readlines()

print(f"\n📄 Archivo tiene {len(lines)} líneas")

# Buscar el método update
print("\n🔍 BUSCANDO MÉTODO UPDATE...")

update_line = -1
for i, line in enumerate(lines):
    if 'def update(self' in line and 'fps' not in line:
        update_line = i
        print(f"✅ Método update encontrado en línea {i+1}")
        break

if update_line == -1:
    print("❌ No se encontró el método update")
    exit(1)

# Buscar el final del método update (antes del return o siguiente def)
end_of_update = -1
indent_level = len(lines[update_line]) - len(lines[update_line].lstrip())

for i in range(update_line + 1, len(lines)):
    line = lines[i]
    if line.strip() == '':
        continue
    
    current_indent = len(line) - len(line.lstrip())
    
    # Si encontramos algo al mismo nivel o menor que def update
    if current_indent <= indent_level and line.strip():
        end_of_update = i
        break
    
    # O si encontramos un return al nivel correcto
    if line.strip().startswith('return') and current_indent == indent_level + 4:
        end_of_update = i
        break

if end_of_update == -1:
    # No encontramos el final, usar las últimas líneas del archivo
    end_of_update = len(lines) - 1

print(f"✅ Fin del método en línea {end_of_update}")

# Insertar el código de aplicación de deltas ANTES del final del método
insert_position = end_of_update - 1

# Buscar una buena posición (después de actualizar todas las fuentes)
for i in range(end_of_update - 1, update_line, -1):
    if 'self._send_positions()' in lines[i] or 'send_position' in lines[i]:
        insert_position = i
        print(f"✅ Mejor posición encontrada: antes de línea {i+1}")
        break

# Código a insertar
delta_code = '''
        # ===== APLICAR DELTAS ACUMULADOS =====
        # Arquitectura paralela: aplicar todos los deltas calculados
        try:
            from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
            import numpy as np
            
            if compat.is_concentration_dual_mode():
                # Aplicar deltas para CADA fuente
                applied_count = 0
                
                for i in range(len(self._positions)):
                    # Intentar diferentes formas de obtener source_id
                    source_id = None
                    
                    # Método 1: desde _source_motions
                    if hasattr(self, '_source_motions') and i < len(self._source_motions):
                        if hasattr(self._source_motions[i], 'source_id'):
                            source_id = self._source_motions[i].source_id
                    
                    # Método 2: usar el índice directamente
                    if source_id is None:
                        source_id = i
                    
                    # Obtener delta acumulado
                    delta = compat.get_accumulated_delta(source_id)
                    
                    if delta is not None:
                        # Aplicar delta a la posición
                        self._positions[i] += delta
                        applied_count += 1
                        
                        # Limpiar delta aplicado
                        compat.clear_deltas(source_id)
                
                if applied_count > 0 and compat.config.get('LOG_DELTAS', False):
                    print(f"   ✅ Applied deltas to {applied_count} sources")
                    
        except Exception as e:
            print(f"   ❌ Error applying deltas: {e}")
        # ===== FIN APLICACIÓN DE DELTAS =====
'''

# Obtener la indentación correcta
base_indent = '        '  # 8 espacios típicamente para métodos

# Insertar el código
lines.insert(insert_position, delta_code)

# Guardar el archivo modificado
with open(engine_file, 'w') as f:
    f.writelines(lines)

print(f"\n✅ CÓDIGO INSERTADO en línea {insert_position}")

# Verificar que se guardó correctamente
with open(engine_file, 'r') as f:
    content = f.read()
    
if "APLICAR DELTAS ACUMULADOS" in content:
    print("✅ VERIFICACIÓN: El código se guardó correctamente")
else:
    print("❌ ERROR: El código no se guardó")

print("\n" + "=" * 80)
print("📋 RESUMEN:")
print("=" * 80)
print("1. ✅ Backup creado")
print("2. ✅ Código de aplicación de deltas insertado")
print("3. ✅ Archivo guardado")
print("\n⚡ REINICIA EL CONTROLADOR para ver los cambios")
print("\nSi algo sale mal, restaura desde:", backup_name)
print("=" * 80)