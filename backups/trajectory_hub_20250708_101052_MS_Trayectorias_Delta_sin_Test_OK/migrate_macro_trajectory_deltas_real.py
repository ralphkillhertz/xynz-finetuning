# === migrate_macro_trajectory_deltas_real.py ===
# 🔧 Fix: Añadir calculate_delta a MacroTrajectory existente
# ⚡ Impacto: ALTO - Permite composición con otros componentes
# 🎯 Tiempo: 2 minutos

import os
import shutil
from datetime import datetime

print("🚀 Migrando MacroTrajectory REAL a sistema de deltas...")

file_path = "trajectory_hub/core/motion_components.py"
backup_path = f"{file_path}.backup_macro_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)
print(f"📦 Backup: {backup_path}")

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar dónde insertar calculate_delta (después del método update)
insert_line = None
for i, line in enumerate(lines):
    if 'class MacroTrajectory' in line:
        # Buscar el método update
        for j in range(i, min(i+100, len(lines))):
            if 'def update(' in lines[j] and 'self' in lines[j]:
                # Buscar el final del método update
                indent_level = len(lines[j]) - len(lines[j].lstrip())
                for k in range(j+1, len(lines)):
                    if lines[k].strip() and (len(lines[k]) - len(lines[k].lstrip())) <= indent_level:
                        # Encontramos el siguiente método o fin de clase
                        insert_line = k
                        break
                break
        break

if insert_line is None:
    print("❌ No se pudo encontrar dónde insertar calculate_delta")
    exit(1)

# Crear el método calculate_delta
calculate_delta_method = '''    
    def calculate_delta(self, state: 'MotionState', current_time: float, dt: float) -> Optional['MotionDelta']:
        """Calcular delta de movimiento para trayectoria macro"""
        if not self.enabled or not self.trajectory_func:
            return None
        
        # Calcular nueva fase
        new_phase = self.phase + self.speed * dt
        
        # Obtener posición objetivo de la trayectoria
        target_position = self.trajectory_func(new_phase)
        
        # Calcular delta desde la posición actual
        delta_position = target_position - self.last_position
        
        # Actualizar fase y última posición para próximo cálculo
        self.phase = new_phase
        self.last_position = target_position.copy()
        
        # Manejar orientación si existe
        delta_orientation = np.zeros(3)
        if self.orientation_func:
            target_orientation = self.orientation_func(new_phase)
            delta_orientation = target_orientation - self.last_orientation
            self.last_orientation = target_orientation.copy()
        
        # Crear y retornar MotionDelta
        return MotionDelta(
            position=delta_position,
            orientation=delta_orientation,
            aperture=0.0
        )
'''

# Insertar el método
lines.insert(insert_line, calculate_delta_method + '\n')
print(f"✅ Método calculate_delta insertado en línea {insert_line}")

# Guardar archivo
with open(file_path, 'w') as f:
    f.writelines(lines)

print("✅ MacroTrajectory migrado exitosamente")

# Crear test mejorado
test_code = '''# === test_macro_trajectory_deltas_working.py ===
import numpy as np
import time
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test de MacroTrajectory con sistema de deltas...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
print("\\n1️⃣ Creando macro 'orbita'...")
engine.create_macro("orbita", [0, 1, 2, 3, 4])

# Configurar trayectoria circular
print("\\n2️⃣ Configurando trayectoria circular...")
try:
    engine.set_macro_trajectory("orbita", "circular", speed=2.0)
    print("✅ Trayectoria configurada")
except Exception as e:
    print(f"❌ Error configurando trayectoria: {e}")
    exit(1)

# Verificar componentes
print("\\n3️⃣ Verificando componentes...")
for sid in range(5):
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        components = list(motion.active_components.keys())
        print(f"  Fuente {sid}: {components}")

# Test de movimiento
print("\\n4️⃣ Probando movimiento (2 segundos)...")
positions_start = {}
for sid in range(5):
    positions_start[sid] = engine._positions[sid].copy()
    print(f"  Fuente {sid} empieza en: {positions_start[sid]}")

# Simular 2 segundos
start_time = time.time()
frames = 0
while time.time() - start_time < 2.0:
    engine.update()
    frames += 1
    time.sleep(1/60)  # 60 FPS

print(f"\\n✅ {frames} frames procesados")

# Verificar movimiento final
print("\\n5️⃣ Verificando posiciones finales:")
all_moved = True
for sid in range(5):
    pos_final = engine._positions[sid]
    distance = np.linalg.norm(pos_final - positions_start[sid])
    
    if distance > 0.1:
        print(f"  ✅ Fuente {sid}: movió {distance:.2f} unidades")
    else:
        print(f"  ❌ Fuente {sid}: NO se movió (dist={distance:.4f})")
        all_moved = False

if all_moved:
    print("\\n🎉 ¡ÉXITO TOTAL! MacroTrajectory funciona con deltas")
else:
    print("\\n⚠️ Algunas fuentes no se movieron")
    
# Test adicional: cambiar tipo de trayectoria
print("\\n6️⃣ Probando cambio de trayectoria...")
engine.set_macro_trajectory("orbita", "figure_eight", speed=1.5)
pos_before = engine._positions[0].copy()

for _ in range(60):  # 1 segundo
    engine.update()
    
pos_after = engine._positions[0].copy()
if np.linalg.norm(pos_after - pos_before) > 0.1:
    print("✅ Figure eight también funciona")
else:
    print("❌ Figure eight no genera movimiento")

print("\\n✅ Test completado")
'''

with open("test_macro_trajectory_deltas_working.py", "w") as f:
    f.write(test_code)

print("\n📝 Test creado: test_macro_trajectory_deltas_working.py")
print("🚀 Ejecuta: python test_macro_trajectory_deltas_working.py")

# Verificar la migración
print("\n🔍 Verificando migración...")
with open(file_path, 'r') as f:
    content = f.read()
    
if "calculate_delta" in content and "class MacroTrajectory" in content:
    print("✅ calculate_delta añadido correctamente a MacroTrajectory")
else:
    print("❌ Error en la migración")