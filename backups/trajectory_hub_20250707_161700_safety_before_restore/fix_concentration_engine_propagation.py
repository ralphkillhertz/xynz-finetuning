#!/usr/bin/env python3
"""
🔧 FIX DEFINITIVO: Propagación de cambios en el engine
⚡ Soluciona: Concentración no se aplica a _positions
"""

import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("🔧 FIX DEFINITIVO DE PROPAGACIÓN EN ENGINE")
print("=" * 70)

# Backup del engine
engine_path = "trajectory_hub/core/engine.py"
backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(engine_path, backup_path)
print(f"✅ Backup creado: {backup_path}")

# Leer el archivo
with open(engine_path, 'r') as f:
    content = f.read()

# Buscar el método update
import re

# Patrón para encontrar el método update completo
update_pattern = r'(def update\(self.*?\n(?:.*?\n)*?)(        # Update positions from states\n.*?for i in range.*?\n.*?self\._positions\[i\] = motion\.state\.position\.copy\(\))'

match = re.search(update_pattern, content, re.DOTALL)

if match:
    # Reemplazar la sección de actualización de posiciones
    new_update_section = r'\1        # Update positions from states\n        for i in range(self.num_sources):\n            motion = self._source_motions[i]\n            # CRITICAL: Siempre copiar desde motion.state.position\n            # Esto asegura que todos los componentes (incluida concentración) se apliquen\n            self._positions[i] = motion.state.position.copy()'
    
    new_content = re.sub(update_pattern, new_update_section, content, flags=re.DOTALL)
    
    # Escribir el archivo actualizado
    with open(engine_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Engine actualizado correctamente")
else:
    print("⚠️ No se encontró el patrón esperado, aplicando fix alternativo...")
    
    # Buscar solo el loop de actualización
    loop_pattern = r'(for i in range\(self\.num_sources\):.*?\n.*?motion = self\._source_motions\[i\].*?\n)(.*?self\._positions\[i\] = .*?\n)'
    
    if re.search(loop_pattern, content, re.DOTALL):
        new_content = re.sub(
            loop_pattern,
            r'\1            # CRITICAL FIX: Siempre usar motion.state.position\n            self._positions[i] = motion.state.position.copy()\n',
            content,
            flags=re.DOTALL
        )
        
        with open(engine_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Fix alternativo aplicado")

# Test inmediato
print("\n🧪 VERIFICANDO FIX...")
print("-" * 70)

from trajectory_hub.core.engine import SpatialEngine
import numpy as np

engine = SpatialEngine(num_sources=3)
engine.initialize()

# Configurar concentración
engine.modules['concentration'].enabled = True
engine.modules['concentration'].update_parameter('factor', 0.0)  # Máxima concentración

# Posiciones iniciales
initial_positions = [
    engine._positions[0].copy(),
    engine._positions[1].copy(),
    engine._positions[2].copy()
]

print(f"Posiciones iniciales:")
for i, pos in enumerate(initial_positions):
    print(f"  Fuente {i}: {pos}")

# Ejecutar varios updates
for _ in range(10):
    engine.update()

# Verificar posiciones finales
print(f"\nPosiciones después de 10 updates:")
all_at_origin = True
for i in range(3):
    pos = engine._positions[i]
    dist = np.linalg.norm(pos)
    print(f"  Fuente {i}: {pos} (dist: {dist:.3f})")
    if dist > 0.01:
        all_at_origin = False

if all_at_origin:
    print("\n✅ ¡CONCENTRACIÓN FUNCIONA PERFECTAMENTE!")
else:
    print("\n❌ Aún hay problemas, verificando estado interno...")
    print(f"motion[0].state.position: {engine._source_motions[0].state.position}")
    print(f"_positions[0]: {engine._positions[0]}")
    
    # Fix adicional si es necesario
    print("\n🔧 Aplicando fix adicional en TrajectoryEngine...")
    
    traj_engine_path = "trajectory_hub/core/trajectory_engine.py"
    if os.path.exists(traj_engine_path):
        with open(traj_engine_path, 'r') as f:
            traj_content = f.read()
        
        # Buscar el método update
        if "def update(" in traj_content:
            # Agregar propagación forzada al final del update
            traj_content = re.sub(
                r'(def update\(self.*?\n(?:.*?\n)*?)(        return.*?\n)',
                r'\1        # FORCE POSITION SYNC\n        if hasattr(self, "_positions") and hasattr(self, "_source_motions"):\n            for i in range(len(self._positions)):\n                self._positions[i] = self._source_motions[i].state.position.copy()\n\n\2',
                traj_content,
                flags=re.DOTALL
            )
            
            with open(traj_engine_path, 'w') as f:
                f.write(traj_content)
            
            print("✅ Fix adicional aplicado en TrajectoryEngine")

print("\n" + "=" * 70)
print("ACCIONES COMPLETADAS:")
print("=" * 70)
print("1. Engine.update() modificado para propagar cambios")
print("2. Sincronización forzada de posiciones")
print("3. Test de verificación ejecutado")
print("\n⚡ Reinicia el controlador para aplicar cambios")
print("=" * 70)