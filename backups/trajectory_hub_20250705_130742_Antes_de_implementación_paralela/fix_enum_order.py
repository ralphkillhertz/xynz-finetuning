#!/usr/bin/env python3
"""
fix_enum_order.py - Mueve el import de Enum al principio del archivo
"""

import os
import re

def fix_enum_import_order():
    """Mover el import de Enum al principio donde debe estar"""
    print("🔧 ARREGLANDO ORDEN DE IMPORT DE ENUM...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(filepath):
        print(f"❌ No se encuentra {filepath}")
        return False
    
    # Leer el archivo completo
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar y remover el import de Enum donde esté
    enum_import_line = None
    filtered_lines = []
    
    for i, line in enumerate(lines):
        if "from enum import Enum" in line:
            enum_import_line = line
            print(f"✅ Encontrado import de Enum en línea {i+1}: {line.strip()}")
        else:
            filtered_lines.append(line)
    
    if not enum_import_line:
        print("⚠️  No se encontró import de Enum, agregándolo...")
        enum_import_line = "from enum import Enum\n"
    
    # Encontrar dónde insertar el import (después de los otros imports)
    insert_index = -1
    
    for i, line in enumerate(filtered_lines):
        # Buscar después del último import
        if line.startswith("import ") or line.startswith("from "):
            insert_index = i + 1
        # Pero antes del primer class o def
        elif (line.startswith("class ") or line.startswith("def ") or 
              line.startswith("@") or line.strip().startswith("#")):
            if insert_index == -1:
                insert_index = i
            break
    
    # Si no encontramos un buen lugar, ponerlo después de los imports numpy
    if insert_index == -1:
        for i, line in enumerate(filtered_lines):
            if "import numpy" in line:
                insert_index = i + 1
                break
    
    # Si aún no encontramos, ponerlo en la línea 11 (después de los imports principales)
    if insert_index == -1:
        insert_index = 11
    
    # Insertar el import en el lugar correcto
    filtered_lines.insert(insert_index, enum_import_line)
    
    print(f"✅ Import de Enum movido a la línea {insert_index + 1}")
    
    # Guardar el archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)
    
    print("✅ Archivo guardado correctamente")
    
    # Mostrar las primeras líneas para verificar
    print("\n📋 Primeras 50 líneas del archivo corregido:")
    print("-" * 60)
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 50:
                print(f"{i+1:3d}: {line.rstrip()}")
                if "ConcentrationMode" in line:
                    print("     ^^^ ConcentrationMode encontrado")
    
    return True

def verify_fix():
    """Verificar que el fix funcionó"""
    print("\n\n🔍 VERIFICANDO FIX...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar posición del import
    enum_import_pos = content.find("from enum import Enum")
    concentration_mode_pos = content.find("class ConcentrationMode(Enum):")
    
    if enum_import_pos == -1:
        print("❌ No se encontró el import de Enum")
        return False
    
    if concentration_mode_pos == -1:
        print("❌ No se encontró ConcentrationMode")
        return False
    
    if enum_import_pos < concentration_mode_pos:
        print("✅ Import de Enum está ANTES de ConcentrationMode")
        print(f"   - Import en posición: {enum_import_pos}")
        print(f"   - ConcentrationMode en posición: {concentration_mode_pos}")
        return True
    else:
        print("❌ Import de Enum está DESPUÉS de ConcentrationMode")
        return False

def test_import_again():
    """Probar el import nuevamente"""
    print("\n\n🧪 PROBANDO IMPORT NUEVAMENTE...\n")
    
    try:
        # Limpiar cache de Python
        import sys
        if 'trajectory_hub.core.motion_components' in sys.modules:
            del sys.modules['trajectory_hub.core.motion_components']
        
        # Intentar importar
        from trajectory_hub.core.motion_components import ConcentrationMode, ConcentrationComponent
        print("✅ ConcentrationMode importado correctamente")
        print("✅ ConcentrationComponent importado correctamente")
        
        # Probar que funciona
        mode = ConcentrationMode.FIXED_POINT
        print(f"✅ ConcentrationMode.FIXED_POINT = {mode.value}")
        
        # Crear componente
        comp = ConcentrationComponent()
        print(f"✅ ConcentrationComponent creado: enabled={comp.enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("🔧 FIX PARA ORDEN DE IMPORT DE ENUM")
    print("="*60)
    
    # Aplicar fix
    if fix_enum_import_order():
        # Verificar
        if verify_fix():
            # Probar
            if test_import_again():
                print("\n" + "="*60)
                print("✅ PROBLEMA COMPLETAMENTE RESUELTO")
                print("\nAhora ejecuta:")
                print("  python test_concentration_minimal.py")
                print("  python test_concentration.py")
            else:
                print("\n⚠️  El import sigue fallando")
                print("Puede ser necesario reiniciar Python o limpiar el cache")
        else:
            print("\n❌ El fix no se aplicó correctamente")
    else:
        print("\n❌ No se pudo aplicar el fix")

if __name__ == "__main__":
    main()