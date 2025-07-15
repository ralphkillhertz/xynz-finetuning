# === fix_manual_rotation_precision.py ===
# 🔧 Fix: Mejorar precisión de rotaciones manuales
# ⚡ Problema: La rotación no llega al objetivo completo
# 🎯 Impacto: ALTO - Rotaciones imprecisas

import os
import re
import numpy as np

def fix_rotation_precision():
    """Mejora la precisión de las rotaciones manuales"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔧 Mejorando precisión de rotaciones manuales...")
    
    # Leer el archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar ManualMacroRotation
    class_start = content.find("class ManualMacroRotation")
    if class_start == -1:
        print("❌ No se encontró ManualMacroRotation")
        return False
    
    # Encontrar el final de la clase
    next_class = content.find("\nclass ", class_start + 1)
    if next_class == -1:
        next_class = len(content)
    
    # Nuevo método calculate_delta mejorado
    new_calculate_delta = '''    def calculate_delta(self, state, current_time, dt):
        """Calcula el delta de rotación manual con mayor precisión"""
        if not self.enabled:
            return None
        
        # Umbral para considerar que llegamos al objetivo
        angle_threshold = 0.01  # radianes (~0.57 grados)
        
        # Calcular diferencias angulares
        pitch_diff = self.target_pitch - self.current_pitch
        yaw_diff = self.target_yaw - self.current_yaw
        roll_diff = self.target_roll - self.current_roll
        
        # Normalizar ángulos a [-pi, pi]
        pitch_diff = np.arctan2(np.sin(pitch_diff), np.cos(pitch_diff))
        yaw_diff = np.arctan2(np.sin(yaw_diff), np.cos(yaw_diff))
        roll_diff = np.arctan2(np.sin(roll_diff), np.cos(roll_diff))
        
        # Si estamos muy cerca del objetivo, snap directo
        if abs(pitch_diff) < angle_threshold:
            self.current_pitch = self.target_pitch
        else:
            # Interpolación mejorada con aceleración cerca del objetivo
            factor = self.interpolation_speed
            smooth_factor = 1.0 - pow(1.0 - factor, dt * 60.0)
            # Aceleración adicional si estamos lejos
            if abs(pitch_diff) > 0.5:
                smooth_factor = min(smooth_factor * 2.0, 1.0)
            self.current_pitch += pitch_diff * smooth_factor
        
        if abs(yaw_diff) < angle_threshold:
            self.current_yaw = self.target_yaw
        else:
            factor = self.interpolation_speed
            smooth_factor = 1.0 - pow(1.0 - factor, dt * 60.0)
            if abs(yaw_diff) > 0.5:
                smooth_factor = min(smooth_factor * 2.0, 1.0)
            self.current_yaw += yaw_diff * smooth_factor
        
        if abs(roll_diff) < angle_threshold:
            self.current_roll = self.target_roll
        else:
            factor = self.interpolation_speed
            smooth_factor = 1.0 - pow(1.0 - factor, dt * 60.0)
            if abs(roll_diff) > 0.5:
                smooth_factor = min(smooth_factor * 2.0, 1.0)
            self.current_roll += roll_diff * smooth_factor
        
        # Calcular matriz de rotación (YXZ order para evitar gimbal lock)
        # Primero Yaw, luego Pitch, luego Roll
        cy = np.cos(self.current_yaw)
        sy = np.sin(self.current_yaw)
        cp = np.cos(self.current_pitch)
        sp = np.sin(self.current_pitch)
        cr = np.cos(self.current_roll)
        sr = np.sin(self.current_roll)
        
        # Matriz de rotación YXZ
        rotation_matrix = np.array([
            [cy*cr + sy*sp*sr, -cy*sr + sy*sp*cr, sy*cp],
            [cp*sr, cp*cr, -sp],
            [-sy*cr + cy*sp*sr, sy*sr + cy*sp*cr, cy*cp]
        ])
        
        # Usar la posición real del state
        current_position = state.position
        
        # Aplicar rotación alrededor del centro
        relative_pos = current_position - self.center
        rotated_pos = rotation_matrix @ relative_pos
        new_position = rotated_pos + self.center
        
        # Crear delta
        delta = MotionDelta()
        delta.position = new_position - current_position
        
        # Solo retornar delta si hay movimiento significativo
        if np.linalg.norm(delta.position) < 0.0001:
            return None
        
        return delta'''
    
    # Buscar y reemplazar el método
    method_pattern = r'def calculate_delta\(self[^:]+\):[^}]+?return delta'
    
    # Reemplazar en la clase
    class_content = content[class_start:next_class]
    new_class_content = re.sub(method_pattern, new_calculate_delta.strip(), class_content, flags=re.DOTALL)
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(motion_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Escribir cambios
    new_content = content[:class_start] + new_class_content + content[next_class:]
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Precisión de rotaciones mejorada")
    return True

def create_precision_test():
    """Test mejorado con más updates y mejor verificación"""
    
    test_code = '''# === test_rotation_precision.py ===
# 🧪 Test de precisión de rotaciones manuales

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🧪 TEST PRECISIÓN: Rotación Manual Mejorada")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60, enable_modulator=False)

# Crear macro con posiciones en cuadrado
macro_name = engine.create_macro("square", source_count=4)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Establecer posiciones en cuadrado
positions = [
    np.array([3.0, 0.0, 0.0]),   # Derecha
    np.array([0.0, 3.0, 0.0]),   # Arriba
    np.array([-3.0, 0.0, 0.0]),  # Izquierda
    np.array([0.0, -3.0, 0.0])   # Abajo
]

print("📍 Posiciones iniciales (cruz):")
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    if sid in engine.motion_states:
        engine.motion_states[sid].state.position = pos.copy()
    print(f"   Fuente {sid}: {pos}")

# Test 1: Rotación de 90 grados
print("\\n🔄 Test 1: Rotación de 90 grados en Yaw")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/2,  # 90 grados
    interpolation_speed=0.15  # Más rápido
)

# Más updates para asegurar convergencia
for i in range(60):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()

print("\\nPosiciones después de rotar 90°:")
expected_90 = [
    np.array([0.0, 3.0, 0.0]),   # De derecha a arriba
    np.array([-3.0, 0.0, 0.0]),  # De arriba a izquierda
    np.array([0.0, -3.0, 0.0]),  # De izquierda a abajo
    np.array([3.0, 0.0, 0.0])    # De abajo a derecha
]

errors_90 = []
for sid, expected in zip(source_ids, expected_90):
    actual = engine._positions[sid]
    error = np.linalg.norm(actual - expected)
    errors_90.append(error)
    status = "✅" if error < 0.1 else "❌"
    print(f"   Fuente {sid}: [{actual[0]:.3f}, {actual[1]:.3f}, {actual[2]:.3f}] (error: {error:.3f}) {status}")

# Test 2: Rotación completa 180 grados
print("\\n🔄 Test 2: Rotación completa (180 grados)")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi,  # 180 grados
    interpolation_speed=0.1
)

# Muchos más updates
for i in range(100):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()
    
    if i % 25 == 0:
        pos = engine._positions[source_ids[0]]
        print(f"   Update {i}: Primera fuente en [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

print("\\n📊 RESULTADO FINAL:")
print("-" * 40)

expected_180 = [
    np.array([-3.0, 0.0, 0.0]),  # 180° de derecha
    np.array([0.0, -3.0, 0.0]),  # 180° de arriba
    np.array([3.0, 0.0, 0.0]),   # 180° de izquierda
    np.array([0.0, 3.0, 0.0])    # 180° de abajo
]

errors_180 = []
for sid, expected in zip(source_ids, expected_180):
    actual = engine._positions[sid]
    error = np.linalg.norm(actual - expected)
    errors_180.append(error)
    status = "✅" if error < 0.1 else "❌"
    print(f"Fuente {sid}: [{actual[0]:.3f}, {actual[1]:.3f}, {actual[2]:.3f}] (error: {error:.3f}) {status}")

# Resumen
print("\\n" + "=" * 60)
avg_error_90 = np.mean(errors_90)
avg_error_180 = np.mean(errors_180)

print(f"Error promedio 90°: {avg_error_90:.3f}")
print(f"Error promedio 180°: {avg_error_180:.3f}")

if avg_error_90 < 0.1 and avg_error_180 < 0.1:
    print("\\n✅ ¡ÉXITO TOTAL! Las rotaciones manuales son precisas")
elif avg_error_90 < 0.5 and avg_error_180 < 0.5:
    print("\\n✅ Las rotaciones funcionan bien (error < 0.5)")
else:
    print("\\n⚠️ Las rotaciones necesitan más ajuste")
'''
    
    with open("test_rotation_precision.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test de precisión creado")

if __name__ == "__main__":
    print("🔧 FIX ROTATION PRECISION")
    print("=" * 50)
    
    if fix_rotation_precision():
        create_precision_test()
        
        print("\n✅ Mejoras aplicadas:")
        print("   - Normalización de ángulos para camino más corto")
        print("   - Snap al objetivo cuando está muy cerca")
        print("   - Aceleración adicional para ángulos grandes")
        print("   - Orden de rotación YXZ para evitar gimbal lock")
        print("\n📝 Ejecuta:")
        print("python test_rotation_precision.py")
    else:
        print("\n❌ Error aplicando mejoras")