#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO: Por qué los deltas no se aplican
"""

import os
import re

print("=" * 80)
print("🔍 DIAGNÓSTICO DE APLICACIÓN DE DELTAS")
print("=" * 80)

# 1. Verificar que el fix se aplicó
print("\n1️⃣ VERIFICANDO QUE EL FIX SE APLICÓ...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar el código agregado
    if "APLICAR DELTAS ACUMULADOS" in content:
        print("✅ Código de aplicación de deltas encontrado")
        
        # Encontrar dónde está
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "APLICAR DELTAS ACUMULADOS" in line:
                print(f"   Ubicado en línea {i+1}")
                
                # Mostrar contexto
                print("\n   Contexto del código:")
                for j in range(max(0, i-5), min(len(lines), i+20)):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j+1:4d}: {lines[j][:80]}")
    else:
        print("❌ NO se encontró el código de aplicación de deltas")

# 2. Buscar el problema real
print("\n\n2️⃣ ANALIZANDO ESTRUCTURA DEL UPDATE...")

# Buscar cómo se actualiza cada fuente
update_patterns = [
    r'for.*in.*sources',
    r'for.*in.*range.*num_sources',
    r'for.*source.*in',
    r'motion\.update',
    r'_positions\[.*\].*=',
    r'send.*position'
]

print("\nPatrones de actualización encontrados:")
for pattern in update_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        print(f"\n   Patrón: {pattern}")
        for match in matches[:3]:
            print(f"      - {match[:60]}")

# 3. Verificar source_id
print("\n\n3️⃣ VERIFICANDO ASIGNACIÓN DE source_id...")

# El problema puede ser que todas las fuentes tienen source_id = 0
source_id_patterns = [
    r'source_id\s*=\s*',
    r'\.source_id\s*=',
    r'SourceMotion\(',
]

for pattern in source_id_patterns:
    matches = re.finditer(pattern, content)
    for match in list(matches)[:5]:
        line_num = content[:match.start()].count('\n') + 1
        line = lines[line_num-1].strip()
        print(f"   Línea {line_num}: {line[:80]}")

# 4. Crear fix mejorado
print("\n\n4️⃣ CREANDO FIX MEJORADO...")

fix_code = '''#!/usr/bin/env python3
"""
🔧 FIX MEJORADO: Aplicación correcta de deltas
"""

import os
import shutil
from datetime import datetime
import re

print("=" * 80)
print("🔧 FIX MEJORADO PARA APLICACIÓN DE DELTAS")
print("=" * 80)

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Backup
backup_dir = f"fix_deltas_v2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)
shutil.copy2(engine_file, os.path.join(backup_dir, os.path.basename(engine_file)))

# Leer archivo
with open(engine_file, 'r') as f:
    content = f.read()

# Primero, verificar si source_id se asigna correctamente
print("\\n1️⃣ VERIFICANDO ASIGNACIÓN DE source_id...")

# Buscar dónde se crean las SourceMotion
creation_pattern = r'(SourceMotion\\()(.*?)(\\))'
matches = list(re.finditer(creation_pattern, content))

if matches:
    print(f"   Encontradas {len(matches)} creaciones de SourceMotion")
    
    # Si no pasan source_id, agregarlo
    for match in matches:
        if 'source_id' not in match.group(2):
            print("   ⚠️ SourceMotion creado sin source_id")

# Buscar el método update principal donde se itera sobre las fuentes
print("\\n2️⃣ BUSCANDO LOOP PRINCIPAL DE FUENTES...")

lines = content.split('\\n')
main_loop_found = False

for i, line in enumerate(lines):
    # Buscar el loop principal
    if re.search(r'for\\s+i\\s+in\\s+range\\(.*num_sources', line):
        print(f"   Loop principal encontrado en línea {i+1}")
        
        # Verificar si hay aplicación de deltas después del loop
        loop_indent = len(line) - len(line.lstrip())
        
        # Buscar el final del loop
        for j in range(i+1, len(lines)):
            if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= loop_indent:
                # Fin del loop encontrado
                print(f"   Fin del loop en línea {j+1}")
                
                # Insertar aplicación de deltas AQUÍ
                if "APLICAR DELTAS" not in lines[j:j+10]:
                    delta_code = """
        # APLICAR DELTAS ACUMULADOS - V2
        try:
            from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
            
            # Aplicar deltas para TODAS las fuentes
            for idx in range(self.num_sources):
                # Obtener el source_id correcto
                if hasattr(self._source_motions[idx], 'source_id'):
                    sid = self._source_motions[idx].source_id
                else:
                    sid = idx  # Fallback al índice
                
                # Obtener y aplicar delta
                delta = compat.get_accumulated_delta(sid)
                if delta is not None:
                    # Aplicar a la posición
                    old_pos = self._positions[idx].copy()
                    self._positions[idx] += delta
                    
                    # Log solo para la primera fuente para no saturar
                    if idx == 0 and compat.config.get('LOG_DELTAS', False):
                        movement = np.linalg.norm(delta)
                        print(f"   [APPLIED] Source {sid}: moved {movement:.4f} from {old_pos} to {self._positions[idx]}")
                    
                    # Limpiar delta aplicado
                    compat.clear_deltas(sid)
                    
        except Exception as e:
            print(f"   ❌ Error applying deltas: {e}")
            import traceback
            traceback.print_exc()
