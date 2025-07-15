#!/usr/bin/env python3
"""
🔧 FIX ERROR DE SINTAXIS EN ENHANCED_TRAJECTORY_ENGINE.PY
"""

import os
import re

print("""
================================================================================
🔧 ARREGLANDO ERROR DE SINTAXIS
================================================================================
Error detectado en línea 21 de enhanced_trajectory_engine.py
Vamos a diagnosticar y arreglar...
================================================================================
""")

# 1. Leer el archivo
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
print(f"\n📋 Leyendo {engine_file}...")

try:
    with open(engine_file, 'r') as f:
        lines = f.readlines()
except Exception as e:
    print(f"❌ Error leyendo archivo: {e}")
    exit(1)

# 2. Examinar las líneas alrededor del error
print("\n🔍 Examinando líneas 15-25:")
print("-" * 50)
for i in range(14, min(25, len(lines))):
    print(f"{i+1:3d}: {lines[i]}", end='')

# 3. Buscar el problema
print("\n\n🔍 Diagnosticando problema...")

# Verificar si falta cerrar paréntesis, corchete o comilla en líneas anteriores
problem_found = False
fix_applied = False

# Buscar líneas con imports
for i in range(min(30, len(lines))):
    line = lines[i]
    
    # Si es la línea problemática
    if i == 20 and "from trajectory_hub.core.concentration_component" in line:
        # Verificar la línea anterior
        prev_line = lines[i-1] if i > 0 else ""
        
        # Contar paréntesis, corchetes, etc.
        open_parens = prev_line.count('(') - prev_line.count(')')
        open_brackets = prev_line.count('[') - prev_line.count(']')
        open_braces = prev_line.count('{') - prev_line.count('}')
        
        if open_parens > 0:
            print(f"❌ Línea {i}: Paréntesis sin cerrar")
            problem_found = True
            # Arreglar: cerrar paréntesis
            if not prev_line.rstrip().endswith(')'):
                lines[i-1] = prev_line.rstrip() + ')\n'
                fix_applied = True
                print(f"✅ Añadido ')' al final de línea {i}")
        
        # Verificar si falta algo más
        if prev_line.strip() and not prev_line.strip().endswith((',', ')', ']', '}', ':')):
            # Verificar si es un import largo
            if 'from' in prev_line or 'import' in prev_line:
                if '(' in prev_line and ')' not in prev_line:
                    # Es un import multilínea mal cerrado
                    print(f"❌ Import multilínea sin cerrar en línea {i}")
                    problem_found = True

# 4. Buscar patrones específicos de imports mal formateados
if not fix_applied:
    for i in range(min(30, len(lines))):
        line = lines[i]
        
        # Buscar imports con problemas
        if 'from' in line and 'import' in line:
            # Verificar formato
            if line.count('(') > line.count(')'):
                # Import multilínea sin cerrar
                j = i + 1
                while j < len(lines) and ')' not in lines[j]:
                    j += 1
                
                if j >= len(lines) or (j < len(lines) and 'from' in lines[j]):
                    # No se cerró el paréntesis antes del siguiente import
                    print(f"❌ Import multilínea sin cerrar en línea {i+1}")
                    
                    # Buscar dónde insertar el cierre
                    insert_at = i + 1
                    while insert_at < len(lines) and lines[insert_at].strip() and not lines[insert_at].strip().startswith('from'):
                        insert_at += 1
                    
                    # Insertar cierre
                    if insert_at > i + 1:
                        lines[insert_at-1] = lines[insert_at-1].rstrip() + ')\n'
                        fix_applied = True
                        print(f"✅ Añadido ')' al final de línea {insert_at}")
                        break

# 5. Si no encontramos el problema específico, intentar un arreglo más general
if not fix_applied:
    print("\n🔧 Aplicando arreglo general...")
    
    # Buscar la línea exacta del error
    for i, line in enumerate(lines):
        if i == 20 and "from trajectory_hub.core.concentration_component" in line:
            # Asegurarse de que el import esté bien formateado
            if not line.strip().startswith('from'):
                # Hay algo antes del from
                lines[i] = 'from trajectory_hub.core.concentration_component import ConcentrationComponent\n'
            else:
                # Verificar que esté completo
                if 'import' not in line:
                    lines[i] = 'from trajectory_hub.core.concentration_component import ConcentrationComponent\n'
            
            fix_applied = True
            print(f"✅ Línea {i+1} reformateada")
            break

# 6. Guardar cambios si se aplicó algún fix
if fix_applied:
    print("\n💾 Guardando cambios...")
    
    # Backup
    backup_name = f"{engine_file}.backup_syntax_fix"
    with open(backup_name, 'w') as f:
        f.writelines(lines)
    
    # Guardar arreglado
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Archivo arreglado")
    print(f"✅ Backup guardado en: {backup_name}")
else:
    print("\n⚠️ No se pudo identificar automáticamente el problema")
    print("Intentando arreglo manual...")
    
    # Mostrar contexto más amplio
    print("\n📋 Contexto ampliado (líneas 10-30):")
    print("-" * 70)
    for i in range(9, min(30, len(lines))):
        print(f"{i+1:3d}: {lines[i]}", end='')

# 7. Verificar sintaxis del archivo
print("\n\n🧪 VERIFICANDO SINTAXIS...")
print("-" * 50)

import ast
import traceback

try:
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Intentar parsear
    ast.parse(content)
    print("✅ ¡Sintaxis correcta! El archivo ahora es válido.")
    
except SyntaxError as e:
    print(f"❌ Todavía hay error de sintaxis:")
    print(f"   Línea {e.lineno}: {e.msg}")
    print(f"   Texto: {e.text}")
    
    # Intentar un arreglo más agresivo
    print("\n🔧 Aplicando arreglo agresivo...")
    
    # Recargar líneas
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar todos los imports y asegurarse de que estén bien
    for i in range(min(50, len(lines))):
        line = lines[i]
        
        if 'from' in line and 'import' in line:
            # Verificar que el import esté en una sola línea
            if '(' in line:
                # Es multilínea, buscar el cierre
                if ')' not in line:
                    # Buscar en las siguientes líneas
                    j = i + 1
                    parts = [line.strip()]
                    
                    while j < len(lines) and ')' not in lines[j]:
                        parts.append(lines[j].strip())
                        j += 1
                    
                    if j < len(lines):
                        parts.append(lines[j].strip())
                        
                    # Unir todo en una línea
                    full_import = ' '.join(parts).replace('  ', ' ')
                    lines[i] = full_import + '\n'
                    
                    # Eliminar las líneas extras
                    for k in range(i+1, j+1):
                        if k < len(lines):
                            lines[k] = ''
                    
                    print(f"✅ Import multilínea convertido a una línea en {i+1}")
    
    # Guardar versión limpia
    with open(engine_file, 'w') as f:
        # Escribir solo líneas no vacías
        for line in lines:
            if line.strip() or line == '\n':
                f.write(line)
    
    print("✅ Archivo limpiado y guardado")

print("""

================================================================================
✅ PROCESO COMPLETADO
================================================================================

PRÓXIMO PASO:
Ejecutar nuevamente el test:
python test_concentration_delta.py

Si aún hay errores, verificar manualmente el archivo.
================================================================================
""")