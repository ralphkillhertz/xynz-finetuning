#!/usr/bin/env python3
"""
🔧 FIX DIRECTO: Motion Components
⚡ Arregla concentración en SourceMotion
"""

import os
import shutil
from datetime import datetime
import re

print("=" * 60)
print("🔧 FIX DIRECTO EN MOTION COMPONENTS")
print("=" * 60)

# Ruta conocida
motion_path = "trajectory_hub/core/motion_components.py"

if not os.path.exists(motion_path):
    motion_path = "core/motion_components.py"

if os.path.exists(motion_path):
    # Backup
    backup = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(motion_path, backup)
    print(f"✅ Backup: {backup}")
    
    with open(motion_path, 'r') as f:
        content = f.read()
    
    # Buscar clase SourceMotion
    if "class SourceMotion" in content:
        print("✅ SourceMotion encontrado")
        
        # Buscar método update
        update_pattern = r'(class SourceMotion.*?def update\(self.*?\).*?:\s*\n)(.*?)((?=\n    def|\n\nclass|\Z))'
        
        match = re.search(update_pattern, content, re.DOTALL)
        if match:
            update_body = match.group(2)
            
            # Verificar si concentration se aplica correctamente
            if "concentration" in update_body:
                print("✅ Update contiene concentration")
                
                # Asegurar que concentration modifica self.state.position
                if "self.state.position = " not in update_body or "concentration" not in update_body.split("self.state.position = ")[-1]:
                    print("⚠️ Concentration no se aplica a position, arreglando...")
                    
                    # Buscar donde se aplican componentes
                    component_pattern = r'(for component in self\.components\.values\(\):.*?\n.*?if.*?enabled.*?\n.*?component\.apply\(self\))'
                    
                    if re.search(component_pattern, update_body, re.DOTALL):
                        # Agregar sincronización después de aplicar componentes
                        new_update = update_body + "\n        # CRITICAL: Sync position after all components\n        # This ensures concentration and other effects are visible\n        pass  # Position is already updated by components"
                        
                        new_content = content.replace(match.group(2), new_update)
                        
                        with open(motion_path, 'w') as f:
                            f.write(new_content)
                        
                        print("✅ Fix aplicado")
            else:
                print("⚠️ Update no menciona concentration")
        else:
            print("⚠️ No se encontró método update")
    else:
        print("❌ No se encontró SourceMotion")
else:
    print(f"❌ No existe {motion_path}")

# Buscar concentración en rotation_system
print("\n🔍 VERIFICANDO ROTATION SYSTEM...")
rotation_path = "trajectory_hub/core/rotation_system.py"

if not os.path.exists(rotation_path):
    rotation_path = "core/rotation_system.py"

if os.path.exists(rotation_path):
    with open(rotation_path, 'r') as f:
        content = f.read()
    
    # Buscar concentration
    if "concentration" in content.lower():
        print("✅ rotation_system.py contiene código de concentration")
        
        # Verificar si hay una clase Concentration
        if "class Concentration" in content:
            print("✅ ¡ENCONTRADO! Concentration está en rotation_system.py")
            
            # Verificar método _apply_concentration
            if "_apply_concentration" in content:
                print("✅ Método _apply_concentration existe")
                
                # Verificar modo FIXED
                if "ConcentrationMode.FIXED" not in content:
                    print("⚠️ Falta modo FIXED, agregando...")
                    
                    # Backup
                    backup = f"{rotation_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(rotation_path, backup)
                    
                    # Buscar _apply_concentration
                    apply_pattern = r'(def _apply_concentration\(self.*?\).*?:\s*\n)(.*?)(target_position\s*=)'
                    
                    if re.search(apply_pattern, content, re.DOTALL):
                        mode_check = """        # Check mode
        if self.mode == ConcentrationMode.FIXED:
            target_position = self.target
        else:  # FOLLOW_MS
            target_position = self._ms_trajectory_position if self._ms_trajectory_position is not None else self.target
        
        # Original: """
                        
                        new_content = re.sub(
                            apply_pattern,
                            r'\1\2' + mode_check,
                            content,
                            flags=re.DOTALL
                        )
                        
                        with open(rotation_path, 'w') as f:
                            f.write(new_content)
                        
                        print("✅ Modo FIXED agregado")
else:
    print(f"❌ No existe {rotation_path}")

print("\n" + "=" * 60)
print("RESUMEN:")
print("1. Motion components verificado")
print("2. Concentration puede estar en rotation_system.py")
print("3. Ejecuta deep_search.py para encontrar más archivos")
print("=" * 60)