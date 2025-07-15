#!/usr/bin/env python3
"""
fix_enum_import_direct.py - Solución directa para el import de Enum
"""

import os

def fix_enum_import_directly():
    """Agregar import de Enum al principio del archivo"""
    print("🔧 ARREGLANDO IMPORT DE ENUM DIRECTAMENTE...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Verificar que el archivo existe
    if not os.path.exists(filepath):
        print(f"❌ No se encuentra {filepath}")
        return False
    
    # Leer el archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar dónde insertar el import
    insert_index = -1
    enum_import_exists = False
    
    for i, line in enumerate(lines):
        # Verificar si ya existe
        if "from enum import Enum" in line:
            enum_import_exists = True
            print("✅ Import de Enum ya existe en línea", i+1)
            break
        
        # Buscar el mejor lugar para insertar
        if "import numpy as np" in line and insert_index == -1:
            insert_index = i + 1
        elif line.startswith("import ") and insert_index == -1:
            insert_index = i
    
    # Si no existe, agregarlo
    if not enum_import_exists:
        if insert_index == -1:
            # Si no encontramos imports, buscar después del docstring
            for i, line in enumerate(lines):
                if i > 0 and '"""' in line and '"""' in lines[i-1]:
                    insert_index = i + 1
                    break
        
        # Si aún no encontramos, ponerlo después de la primera línea
        if insert_index == -1:
            insert_index = 1
            
        # Insertar el import
        lines.insert(insert_index, "from enum import Enum\n")
        print(f"✅ Import de Enum agregado en línea {insert_index + 1}")
        
        # Guardar el archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        print("✅ Archivo guardado")
    
    # Verificar el contenido
    print("\n📋 Primeras 40 líneas del archivo:")
    print("-" * 50)
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 40:
                print(f"{i+1:3d}: {line.rstrip()}")
            else:
                break
    
    return True

def verify_imports():
    """Verificar que todos los imports necesarios están presentes"""
    print("\n\n🔍 VERIFICANDO IMPORTS NECESARIOS...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    required_imports = [
        "import numpy as np",
        "from enum import Enum",
        "from typing import"
    ]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing = []
    for imp in required_imports:
        if imp in content:
            print(f"✅ {imp}")
        else:
            print(f"❌ FALTA: {imp}")
            missing.append(imp)
    
    if missing:
        print("\n⚠️  Agregando imports faltantes...")
        
        # Agregar al principio después del docstring
        lines = content.split('\n')
        insert_pos = 0
        
        # Buscar el final del docstring inicial
        in_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line:
                in_docstring = not in_docstring
                if not in_docstring and i > 0:  # Fin del docstring
                    insert_pos = i + 1
                    break
        
        # Agregar imports faltantes
        for imp in missing:
            lines.insert(insert_pos, imp)
            insert_pos += 1
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Imports agregados")
    
    return len(missing) == 0

def test_import():
    """Probar que el import funciona"""
    print("\n\n🧪 PROBANDO IMPORT...\n")
    
    try:
        # Cambiar al directorio del proyecto
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Intentar importar
        print("Importando motion_components...")
        from trajectory_hub.core.motion_components import ConcentrationMode, ConcentrationComponent
        print("✅ ConcentrationMode importado correctamente")
        print("✅ ConcentrationComponent importado correctamente")
        
        # Verificar que funciona
        mode = ConcentrationMode.FIXED_POINT
        print(f"✅ ConcentrationMode.FIXED_POINT = {mode.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al importar: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("🔧 FIX DIRECTO PARA IMPORT DE ENUM")
    print("="*60)
    
    # Aplicar fix
    if fix_enum_import_directly():
        # Verificar imports
        verify_imports()
        
        # Probar
        if test_import():
            print("\n" + "="*60)
            print("✅ PROBLEMA RESUELTO")
            print("\nAhora puedes ejecutar:")
            print("  python test_concentration_minimal.py")
            print("  python test_concentration.py")
        else:
            print("\n❌ El import sigue fallando")
            print("Verifica manualmente el archivo motion_components.py")
    else:
        print("\n❌ No se pudo aplicar el fix")

if __name__ == "__main__":
    main()