#!/usr/bin/env python3
"""
update_imports.py - Actualiza todos los imports a la nueva estructura
"""
import os
import re

# Mapeo de imports antiguos a nuevos
IMPORT_MAPPINGS = {
    # Core modules
    'from extended_path_engine import': 'from trajectory_hub.core.extended_path_engine import',
    'from trajectory_hub.core.enhanced_trajectory_engine import': 'from trajectory_hub.core.enhanced_trajectory_engine import',
    'from trajectory_hub.core.motion_components import': 'from trajectory_hub.core.motion_components import',
    'from trajectory_hub.core.trajectory_deformers import': 'from trajectory_hub.core.trajectory_deformers import',
    'from trajectory_hub.core.spat_osc_bridge import': 'from trajectory_hub.core.spat_osc_bridge import',
    'from trajectory_hub.core.macro_behaviors import': 'from trajectory_hub.core.macro_behaviors import',
    
    # Import statements
    'import extended_path_engine': 'import trajectory_hub.core.extended_path_engine',
    'from trajectory_hub.core from trajectory_hub.core import enhanced_trajectory_engine': 'import trajectory_hub.core.enhanced_trajectory_engine',
    'from trajectory_hub.core from trajectory_hub.core import motion_components': 'import trajectory_hub.core.motion_components',
    'from trajectory_hub.core from trajectory_hub.core import trajectory_deformers': 'import trajectory_hub.core.trajectory_deformers',
    'from trajectory_hub.core from trajectory_hub.core import spat_osc_bridge': 'import trajectory_hub.core.spat_osc_bridge',
    'import macro_behaviors': 'import trajectory_hub.core.macro_behaviors',
}

def update_file_imports(filepath):
    """Actualizar imports en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Aplicar cada mapeo
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
            
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Actualizado: {filepath}")
            return True
        else:
            print(f"  Sin cambios: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ Error en {filepath}: {e}")
        return False

def update_all_imports(root_dir='trajectory_hub'):
    """Actualizar imports en todos los archivos Python"""
    updated_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignorar directorios especiales
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
        
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                if update_file_imports(filepath):
                    updated_count += 1
                    
    print(f"\n✅ Total archivos actualizados: {updated_count}")

if __name__ == "__main__":
    print("Actualizando imports a la nueva estructura...")
    print("="*50)
    update_all_imports()
    print("="*50)
    print("¡Proceso completado!")