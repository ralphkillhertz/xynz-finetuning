# === fix_macro_rotation_import.py ===
# 🔧 Fix: Corregir import de MacroRotation
# ⚡ CRÍTICO - Sin esto no puede crear el componente

import os
import re

def fix_imports():
    """Corregir imports de MacroRotation"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando y corrigiendo imports...")
    
    # Reemplazar imports incorrectos
    replacements = [
        # Import incorrecto de rotation_system
        (r'from rotation_system import.*MacroRotation.*', 
         '# from rotation_system import ... # Archivo no existe'),
        
        # Import incorrecto con path completo
        (r'from trajectory_hub\.core\.rotation_system import.*MacroRotation.*',
         '# from trajectory_hub.core.rotation_system import ... # Archivo no existe'),
    ]
    
    for old, new in replacements:
        if re.search(old, content):
            content = re.sub(old, new, content)
            print(f"✅ Comentado import incorrecto")
    
    # Verificar si MacroRotation está importado correctamente
    if 'from trajectory_hub.core.motion_components import' in content:
        # Buscar la línea exacta
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'from trajectory_hub.core.motion_components import' in line:
                if 'MacroRotation' not in line:
                    # Añadir MacroRotation al import existente
                    if line.rstrip().endswith(')'):
                        # Import multi-línea
                        lines[i] = line.rstrip()[:-1] + ', MacroRotation)'
                    else:
                        # Import simple
                        lines[i] = line.rstrip() + ', MacroRotation'
                    print(f"✅ Añadido MacroRotation al import existente")
                    content = '\n'.join(lines)
                    break
    else:
        # Añadir import después de otros imports
        import_added = False
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from trajectory_hub.core.motion_components'):
                # Insertar después
                lines.insert(i+1, 'from trajectory_hub.core.motion_components import MacroRotation')
                content = '\n'.join(lines)
                import_added = True
                print("✅ Añadido import de MacroRotation")
                break
        
        if not import_added:
            # Buscar cualquier import de trajectory_hub.core
            for i, line in enumerate(lines):
                if 'from trajectory_hub.core' in line and 'import' in line:
                    lines.insert(i+1, 'from trajectory_hub.core.motion_components import MacroRotation')
                    content = '\n'.join(lines)
                    print("✅ Añadido import de MacroRotation")
                    break
    
    # Ahora buscar set_macro_rotation y asegurar que cree MacroRotation
    print("\n🔍 Verificando set_macro_rotation...")
    
    # Buscar donde se asigna active_components['macro_rotation']
    pattern = r"(active_components\['macro_rotation'\]\s*=\s*)(\{\}|dict\(\))"
    
    def replacement(match):
        print("✅ Cambiando dict vacío por MacroRotation()")
        return match.group(1) + "MacroRotation()"
    
    content = re.sub(pattern, replacement, content)
    
    # Guardar
    import shutil
    from datetime import datetime
    backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_name)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Archivo actualizado")
    print(f"📦 Backup: {backup_name}")
    
    return True

if __name__ == "__main__":
    print("🔧 Corrigiendo imports de MacroRotation...")
    
    if fix_imports():
        print("\n✅ Imports corregidos")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
    else:
        print("\n❌ Error al corregir imports")