"""
                    
                    # Insertar con la indentación correcta
                    indent_str = ' ' * loop_indent
                    indented_code = '\\n'.join(indent_str + line for line in delta_code.strip().split('\\n'))
                    
                    lines.insert(j, indented_code)
                    main_loop_found = True
                    print(f"   ✅ Código de aplicación insertado después del loop principal")
                
                break
        break

# También necesitamos asegurar que source_id se asigna correctamente
print("\\n3️⃣ ARREGLANDO ASIGNACIÓN DE source_id...")

# Buscar donde se crean las SourceMotion
for i, line in enumerate(lines):
    if 'SourceMotion()' in line:
        # Buscar el índice
        # Probablemente está en un loop como: for i in range(...)
        for j in range(max(0, i-10), i):
            if re.search(r'for\\s+(\\w+)\\s+in\\s+range', lines[j]):
                index_var = re.search(r'for\\s+(\\w+)\\s+in\\s+range', lines[j]).group(1)
                # Cambiar SourceMotion() por SourceMotion(source_id=i)
                lines[i] = lines[i].replace('SourceMotion()', f'SourceMotion(source_id={index_var})')
                print(f"   ✅ Corregido en línea {i+1}: SourceMotion(source_id={index_var})")
                break

# Guardar cambios
if main_loop_found:
    new_content = '\\n'.join(lines)
    
    # Asegurar import de numpy
    if 'import numpy as np' not in new_content:
        new_content = 'import numpy as np\\n' + new_content
    
    with open(engine_file, 'w') as f:
        f.write(new_content)
    
    print("\\n✅ FIX MEJORADO APLICADO")
else:
    print("\\n❌ No se pudo aplicar el fix automáticamente")

print("\\n" + "=" * 80)
print("REINICIA EL CONTROLADOR para aplicar cambios")
print("=" * 80)
'''

with open("fix_deltas_v2.py", 'w') as f:
    f.write(fix_code)

print("✅ Script de fix mejorado creado: fix_deltas_v2.py")

# 5. Solución alternativa
print("\n\n5️⃣ SOLUCIÓN ALTERNATIVA - DESACTIVAR MODO DUAL:")
print("-" * 60)

disable_code = '''import json
with open('trajectory_hub/config/parallel_config.json', 'r') as f:
    config = json.load(f)
config['CONCENTRATION_DUAL_MODE'] = False
with open('trajectory_hub/config/parallel_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print("✅ Modo dual DESACTIVADO - Reinicia el controlador")
'''

print("Para desactivar temporalmente el modo dual:")
print(disable_code)

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 80)

# Resumen del problema
print("\n🔍 PROBLEMA IDENTIFICADO:")
print("1. Los deltas se calculan solo para Source 0")
print("2. Posible causa: todas las fuentes tienen source_id = 0")
print("3. O el código de aplicación no se ejecuta en el lugar correcto")
print("\n💡 SOLUCIONES:")
print("1. Ejecutar: python fix_deltas_v2.py")
print("2. O desactivar modo dual temporalmente (ver arriba)")
print("=" * 80)