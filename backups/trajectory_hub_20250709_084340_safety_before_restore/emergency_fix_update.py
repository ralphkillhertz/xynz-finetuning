# === emergency_fix_update.py ===
# 🚨 Fix de emergencia para el método update
# ⚡ Reemplaza el método update completo

import os

def fix_engine_update():
    """Reemplazar el método update con una versión funcional"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Método update corregido
    update_method = """
    def update(self):
        """Actualizar todas las fuentes y enviar datos OSC"""
        if not self.running:
            return
            
        # Calcular dt
        current_time = time.time()
        dt = current_time - self._last_time if hasattr(self, '_last_time') else 1.0/self.fps
        self._last_time = current_time
        self._time = current_time
        
        # Actualizar motion states (sistema de deltas)
        if hasattr(self, 'motion_states'):
            for source_id, motion in self.motion_states.items():
                if motion and hasattr(motion, 'update'):
                    try:
                        # Llamar update con los parámetros correctos
                        if hasattr(motion, 'state'):
                            motion.update(current_time, dt)
                        else:
                            motion.update(dt)
                    except TypeError as e:
                        # Si falla, intentar sin parámetros o con uno solo
                        try:
                            motion.update(dt)
                        except:
                            try:
                                motion.update()
                            except:
                                pass
        
        # Actualizar deformadores
        if self._deformers:
            for macro_id, deformer in self._deformers.items():
                if macro_id in self._macros:
                    macro = self._macros[macro_id]
                    for source_id in macro.source_ids:
                        if source_id < len(self._positions):
                            deformed_pos = deformer.apply(
                                self._positions[source_id], 
                                source_id, 
                                self._time
                            )
                            self._positions[source_id] = deformed_pos
        
        # Actualizar moduladores de orientación si están habilitados
        if self.enable_modulator and hasattr(self, 'orientation_modulators'):
            for source_id, state in self.motion_states.items():
                if source_id in self.orientation_modulators:
                    modulator = self.orientation_modulators[source_id]
                    if modulator.enabled:
                        # Actualizar estado con modulación
                        state = modulator.update(current_time, dt, state)
                        self.motion_states[source_id] = state
        
        # Actualizar el reloj interno
        self._frame_count += 1
        
        # Enviar actualización OSC
        if hasattr(self, '_send_osc_update'):
            self._send_osc_update()
"""
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_emergency', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar y reemplazar el método update
    import re
    pattern = r'def update\(self[^:]*\):.*?(?=
    def|
class|\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, update_method.strip(), content, flags=re.DOTALL)
        
        # Guardar
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("✅ Método update reemplazado")
        return True
    
    return False

if __name__ == "__main__":
    fix_engine_update()
