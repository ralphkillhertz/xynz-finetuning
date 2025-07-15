#!/usr/bin/env python3
"""
🔧 Diagnóstico: Por qué MotionState no se puede importar
⚡ Análisis: Sintaxis, orden, estructura
🎯 Objetivo: Identificar el problema exacto
"""

import ast
import re

def check_file_syntax():
    """Verifica la sintaxis del archivo"""
    print("1️⃣ Verificando sintaxis de motion_components.py...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    try:
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Intentar parsear
        ast.parse(content)
        print("   ✅ Sintaxis correcta")
        return True, None
    except SyntaxError as e:
        print(f"   ❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
        
        # Mostrar contexto
        lines = content.split('\n')
        if e.lineno <= len(lines):
            print("\n   Contexto del error:")
            for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+2)):
                marker = ">>>" if i == e.lineno-1 else "   "
                print(f"   {marker} {i+1}: {lines[i][:80]}")
        
        return False, e
    except Exception as e:
        print(f"   ❌ Error general: {e}")
        return False, e

def find_class_definitions():
    """Encuentra dónde están definidas las clases"""
    print("\n2️⃣ Buscando definiciones de clases...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    classes_found = {}
    
    for i, line in enumerate(lines):
        # Buscar definiciones de clase
        if line.strip().startswith('class ') or line.strip().startswith('@dataclass'):
            if line.strip().startswith('@dataclass'):
                # Ver la siguiente línea
                if i+1 < len(lines) and lines[i+1].strip().startswith('class '):
                    class_match = re.match(r'class\s+(\w+)', lines[i+1].strip())
                    if class_match:
                        class_name = class_match.group(1)
                        classes_found[class_name] = i+2  # línea del @dataclass
            else:
                class_match = re.match(r'class\s+(\w+)', line.strip())
                if class_match:
                    class_name = class_match.group(1)
                    classes_found[class_name] = i+1
    
    # Mostrar clases importantes
    important_classes = ['MotionState', 'MotionDelta', 'MotionComponent', 'SourceMotion']
    
    for cls in important_classes:
        if cls in classes_found:
            print(f"   ✅ {cls} en línea {classes_found[cls]}")
        else:
            print(f"   ❌ {cls} NO ENCONTRADO")
    
    return classes_found

def check_import_order():
    """Verifica si hay problemas de orden en las definiciones"""
    print("\n3️⃣ Verificando orden de definiciones...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar si MotionState se usa antes de ser definido
    motion_state_def = content.find('class MotionState')
    if motion_state_def == -1:
        motion_state_def = content.find('@dataclass\nclass MotionState')
    
    if motion_state_def > 0:
        # Buscar usos de MotionState antes de su definición
        before_def = content[:motion_state_def]
        
        # Buscar referencias a MotionState
        refs = re.findall(r'\bMotionState\b', before_def)
        if refs:
            print(f"   ⚠️ MotionState se usa {len(refs)} veces antes de ser definido")
        else:
            print("   ✅ MotionState no se usa antes de su definición")
    
    return motion_state_def

def create_minimal_test():
    """Crea un archivo de prueba mínimo"""
    print("\n4️⃣ Creando test mínimo...")
    
    test_code = '''# Test mínimo de importación
import sys
import os

# Añadir el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Path de Python:")
for p in sys.path[:5]:
    print(f"  {p}")

print("\\nIntentando import directo...")
try:
    import trajectory_hub.core.motion_components as mc
    print("✅ Módulo importado")
    
    # Ver qué contiene
    print("\\nContenido del módulo:")
    for item in dir(mc):
        if not item.startswith('_'):
            print(f"  - {item}")
            
    # Intentar acceder a MotionState
    if hasattr(mc, 'MotionState'):
        print("\\n✅ MotionState está en el módulo")
        ms = mc.MotionState()
        print(f"   Creado: {type(ms)}")
    else:
        print("\\n❌ MotionState NO está en el módulo")
        
except Exception as e:
    print(f"❌ Error al importar: {e}")
    
    # Intentar import más específico
    print("\\nIntentando import desde trajectory_hub...")
    try:
        from trajectory_hub.core.motion_components import MotionState
        print("✅ MotionState importado directamente")
    except Exception as e2:
        print(f"❌ Error: {e2}")
'''
    
    with open("test_minimal_import.py", 'w') as f:
        f.write(test_code)
    
    print("   ✅ Test creado: test_minimal_import.py")

def suggest_fix():
    """Sugiere una solución basada en el diagnóstico"""
    print("\n5️⃣ SOLUCIÓN SUGERIDA:")
    
    print("""
   El problema parece ser que MotionState no se está exportando correctamente.
   
   Opciones:
   
   1. Ejecutar el test mínimo para más información:
      $ python test_minimal_import.py
   
   2. Verificar el __init__.py del módulo:
      $ cat trajectory_hub/core/__init__.py
   
   3. Usar el import completo en el código:
      from trajectory_hub.core.motion_components import MotionState
   
   4. Restaurar de un backup funcional:
      $ cp trajectory_hub/core/motion_components.py.backup_20250707_164013 trajectory_hub/core/motion_components.py
   """)

def main():
    print("🔍 DIAGNÓSTICO PROFUNDO DEL PROBLEMA DE IMPORTACIÓN")
    print("=" * 60)
    
    # 1. Verificar sintaxis
    syntax_ok, error = check_file_syntax()
    if not syntax_ok:
        print("\n❌ Hay un error de sintaxis que impide la importación")
        return
    
    # 2. Buscar clases
    classes = find_class_definitions()
    
    # 3. Verificar orden
    check_import_order()
    
    # 4. Crear test
    create_minimal_test()
    
    # 5. Sugerir solución
    suggest_fix()

if __name__ == "__main__":
    main()