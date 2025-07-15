# === fix_manual_rotation_state.py ===
# 🔧 Fix: Sincronizar state.position y corregir acumulación de deltas
# ⚡ El problema es que state.position no refleja la posición real
# 🎯 Impacto: CRÍTICO - Sin esto las rotaciones se acumulan incorrectamente

import os
import re

def fix_manual_rotation_calculate_delta():
    """Corrige el calculate_delta para usar la posición correcta"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔧 Corrigiendo calculate_delta en ManualMacroRotation...")
    
    # Leer el archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método calculate_delta en ManualMacroRotation
    # Encontrar la clase primero
    class_start = content.find("class ManualMacroRotation")
    if class_start == -1:
        print("❌ No se encontró ManualMacroRotation")
        return False
    
    # Encontrar el final de la clase
    next_class = content.find("\nclass ", class_start + 1)
    if next_class == -1:
        next_class = len(content)
    
    class_content = content[class_start:next_class]
    
    # Nuevo método calculate_delta corregido
    new_calculate_delta = '''    def calculate_delta(self, state, current_time, dt):
        """Calcula el delta de rotación manual"""
        if not self.enabled:
            return None
        
        # Interpolar hacia los ángulos objetivo
        factor = self.interpolation_speed
        
        # Suavizar la interpolación con dt
        smooth_factor = 1.0 - pow(1.0 - factor, dt * 60.0)  # Normalizado a 60 FPS
        
        # Calcular la diferencia angular
        pitch_diff = self.target_pitch - self.current_pitch
        yaw_diff = self.target_yaw - self.current_yaw
        roll_diff = self.target_roll - self.current_roll
        
        # Solo actualizar si hay diferencia significativa
        if abs(pitch_diff) > 0.001 or abs(yaw_diff) > 0.001 or abs(roll_diff) > 0.001:
            self.current_pitch += pitch_diff * smooth_factor
            self.current_yaw += yaw_diff * smooth_factor
            self.current_roll += roll_diff * smooth_factor
        
        # Calcular matriz de rotación con los ángulos actuales
        rotation_matrix = self._calculate_rotation_matrix(
            self.current_pitch, 
            self.current_yaw, 
            self.current_roll
        )
        
        # IMPORTANTE: Usar la posición real del state, no [0,0,0]
        current_position = state.position
        
        # Aplicar rotación alrededor del centro
        relative_pos = current_position - self.center
        rotated_pos = rotation_matrix @ relative_pos
        new_position = rotated_pos + self.center
        
        # Crear delta (diferencia entre nueva y actual)
        delta = MotionDelta()
        delta.position = new_position - current_position
        
        # Solo retornar delta si hay movimiento significativo
        if np.linalg.norm(delta.position) < 0.0001:
            return None
        
        return delta'''
    
    # Buscar y reemplazar el método calculate_delta
    method_pattern = r'def calculate_delta\(self[^:]+\):[^}]+?return delta'
    
    if re.search(method_pattern, class_content, re.DOTALL):
        # Reemplazar el método existente
        new_class_content = re.sub(method_pattern, new_calculate_delta.strip(), class_content, flags=re.DOTALL)
        
        # Reemplazar en el contenido completo
        new_content = content[:class_start] + new_class_content + content[next_class:]
        
        # Hacer backup
        import shutil
        from datetime import datetime
        backup_name = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(motion_path, backup_name)
        print(f"✅ Backup creado: {backup_name}")
        
        # Escribir
        with open(motion_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ calculate_delta corregido")
        return True
    else:
        print("❌ No se encontró el método calculate_delta")
        return False

def fix_state_synchronization():
    """Asegura que state.position se sincronice con _positions"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("\n🔧 Verificando sincronización de state en engine.update()...")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    update_match = re.search(r'def update\(self.*?\):\s*\n(.*?)(?=\n    def|\Z)', content, re.DOTALL)
    
    if update_match:
        update_body = update_match.group(1)
        
        # Ver si ya sincroniza state.position
        if "state.position = " in update_body or "motion.state.position = " in update_body:
            print("✅ Ya parece sincronizar state.position")
        else:
            print("⚠️ No parece sincronizar state.position")
            print("   Esto puede causar que los deltas se calculen incorrectamente")
    
    return True

