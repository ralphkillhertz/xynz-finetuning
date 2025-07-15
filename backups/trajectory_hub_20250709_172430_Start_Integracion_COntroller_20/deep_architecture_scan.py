import os
import re
from pathlib import Path

def deep_scan():
    """Escanear toda la arquitectura para entender el flujo real"""
    print("🔍 ESCANEO PROFUNDO DE ARQUITECTURA")
    print("="*60)
    
    # 1. Buscar dónde se calculan las formaciones
    print("\n1️⃣ BUSCANDO CÁLCULO DE FORMACIONES...")
    formation_files = find_formation_calculations()
    
    # 2. Buscar el flujo de creación de macros
    print("\n2️⃣ BUSCANDO FLUJO DE CREACIÓN DE MACROS...")
    macro_flow = find_macro_creation_flow()
    
    # 3. Buscar dónde sphere está siendo mapeado a circle
    print("\n3️⃣ BUSCANDO MAPEO SPHERE → CIRCLE...")
    sphere_mapping = find_sphere_mapping()
    
    # 4. Generar reporte
    generate_report(formation_files, macro_flow, sphere_mapping)

def find_formation_calculations():
    """Buscar dónde se calculan realmente las formaciones"""
    results = {}
    
    # Patrones a buscar
    patterns = [
        r'_calculate_\w+_positions',
        r'_create_\w+_formation',
        r'def.*circle.*position',
        r'def.*sphere.*position',
        r'formation.*=.*circle|line|grid',
        r'positions\s*=.*calculate'
    ]
    
    # Buscar en todos los archivos Python
    for root, dirs, files in os.walk("trajectory_hub"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if filepath not in results:
                                results[filepath] = []
                            
                            line_num = content[:match.start()].count('\n') + 1
                            results[filepath].append({
                                'line': line_num,
                                'text': match.group(0),
                                'pattern': pattern
                            })
                except:
                    pass
    
    # Mostrar resultados
    for filepath, matches in results.items():
        print(f"\n📄 {filepath}")
        for match in matches[:3]:  # Primeros 3
            print(f"   L{match['line']}: {match['text']}")
    
    return results

def find_macro_creation_flow():
    """Encontrar el flujo real de creación de macros"""
    flow = {}
    
    # Buscar métodos relacionados con crear macro
    patterns = [
        r'def.*create.*macro',
        r'def.*handle.*create',
        r'formation.*choice',
        r'if.*formation.*==.*"sphere"',
        r'elif.*formation.*==.*"sphere"',
        r'case.*"sphere"'
    ]
    
    for root, dirs, files in os.walk("trajectory_hub"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            
                            if filepath not in flow:
                                flow[filepath] = []
                            
                            # Contexto
                            start = max(0, line_num - 3)
                            end = min(len(lines), line_num + 3)
                            context = '\n'.join(f"   {i+1}: {lines[i]}" 
                                              for i in range(start, end))
                            
                            flow[filepath].append({
                                'line': line_num,
                                'match': match.group(0),
                                'context': context
                            })
                except:
                    pass
    
    return flow

def find_sphere_mapping():
    """Buscar dónde sphere está siendo mapeado"""
    mappings = []
    
    # Buscar archivos que contengan "sphere"
    for root, dirs, files in os.walk("trajectory_hub"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    if 'sphere' in content:
                        # Buscar líneas específicas
                        for i, line in enumerate(lines):
                            if 'sphere' in line.lower():
                                # Verificar si está cerca de 'circle'
                                context_start = max(0, i-5)
                                context_end = min(len(lines), i+5)
                                context = '\n'.join(lines[context_start:context_end])
                                
                                if 'circle' in context:
                                    mappings.append({
                                        'file': filepath,
                                        'line': i+1,
                                        'text': line.strip(),
                                        'context': context
                                    })
                except:
                    pass
    
    return mappings

def generate_report(formation_files, macro_flow, sphere_mapping):
    """Generar reporte con solución"""
    print("\n" + "="*60)
    print("📊 REPORTE DE ARQUITECTURA")
    print("="*60)
    
    # Archivo principal de formaciones
    if formation_files:
        main_file = max(formation_files.items(), 
                       key=lambda x: len(x[1]))[0]
        print(f"\n🎯 ARCHIVO PRINCIPAL DE FORMACIONES:")
        print(f"   {main_file}")
        
        # Verificar si tiene sphere
        with open(main_file, 'r') as f:
            content = f.read()
        
        if '_calculate_sphere' not in content and '_create_sphere' not in content:
            print("   ❌ NO tiene implementación de sphere")
            print(f"\n💡 SOLUCIÓN: Añadir sphere a {main_file}")
            
            # Generar script de fix específico
            generate_fix_script(main_file, formation_files, macro_flow)
    
    # Mapeos incorrectos
    if sphere_mapping:
        print(f"\n⚠️ POSIBLES MAPEOS SPHERE → CIRCLE:")
        for mapping in sphere_mapping[:3]:
            print(f"   {mapping['file']}:{mapping['line']}")
            print(f"   {mapping['text']}")

def generate_fix_script(main_file, formation_files, macro_flow):
    """Generar script de fix específico"""
    print("\n🔧 GENERANDO SOLUCIÓN...")
    
    fix_content = f'''import os
import re
from datetime import datetime
import shutil

def fix_sphere():
    """Implementar sphere en el archivo correcto"""
    print("🔧 IMPLEMENTANDO SPHERE 3D")
    
    # Archivo principal
    main_file = "{main_file}"
    
    # Backup
    backup = f"{{main_file}}.backup_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    shutil.copy(main_file, backup)
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Buscar dónde añadir sphere
    if "_calculate_circle_positions" in content:
        # Añadir después de circle
        sphere_method = \'\'\'
def _calculate_sphere_positions(self, n_sources, center=(0, 0, 0), radius=2.0):
    """Calcular posiciones en esfera 3D"""
    import numpy as np
    
    positions = []
    golden_angle = np.pi * (3.0 - np.sqrt(5.0))
    
    for i in range(n_sources):
        y = 1 - (i / float(n_sources - 1)) * 2 if n_sources > 1 else 0
        radius_at_y = np.sqrt(1 - y * y)
        theta = golden_angle * i
        
        x = np.cos(theta) * radius_at_y
        z = np.sin(theta) * radius_at_y
        
        positions.append((
            center[0] + x * radius,
            center[1] + y * radius,
            center[2] + z * radius
        ))
    
    return positions
\'\'\'
        
        # Insertar después de circle
        circle_end = content.find("return positions", 
                                content.find("_calculate_circle_positions"))
        if circle_end > 0:
            insert_pos = content.find("\\n\\n", circle_end) + 2
            content = content[:insert_pos] + sphere_method + content[insert_pos:]
            
            print("✅ Método sphere añadido")
    
    # Buscar donde se mapean las formaciones
    # Añadir sphere donde sea necesario
    
    with open(main_file, 'w') as f:
        f.write(content)
    
    print("✅ Sphere implementado")

if __name__ == "__main__":
    fix_sphere()
'''
    
    with open("fix_sphere_specific.py", 'w') as f:
        f.write(fix_content)
    
    print("✅ Script generado: fix_sphere_specific.py")

if __name__ == "__main__":
    deep_scan()