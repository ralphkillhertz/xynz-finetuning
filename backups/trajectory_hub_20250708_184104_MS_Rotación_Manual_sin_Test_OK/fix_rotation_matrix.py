# === fix_rotation_matrix.py ===
# 🔧 Fix: Corregir matriz de rotación para que funcione correctamente
# ⚡ Problema: Rotación introduce valores Z incorrectos
# 🎯 Impacto: CRÍTICO - Rotaciones completamente incorrectas

import os
import re
import numpy as np

def fix_rotation_matrix():
    """Corrige la matriz de rotación en ManualMacroRotation"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔧 Corrigiendo matriz de rotación...")
    
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
    
    # Método _calculate_rotation_matrix corregido
    new_rotation_method = '''    def _calculate_rotation_matrix(self, pitch, yaw, roll):
        """Calcula matriz de rotación 3D correctamente"""
        # Matrices individuales de rotación
        # Rotación en X (pitch)
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(pitch), -np.sin(pitch)],
            [0, np.sin(pitch), np.cos(pitch)]
        ])
        
        # Rotación en Y (yaw) - Esta es la más común
        Ry = np.array([
            [np.cos(yaw), 0, np.sin(yaw)],
            [0, 1, 0],
            [-np.sin(yaw), 0, np.cos(yaw)]
        ])
        
        # Rotación en Z (roll)
        Rz = np.array([
            [np.cos(roll), -np.sin(roll), 0],
            [np.sin(roll), np.cos(roll), 0],
            [0, 0, 1]
        ])
        
        # Orden: primero yaw, luego pitch, luego roll
        # Esto evita gimbal lock y es más intuitivo
        return Rz @ Rx @ Ry'''
    
    # Método calculate_delta simplificado
    new_calculate_delta = '''    def calculate_delta(self, state, current_time, dt):
        """Calcula el delta de rotación manual"""
        if not self.enabled:
            return None
        
        # Umbral para considerar que llegamos al objetivo
        angle_threshold = 0.001  # radianes
        
        # Calcular diferencias angulares
        pitch_diff = self.target_pitch - self.current_pitch
        yaw_diff = self.target_yaw - self.current_yaw
        roll_diff = self.target_roll - self.current_roll
        
        # Normalizar ángulos a [-pi, pi] para tomar el camino más corto
        pitch_diff = np.arctan2(np.sin(pitch_diff), np.cos(pitch_diff))
        yaw_diff = np.arctan2(np.sin(yaw_diff), np.cos(yaw_diff))
        roll_diff = np.arctan2(np.sin(roll_diff), np.cos(roll_diff))
        
        # Factor de interpolación base
        base_factor = self.interpolation_speed
        
        # Aplicar interpolación suave
        smooth_factor = 1.0 - pow(1.0 - base_factor, dt * 60.0)
        
        # Actualizar ángulos actuales
        if abs(pitch_diff) > angle_threshold:
            self.current_pitch += pitch_diff * smooth_factor
        else:
            self.current_pitch = self.target_pitch
            
        if abs(yaw_diff) > angle_threshold:
            self.current_yaw += yaw_diff * smooth_factor
        else:
            self.current_yaw = self.target_yaw
            
        if abs(roll_diff) > angle_threshold:
            self.current_roll += roll_diff * smooth_factor
        else:
            self.current_roll = self.target_roll
        
        # Normalizar ángulos actuales
        self.current_pitch = np.arctan2(np.sin(self.current_pitch), np.cos(self.current_pitch))
        self.current_yaw = np.arctan2(np.sin(self.current_yaw), np.cos(self.current_yaw))
        self.current_roll = np.arctan2(np.sin(self.current_roll), np.cos(self.current_roll))
        
        # Calcular matriz de rotación
        rotation_matrix = self._calculate_rotation_matrix(
            self.current_pitch, 
            self.current_yaw, 
            self.current_roll
        )
        
        # Usar la posición real del state
        current_position = np.array(state.position)
        
        # Aplicar rotación alrededor del centro
        relative_pos = current_position - self.center
        rotated_pos = rotation_matrix @ relative_pos
        new_position = rotated_pos + self.center
        
        # Crear delta
        delta = MotionDelta()
        delta.position = new_position - current_position
        
        # Debug para ver qué está pasando
        if abs(yaw_diff) > 0.01:  # Solo si estamos rotando significativamente
            # Verificar que la rotación es correcta
            dist_before = np.linalg.norm(relative_pos)
            dist_after = np.linalg.norm(rotated_pos)
            if abs(dist_before - dist_after) > 0.001:
                print(f"⚠️ Distancia cambió: {dist_before:.3f} -> {dist_after:.3f}")
        
        # Solo retornar delta si hay movimiento significativo
        if np.linalg.norm(delta.position) < 0.0001:
            return None
        
        return delta'''
    
    # Buscar clase ManualMacroRotation completa
    class_content = content[class_start:next_class]
    
    # Primero agregar el método _calculate_rotation_matrix si no existe
    if "_calculate_rotation_matrix" not in class_content:
        # Insertar antes del método calculate_delta
        calc_delta_pos = class_content.find("def calculate_delta")
        if calc_delta_pos != -1:
            class_content = (class_content[:calc_delta_pos] + 
                           new_rotation_method + "\n\n    " + 
                           class_content[calc_delta_pos:])
    else:
        # Reemplazar el método existente
        rotation_pattern = r'def _calculate_rotation_matrix\(self[^:]+\):[^}]+?return[^\n]+'
        class_content = re.sub(rotation_pattern, new_rotation_method.strip(), class_content, flags=re.DOTALL)
    
    # Reemplazar calculate_delta
    delta_pattern = r'def calculate_delta\(self[^:]+\):[^}]+?return delta'
    class_content = re.sub(delta_pattern, new_calculate_delta.strip(), class_content, flags=re.DOTALL)
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(motion_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Escribir cambios
    new_content = content[:class_start] + class_content + content[next_class:]
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Matriz de rotación corregida")
    return True

def create_simple_yaw_test():
    """Test simple solo con rotación Yaw"""
    
    test_code = '''# === test_yaw_rotation.py ===
# 🧪 Test simple de rotación Yaw únicamente

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🧪 TEST SIMPLE: Solo rotación Yaw")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)

# Crear macro
macro_name = engine.create_macro("square", source_count=4)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Posiciones simples en cuadrado
positions = [
    np.array([2.0, 2.0, 0.0]),   # Superior derecha
    np.array([-2.0, 2.0, 0.0]),  # Superior izquierda
    np.array([-2.0, -2.0, 0.0]), # Inferior izquierda
    np.array([2.0, -2.0, 0.0])   # Inferior derecha
]

print("📍 Posiciones iniciales:")
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    if sid in engine.motion_states:
        engine.motion_states[sid].state.position = pos.copy()
    print(f"   Fuente {sid}: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]")

# Test: Rotación de 90 grados SOLO en Yaw
print("\\n🔄 Rotando 90 grados en Yaw (sin pitch ni roll)")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/2,      # 90 grados
    pitch=0.0,          # Sin pitch
    roll=0.0,           # Sin roll
    interpolation_speed=0.2  # Más rápido
)

# Verificar valores iniciales
if macro_name in engine.motion_states:
    for sid in source_ids:
        if sid in engine.motion_states:
            comp = engine.motion_states[sid].active_components.get('manual_macro_rotation')
            if comp:
                print(f"\\n🎯 Rotación configurada:")
                print(f"   Target Yaw: {comp.target_yaw:.3f} ({math.degrees(comp.target_yaw):.1f}°)")
                print(f"   Target Pitch: {comp.target_pitch:.3f}")
                print(f"   Target Roll: {comp.target_roll:.3f}")
                break

# Ejecutar rotación
print("\\n⚙️ Ejecutando rotación...")
for i in range(100):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()
    
    # Mostrar progreso
    if i in [0, 25, 50, 75, 99]:
        pos = engine._positions[source_ids[0]]
        print(f"   Frame {i:3d}: Primera fuente en [{pos[0]:6.3f}, {pos[1]:6.3f}, Z={pos[2]:6.3f}]")

# Verificar resultado final
print("\\n📊 RESULTADO FINAL:")
print("-" * 60)

# Posiciones esperadas después de 90° de rotación en Yaw
# Rotación 90° antihoraria vista desde arriba
expected = [
    np.array([-2.0, 2.0, 0.0]),  # De [2,2] a [-2,2]
    np.array([-2.0, -2.0, 0.0]), # De [-2,2] a [-2,-2]
    np.array([2.0, -2.0, 0.0]),  # De [-2,-2] a [2,-2]
    np.array([2.0, 2.0, 0.0])    # De [2,-2] a [2,2]
]

total_error = 0
z_errors = []
for i, (sid, exp) in enumerate(zip(source_ids, expected)):
    actual = engine._positions[sid]
    error_xy = np.linalg.norm(actual[:2] - exp[:2])  # Error solo en XY
    error_z = abs(actual[2])  # Z debería ser 0
    z_errors.append(error_z)
    total_error += error_xy
    
    status = "✅" if error_xy < 0.1 and error_z < 0.001 else "❌"
    print(f"Fuente {sid}:")
    print(f"   Actual:   [{actual[0]:6.3f}, {actual[1]:6.3f}, {actual[2]:6.3f}]")
    print(f"   Esperado: [{exp[0]:6.3f}, {exp[1]:6.3f}, {exp[2]:6.3f}]")
    print(f"   Error XY: {error_xy:.3f}, Error Z: {error_z:.6f} {status}")

print("\\n" + "=" * 60)
avg_error = total_error / len(source_ids)
max_z_error = max(z_errors)

if avg_error < 0.1 and max_z_error < 0.001:
    print("✅ ¡ÉXITO! Rotación Yaw funciona perfectamente")
    print("   - Todas las fuentes rotaron correctamente")
    print("   - Z se mantuvo en 0 (sin elevación espuria)")
else:
    print("⚠️ Problemas detectados:")
    if avg_error >= 0.1:
        print(f"   - Error XY promedio: {avg_error:.3f}")
    if max_z_error >= 0.001:
        print(f"   - Aparecen valores Z no deseados: max={max_z_error:.6f}")
'''
    
    with open("test_yaw_rotation.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test de Yaw simple creado")

if __name__ == "__main__":
    print("🔧 FIX ROTATION MATRIX")
    print("=" * 50)
    
    if fix_rotation_matrix():
        create_simple_yaw_test()
        
        print("\n✅ Correcciones aplicadas:")
        print("   - Matriz de rotación corregida (orden Rz @ Rx @ Ry)")
        print("   - Matrices individuales para cada eje")
        print("   - Debug de distancias para detectar problemas")
        print("   - Test simple solo con Yaw")
        print("\n📝 Ejecuta:")
        print("python test_yaw_rotation.py")
    else:
        print("\n❌ Error aplicando correcciones")