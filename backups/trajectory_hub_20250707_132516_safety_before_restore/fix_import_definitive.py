#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO - ARREGLAR IMPORTS DUPLICADOS
"""

import os
import re
from datetime import datetime

print("""
================================================================================
🔧 FIX DEFINITIVO DE IMPORTS
================================================================================
Problema identificado: Dos declaraciones 'from' seguidas
Vamos a reorganizar los imports correctamente
================================================================================
""")

# 1. Leer el archivo
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
print(f"📋 Leyendo {engine_file}...")

with open(engine_file, 'r') as f:
    content = f.read()

# Backup
backup_name = f"{engine_file}.backup_definitive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w') as f:
    f.write(content)
print(f"✅ Backup creado: {backup_name}")

# 2. Buscar y arreglar el problema específico
print("\n🔍 Buscando imports problemáticos...")

# Patrón para encontrar el import problemático
pattern = r'from trajectory_hub\.core\.motion_components import \(\s*from trajectory_hub\.core\.concentration_component import ConcentrationComponent'

if re.search(pattern, content):
    print("✅ Encontrado el problema: dos 'from' seguidos")
    
    # Estrategia: Separar los imports correctamente
    # Primero, encontrar todos los imports de motion_components
    motion_imports_pattern = r'from trajectory_hub\.core\.motion_components import \([^)]*\)'
    motion_match = re.search(motion_imports_pattern, content, re.DOTALL)
    
    if motion_match:
        # Extraer el contenido del import
        import_content = motion_match.group(0)
        
        # Eliminar el "from concentration_component" erróneo del medio
        import_content = re.sub(
            r'from trajectory_hub\.core\.concentration_component import ConcentrationComponent\s*',
            '',
            import_content
        )
        
        # Reemplazar en el contenido
        content = content[:motion_match.start()] + import_content + content[motion_match.end():]
        
        # Ahora añadir el import de concentration_component correctamente DESPUÉS
        # Buscar dónde termina el import de motion_components
        insert_pos = content.find(import_content) + len(import_content)
        
        # Buscar el siguiente salto de línea
        next_newline = content.find('\n', insert_pos)
        if next_newline > 0:
            # Insertar el import correcto
            concentration_import = "\nfrom trajectory_hub.core.concentration_component import ConcentrationComponent"
            content = content[:next_newline] + concentration_import + content[next_newline:]
            print("✅ Import de ConcentrationComponent añadido correctamente")

else:
    # Buscar patrón alternativo
    print("🔍 Buscando patrón alternativo...")
    
    # Buscar líneas específicas
    lines = content.split('\n')
    fixed_lines = []
    skip_next = False
    import_block = []
    in_multiline_import = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # Detectar inicio de import multilínea
        if 'from trajectory_hub.core.motion_components import (' in line:
            in_multiline_import = True
            import_block = [line]
            continue
            
        # Si estamos en import multilínea
        if in_multiline_import:
            # Si encontramos otro 'from' dentro del import
            if line.strip().startswith('from '):
                # Este es el import de concentration que está mal ubicado
                # Lo guardaremos para ponerlo después
                concentration_line = line.strip()
                continue
            
            # Si encontramos el cierre del paréntesis
            if ')' in line:
                import_block.append(line)
                in_multiline_import = False
                
                # Añadir todo el bloque de import
                fixed_lines.extend(import_block)
                
                # Añadir el import de concentration después
                fixed_lines.append('from trajectory_hub.core.concentration_component import ConcentrationComponent')
                continue
            
            # Línea normal del import multilínea
            import_block.append(line)
            continue
            
        # Línea normal
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)

# 3. Limpiar imports duplicados o mal formateados
print("\n🧹 Limpiando imports...")

# Asegurarse de que no haya imports vacíos
content = re.sub(r'from\s+\S+\s+import\s*\(\s*\)', '', content)

# Eliminar líneas vacías múltiples
content = re.sub(r'\n\n\n+', '\n\n', content)

# 4. Guardar el archivo arreglado
print("\n💾 Guardando archivo corregido...")
with open(engine_file, 'w') as f:
    f.write(content)

# 5. Verificar sintaxis
print("\n🧪 VERIFICANDO SINTAXIS...")
print("-" * 50)

import ast
import sys

try:
    ast.parse(content)
    print("✅ ¡SINTAXIS CORRECTA!")
    
    # Verificar que podemos importar
    print("\n🧪 Verificando import...")
    try:
        # Limpiar cache de imports
        if 'trajectory_hub.core.enhanced_trajectory_engine' in sys.modules:
            del sys.modules['trajectory_hub.core.enhanced_trajectory_engine']
        
        # Intentar importar
        import trajectory_hub.core.enhanced_trajectory_engine
        print("✅ ¡Import exitoso!")
        
    except Exception as e:
        print(f"⚠️ Error al importar: {e}")
        print("   Pero la sintaxis es correcta, el error puede ser de otro módulo")
    
except SyntaxError as e:
    print(f"❌ Error de sintaxis:")
    print(f"   Línea {e.lineno}: {e.msg}")
    print(f"   {e.text}")
    
    # Mostrar contexto
    lines = content.split('\n')
    if e.lineno:
        print("\n📋 Contexto del error:")
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        for i in range(start, end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"{marker} {i+1:3d}: {lines[i]}")

print("""

================================================================================
✅ PROCESO COMPLETADO
================================================================================

PRÓXIMOS PASOS:
1. python continue_implementation.py
2. python test_concentration_delta.py

Si aún hay problemas, verifica manualmente los imports en las líneas 19-25.
================================================================================
""")