#!/usr/bin/env python3
"""
🔍 BÚSQUEDA EXACTA DE CONCENTRATION
"""

import os
import re

print("=" * 80)
print("🔍 BUSCANDO CONCENTRATION EN TODO EL PROYECTO")
print("=" * 80)

# Patrones a buscar
patterns = [
    r'class Concentration',
    r'def concentration',
    r'concentration_factor',
    r'concentration_control',
    r'apply_concentration',
    r'_concentration',
    r'\.concentration',
    r"'31'.*concentration",  # Opción 31 del menú
    r'"31".*concentration'
]

found_files = {}
menu_31_details = []

# Buscar en todos los archivos
for root, dirs, files in os.walk("trajectory_hub"):
    # Ignorar backups
    if 'backup' in root or '__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Buscar patrones
                matches = []
                for pattern in patterns:
                    for i, line in enumerate(lines):
                        if re.search(pattern, line, re.IGNORECASE):
                            matches.append({
                                'line_num': i + 1,
                                'line': line.strip()[:100],
                                'pattern': pattern
                            })
                            
                            # Si es opción 31, buscar más contexto
                            if "'31'" in line or '"31"' in line:
                                context = []
                                for j in range(max(0, i-5), min(len(lines), i+15)):
                                    context.append(f"{j+1:4d}: {lines[j]}")
                                menu_31_details.append({
                                    'file': filepath,
                                    'context': '\n'.join(context)
                                })
                
                if matches:
                    found_files[filepath] = matches
                    
            except Exception as e:
                print(f"Error leyendo {filepath}: {e}")

# Mostrar resultados organizados
print("\n📁 ARCHIVOS CON REFERENCIAS A CONCENTRATION:")
print("-" * 80)

# Priorizar archivos con definiciones de clase
class_files = []
implementation_files = []
reference_files = []

for filepath, matches in found_files.items():
    has_class = any('class Concentration' in m['line'] for m in matches)
    has_implementation = any('apply' in m['line'] or 'def' in m['line'] for m in matches)
    
    if has_class:
        class_files.append((filepath, matches))
    elif has_implementation:
        implementation_files.append((filepath, matches))
    else:
        reference_files.append((filepath, matches))

# Mostrar clases primero
if class_files:
    print("\n🎯 ARCHIVOS CON CLASE CONCENTRATION:")
    for filepath, matches in class_files:
        print(f"\n✅ {filepath}")
        for m in matches[:5]:  # Primeras 5 coincidencias
            print(f"   Línea {m['line_num']}: {m['line']}")

# Implementaciones
if implementation_files:
    print("\n🔧 ARCHIVOS CON IMPLEMENTACIÓN:")
    for filepath, matches in implementation_files[:5]:
        print(f"\n📄 {filepath}")
        for m in matches[:3]:
            print(f"   Línea {m['line_num']}: {m['line']}")

# Opción 31 del menú
if menu_31_details:
    print("\n🎮 OPCIÓN 31 DEL MENÚ (CONCENTRATION):")
    print("-" * 80)
    for detail in menu_31_details[:2]:  # Primeros 2
        print(f"\n📄 {detail['file']}")
        print(detail['context'])

# Buscar específicamente en rotation_system.py
print("\n🔍 VERIFICANDO rotation_system.py...")
rotation_file = None
for root, dirs, files in os.walk("trajectory_hub"):
    if "rotation_system.py" in files:
        rotation_file = os.path.join(root, "rotation_system.py")
        break

if rotation_file:
    print(f"✅ Encontrado: {rotation_file}")
    with open(rotation_file, 'r') as f:
        content = f.read()
    
    # Buscar Concentration aquí
    if 'Concentration' in content:
        print("   ✅ CONTIENE CONCENTRATION")
        
        # Extraer la clase
        class_match = re.search(r'class Concentration.*?(?=class|\Z)', content, re.DOTALL)
        if class_match:
            print("\n   ESTRUCTURA DE LA CLASE:")
            class_content = class_match.group(0)
            
            # Buscar métodos
            methods = re.findall(r'def (\w+)\(self', class_content)
            print(f"   Métodos: {', '.join(methods[:10])}")
            
            # Verificar si tiene apply
            if 'apply' in methods:
                print("   ✅ Tiene método apply()")
            
            # Verificar dependencias de IS
            if 'individual_trajectory' in class_content:
                print("   ⚠️ Parece depender de individual_trajectory")

# Resumen
print("\n" + "=" * 80)
print("RESUMEN DE BÚSQUEDA")
print("=" * 80)

total_files = len(found_files)
print(f"Total archivos con referencias: {total_files}")

if class_files:
    print(f"\n✅ CONCENTRATION ENCONTRADO EN:")
    for filepath, _ in class_files[:3]:
        print(f"   - {filepath}")
elif rotation_file and 'Concentration' in content:
    print(f"\n✅ CONCENTRATION ENCONTRADO EN:")
    print(f"   - {rotation_file}")
else:
    print("\n❌ No se encontró la clase Concentration")
    print("Posibles ubicaciones basadas en referencias:")
    for filepath, _ in list(implementation_files)[:3]:
        print(f"   - {filepath}")

print("\n💡 PRÓXIMO PASO: Modificar el script para buscar en la ubicación correcta")
print("=" * 80)