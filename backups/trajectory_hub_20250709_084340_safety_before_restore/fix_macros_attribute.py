# === fix_macros_attribute.py ===
# 🔧 Fix: Encontrar el nombre correcto del atributo de macros
# ⚡ Solución para 'no attribute macros'

import os
import re

def find_macro_storage():
    """Buscar cómo se almacenan los macros en el engine"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    print("🔍 Buscando almacenamiento de macros...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar patrones de almacenamiento de macros
    patterns = [
        r'self\._macros\s*=',
        r'self\.macros\s*=',
        r'self\.macro_\w+\s*=\s*\{',
        r'self\.\w*macro\w*\s*=\s*\{',
        r'Macro\(.*?\)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"✅ Encontrado: {matches}")
    
    # Buscar en __init__
    init_match = re.search(r'def __init__\(.*?\):(.*?)(?=\n    def|\Z)', content, re.DOTALL)
    if init_match:
        init_content = init_match.group(1)
        macro_lines = [line.strip() for line in init_content.split('\n') if 'macro' in line.lower()]
        print("\n📋 Líneas con 'macro' en __init__:")
        for line in macro_lines[:10]:  # Mostrar solo las primeras 10
            print(f"   {line}")
    
    # Buscar la clase Macro
    macro_class = re.search(r'class\s+Macro[^:]*:', content)
    if macro_class:
        print(f"\n✅ Encontrada clase: {macro_class.group()}")
    
    # Buscar en create_macro cómo se guarda
    create_macro_match = re.search(r'def create_macro\(.*?\):(.*?)(?=\n    def|\Z)', content, re.DOTALL)
    if create_macro_match:
        create_content = create_macro_match.group(1)
        # Buscar asignaciones
        assignments = re.findall(r'self\.(\w+)\[.*?\]\s*=.*?Macro', create_content)
        if assignments:
            print(f"\n✅ Macros se guardan en: self.{assignments[0]}")
            return assignments[0]
    
    return None

def fix_create_macro_return_correct():
    """Arreglar el return con el nombre correcto del atributo"""
    
    # Primero encontrar el nombre correcto
    macro_attr = find_macro_storage()
    
    if not macro_attr:
        print("⚠️ No se encontró automáticamente, buscando manualmente...")
        
        # Buscar manualmente
        file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar en create_macro
        in_create_macro = False
        for i, line in enumerate(lines):
            if 'def create_macro' in line:
                in_create_macro = True
            
            if in_create_macro and 'Macro(' in line:
                # Buscar la asignación
                if '=' in line and 'self.' in line:
                    match = re.search(r'self\.(\w+)\[', line)
                    if match:
                        macro_attr = match.group(1)
                        print(f"✅ Encontrado: macros se guardan en self.{macro_attr}")
                        break
    
    if macro_attr:
        # Ahora corregir el return
        file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup
        with open(f'{file_path}.backup_macro_attr', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Reemplazar
        content = content.replace('return self.macros[macro_id]', f'return self.{macro_attr}[macro_id]')
        content = content.replace('return self.macros[name]', f'return self.{macro_attr}[name]')
        content = content.replace('return self.macros[macro_name]', f'return self.{macro_attr}[macro_name]')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Returns corregidos para usar self.{macro_attr}")
        return macro_attr
    
    return None

def create_diagnostic_test():
    """Test de diagnóstico para verificar la estructura"""
    
    test_code = '''# === test_diagnostic.py ===
# 🔍 Diagnóstico de la estructura del engine

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print("🔍 DIAGNÓSTICO DEL ENGINE")
print("=" * 60)

# Listar atributos
print("\\nAtributos del engine que contienen 'macro':")
attrs = [attr for attr in dir(engine) if 'macro' in attr.lower()]
for attr in sorted(attrs):
    try:
        value = getattr(engine, attr)
        print(f"  {attr}: {type(value)}")
        if isinstance(value, dict) and len(value) == 0:
            print(f"    → Diccionario vacío (posible almacén de macros)")
    except:
        print(f"  {attr}: (no accesible)")

# Buscar específicamente _macros
print("\\nBuscando atributos privados:")
private_attrs = [attr for attr in dir(engine) if attr.startswith('_') and 'macro' in attr.lower()]
for attr in private_attrs:
    try:
        value = getattr(engine, attr)
        print(f"  {attr}: {type(value)}")
    except:
        pass

# Crear un macro y ver dónde se guarda
print("\\nCreando macro de prueba...")
result = engine.create_macro("test", 2)
print(f"create_macro retornó: {type(result)} = {result}")

# Buscar dónde se guardó
print("\\nBuscando el macro creado:")
for attr in dir(engine):
    try:
        value = getattr(engine, attr)
        if isinstance(value, dict) and "test" in value:
            print(f"  ✅ Encontrado en: engine.{attr}")
            print(f"     Tipo del valor: {type(value['test'])}")
            if hasattr(value['test'], 'source_ids'):
                print(f"     source_ids: {value['test'].source_ids}")
    except:
        pass
'''
    
    with open('test_diagnostic.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ test_diagnostic.py creado")

if __name__ == "__main__":
    print("🔧 FIXING MACROS ATTRIBUTE")
    print("=" * 60)
    
    print("\n1️⃣ Buscando dónde se almacenan los macros...")
    find_macro_storage()
    
    print("\n2️⃣ Corrigiendo returns...")
    attr_name = fix_create_macro_return_correct()
    
    print("\n3️⃣ Creando test de diagnóstico...")
    create_diagnostic_test()
    
    print("\n📋 Ejecutar: python test_diagnostic.py")