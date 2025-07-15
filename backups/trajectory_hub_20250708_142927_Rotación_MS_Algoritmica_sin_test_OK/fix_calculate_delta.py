# === fix_calculate_delta.py ===
# 🔧 Fix del método calculate_delta en ConcentrationComponent
# ⚡ ESTE es el problema real

import os
import re
from datetime import datetime

def fix_calculate_delta():
    """Arregla el método calculate_delta para que funcione correctamente"""
    
    print("🔧 ARREGLANDO CALCULATE_DELTA")
    print("="*60)
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    # Leer archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar ConcentrationComponent
    class_match = re.search(r'class ConcentrationComponent.*?(?=\nclass|\Z)', content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encontró ConcentrationComponent")
        return False
    
    class_content = class_match.group(0)
    
    # Buscar calculate_delta
    method_match = re.search(r'def calculate_delta\(self.*?\n(?=\s{4}def|\s{0,4}class|\Z)', class_content, re.DOTALL)
    
    if method_match:
        print("✅ Encontrado calculate_delta")
        old_method = method_match.group(0)
        
        # Nuevo método que FUNCIONA
        new_method = '''def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula el delta de movimiento hacia el punto objetivo"""
        if not self.enabled:
            return MotionDelta(position=np.zeros(3))
        
        # Usar la posición actual del state
        current_pos = state.position
        
        # El target es target_point (hacia donde queremos concentrar)
        target = self.target_point
        
        # Calcular dirección y distancia
        direction = target - current_pos
        distance = np.linalg.norm(direction)
        
        # Si ya estamos en el target, no hay movimiento
        if distance < 0.001:
            return MotionDelta(position=np.zeros(3))
        
        # Calcular movimiento basado en el factor y dt
        movement = direction * self.concentration_factor * dt
        
        # Limitar el movimiento para no pasarnos del target
        movement_distance = np.linalg.norm(movement)
        if movement_distance > distance:
            movement = direction * (distance / np.linalg.norm(direction))
        
        return MotionDelta(
            position=movement,
            source='concentration',
            weight=self.weight
        )
'''
        
        # Reemplazar el método
        new_class_content = class_content.replace(old_method, new_method)
        new_content = content.replace(class_content, new_class_content)
        
        # Escribir archivo
        with open(motion_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ calculate_delta arreglado")
        
        # Verificar sintaxis
        try:
            compile(new_content, motion_path, 'exec')
            print("✅ Sintaxis verificada")
            return True
        except Exception as e:
            print(f"❌ Error de sintaxis: {e}")
            # Restaurar
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(motion_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return False
    else:
        print("❌ No se encontró calculate_delta")
        return False

if __name__ == "__main__":
    print("🎯 FIX DEL PROBLEMA REAL")
    print("\nProblema identificado:")
    print("  - calculate_delta retorna [0,0,0] aunque debería retornar [-0.128,0,0]")
    print("  - El método no está calculando correctamente el movimiento")
    
    if fix_calculate_delta():
        print("\n✅ FIX APLICADO")
        print("\n🎉 AHORA SÍ - Ejecuta:")
        print("$ python test_concentration_success.py")