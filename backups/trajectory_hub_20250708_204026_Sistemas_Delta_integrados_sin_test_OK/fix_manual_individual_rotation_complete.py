import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_manual_rotation():
    """Corrige ManualIndividualRotation para que actualice current_yaw"""
    
    print("🔧 CORRIGIENDO ManualIndividualRotation...")
    print("=" * 60)
    
    # Leer motion_components.py
    filepath = 'trajectory_hub/core/motion_components.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar la clase
    class_line = -1
    for i, line in enumerate(lines):
        if "class ManualIndividualRotation" in line:
            class_line = i
            print(f"✅ Clase encontrada en línea {i+1}")
            break
    
    if class_line == -1:
        print("❌ No se encontró la clase")
        return False
    
    # 1. Buscar el método update y corregirlo/añadirlo
    print("\n🔍 Buscando método update()...")
    
    update_found = False
    update_line = -1
    
    # Buscar desde la clase hasta la siguiente clase
    next_class = len(lines)
    for i in range(class_line + 1, len(lines)):
        if lines[i].strip().startswith("class "):
            next_class = i
            break
    
    # Buscar update en el rango de la clase
    for i in range(class_line, next_class):
        if "def update(" in lines[i]:
            update_found = True
            update_line = i
            print(f"✅ Método update encontrado en línea {i+1}")
            break
    
    if not update_found:
        print("⚠️ No se encontró método update, añadiéndolo...")
        
        # Buscar dónde insertar (después de __init__ o antes de calculate_delta)
        insert_line = -1
        for i in range(class_line, next_class):
            if "def calculate_delta(" in lines[i]:
                insert_line = i
                break
        
        if insert_line == -1:
            # Buscar el final de __init__
            for i in range(class_line, next_class):
                if "def __init__" in lines[i]:
                    # Buscar el final del método
                    indent_count = len(lines[i]) - len(lines[i].lstrip())
                    for j in range(i + 1, next_class):
                        if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent_count:
                            insert_line = j
                            break
        
        if insert_line > 0:
            update_method = '''
    def update(self, current_time: float, dt: float, state: 'MotionState') -> 'MotionState':
        """Actualiza los ángulos internos con interpolación"""
        if not self.enabled:
            return state
        
        import numpy as np
        
        # Calcular diferencias angulares
        yaw_diff = self.target_yaw - self.current_yaw
        pitch_diff = self.target_pitch - self.current_pitch
        roll_diff = self.target_roll - self.current_roll
        
        # Normalizar diferencias para tomar el camino más corto
        while yaw_diff > np.pi: yaw_diff -= 2 * np.pi
        while yaw_diff < -np.pi: yaw_diff += 2 * np.pi
        while pitch_diff > np.pi: pitch_diff -= 2 * np.pi
        while pitch_diff < -np.pi: pitch_diff += 2 * np.pi
        while roll_diff > np.pi: roll_diff -= 2 * np.pi
        while roll_diff < -np.pi: roll_diff += 2 * np.pi
        
        # Calcular paso máximo según velocidad de interpolación
        max_step = self.interpolation_speed * dt
        
        # Aplicar interpolación
        if abs(yaw_diff) > 0.001:
            self.current_yaw += np.clip(yaw_diff, -max_step, max_step)
        if abs(pitch_diff) > 0.001:
            self.current_pitch += np.clip(pitch_diff, -max_step, max_step)
        if abs(roll_diff) > 0.001:
            self.current_roll += np.clip(roll_diff, -max_step, max_step)
        
        # Verificar si llegamos al objetivo
        if (abs(yaw_diff) < 0.001 and 
            abs(pitch_diff) < 0.001 and 
            abs(roll_diff) < 0.001):
            self.enabled = False
            self.current_yaw = self.target_yaw
            self.current_pitch = self.target_pitch
            self.current_roll = self.target_roll
        
        return state

'''
            lines.insert(insert_line, update_method)
            print(f"✅ Método update añadido en línea {insert_line}")
    
    # 2. Corregir calculate_delta para que NO recalcule current_yaw
    print("\n🔍 Corrigiendo calculate_delta...")
    
    for i in range(class_line, min(next_class, len(lines))):
        if "def calculate_delta(" in lines[i]:
            print(f"✅ calculate_delta encontrado en línea {i+1}")
            
            # Buscar líneas que recalculan current_yaw
            for j in range(i, min(i + 50, len(lines))):
                if "current_yaw = np.arctan2" in lines[j] or "current_yaw = math.atan2" in lines[j]:
                    print(f"   ⚠️ Línea {j+1} recalcula current_yaw, comentándola...")
                    lines[j] = "        # " + lines[j].lstrip() + "  # Usar self.current_yaw en lugar de recalcular\n"
            break
    
    # 3. Guardar el archivo
    print("\n💾 Guardando archivo...")
    
    # Backup
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'{filepath}.backup_{timestamp}'
    shutil.copy(filepath, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Archivo guardado")
    
    return True

def test_rotation():
    """Test de la rotación manual"""
    print("\n🧪 TEST DE ROTACIÓN MANUAL:")
    print("-" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear engine y fuente
        engine = EnhancedTrajectoryEngine(n_sources=10, fps=60)
        engine.create_source(0)
        
        # Posición inicial
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        print(f"Posición inicial: {engine._positions[0]}")
        
        # Configurar rotación manual a 90 grados
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,  # grados
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0  # grados/segundo
        )
        print(f"Rotación configurada: {success}")
        
        # Verificar componente
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"Componente activo: {comp.enabled}")
                print(f"Target yaw: {np.degrees(comp.target_yaw):.1f}°")
        
        # Simular 2 segundos
        print("\nSimulando movimiento...")
        positions = []
        for i in range(120):  # 2 segundos a 60 fps
            engine.update(1/60)
            pos = engine._positions[0].copy()
            positions.append(pos)
            
            if i % 20 == 0:  # Cada 0.33 segundos
                print(f"t={i/60:.2f}s: pos=[{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
        
        # Verificar resultado
        initial = np.array([3.0, 0.0, 0.0])
        final = positions[-1]
        expected = np.array([0.0, 3.0, 0.0])  # 90 grados
        
        distance_moved = np.linalg.norm(final - initial)
        error = np.linalg.norm(final - expected)
        
        print(f"\n📊 RESULTADOS:")
        print(f"Posición final: [{final[0]:.3f}, {final[1]:.3f}, {final[2]:.3f}]")
        print(f"Esperada: [{expected[0]:.3f}, {expected[1]:.3f}, {expected[2]:.3f}]")
        print(f"Distancia movida: {distance_moved:.3f}")
        print(f"Error: {error:.3f}")
        
        if distance_moved > 0.1:
            print("\n✅ ¡LA ROTACIÓN FUNCIONA!")
        else:
            print("\n❌ La fuente no se movió")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_manual_rotation():
        test_rotation()