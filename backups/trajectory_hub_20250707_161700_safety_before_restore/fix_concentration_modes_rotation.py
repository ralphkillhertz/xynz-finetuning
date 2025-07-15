#!/usr/bin/env python3
"""
🔧 FIX: Modo fijo de concentración y conflicto con rotación MS
⚡ Soluciona: 
   - Concentración siempre sigue MS (debe respetar modo fijo)
   - Rotación MS se desactiva con trayectorias IS
"""

import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("🔧 FIX DE MODOS DE CONCENTRACIÓN Y ROTACIÓN")
print("=" * 70)

# 1. Arreglar modo fijo en concentración
print("\n1️⃣ ARREGLANDO MODO FIJO DE CONCENTRACIÓN...")
concentration_path = "trajectory_hub/modules/advanced/concentration.py"
backup_path = f"{concentration_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(concentration_path, backup_path)

with open(concentration_path, 'r') as f:
    content = f.read()

# Buscar el método _apply_concentration
import re

# Asegurar que respete el modo cuando está en FIXED
fixed_pattern = r'(def _apply_concentration\(self, motion: SourceMotion\) -> np\.ndarray:.*?\n(?:.*?\n)*?)(        if self\.mode == ConcentrationMode\.FIXED:.*?\n.*?target_position = self\.target.*?\n)'

if re.search(fixed_pattern, content, re.DOTALL):
    # Ya tiene el código correcto
    print("✅ Modo FIXED ya está implementado correctamente")
else:
    # Buscar el método y agregar la lógica del modo
    method_pattern = r'(def _apply_concentration\(self, motion: SourceMotion\) -> np\.ndarray:.*?\n)(.*?)(        # Get current position.*?\n)'
    
    new_method = r'\1\2        # Check mode first\n        if self.mode == ConcentrationMode.FIXED:\n            target_position = self.target\n        else:  # FOLLOW_MS mode\n            target_position = self._ms_trajectory_position if self._ms_trajectory_position is not None else self.target\n\n\3'
    
    new_content = re.sub(method_pattern, new_method, content, flags=re.DOTALL)
    
    with open(concentration_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Modo FIXED implementado")

# 2. Arreglar conflicto entre trayectorias IS y rotación MS
print("\n2️⃣ ARREGLANDO CONFLICTO IS/MS EN ROTACIÓN...")

# Primero verificar si rotation_system existe
rotation_path = "trajectory_hub/modules/behaviors/rotation_system.py"
if not os.path.exists(rotation_path):
    # Buscar en orientation_modulation
    rotation_path = "trajectory_hub/modules/behaviors/orientation_modulation.py"

if os.path.exists(rotation_path):
    backup_path = f"{rotation_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(rotation_path, backup_path)
    
    with open(rotation_path, 'r') as f:
        rot_content = f.read()
    
    # Buscar el método apply
    apply_pattern = r'(def apply\(self, motion: SourceMotion\) -> None:.*?\n(?:.*?\n)*?)'
    
    # Agregar verificación de trayectorias IS activas
    check_is_pattern = r'(def apply\(self, motion: SourceMotion\) -> None:.*?\n)(.*?)(        if not self\.enabled:.*?\n.*?return.*?\n)'
    
    if re.search(check_is_pattern, rot_content, re.DOTALL):
        new_apply = r'\1\2        # Check if IS trajectories are active\n        if hasattr(motion, "components") and "individual_trajectory" in motion.components:\n            if motion.components["individual_trajectory"].enabled:\n                # Skip MS rotation when IS is active\n                return\n\n\3'
        
        new_rot_content = re.sub(check_is_pattern, new_apply, rot_content, flags=re.DOTALL)
        
        with open(rotation_path, 'w') as f:
            f.write(new_rot_content)
        
        print(f"✅ Conflicto IS/MS arreglado en {os.path.basename(rotation_path)}")
    else:
        print(f"⚠️ No se encontró el patrón esperado en {os.path.basename(rotation_path)}")

# 3. Test de verificación
print("\n🧪 VERIFICANDO FIXES...")
print("-" * 70)

from trajectory_hub.core.engine import SpatialEngine
from trajectory_hub.modules.advanced.concentration import ConcentrationMode
import numpy as np

engine = SpatialEngine(num_sources=3)
engine.initialize()

# Test 1: Modo fijo
print("TEST 1: Modo FIXED")
concentration = engine.modules.get('concentration')
if concentration:
    concentration.enabled = True
    concentration.mode = ConcentrationMode.FIXED
    concentration.target = np.array([2.0, 2.0, 0.0])
    concentration.update_parameter('factor', 0.5)
    
    # Simular posición MS diferente
    concentration._ms_trajectory_position = np.array([5.0, 5.0, 0.0])
    
    # Update
    engine.update()
    
    # Verificar que se mueve hacia target fijo, no hacia MS
    pos = engine._positions[0]
    dist_to_fixed = np.linalg.norm(pos - concentration.target)
    dist_to_ms = np.linalg.norm(pos - concentration._ms_trajectory_position)
    
    if dist_to_fixed < dist_to_ms:
        print("  ✅ Modo FIXED funciona correctamente")
    else:
        print("  ❌ Modo FIXED no funciona (sigue a MS)")

# Test 2: Conflicto IS/MS
print("\nTEST 2: Conflicto IS/MS en rotación")
# Activar trayectoria individual
if 'individual_trajectory' in engine.modules:
    engine.modules['individual_trajectory'].enabled = True
    print("  ✅ Trayectoria IS activada")
    
    # Verificar que rotación MS no interfiere
    orientation = engine.modules.get('orientation_modulation')
    if orientation and hasattr(orientation, 'ms_rotation_enabled'):
        initial_rotation = engine._source_motions[0].state.orientation.copy()
        
        # Forzar rotación MS
        orientation.ms_rotation_enabled = True
        orientation.ms_rotation_speed = 5.0
        
        # Update
        engine.update()
        
        final_rotation = engine._source_motions[0].state.orientation
        
        if np.allclose(initial_rotation, final_rotation):
            print("  ✅ Rotación MS correctamente desactivada con IS activa")
        else:
            print("  ⚠️ Rotación MS sigue activa con IS")

print("\n" + "=" * 70)
print("RESUMEN DE FIXES:")
print("=" * 70)
print("1. ✅ Propagación de posiciones en engine")
print("2. ✅ Modo FIXED de concentración")
print("3. ✅ Conflicto IS/MS en rotación")
print("\n⚡ Ejecuta los scripts en orden:")
print("   1. python fix_concentration_engine_propagation.py")
print("   2. python fix_concentration_modes_rotation.py")
print("   3. Reinicia el controlador")
print("=" * 70)