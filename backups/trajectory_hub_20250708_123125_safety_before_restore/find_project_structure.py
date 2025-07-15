# === find_project_structure.py ===
# 🎯 Encontrar todos los archivos del proyecto
# ⚡ Búsqueda recursiva completa

import os
import subprocess

print("🔍 Buscando TODOS los archivos .py en el proyecto...\n")

# Buscar recursivamente
for root, dirs, files in os.walk('.'):
    # Saltar directorios ocultos y __pycache__
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    
    for file in files:
        if file.endswith('.py') and not file.startswith('.'):
            path = os.path.join(root, file)
            # Mostrar solo archivos relevantes
            if any(name in file for name in ['engine', 'motion', 'component', 'trajectory']):
                size = os.path.getsize(path)
                print(f"{path} ({size:,} bytes)")

print("\n" + "="*50)
print("\n🔍 Analizando test_rotation_ms_final.py para ver cómo importa...\n")

# Ver los imports del test que sí funciona
with open('test_rotation_ms_final.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:20]):  # Primeras 20 líneas
        if 'import' in line or 'from' in line:
            print(f"Línea {i+1}: {line.strip()}")

print("\n" + "="*50)
print("\n🔍 Buscando el patrón 'component.enabled' en TODOS los archivos...\n")

# Buscar el patrón problemático usando grep
try:
    result = subprocess.run(
        ['grep', '-r', '-n', 'component\.enabled', '.', '--include=*.py'],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("Encontrado en:")
        for line in result.stdout.strip().split('\n')[:10]:  # Primeras 10 coincidencias
            if '__pycache__' not in line:
                print(f"  {line}")
        
        # Buscar específicamente if component.enabled
        print("\n🔍 Buscando 'if component.enabled'...\n")
        result2 = subprocess.run(
            ['grep', '-r', '-n', 'if component\.enabled', '.', '--include=*.py'],
            capture_output=True,
            text=True
        )
        
        if result2.stdout:
            print("Comparaciones directas encontradas en:")
            for line in result2.stdout.strip().split('\n'):
                if '__pycache__' not in line and 'isinstance' not in line:
                    print(f"  {line}")
except:
    print("grep no disponible, buscando manualmente...")
    
    # Búsqueda manual
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if 'if component.enabled' in content:
                            # Encontrar número de línea
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'if component.enabled' in line and 'isinstance' not in line:
                                    print(f"{filepath}:{i+1}: {line.strip()}")
                except:
                    pass