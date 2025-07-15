# === verify_and_fix_rotation.py ===
# 🔧 Fix: Verificar y corregir completamente el algoritmo de rotación
# ⚡ Diagnóstico profundo + corrección definitiva
# 🎯 Impacto: CRÍTICO - Rotación manual MS

import numpy as np
import ast
import re

def verify_current_algorithm():
    """Verifica qué algoritmo está actualmente en el archivo"""
    print("🔍 Verificando algoritmo actual en ManualMacroRotation...")
    
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        content = f.read()
    
    # Buscar el método calculate_delta en ManualMacroRotation
    start = content.find("class ManualMacroRotation")
    if start == -1:
        print("❌ No se encontró ManualMacroRotation")
        return False
        
    # Buscar calculate_delta dentro de esa clase
    class_section = content[start:start+10000]  # Suficiente para la clase
    
    if "usando ángulos polares" in class_section:
        print("✅ El nuevo algoritmo está presente")
        if "np.arctan2(relative_pos[1], relative_pos[0])" in class_section:
            print("✅ Usa atan2 correctamente")
        else:
            print("❌ No encuentra atan2")
            
        # Verificar si hay algún problema
        if "rotation_matrix" in class_section:
            print("⚠️ PROBLEMA: Todavía hay referencias a rotation_matrix")
            return False
    else:
        print("❌ El algoritmo antiguo sigue presente")
        return False
        
    return True

def apply_definitive_fix():
    """Aplica la corrección definitiva del algoritmo"""
    print("\n🔧 Aplicando corrección definitiva...")
    
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        lines = f.readlines()
    
    # Buscar ManualMacroRotation
    in_class = False
    in_calculate_delta = False
    class_indent = ""
    method_start = -1
    method_end = -1
    
    for i, line in enumerate(lines):
        if "class ManualMacroRotation" in line:
            in_class = True
            class_indent = line[:len(line) - len(line.lstrip())]
            
        if in_class and "def calculate_delta" in line and "ManualMacroRotation" in ''.join(lines[max(0,i-50):i]):
            in_calculate_delta = True
            method_start = i
            print(f"📍 Encontrado calculate_delta en línea {i+1}")
            
        if in_calculate_delta and method_start > 0:
            # Buscar el final del método
            if i > method_start and line.strip() and not line.startswith(class_indent + "    "):
                method_end = i
                break
    
    if method_start == -1:
        print("❌ No se encontró el método calculate_delta")
        return False
        
    print(f"📝 Reemplazando líneas {method_start+1} a {method_end}")
    
    # El método correcto completo
    new_method = f'''{class_indent}    def calculate_delta(self, state: 'MotionState', current_time: float, dt: float) -> Optional['MotionDelta']:
{class_indent}        """Calcula el cambio necesario para la rotación manual usando ángulos polares"""
{class_indent}        if not self.enabled:
{class_indent}            return None
{class_indent}            
{class_indent}        from trajectory_hub.core import MotionDelta
{class_indent}        delta = MotionDelta()
{class_indent}        
{class_indent}        current_position = np.array(state.position)
{class_indent}        relative_pos = current_position - self.center
{class_indent}        
{class_indent}        # Solo procesar si no está en el centro
{class_indent}        distance_xy = np.sqrt(relative_pos[0]**2 + relative_pos[1]**2)
{class_indent}        if distance_xy < 0.001:
{class_indent}            # Si está muy cerca del centro, mover ligeramente
{class_indent}            delta.position = np.array([0.1, 0.0, 0.0])
{class_indent}            return delta
{class_indent}        
{class_indent}        # Calcular ángulo actual usando atan2
{class_indent}        current_angle = np.arctan2(relative_pos[1], relative_pos[0])
{class_indent}        
{class_indent}        # Para debug
{class_indent}        # print(f"Pos: {{current_position}}, Angle: {{np.degrees(current_angle):.1f}}°")
{class_indent}        
{class_indent}        # Calcular diferencia angular con el objetivo
{class_indent}        angle_diff = self.target_yaw - current_angle
{class_indent}        
{class_indent}        # Normalizar a [-pi, pi] para tomar la ruta más corta
{class_indent}        while angle_diff > np.pi:
{class_indent}            angle_diff -= 2 * np.pi
{class_indent}        while angle_diff < -np.pi:
{class_indent}            angle_diff += 2 * np.pi
{class_indent}        
{class_indent}        # Aplicar interpolación
{class_indent}        angle_step = angle_diff * self.interpolation_speed * dt
{class_indent}        new_angle = current_angle + angle_step
{class_indent}        
{class_indent}        # Calcular nueva posición manteniendo la distancia
{class_indent}        new_x = distance_xy * np.cos(new_angle) + self.center[0]
{class_indent}        new_y = distance_xy * np.sin(new_angle) + self.center[1]
{class_indent}        new_z = current_position[2]  # Z sin cambios para YAW
{class_indent}        
{class_indent}        new_position = np.array([new_x, new_y, new_z])
{class_indent}        delta.position = new_position - current_position
{class_indent}        
{class_indent}        return delta
'''
    
    # Reemplazar el método
    new_lines = lines[:method_start] + [new_method + '\n'] + lines[method_end:]
    
    # Guardar
    with open("trajectory_hub/core/motion_components.py", 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Método reemplazado completamente")
    return True

def test_rotation_math():
    """Prueba la matemática de la rotación"""
    print("\n🧮 Verificando matemática de rotación:")
    
    # Simular 4 fuentes en cuadrado
    positions = [
        [3, 0, 0],
        [0, 3, 0],
        [-3, 0, 0],
        [0, -3, 0]
    ]
    
    center = np.array([0, 0, 0])
    target_yaw = np.pi/2  # 90 grados
    
    for i, pos in enumerate(positions):
        current_position = np.array(pos)
        relative_pos = current_position - center
        
        # Ángulo actual
        current_angle = np.arctan2(relative_pos[1], relative_pos[0])
        distance = np.sqrt(relative_pos[0]**2 + relative_pos[1]**2)
        
        # Nueva posición después de rotar 90°
        new_angle = current_angle + np.pi/2
        new_x = distance * np.cos(new_angle)
        new_y = distance * np.sin(new_angle)
        
        print(f"   Fuente {i}: {pos} → [{new_x:.1f}, {new_y:.1f}, 0.0]")
        print(f"      Ángulo: {np.degrees(current_angle):.1f}° → {np.degrees(new_angle):.1f}°")

if __name__ == "__main__":
    print("🔍 Diagnóstico y corrección de ManualMacroRotation")
    print("="*60)
    
    # Verificar estado actual
    if verify_current_algorithm():
        print("\n⚠️ El algoritmo parece correcto pero no funciona")
        print("🔧 Aplicando versión definitiva...")
    
    # Aplicar fix definitivo
    if apply_definitive_fix():
        print("\n✅ Corrección aplicada")
        test_rotation_math()
        print("\n🎯 Próximo paso:")
        print("$ python test_rotation_controlled.py")
    else:
        print("\n❌ Error al aplicar corrección")