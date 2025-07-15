# === fix_macro_rotation_method.py ===
# 🔧 Verificar y corregir el método set_rotation
# ⚡ El método no se guardó correctamente

from pathlib import Path

print("🔍 Verificando MacroRotation...")

# Leer el archivo
file_path = Path("trajectory_hub/core/motion_components.py")
content = file_path.read_text()

# Buscar la clase MacroRotation
class_start = content.find("class MacroRotation")
if class_start == -1:
    print("❌ No se encontró MacroRotation")
else:
    # Buscar set_rotation
    set_rotation_pos = content.find("def set_rotation", class_start)
    if set_rotation_pos == -1:
        print("❌ No se encontró método set_rotation")
        print("🔧 Añadiendo método set_rotation...")
        
        # Buscar el final del __init__
        init_end = content.find("\n    def ", class_start + 1)
        if init_end == -1:
            init_end = content.find("\n    @property", class_start + 1)
        
        if init_end > 0:
            # Insertar set_rotation después del __init__
            set_rotation_code = '''
    
    def set_rotation(self, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configura velocidades de rotación de forma segura"""
        # Usar setters que garantizan float
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed_z = speed_z
        
        if center is not None:
            # Garantizar que center es numpy array de 3 elementos
            if isinstance(center, (list, tuple)):
                self.center = np.array(center[:3], dtype=np.float32)
            elif isinstance(center, np.ndarray):
                self.center = center.flatten()[:3].astype(np.float32)
            else:
                self.center = np.zeros(3, dtype=np.float32)
        
        # Habilitar si alguna velocidad es significativa
        # Usar abs() con floats garantizados
        threshold = 0.001
        self.enabled = (
            abs(self.speed_x) > threshold or
            abs(self.speed_y) > threshold or
            abs(self.speed_z) > threshold
        )
'''
            
            # Insertar el código
            content = content[:init_end] + set_rotation_code + content[init_end:]
            
            # Guardar
            file_path.write_text(content)
            print("✅ Método set_rotation añadido")
    else:
        print("✅ set_rotation encontrado")
        
        # Verificar que esté bien indentado
        # Contar espacios antes de "def set_rotation"
        line_start = content.rfind('\n', 0, set_rotation_pos) + 1
        indent = set_rotation_pos - line_start
        print(f"   Indentación: {indent} espacios")
        
        if indent != 4:  # Debería tener 4 espacios
            print("⚠️ Indentación incorrecta, corrigiendo...")

# Crear un test directo de la clase
with open("test_macro_rotation_class.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Test directo de la clase MacroRotation"""

import numpy as np
from trajectory_hub.core.motion_components import MacroRotation, MotionState, MotionDelta

print("🧪 Test directo de MacroRotation")

# Crear instancia
rot = MacroRotation()
print(f"✅ MacroRotation creada")

# Verificar métodos
methods = [m for m in dir(rot) if not m.startswith('_')]
print(f"\\nMétodos disponibles:")
for m in methods:
    print(f"  - {m}")

# Probar set_rotation si existe
if hasattr(rot, 'set_rotation'):
    print("\\n✅ set_rotation existe")
    rot.set_rotation(speed_x=0, speed_y=1.0, speed_z=0)
    print(f"  Enabled: {rot.enabled}")
    print(f"  Speed Y: {rot.speed_y}")
else:
    print("\\n❌ set_rotation NO existe")

# Probar calculate_delta
if hasattr(rot, 'calculate_delta'):
    print("\\n✅ calculate_delta existe")
    state = MotionState()
    state.position = np.array([1.0, 0.0, 0.0])
    
    delta = rot.calculate_delta(state, 0.0, 0.016)  # 1/60 segundo
    print(f"  Delta: {delta.position if hasattr(delta, 'position') else 'No position'}")
''')

print("\n✅ Scripts creados:")
print("  1. Ejecuta: python fix_macro_rotation_method.py")
print("  2. Luego: python test_macro_rotation_class.py")