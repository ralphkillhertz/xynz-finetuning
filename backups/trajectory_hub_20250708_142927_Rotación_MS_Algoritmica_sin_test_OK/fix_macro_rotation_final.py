# === fix_macro_rotation_final.py ===
# 🔧 Solución definitiva: verificar y corregir la clase MacroRotation
# ⚡ Asegurar que solo hay una definición correcta

from pathlib import Path
import re

print("🔍 Buscando todas las definiciones de MacroRotation...")

# 1. Buscar en motion_components.py
motion_path = Path("trajectory_hub/core/motion_components.py")
content = motion_path.read_text()

# Contar cuántas veces aparece "class MacroRotation"
matches = re.findall(r'class MacroRotation', content)
print(f"\n📊 Definiciones encontradas en motion_components.py: {len(matches)}")

if len(matches) > 1:
    print("❌ Múltiples definiciones encontradas!")
    
    # Encontrar todas las posiciones
    positions = []
    start = 0
    while True:
        pos = content.find("class MacroRotation", start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    
    print(f"   Posiciones: {positions}")
    
    # Mantener solo la última (más completa)
    print("\n🔧 Eliminando definiciones duplicadas...")
    
    # Trabajar de atrás hacia adelante para no afectar índices
    for i in range(len(positions) - 2, -1, -1):
        start_pos = positions[i]
        # Encontrar el final de esta clase
        next_class = content.find("\nclass ", start_pos + 1)
        if next_class == -1 or (i < len(positions) - 1 and next_class > positions[i + 1]):
            next_class = positions[i + 1]
        
        # Eliminar esta definición
        content = content[:start_pos] + content[next_class:]
    
    # Guardar
    motion_path.write_text(content)
    print("✅ Definiciones duplicadas eliminadas")

# 2. Verificar que la definición restante tenga calculate_delta
if "def calculate_delta" not in content[content.rfind("class MacroRotation"):]:
    print("\n❌ La clase MacroRotation no tiene calculate_delta")
    print("🔧 Buscando la implementación correcta...")
    
    # Buscar en los backups
    backups = list(Path(".").glob("trajectory_hub/core/motion_components.backup_*"))
    for backup in sorted(backups, reverse=True):
        backup_content = backup.read_text()
        if "class MacroRotation" in backup_content and "def calculate_delta" in backup_content:
            print(f"✅ Implementación correcta encontrada en: {backup}")
            
            # Extraer la clase completa
            start = backup_content.find("class MacroRotation")
            next_class = backup_content.find("\nclass ", start + 1)
            if next_class == -1:
                next_class = len(backup_content)
            
            correct_class = backup_content[start:next_class]
            
            # Reemplazar en el archivo actual
            current_start = content.rfind("class MacroRotation")
            current_next = content.find("\nclass ", current_start + 1)
            if current_next == -1:
                current_next = len(content)
            
            content = content[:current_start] + correct_class + content[current_next:]
            motion_path.write_text(content)
            print("✅ Clase MacroRotation restaurada con calculate_delta")
            break

# 3. Crear test final
with open("test_macro_rotation_working.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Test final de MacroRotation que debe funcionar"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎯 TEST FINAL MacroRotation - Versión Definitiva")
print("=" * 60)

# 1. Crear engine y macro
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("rotation_test", source_count=4, formation="square", spacing=4.0)
print(f"✅ Macro creado: {macro_name}")

# 2. Verificar posiciones iniciales
print("\\n📍 Posiciones iniciales:")
initial_positions = {}
for i in range(4):
    pos = engine._positions[i].copy()
    initial_positions[i] = pos
    print(f"  F{i}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# 3. Aplicar rotación
print("\\n🔄 Aplicando rotación Y = 1.0 rad/s...")
success = engine.set_macro_rotation(macro_name, speed_y=1.0)
print(f"  Configuración: {'✅ Exitosa' if success else '❌ Falló'}")

# 4. Debug componentes
if success:
    print("\\n🔍 Verificando componentes:")
    for i in range(4):
        if i in engine.motion_states:
            motion = engine.motion_states[i]
            if 'macro_rotation' in motion.active_components:
                rot = motion.active_components['macro_rotation']
                print(f"  F{i}: enabled={rot.enabled}, speed_y={rot.speed_y}")
                
                # Verificar que tenga calculate_delta
                if hasattr(rot, 'calculate_delta'):
                    # Test rápido
                    delta = rot.calculate_delta(motion, 0, 0.016)
                    print(f"       calculate_delta: ✅ (delta={delta.position if hasattr(delta, 'position') else 'None'})")
                else:
                    print(f"       calculate_delta: ❌ NO EXISTE")

# 5. Simular
print("\\n⏱️ Simulando 60 frames (1 segundo)...")
for frame in range(60):
    engine.update()
    
    # Mostrar progreso
    if frame % 20 == 0:
        pos = engine._positions[0]
        print(f"  Frame {frame}: F0 en [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# 6. Verificar resultados
print("\\n📊 RESULTADOS:")
total_movement = 0.0

for i in range(4):
    initial = initial_positions[i]
    final = engine._positions[i]
    distance = np.linalg.norm(final - initial)
    total_movement += distance
    
    print(f"\\nF{i}:")
    print(f"  Inicial: [{initial[0]:6.2f}, {initial[1]:6.2f}, {initial[2]:6.2f}]")
    print(f"  Final:   [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
    print(f"  Distancia: {distance:.3f}")
    
    # Calcular ángulo de rotación
    if distance > 0.01:
        angle = np.arctan2(final[2] - initial[2], final[0] - initial[0])
        print(f"  Ángulo: {np.degrees(angle):.1f}°")

avg_movement = total_movement / 4
print(f"\\n📈 Movimiento promedio: {avg_movement:.3f}")

# 7. Veredicto
if avg_movement > 0.5:
    print("\\n✅ ¡ÉXITO TOTAL! MacroRotation funciona perfectamente")
    print("   El sistema de deltas está operativo")
else:
    print("\\n❌ Sin movimiento suficiente")
    print("   Verificar el procesamiento de deltas en engine.update()")
''')

print("\n✅ Archivos corregidos")
print("\n📝 Ejecuta:")
print("  1. python test_macro_rotation_working.py")