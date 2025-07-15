# === fix_update_return_final.py ===
# 🔧 Fix definitivo para ManualIndividualRotation.update()
# ⚡ Asegurar que retorne state

import shutil
from datetime import datetime

print("🔧 FIX DEFINITIVO DE ManualIndividualRotation.update()")
print("=" * 60)

# Leer archivo
try:
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar ManualIndividualRotation
    class_start = None
    for i, line in enumerate(lines):
        if 'class ManualIndividualRotation' in line:
            class_start = i
            break
    
    if class_start is None:
        print("❌ No se encontró ManualIndividualRotation")
        exit(1)
    
    # Buscar el método update
    update_start = None
    update_end = None
    indent_level = None
    
    for i in range(class_start, len(lines)):
        line = lines[i]
        
        if 'def update(' in line and 'self' in line:
            update_start = i
            indent_level = len(line) - len(line.lstrip())
            print(f"✅ Encontrado update() en línea {i+1}")
            continue
            
        if update_start is not None and line.strip():
            current_indent = len(line) - len(line.lstrip())
            
            # Si encontramos otro método o clase al mismo nivel
            if (line.strip().startswith('def ') or line.strip().startswith('class ')) and current_indent <= indent_level:
                update_end = i
                break
    
    # Si no encontramos el final, buscar hasta el final de la clase
    if update_start and not update_end:
        for i in range(update_start + 1, len(lines)):
            if lines[i].strip().startswith('class '):
                update_end = i
                break
        if not update_end:
            update_end = len(lines)
    
    print(f"\n📄 Método update actual (líneas {update_start+1} a {update_end}):")
    print("-" * 60)
    
    # Verificar si ya tiene return state
    has_return_state = False
    last_code_line = None
    
    for i in range(update_start, update_end):
        print(f"{i+1:4d}: {lines[i].rstrip()}")
        if 'return state' in lines[i]:
            has_return_state = True
        if lines[i].strip() and not lines[i].strip().startswith('#'):
            last_code_line = i
    
    print("-" * 60)
    
    if has_return_state:
        print("✅ El método YA retorna state")
    else:
        print("⚠️ El método NO retorna state, corrigiendo...")
        
        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'trajectory_hub/core/motion_components.py.backup_{timestamp}'
        shutil.copy2('trajectory_hub/core/motion_components.py', backup_path)
        print(f"💾 Backup: {backup_path}")
        
        # Encontrar la indentación correcta
        base_indent = " " * (indent_level + 4)
        
        # Insertar return state antes del final del método
        if last_code_line:
            # Si hay un return vacío, reemplazarlo
            if 'return' in lines[last_code_line] and 'return state' not in lines[last_code_line]:
                lines[last_code_line] = f"{base_indent}return state\n"
                print(f"✅ Reemplazado 'return' por 'return state' en línea {last_code_line+1}")
            else:
                # Insertar después de la última línea de código
                lines.insert(last_code_line + 1, f"{base_indent}return state\n")
                print(f"✅ Añadido 'return state' en línea {last_code_line+2}")
        
        # Guardar
        with open('trajectory_hub/core/motion_components.py', 'w') as f:
            f.writelines(lines)
        
        print("✅ Archivo guardado")
    
    # Ahora verificar calculate_delta
    print("\n🔍 Verificando calculate_delta...")
    
    calc_start = None
    for i in range(class_start, len(lines)):
        if 'def calculate_delta(' in lines[i]:
            calc_start = i
            break
    
    if calc_start:
        print("✅ calculate_delta encontrado")
        print("\n📄 Primeras líneas de calculate_delta:")
        print("-" * 60)
        for i in range(calc_start, min(calc_start + 20, len(lines))):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
            if 'relative_pos' in lines[i]:
                print("      ⚡ Calculando posición relativa")
            if 'math.atan2' in lines[i]:
                print("      ⚡ Calculando ángulo actual")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Fix completado")