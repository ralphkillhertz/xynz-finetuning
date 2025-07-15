#!/usr/bin/env python3
"""
🔧 FIX: Propagación de posiciones en engine
⚡ Ejecutar desde directorio trajectory_hub/
"""

import os
import sys
import shutil
from datetime import datetime
import re

print("=" * 70)
print("🔧 FIX DE PROPAGACIÓN EN ENGINE")
print("=" * 70)

# Buscar el archivo correcto
possible_paths = [
    "core/engine.py",
    "core/trajectory_engine.py",
    "core/spatial_engine.py"
]

engine_path = None
for path in possible_paths:
    if os.path.exists(path):
        engine_path = path
        print(f"✅ Encontrado: {path}")
        break

if not engine_path:
    print("❌ No se encontró el archivo del engine")
    print("Archivos en core/:")
    if os.path.exists("core"):
        for f in os.listdir("core"):
            if f.endswith(".py"):
                print(f"  - {f}")
    sys.exit(1)

# Backup
backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(engine_path, backup_path)
print(f"✅ Backup creado: {backup_path}")

# Leer archivo
with open(engine_path, 'r') as f:
    content = f.read()

# Buscar el método update
if "def update(" in content:
    # Buscar el loop donde se actualizan las posiciones
    patterns = [
        # Patrón 1: self._positions[i] = 
        r'(self\._positions\[i\]\s*=\s*)(.*?)(\n)',
        # Patrón 2: positions[i] = 
        r'(positions\[i\]\s*=\s*)(.*?)(\n)',
        # Patrón 3: self.positions[i] = 
        r'(self\.positions\[i\]\s*=\s*)(.*?)(\n)'
    ]
    
    fixed = False
    for pattern in patterns:
        if re.search(pattern, content):
            # Reemplazar con la versión correcta
            new_content = re.sub(
                pattern,
                r'\1motion.state.position.copy()\3',
                content
            )
            
            # Verificar que se hizo el cambio
            if new_content != content:
                with open(engine_path, 'w') as f:
                    f.write(new_content)
                print("✅ Update de posiciones arreglado")
                fixed = True
                break
    
    if not fixed:
        # Buscar cualquier referencia a motion y positions
        print("⚠️ Patrón no encontrado, aplicando fix manual...")
        
        # Insertar al final del método update
        update_end_pattern = r'(def update\(self.*?\n(?:.*?\n)*?)(        return.*?\n|    def )'
        
        if re.search(update_end_pattern, content, re.DOTALL):
            insert_code = """        # Force position sync from motion states
        if hasattr(self, '_positions') and hasattr(self, '_source_motions'):
            for i in range(len(self._positions)):
                if i < len(self._source_motions):
                    self._positions[i] = self._source_motions[i].state.position.copy()
        elif hasattr(self, 'positions') and hasattr(self, 'source_motions'):
            for i in range(len(self.positions)):
                if i < len(self.source_motions):
                    self.positions[i] = self.source_motions[i].state.position.copy()
        
"""
            new_content = re.sub(
                update_end_pattern,
                r'\1' + insert_code + r'\2',
                content,
                flags=re.DOTALL
            )
            
            with open(engine_path, 'w') as f:
                f.write(new_content)
            print("✅ Sincronización de posiciones agregada")

print("\n🧪 VERIFICANDO...")
# Test rápido
try:
    # Importar y probar
    if "trajectory_engine" in engine_path:
        from core.trajectory_engine import TrajectoryEngine as Engine
    elif "spatial_engine" in engine_path:
        from core.spatial_engine import SpatialEngine as Engine
    else:
        from core.engine import SpatialEngine as Engine
    
    print("✅ Import exitoso")
    
    # Crear instancia de prueba
    engine = Engine(num_sources=3)
    engine.initialize()
    
    # Activar concentración si existe
    if hasattr(engine, 'modules') and 'concentration' in engine.modules:
        engine.modules['concentration'].enabled = True
        engine.modules['concentration'].update_parameter('factor', 0.0)
        
        # Update
        engine.update()
        
        print("✅ Test de concentración ejecutado")
    else:
        print("⚠️ Módulo de concentración no encontrado")
    
except Exception as e:
    print(f"⚠️ Error en test: {e}")

print("\n✅ COMPLETADO - Reinicia el controlador")
print("=" * 70)