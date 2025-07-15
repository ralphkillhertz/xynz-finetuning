# === fix_if_block_indent.py ===
# 🔧 Fix: Corregir indentación dentro del bloque if
# ⚡ Impacto: CRÍTICO - Resuelve IndentationError

import os

def fix_if_block():
    """Corrige la indentación dentro de los bloques if"""
    
    print("🔧 FIX DE BLOQUES IF EN set_macro_rotation\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer líneas
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Corrigiendo indentación de bloques...")
    
    # Buscar y corregir set_macro_rotation
    in_method = False
    in_if_block = False
    base_indent = 8  # Indentación base del método
    
    for i in range(len(lines)):
        line = lines[i]
        
        # Detectar inicio del método
        if 'def set_macro_rotation' in line:
            in_method = True
            continue
            
        # Si estamos en el método
        if in_method:
            # Detectar fin del método
            if line.strip().startswith('def ') and i > 636:
                in_method = False
                continue
                
            # Detectar bloques if/for/while
            stripped = line.strip()
            
            if stripped.startswith('if ') and stripped.endswith(':'):
                in_if_block = True
                # El if debe tener 8 espacios
                lines[i] = ' ' * base_indent + stripped + '\n'
            elif stripped.startswith('for ') and stripped.endswith(':'):
                in_if_block = True
                lines[i] = ' ' * base_indent + stripped + '\n'
            elif in_if_block and stripped and not stripped.endswith(':'):
                # Contenido dentro del if debe tener 12 espacios
                if not stripped.startswith('return') and not stripped.startswith('#'):
                    lines[i] = ' ' * (base_indent + 4) + stripped + '\n'
                else:
                    lines[i] = ' ' * (base_indent + 4) + stripped + '\n'
            elif stripped == '':
                # Línea vacía, mantener
                continue
            elif not in_if_block and stripped:
                # Código fuera de bloques if
                lines[i] = ' ' * base_indent + stripped + '\n'
                
            # Detectar fin de bloque if
            if in_if_block and (stripped.startswith('return') or 
                               (i+1 < len(lines) and lines[i+1].strip() and 
                                not lines[i+1].startswith(' ' * (base_indent + 4)))):
                in_if_block = False
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Bloques if corregidos")
    
    # Mostrar resultado
    print("\n📋 Verificación (líneas 636-650):")
    for i in range(635, min(len(lines), 650)):
        if i < len(lines):
            line = lines[i].rstrip()
            spaces = len(lines[i]) - len(lines[i].lstrip())
            visual = '·' * spaces + lines[i].lstrip().rstrip()
            print(f"L{i+1} ({spaces:2d}): {visual[:70]}")

if __name__ == "__main__":
    fix_if_block()
    print("\n🚀 Ejecutando test...")
    os.system("python test_rotation_ms_final.py")