def create_final_test():
    """Test final de rotación manual"""
    
    test_code = '''# === test_manual_rotation_final.py ===
# 🧪 Test final de rotación manual con deltas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🧪 TEST FINAL: Rotación Manual con Deltas")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60, enable_modulator=False)

# Crear macro con posiciones en cuadrado
macro_name = engine.create_macro("square", source_count=4)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Establecer posiciones en cuadrado
positions = [
    np.array([3.0, 3.0, 0.0]),   # Superior derecha
    np.array([-3.0, 3.0, 0.0]),  # Superior izquierda
    np.array([-3.0, -3.0, 0.0]), # Inferior izquierda
    np.array([3.0, -3.0, 0.0])   # Inferior derecha
]

print("📍 Posiciones iniciales (cuadrado):")
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    # IMPORTANTE: Sincronizar con el state
    if sid in engine.motion_states:
        engine.motion_states[sid].state.position = pos.copy()
    print(f"   Fuente {sid}: {pos}")

# Test 1: Rotación de 45 grados
print("\\n🔄 Test 1: Rotación de 45 grados en Yaw")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/4,  # 45 grados
    interpolation_speed=0.1
)

# Ejecutar updates
for i in range(20):
    engine.update()
    
    # Sincronizar states después de cada update
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()

print("\\nPosiciones después de rotar 45°:")
for sid in source_ids:
    print(f"   Fuente {sid}: {engine._positions[sid]}")

# Test 2: Rotación completa
print("\\n🔄 Test 2: Rotación completa (180 grados)")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi,  # 180 grados
    interpolation_speed=0.05  # Más lento
)

for i in range(40):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()
    
    if i % 10 == 0:
        pos = engine._positions[source_ids[0]]
        print(f"   Update {i}: Primera fuente en [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Verificar resultado
print("\\n📊 RESULTADO FINAL:")
print("-" * 40)

# El cuadrado debería estar rotado 180 grados
expected_positions = [
    np.array([-3.0, -3.0, 0.0]),  # Opuesto a superior derecha
    np.array([3.0, -3.0, 0.0]),   # Opuesto a superior izquierda
    np.array([3.0, 3.0, 0.0]),    # Opuesto a inferior izquierda
    np.array([-3.0, 3.0, 0.0])    # Opuesto a inferior derecha
]

all_correct = True
for sid, expected in zip(source_ids, expected_positions):
    actual = engine._positions[sid]
    error = np.linalg.norm(actual - expected)
    
    status = "✅" if error < 0.5 else "❌"
    print(f"Fuente {sid}: {actual} (error: {error:.3f}) {status}")
    
    if error > 0.5:
        all_correct = False

print("\\n" + "=" * 60)
if all_correct:
    print("✅ ¡ÉXITO! La rotación manual funciona perfectamente con deltas")
else:
    print("⚠️ La rotación funciona pero no es perfecta")
'''
    
    with open("test_manual_rotation_final.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test final creado")

if __name__ == "__main__":
    print("🔧 FIX MANUAL ROTATION STATE")
    print("=" * 50)
    
    if fix_manual_rotation_calculate_delta():
        fix_state_synchronization()
        create_final_test()
        
        print("\n✅ Fixes aplicados")
        print("\n📝 Ejecuta:")
        print("python test_manual_rotation_final.py")
        print("\n💡 El fix corrige:")
        print("   - Usa state.position real en lugar de [0,0,0]")
        print("   - Evita acumulación infinita de deltas")
        print("   - Solo retorna delta si hay movimiento significativo")
    else:
        print("\n❌ Error aplicando fixes")