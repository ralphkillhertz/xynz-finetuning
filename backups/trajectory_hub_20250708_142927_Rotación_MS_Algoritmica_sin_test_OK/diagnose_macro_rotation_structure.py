# === diagnose_macro_rotation_structure.py ===
# 🔍 Diagnóstico: Ver estructura exacta de MacroRotation
# ⚡ Para aplicar fix correcto

import os
import re

def diagnose_macro_rotation():
    """Ver la estructura exacta de MacroRotation"""
    
    file_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar MacroRotation
    in_macro_rotation = False
    class_start = -1
    indent_level = 0
    method_count = 0
    
    print("🔍 Buscando MacroRotation...")
    
    for i, line in enumerate(lines):
        if 'class MacroRotation' in line:
            in_macro_rotation = True
            class_start = i
            indent_level = len(line) - len(line.lstrip())
            print(f"\n✅ Encontrada en línea {i+1}")
            print(f"📍 Indentación: {indent_level} espacios")
            print("\n📋 Estructura de la clase:")
            continue
            
        if in_macro_rotation:
            # Si es una nueva clase al mismo nivel, terminar
            if line.strip().startswith('class ') and len(line) - len(line.lstrip()) <= indent_level:
                break
                
            # Si es un método
            if line.strip().startswith('def '):
                method_name = line.strip().split('(')[0].replace('def ', '')
                print(f"  - {method_name}()")
                method_count += 1
                
                # Ver si es calculate_delta
                if 'calculate_delta' in method_name:
                    print(f"    ✅ calculate_delta EXISTE en línea {i+1}")
    
    # Mostrar contexto alrededor de la clase
    if class_start >= 0:
        print(f"\n📄 Contexto (líneas {class_start}-{class_start+20}):")
        for i in range(max(0, class_start), min(len(lines), class_start + 20)):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
    
    # Buscar si calculate_delta existe en algún lugar
    print("\n🔍 Buscando 'calculate_delta' en todo el archivo...")
    for i, line in enumerate(lines):
        if 'calculate_delta' in line and 'def' in line:
            print(f"  Línea {i+1}: {line.strip()}")
    
    return method_count

if __name__ == "__main__":
    print("🔧 Diagnóstico de MacroRotation")
    print("=" * 60)
    
    methods = diagnose_macro_rotation()
    print(f"\n📊 Total métodos encontrados: {methods}")
    
    print("\n💡 Si calculate_delta no existe, necesitamos añadirlo manualmente")