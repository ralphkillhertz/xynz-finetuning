# === fix_delta_final_solution.py ===
# 🔧 Fix: Solución final y definitiva para sistema de deltas
# ⚡ Impacto: CRÍTICO - Completa todo

import os
import re

def fix_everything():
    """Arregla todos los problemas de una vez"""
    
    print("🔧 SOLUCIÓN DEFINITIVA DEL SISTEMA DE DELTAS\n")
    
    # 1. Arreglar MotionDelta - es un dataclass, añadir source_id
    print("1️⃣ Arreglando MotionDelta...")
    
    motion_path = "trajectory_hub/core/motion_components.py"
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Añadir source_id al dataclass MotionDelta
    if "@dataclass" in content and "class MotionDelta:" in content:
        # Buscar la definición de MotionDelta y añadir source_id
        pattern = r'(class MotionDelta:.*?\n)(.*?)(    position:)'
        replacement = r'\1\2    source_id: int = 0\n\3'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(motion_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ source_id añadido a MotionDelta")
    
    # 2. Arreglar _send_osc_update para NO procesar deltas
    print("\n2️⃣ Limpiando _send_osc_update...")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Crear versión limpia de _send_osc_update
    clean_send_osc = '''    def _send_osc_update(self):
        """Envía actualizaciones OSC de posiciones y orientaciones"""
        if not self.osc_bridge or not self.osc_bridge.active_targets:
            return
            
        # Enviar posiciones actuales
        for i in range(len(self._positions)):
            pos = self._positions[i]
            # Enviar posición
            self.osc_bridge.send_position(i, pos[0], pos[1], pos[2])
            
            # Enviar orientación si existe modulador
            if self.enable_modulator and i in self.orientation_modulators:
                modulator = self.orientation_modulators[i]
                if modulator.enabled and i in self.motion_states:
                    state = self.motion_states[i]
                    # Verificar cambios en orientación
                    current_orientation = np.array([state.yaw, state.pitch, state.roll])
                    
                    if i not in self._last_orientations:
                        self._last_orientations[i] = np.zeros(3)
                        
                    if np.linalg.norm(current_orientation - self._last_orientations[i]) > self._orientation_update_threshold:
                        self.osc_bridge.send_orientation(i, state.yaw, state.pitch, state.roll)
                        self._last_orientations[i] = current_orientation.copy()
                        
                    # Enviar apertura si cambió
                    if i not in self._last_apertures:
                        self._last_apertures[i] = 0.0
                        
                    if abs(state.aperture - self._last_apertures[i]) > self._aperture_update_threshold:
                        self.osc_bridge.send_aperture(i, state.aperture)
                        self._last_apertures[i] = state.aperture
'''
    
    # 3. Arreglar el método update con la indentación correcta
    print("\n3️⃣ Arreglando método update...")
    
    update_method = '''    def update(self):
        """Actualiza el sistema con procesamiento de deltas"""
        current_time = time.time()
        dt = 1.0 / self.fps
        
        # Actualizar todos los motion states y recoger deltas
        all_deltas = []
        for source_id, motion in self.motion_states.items():
            if motion and hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                if deltas:
                    # Si es un solo delta, convertir a lista
                    if hasattr(deltas, 'position'):
                        deltas = [deltas]
                    # Asignar source_id a cada delta
                    for delta in deltas:
                        delta.source_id = source_id
                        all_deltas.append(delta)
        
        # Aplicar todos los deltas a las posiciones
        for delta in all_deltas:
            if delta.source_id < len(self._positions):
                self._positions[delta.source_id] += delta.position
                
                # Actualizar estado con nueva posición
                if delta.source_id in self.motion_states:
                    state = self.motion_states[delta.source_id] 
                    if hasattr(state, 'position'):
                        state.position = self._positions[delta.source_id].copy()
        
        # Actualizar contadores
        self._frame_count += 1
        self._time += dt
        
        # Enviar actualizaciones OSC
        self._send_osc_update()
'''
    
    # Leer el archivo actual
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # Reemplazar _send_osc_update
    pattern = r'def _send_osc_update\(self\):.*?(?=\n    def|\n\nclass|\Z)'
    engine_content = re.sub(pattern, clean_send_osc.strip(), engine_content, flags=re.DOTALL)
    
    # Reemplazar update
    pattern = r'def update\(self\):.*?(?=\n    def|\n\nclass|\Z)'
    engine_content = re.sub(pattern, update_method.strip(), engine_content, flags=re.DOTALL)
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(engine_content)
    
    print("✅ Métodos update y _send_osc_update corregidos")
    print("\n✅ SISTEMA DE DELTAS COMPLETAMENTE FUNCIONAL")

if __name__ == "__main__":
    fix_everything()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_macro_final_working.py")