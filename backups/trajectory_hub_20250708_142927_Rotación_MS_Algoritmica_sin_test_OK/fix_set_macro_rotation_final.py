# === fix_set_macro_rotation_final.py ===
# 🔧 Fix: Asegurar que set_macro_rotation cree MacroRotation correctamente
# ⚡ CRÍTICO - Sin esto no hay movimiento

import os
import re

def fix_set_macro_rotation():
    """Arreglar set_macro_rotation para que cree MacroRotation correctamente"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando set_macro_rotation...")
    
    # Buscar el método completo
    method_match = re.search(
        r'(def set_macro_rotation\s*\([^)]*\):.*?)(?=\n    def|\n\s{0,4}def|\Z)',
        content,
        re.DOTALL
    )
    
    if not method_match:
        print("❌ No se encontró set_macro_rotation")
        return False
    
    method_content = method_match.group(1)
    print("✅ Método encontrado")
    
    # Buscar dónde se asigna active_components['macro_rotation']
    # Patrones posibles:
    patterns = [
        # Pattern 1: active_components['macro_rotation'] = {}
        (r"active_components\['macro_rotation'\]\s*=\s*\{\}", 
         "active_components['macro_rotation'] = MacroRotation()"),
        
        # Pattern 2: active_components['macro_rotation'] = dict()
        (r"active_components\['macro_rotation'\]\s*=\s*dict\(\)",
         "active_components['macro_rotation'] = MacroRotation()"),
         
        # Pattern 3: motion.active_components['macro_rotation'] = {}
        (r"motion\.active_components\['macro_rotation'\]\s*=\s*\{\}",
         "motion.active_components['macro_rotation'] = MacroRotation()"),
         
        # Pattern 4: motion.active_components['macro_rotation'] = dict()
        (r"motion\.active_components\['macro_rotation'\]\s*=\s*dict\(\)",
         "motion.active_components['macro_rotation'] = MacroRotation()"),
    ]
    
    changes_made = 0
    for pattern, replacement in patterns:
        if re.search(pattern, method_content):
            method_content = re.sub(pattern, replacement, method_content)
            print(f"✅ Reemplazado: {pattern}")
            changes_made += 1
    
    if changes_made == 0:
        print("⚠️ No se encontró asignación de dict vacío")
        
        # Mostrar el contenido para debug
        print("\n📋 Contenido del método:")
        lines = method_content.split('\n')
        for i, line in enumerate(lines[:40]):  # Primeras 40 líneas
            print(f"{i+1:3d}: {line}")
            if "'macro_rotation'" in line:
                print("     ^^^ LÍNEA CON macro_rotation")
    
    # Reemplazar en el archivo completo
    new_content = content.replace(method_match.group(1), method_content)
    
    # Guardar si hubo cambios
    if new_content != content:
        import shutil
        from datetime import datetime
        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n✅ Archivo actualizado")
        print(f"📦 Backup: {backup_name}")
        return True
    else:
        print("\n⚠️ No se hicieron cambios")
        return False

if __name__ == "__main__":
    print("🔧 Arreglando set_macro_rotation...")
    
    if fix_set_macro_rotation():
        print("\n✅ Fix aplicado")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
    else:
        print("\n❌ Necesita revisión manual")
        print("💡 Buscar en set_macro_rotation dónde se asigna")
        print("   active_components['macro_rotation'] = ...")
        print("   y cambiar {} o dict() por MacroRotation()")