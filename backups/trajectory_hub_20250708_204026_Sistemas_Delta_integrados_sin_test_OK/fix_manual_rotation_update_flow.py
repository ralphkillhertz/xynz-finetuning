import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_manual_rotation():
    """Corrige el flujo de actualización de ManualIndividualRotation"""
    
    # Leer motion_components.py
    with open('trajectory_hub/core/motion_components.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Corregir el método update() de ManualIndividualRotation
    print("🔧 Corrigiendo método update() de ManualIndividualRotation...")
    
    # Buscar la clase ManualIndividualRotation
    class_start = content.find("class ManualIndividualRotation:")
    if class_start == -1:
        print("❌ No se encontró la clase ManualIndividualRotation")
        return False
        
    # Buscar el método update
    update_start = content.find("def update(", class_start)
    if update_start == -1:
        print("⚠️ No se encontró método update, añadiéndolo...")
        # Buscar el final de __init__
        init_end = content.find("\n    def ", class_start + 50)
        if init_end == -1:
            init_end = content.find("\n\nclass", class_start + 50)
        
        update_method = '''
    def update(self, current_time: float, dt: float, state: 'MotionState') -> 'MotionState':
        """Actualiza el estado interno y retorna el state modificado"""
        if not self.enabled:
            return state
            
        # Sincronizar posición del state
        import numpy as np
        state.position = np.array(state.position)
        
        # Calcular interpolación de ángulos
        yaw_diff = self.target_yaw - self.current_yaw
        pitch_diff = self.target_pitch - self.current_pitch
        roll_diff = self.target_roll - self.current_roll
        
        # Normalizar diferencias angulares
        while yaw_diff > np.pi: yaw_diff -= 2 * np.pi
        while yaw_diff < -np.pi: yaw_diff += 2 * np.pi
        while pitch_diff > np.pi: pitch_diff -= 2 * np.pi
        while pitch_diff < -np.pi: pitch_diff += 2 * np.pi
        while roll_diff > np.pi: roll_diff -= 2 * np.pi
        while roll_diff < -np.pi: roll_diff += 2 * np.pi
        
        # Aplicar interpolación
        max_step = self.interpolation_speed * dt
        self.current_yaw += np.clip(yaw_diff, -max_step, max_step)
        self.current_pitch += np.clip(pitch_diff, -max_step, max_step)
        self.current_roll += np.clip(roll_diff, -max_step, max_step)
        
        # Normalizar ángulos actuales
        self.current_yaw = (self.current_yaw + np.pi) % (2 * np.pi) - np.pi
        self.current_pitch = (self.current_pitch + np.pi) % (2 * np.pi) - np.pi
        self.current_roll = (self.current_roll + np.pi) % (2 * np.pi) - np.pi
        
        # Actualizar enabled basado en si llegamos al objetivo
        if abs(yaw_diff) < 0.001 and abs(pitch_diff) < 0.001 and abs(roll_diff) < 0.001:
            self.enabled = False
            
        return state
'''
        content = content[:init_end] + update_method + content[init_end:]
        print("✅ Método update() añadido")
    else:
        print("✅ Método update() encontrado, verificando implementación...")
    
    # 2. Asegurar que calculate_delta use current_yaw actualizado
    print("\n🔧 Verificando calculate_delta...")
    
    # Buscar calculate_delta
    calc_start = content.find("def calculate_delta(", class_start)
    if calc_start != -1:
        # Buscar donde se calcula current_yaw en calculate_delta
        calc_end = content.find("\n    def ", calc_start + 100)
        if calc_end == -1:
            calc_end = content.find("\n\nclass", calc_start + 100)
            
        calc_section = content[calc_start:calc_end]
        
        # Si calculate_delta está calculando current_yaw internamente, quitarlo
        if "current_yaw = np.arctan2" in calc_section:
            print("⚠️ calculate_delta está recalculando current_yaw, usando el valor de la instancia...")
            # Comentar la línea que recalcula
            calc_section = calc_section.replace(
                "current_yaw = np.arctan2(relative_pos[1], relative_pos[0])",
                "# current_yaw = np.arctan2(relative_pos[1], relative_pos[0])  # Usar self.current_yaw"
            )
            content = content[:calc_start] + calc_section + content[calc_end:]
    
    # 3. Corregir engine.update() para sincronizar states
    print("\n🔧 Corrigiendo sincronización en engine.update()...")
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # Buscar el método update del engine
    update_start = engine_content.find("def update(self, dt: float):")
    if update_start != -1:
        # Buscar donde se actualizan las posiciones
        update_section_start = update_start
        update_section_end = engine_content.find("\n    def ", update_start + 100)
        if update_section_end == -1:
            update_section_end = len(engine_content)
            
        update_section = engine_content[update_section_start:update_section_end]
        
        # Buscar la línea que sincroniza state.position
        if "state.position = self._positions[source_id].copy()" not in update_section:
            print("⚠️ Falta sincronización de state.position, añadiendo...")
            # Buscar donde insertar la sincronización
            sync_pos = update_section.find("for source_id, motion in self.motion_states.items():")
            if sync_pos != -1:
                # Buscar el inicio del bloque
                block_start = update_section.find("\n", sync_pos) + 1
                indent = "            "  # Ajustar según indentación
                sync_line = f"{indent}# Sincronizar posición del state con el engine\n{indent}if source_id in self._positions:\n{indent}    motion.state.position = self._positions[source_id].copy()\n"
                
                update_section = update_section[:block_start] + sync_line + update_section[block_start:]
                engine_content = engine_content[:update_section_start] + update_section + engine_content[update_section_end:]
                print("✅ Sincronización añadida")
    
    # Guardar archivos
    print("\n💾 Guardando archivos...")
    
    # Backup y guardar motion_components.py
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy('trajectory_hub/core/motion_components.py', 
                f'trajectory_hub/core/motion_components.py.backup_{timestamp}')
    
    with open('trajectory_hub/core/motion_components.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ motion_components.py guardado (backup: {timestamp})")
    
    # Backup y guardar engine
    shutil.copy(engine_path, f'{engine_path}.backup_{timestamp}')
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(engine_content)
    print(f"✅ enhanced_trajectory_engine.py guardado")
    
    print("\n✨ Correcciones aplicadas exitosamente")
    return True

def test_rotation():
    """Test rápido de la rotación manual"""
    print("\n🧪 TEST RÁPIDO:")
    print("-" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear engine y fuente
        engine = EnhancedTrajectoryEngine(n_sources=1, update_rate=60)
        engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        
        # Configurar rotación manual
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0
        )
        
        print(f"Rotación configurada: {success}")
        print(f"Posición inicial: {engine._positions[0]}")
        
        # Simular algunos frames
        for i in range(5):
            engine.update(1/60)
            print(f"Frame {i}: pos = {engine._positions[0]}")
            
        # Verificar que se movió
        if not np.array_equal(engine._positions[0], [3.0, 0.0, 0.0]):
            print("\n✅ ¡LA ROTACIÓN FUNCIONA!")
        else:
            print("\n⚠️ La fuente no se movió")
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_manual_rotation():
        test_rotation()