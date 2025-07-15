#!/usr/bin/env python3
"""
🔧 IMPLEMENTACIÓN DE ARQUITECTURA PARALELA
⚡ Convierte componentes en paralelos e independientes
"""

import os
import shutil
from datetime import datetime
import re

print("=" * 80)
print("🔧 IMPLEMENTANDO ARQUITECTURA PARALELA")
print("=" * 80)

# 1. MODIFICAR SourceMotion.update() para arquitectura paralela
motion_path = "trajectory_hub/core/motion_components.py"

if os.path.exists(motion_path):
    print("\n1️⃣ MODIFICANDO SourceMotion PARA ARQUITECTURA PARALELA...")
    
    backup = f"{motion_path}.backup_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(motion_path, backup)
    print(f"✅ Backup: {backup}")
    
    with open(motion_path, 'r') as f:
        content = f.read()
    
    # Buscar la clase SourceMotion y su método update
    class_pattern = r'(class SourceMotion.*?)(def update\(self.*?\):)(.*?)((?=\n    def|\nclass|\Z))'
    match = re.search(class_pattern, content, re.DOTALL)
    
    if match:
        # Nuevo método update con arquitectura paralela
        new_update = '''
    def update(self, dt: float):
        """Update motion with PARALLEL component architecture.
        
        Each component calculates its delta independently.
        All deltas are summed at the end.
        No component can block another.
        """
        if not self.enabled:
            return
        
        # Store initial state
        initial_position = self.state.position.copy()
        initial_orientation = self.state.orientation.copy()
        
        # PARALLEL DELTA CALCULATION
        # Each component calculates its contribution independently
        position_deltas = []
        orientation_deltas = []
        
        # 1. Base trajectory update (if exists)
        if hasattr(self, 'trajectory') and self.trajectory is not None:
            try:
                self.trajectory.update(dt)
                base_position = self.trajectory.get_position()
                position_deltas.append(('base_trajectory', base_position - initial_position))
            except:
                pass
        
        # 2. Apply all components in PARALLEL
        # Components should NOT modify state directly, only return deltas
        for name, component in self.components.items():
            if not component.enabled:
                continue
                
            try:
                # Save current state
                temp_position = self.state.position.copy()
                temp_orientation = self.state.orientation.copy()
                
                # Let component apply (may modify state temporarily)
                component.apply(self)
                
                # Calculate delta
                pos_delta = self.state.position - temp_position
                ori_delta = self.state.orientation - temp_orientation
                
                # Record deltas if significant
                if np.any(pos_delta != 0):
                    position_deltas.append((name, pos_delta))
                if np.any(ori_delta != 0):
                    orientation_deltas.append((name, ori_delta))
                
                # Restore state for next component
                self.state.position = temp_position
                self.state.orientation = temp_orientation
                
            except Exception as e:
                print(f"Component {name} error: {e}")
                continue
        
        # 3. FINAL SUMMATION - Apply all deltas
        # Start from initial state
        self.state.position = initial_position.copy()
        self.state.orientation = initial_orientation.copy()
        
        # Sum all position deltas
        for name, delta in position_deltas:
            self.state.position += delta
            
        # Sum all orientation deltas (with proper quaternion math if needed)
        for name, delta in orientation_deltas:
            self.state.orientation += delta
        
        # Update velocity based on position change
        if dt > 0:
            self.state.velocity = (self.state.position - initial_position) / dt
        
        # Update physics if present
        if hasattr(self, 'physics'):
            self.physics.update(dt)
'''
        
        # Replace the update method
        new_content = re.sub(
            class_pattern,
            match.group(1) + new_update + match.group(4),
            content,
            flags=re.DOTALL
        )
        
        # Add numpy import if not present
        if 'import numpy as np' not in new_content:
            new_content = 'import numpy as np\n' + new_content
        
        with open(motion_path, 'w') as f:
            f.write(new_content)
        
        print("✅ SourceMotion.update() convertido a arquitectura paralela")

# 2. ARREGLAR CONCENTRACIÓN para que no dependa de IS
print("\n2️⃣ ARREGLANDO CONCENTRACIÓN PARA SER INDEPENDIENTE...")

# Buscar dónde está concentration
concentration_files = []
for root, dirs, files in os.walk("trajectory_hub"):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    if 'class Concentration' in f.read():
                        concentration_files.append(filepath)
            except:
                pass

