#!/usr/bin/env python3
"""
🔍 ENCONTRAR - Dónde se almacenan las fuentes
⚡ Buscar en el engine dónde están realmente
"""

import os
import re

def find_sources_storage():
    """Encontrar dónde y cómo se almacenan las fuentes"""
    
    print("🔍 BUSCANDO ALMACENAMIENTO DE FUENTES\n")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Buscar create_source
    print("1️⃣ ANALIZANDO create_source()...")
    
    create_source_pattern = r'def create_source.*?\n(.*?)(?=\n    def|\nclass|\Z)'
    create_match = re.search(create_source_pattern, content, re.DOTALL)
    
    if create_match:
        create_method = create_match.group(0)
        print("✅ Método create_source encontrado")
        
        # Ver qué hace con la fuente creada
        lines = create_method.split('\n')
        for i, line in enumerate(lines[:20]):  # Primeras 20 líneas
            if '=' in line and ('source' in line.lower() or 'Source' in line):
                print(f"   → {line.strip()}")
            if 'self.' in line and '=' in line:
                print(f"   → {line.strip()}")
    
    # 2. Buscar __init__
    print("\n2️⃣ ANALIZANDO __init__()...")
    
    init_pattern = r'def __init__\(self.*?\):\s*\n(.*?)(?=\n    def|\nclass|\Z)'
    init_match = re.search(init_pattern, content, re.DOTALL)
    
    if init_match:
        init_method = init_match.group(0)
        
        # Buscar inicializaciones de diccionarios/listas
        dict_inits = re.findall(r'self\.(\w+)\s*=\s*(?:\{\}|dict\(\)|DefaultDict|\[\])', init_method)
        print("   Contenedores inicializados:")
        for container in dict_inits:
            print(f"   • self.{container}")
            
            # Ver si este contenedor se usa para fuentes
            if re.search(rf'self\.{container}\[.*?\]\s*=.*?[Ss]ource', content):
                print(f"     ✅ USADO PARA FUENTES")
    
    # 3. Buscar patrones de almacenamiento
    print("\n3️⃣ BUSCANDO PATRONES DE ALMACENAMIENTO...")
    
    # Buscar asignaciones tipo self.algo[id] = source
    storage_patterns = re.findall(r'self\.(\w+)\[([^\]]+)\]\s*=\s*([^\n]+)', content)
    
    source_containers = set()
    for container, key, value in storage_patterns:
        if 'source' in value.lower() or 'Source' in value:
            source_containers.add(container)
            print(f"   → self.{container}[{key}] = {value.strip()}")
    
    if source_containers:
        print(f"\n✅ Contenedores de fuentes encontrados: {list(source_containers)}")
    
    # 4. Buscar en create_macro
    print("\n4️⃣ ANALIZANDO create_macro()...")
    
    create_macro_pattern = r'def create_macro.*?\n(.*?)(?=\n    def|\nclass|\Z)'
    macro_match = re.search(create_macro_pattern, content, re.DOTALL)
    
    if macro_match:
        macro_method = macro_match.group(0)
        
        # Ver si create_macro llama a create_source
        if 'create_source' in macro_method:
            print("   ✅ create_macro llama a create_source")
            
            # Ver qué hace con el resultado
            source_creation = re.findall(r'(\w+)\s*=\s*self\.create_source', macro_method)
            if source_creation:
                print(f"   → Guarda en variable: {source_creation}")
    
    # 5. Buscar métodos que accedan a fuentes
    print("\n5️⃣ MÉTODOS QUE ACCEDEN A FUENTES...")
    
    # Buscar métodos que iteren sobre fuentes
    for_patterns = re.findall(r'for\s+(\w+)(?:,\s*(\w+))?\s+in\s+self\.(\w+)(?:\.items\(\)|\.values\(\))?:', content)
    
    for pattern in for_patterns:
        if 'source' in pattern[0].lower() or (len(pattern) > 1 and pattern[1] and 'source' in pattern[1].lower()):
            container = pattern[2]
            print(f"   → Itera sobre self.{container}")
    
    # 6. Generar script de prueba específico
    print("\n6️⃣ GENERANDO SCRIPT DE PRUEBA...")
    
    test_script = f'''#!/usr/bin/env python3
"""
🧪 Test específico basado en lo encontrado
"""

import os
import sys

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# Ver todos los atributos del engine
print("\\n📊 Atributos del engine:")
for attr in dir(engine):
    if not attr.startswith('_'):
        value = getattr(engine, attr)
        if isinstance(value, (dict, list)) and not callable(value):
            print(f"   • {attr}: {type(value).__name__} con {len(value)} elementos")

# Crear macro
macro_id = engine.create_macro("test", source_count=2)
print(f"\\n✅ Macro creado: {macro_id}")

# Ver qué cambió
print("\\n📊 Después de crear macro:")
for attr in dir(engine):
    if not attr.startswith('_'):
        value = getattr(engine, attr)
        if isinstance(value, (dict, list)) and not callable(value) and len(value) > 0:
            print(f"   • {attr}: {type(value).__name__} con {len(value)} elementos")
            
            # Si es un dict, mostrar las claves
            if isinstance(value, dict) and len(value) < 10:
                print(f"     Claves: {list(value.keys())}")

# Intentar acceder a fuentes por los contenedores encontrados
print("\\n🔍 Buscando fuentes en contenedores...")
'''
    
    # Agregar búsqueda para cada contenedor encontrado
    for container in source_containers:
        test_script += f'''
if hasattr(engine, '{container}'):
    container = engine.{container}
    print(f"\\n   → engine.{container}: {{len(container)}} elementos")
    if container:
        first_key = list(container.keys())[0]
        first_item = container[first_key]
        print(f"     Primer elemento: {{type(first_item).__name__}}")
        if hasattr(first_item, 'motion'):
            print(f"     → tiene motion: {{type(first_item.motion).__name__}}")
        if hasattr(first_item, 'get_position'):
            pos = first_item.get_position()
            print(f"     → get_position(): {{pos}}")
'''
    
    with open("test_find_sources.py", 'w') as f:
        f.write(test_script)
    
    print("   ✅ Script creado: test_find_sources.py")
    
    return source_containers

if __name__ == "__main__":
    containers = find_sources_storage()
    
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    if containers:
        print(f"\n✅ Probables contenedores de fuentes: {list(containers)}")
        print("\n🚀 Ejecuta el test para verificar:")
        print("   python test_find_sources.py")
    else:
        print("\n⚠️  No se encontraron contenedores obvios")
        print("   Las fuentes podrían estar en una estructura más compleja")