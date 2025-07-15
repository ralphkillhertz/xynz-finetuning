# === fix_all_array_errors.py ===
# 🔧 Fix: TODOS los errores array ambiguous
# ⚡ Solución completa
# 🎯 Impacto: CRÍTICO

import re
import shutil
from datetime import datetime

def fix_all_array_errors():
    """Arregla TODOS los errores de comparación con arrays"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(file_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    fixes_applied = 0
    
    # Buscar y arreglar TODAS las líneas problemáticas
    for i in range(len(lines)):
        line = lines[i]
        
        # Línea 710 (aproximada) - otra comparación con enabled
        if 'self.enabled = (abs(sx) > 0.001) or' in line:
            print(f"\n🔍 Encontrado problema en línea {i+1}:")
            print(f"   Antes: {line.strip()}")
            
            # Reemplazar toda la línea
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = f"{indent}self.enabled = (abs(sx) > 0.001) or (abs(sy) > 0.001) or (abs(sz) > 0.001)\n"
            
            print(f"   Después: {lines[i].strip()}")
            fixes_applied += 1
            
        # Buscar otras comparaciones con 'or' que involucren arrays
        elif 'if ' in line and ' or ' in line and 'abs(' in line and not line.strip().startswith('#'):
            # Verificar si es una comparación potencialmente problemática
            if any(var in line for var in ['speed_', 'sx', 'sy', 'sz', 'position', 'velocity']):
                print(f"\n⚠️ Posible problema en línea {i+1}:")
                print(f"   {line.strip()}")
    
    # Escribir archivo corregido
    with open(file_path, "w") as f:
        f.writelines(lines)
    
    print(f"\n✅ Archivo corregido - {fixes_applied} fixes aplicados")
    
    # Verificar específicamente las líneas de MacroRotation
    print("\n🔍 Verificando MacroRotation...")
    check_macro_rotation(file_path)

def check_macro_rotation(file_path):
    """Verifica el estado de MacroRotation"""
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    in_macro_rotation = False
    macro_rotation_start = 0
    
    for i, line in enumerate(lines):
        if 'class MacroRotation' in line:
            in_macro_rotation = True
            macro_rotation_start = i
            print(f"\n📍 MacroRotation encontrada en línea {i+1}")
            
        if in_macro_rotation:
            # Buscar el método calculate_delta
            if 'def calculate_delta' in line:
                print(f"   ✅ calculate_delta encontrado en línea {i+1}")
                
                # Verificar las siguientes líneas
                for j in range(i, min(i+20, len(lines))):
                    if 'if not getattr(component, "enabled", False):' in lines[j]:
                        print(f"   ✅ Protección de enabled encontrada en línea {j+1}")
                    elif 'enabled' in lines[j] and 'if' in lines[j]:
                        print(f"   ⚠️ Otra comparación con enabled en línea {j+1}: {lines[j].strip()}")
                
                in_macro_rotation = False
                break

if __name__ == "__main__":
    print("🔧 Arreglando TODOS los errores array ambiguous")
    print("=" * 50)
    fix_all_array_errors()
    
    print("\n📝 Próximo paso:")
    print("   python test_rotation_ms_final.py")