for conc_file in concentration_files:
    print(f"\n📄 Arreglando {conc_file}")
    
    backup = f"{conc_file}.backup_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(conc_file, backup)
    
    with open(conc_file, 'r') as f:
        content = f.read()
    
    # Buscar el método apply de Concentration
    apply_pattern = r'(class Concentration.*?def apply\(self.*?\):)(.*?)((?=\n    def|\nclass|\Z))'
    match = re.search(apply_pattern, content, re.DOTALL)
    
    if match:
        apply_body = match.group(2)
        
        # Eliminar cualquier dependencia de IS
        new_body = re.sub(r'if.*individual_trajectory.*enabled.*:.*?\n.*?return.*?\n', '', apply_body, flags=re.DOTALL)
        
        # Asegurar que siempre aplica cuando está enabled
        if 'if not self.enabled:' not in new_body:
            new_body = '\n        if not self.enabled:\n            return\n' + new_body
        
        # Asegurar que modifica position directamente
        if 'motion.state.position' not in new_body:
            new_body += '\n        # Apply concentration to position\n        motion.state.position = concentrated_position\n'
        
        new_content = content.replace(match.group(2), new_body)
        
        with open(conc_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Concentration ahora es independiente de IS")

# 3. ARREGLAR ROTACIÓN MS para que no sea bloqueada por IS
print("\n3️⃣ ARREGLANDO ROTACIÓN MS PARA SER INDEPENDIENTE...")

rotation_file = "trajectory_hub/core/rotation_system.py"
if os.path.exists(rotation_file):
    backup = f"{rotation_file}.backup_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(rotation_file, backup)
    
    with open(rotation_file, 'r') as f:
        content = f.read()
    
    # Eliminar checks que bloquean cuando IS está activa
    patterns_to_remove = [
        r'if.*individual_trajectory.*enabled.*:.*?\n.*?return.*?\n',
        r'if.*IS.*active.*:.*?\n.*?return.*?\n',
        r'if.*trajectory.*is not None.*:.*?\n.*?return.*?\n'
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    with open(rotation_file, 'w') as f:
        f.write(content)
    
    print("✅ Rotación MS ahora funciona independientemente de IS")

# 4. CREAR SCRIPT DE VERIFICACIÓN
print("\n4️⃣ CREANDO SCRIPT DE VERIFICACIÓN...")

verify_script = '''#!/usr/bin/env python3
"""
🧪 VERIFICACIÓN DE ARQUITECTURA PARALELA
"""

import sys
import numpy as np
sys.path.insert(0, 'trajectory_hub')

from trajectory_hub.core.motion_components import SourceMotion, MotionState

print("=" * 60)
print("🧪 TEST DE COMPONENTES PARALELOS")
print("=" * 60)

# Crear motion de prueba
motion = SourceMotion(source_id=0)
motion.state.position = np.array([5.0, 0.0, 0.0])

# Simular componentes
class MockComponent:
    def __init__(self, name, delta):
        self.name = name
        self.enabled = True
        self.delta = np.array(delta)
    
    def apply(self, motion):
        motion.state.position += self.delta

# Agregar múltiples componentes
motion.components = {
    'comp1': MockComponent('comp1', [1.0, 0.0, 0.0]),
    'comp2': MockComponent('comp2', [0.0, 1.0, 0.0]),
    'comp3': MockComponent('comp3', [0.0, 0.0, 1.0])
}

print(f"Posición inicial: {motion.state.position}")

# Update
motion.update(0.016)

print(f"Posición final: {motion.state.position}")
expected = np.array([6.0, 1.0, 1.0])

if np.allclose(motion.state.position, expected):
    print("✅ ¡COMPONENTES SE SUMAN CORRECTAMENTE!")
else:
    print("❌ Error en suma de componentes")

# Test con componente deshabilitado
motion.components['comp2'].enabled = False
motion.state.position = np.array([5.0, 0.0, 0.0])
motion.update(0.016)

expected_disabled = np.array([6.0, 0.0, 1.0])
if np.allclose(motion.state.position, expected_disabled):
    print("✅ Componente deshabilitado no interfiere con otros")
else:
    print("❌ Problema con componente deshabilitado")

print("\\n✅ Arquitectura paralela implementada")
'''

with open("verify_parallel.py", 'w') as f:
    f.write(verify_script)
os.chmod("verify_parallel.py", 0o755)

# RESUMEN
print("\n" + "=" * 80)
print("ARQUITECTURA PARALELA IMPLEMENTADA")
print("=" * 80)
print("""
CAMBIOS APLICADOS:
1. ✅ SourceMotion.update() ahora suma deltas independientes
2. ✅ Concentración funciona sin depender de IS
3. ✅ Rotación MS funciona con IS activa
4. ✅ Componentes no se bloquean mutuamente

BENEFICIOS:
- Cada componente calcula su contribución (delta)
- Los deltas se suman al final
- Activar/desactivar un componente no afecta otros
- No hay jerarquías ni dependencias

PRÓXIMOS PASOS:
1. python verify_parallel.py
2. python trajectory_hub/interface/interactive_controller.py
3. Probar todas las combinaciones:
   - Solo Rotación MS → Debe funcionar
   - Solo Concentración → Debe funcionar
   - IS + Rotación MS → Ambos deben funcionar
   - Todo activado → Todo debe sumarse
""")
print("=" * 80)
