#!/usr/bin/env python3
"""
🔧 FIX: Modos de concentración y conflicto IS/MS
⚡ Ejecutar desde directorio trajectory_hub/
"""

import os
import sys
import shutil
from datetime import datetime
import re

print("=" * 70)
print("🔧 FIX DE MODOS Y ROTACIÓN")
print("=" * 70)

# 1. FIX CONCENTRACIÓN
print("\n1️⃣ MODO FIJO DE CONCENTRACIÓN...")

concentration_paths = [
    "modules/advanced/concentration.py",
    "modules/behaviors/concentration.py",
    "modules/concentration.py"
]

concentration_path = None
for path in concentration_paths:
    if os.path.exists(path):
        concentration_path = path
        print(f"✅ Encontrado: {path}")
        break

if concentration_path:
    backup = f"{concentration_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(concentration_path, backup)
    
    with open(concentration_path, 'r') as f:
        content = f.read()
    
    # Buscar _apply_concentration
    if "_apply_concentration" in content:
        # Verificar si ya tiene lógica de modo
        if "ConcentrationMode.FIXED" in content:
            print("✅ Modo FIXED ya implementado")
        else:
            # Insertar lógica de modo
            apply_pattern = r'(def _apply_concentration\(self.*?\).*?:\s*\n)(.*?)(current_position\s*=)'
            
            mode_logic = """        # Select target based on mode
        if self.mode == ConcentrationMode.FIXED:
            target_position = self.target
        else:  # FOLLOW_MS
            target_position = self._ms_trajectory_position if self._ms_trajectory_position is not None else self.target
        
        # Get """
            
            new_content = re.sub(
                apply_pattern,
                r'\1\2' + mode_logic,
                content,
                flags=re.DOTALL
            )
            
            if new_content != content:
                with open(concentration_path, 'w') as f:
                    f.write(new_content)
                print("✅ Modo FIXED implementado")
else:
    print("⚠️ concentration.py no encontrado")

# 2. FIX ROTACIÓN
print("\n2️⃣ CONFLICTO IS/MS EN ROTACIÓN...")

rotation_paths = [
    "modules/behaviors/orientation_modulation.py",
    "modules/behaviors/rotation_system.py",
    "modules/orientation_modulation.py"
]

rotation_path = None
for path in rotation_paths:
    if os.path.exists(path):
        rotation_path = path
        print(f"✅ Encontrado: {path}")
        break

if rotation_path:
    backup = f"{rotation_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(rotation_path, backup)
    
    with open(rotation_path, 'r') as f:
        content = f.read()
    
    # Buscar método apply
    if "def apply(" in content:
        # Verificar si ya tiene check de IS
        if "individual_trajectory" in content:
            print("✅ Check de IS ya implementado")
        else:
            # Insertar check al inicio del apply
            apply_pattern = r'(def apply\(self.*?\).*?:\s*\n)(.*?)(if not self\.enabled:)'
            
            is_check = """        # Skip MS rotation if IS trajectories are active
        if hasattr(motion, 'components'):
            if 'individual_trajectory' in motion.components:
                if motion.components['individual_trajectory'].enabled:
                    return
        
        """
            
            new_content = re.sub(
                apply_pattern,
                r'\1\2' + is_check + r'\3',
                content,
                flags=re.DOTALL
            )
            
            if new_content != content:
                with open(rotation_path, 'w') as f:
                    f.write(new_content)
                print("✅ Check IS/MS implementado")
else:
    print("⚠️ orientation_modulation.py no encontrado")

# 3. LISTAR ARCHIVOS PARA DEBUG
print("\n📁 ESTRUCTURA DE ARCHIVOS:")
print("-" * 40)

dirs_to_check = ["core", "modules", "modules/behaviors", "modules/advanced"]
for dir_path in dirs_to_check:
    if os.path.exists(dir_path):
        print(f"\n{dir_path}/:")
        for f in os.listdir(dir_path):
            if f.endswith(".py") and not f.startswith("__"):
                print(f"  - {f}")

print("\n✅ FIXES APLICADOS")
print("⚡ Reinicia el controlador para aplicar cambios")
print("=" * 70)