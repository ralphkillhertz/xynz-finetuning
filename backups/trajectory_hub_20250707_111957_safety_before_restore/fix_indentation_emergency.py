#!/usr/bin/env python3
"""
🚨 FIX DE EMERGENCIA - Corregir indentación
⚡ Arreglar el error de sintaxis causado por el fix anterior
"""

import os
import re

def fix_indentation_error():
    """Corregir error de indentación en motion_components.py"""
    
    print("🚨 FIX DE EMERGENCIA - Corrigiendo indentación\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_file):
        print(f"❌ No se encuentra {motion_file}")
        return False
    
    print(f"📄 Leyendo {motion_file}...")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar la línea problemática
    problem_line = None
    for i, line in enumerate(lines):
        if "self.name = name" in line and line.startswith("    self.name"):
            problem_line = i
            print(f"   ❌ Error encontrado en línea {i+1}: {line.strip()}")
            break
    
    if problem_line is None:
        print("   ⚠️  No se encontró el error específico")
        # Buscar cualquier problema de indentación alrededor de __init__
        for i, line in enumerate(lines):
            if "__init__" in line:
                print(f"   📍 __init__ encontrado en línea {i+1}")
                # Verificar las siguientes líneas
                for j in range(i+1, min(i+20, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('        '):
                        print(f"   ❌ Posible error de indentación en línea {j+1}: {lines[j][:50]}")
    
    # Intentar arreglar automáticamente
    print("\n🔧 Intentando corregir automáticamente...")
    
    # Buscar patrones de __init__ y asegurar indentación correcta
    fixed_lines = []
    in_init = False
    init_indent = "        "  # 8 espacios para métodos de clase
    
    for i, line in enumerate(lines):
        if "def __init__" in line:
            in_init = True
            fixed_lines.append(line)
            continue
        
        if in_init and line.strip():
            # Si estamos en __init__ y la línea no está vacía
            if "def " in line and not line.startswith(init_indent):
                # Nueva función, salir de __init__
                in_init = False
                fixed_lines.append(line)
            elif line.startswith("self.") or "# Offsets para" in line:
                # Asegurar indentación correcta
                stripped = line.lstrip()
                fixed_lines.append(init_indent + stripped)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Guardar versión corregida
    backup_file = motion_file + ".error_backup"
    print(f"\n💾 Creando backup: {backup_file}")
    
    with open(backup_file, 'w') as f:
        f.writelines(lines)
    
    print(f"📝 Guardando versión corregida...")
    
    with open(motion_file, 'w') as f:
        f.writelines(fixed_lines)
    
    print("\n✅ Corrección aplicada")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis...")
    try:
        with open(motion_file, 'r') as f:
            compile(f.read(), motion_file, 'exec')
        print("   ✅ Sintaxis correcta")
        return True
    except SyntaxError as e:
        print(f"   ❌ Todavía hay errores: {e}")
        print(f"   📍 Línea {e.lineno}: {e.text}")
        
        # Intentar restaurar del backup más reciente
        print("\n🔄 Buscando backup más reciente...")
        import glob
        backups = sorted(glob.glob("backup_delta_correct_*/motion_components.py"))
        if backups:
            latest_backup = backups[-1]
            print(f"   📁 Restaurando desde: {latest_backup}")
            import shutil
            shutil.copy2(latest_backup, motion_file)
            
            # Re-aplicar los cambios de deltas manualmente
            print("   🔧 Re-aplicando cambios de deltas...")
            apply_delta_changes_safely()
            return True
        
        return False

def apply_delta_changes_safely():
    """Re-aplicar los cambios de deltas de forma segura"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Solo agregar los atributos de offset si no existen
    if "concentration_offset" not in content:
        # Buscar el __init__ y agregar después de las primeras asignaciones
        init_pattern = r'(def __init__\(self.*?\):\s*\n(?:.*?\n)*?)(        self\.\w+ = .*?\n)'
        
        offset_attrs = """        # Offsets para arquitectura de deltas
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)\n"""
        
        content = re.sub(init_pattern, r'\1\2' + offset_attrs, content, count=1)
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("   ✅ Cambios de deltas aplicados de forma segura")

if __name__ == "__main__":
    success = fix_indentation_error()
    
    if success:
        print("\n🎉 Error corregido exitosamente")
        print("\n🚀 Ahora puedes ejecutar:")
        print("   python trajectory_hub/interface/interactive_controller.py")
    else:
        print("\n❌ No se pudo corregir automáticamente")
        print("\n💡 Opciones:")
        print("   1. Restaurar backup: cp trajectory_hub/core/motion_components.py.error_backup trajectory_hub/core/motion_components.py")
        print("   2. Restaurar desde backup de deltas: cp backup_delta_correct_*/motion_components.py trajectory_hub/core/motion_components.py")