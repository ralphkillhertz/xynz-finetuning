#!/usr/bin/env python3
"""
🔧 Fix: Forzar actualización OSC inmediata
⚡ Impacto: ALTO - Corrige visualización en Spat
"""

import os
import shutil
from datetime import datetime

def fix_osc_updates():
    """Asegurar que los cambios se envíen inmediatamente a Spat"""
    
    # Backup
    backup_dir = f"backup_osc_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. Fix en enhanced_trajectory_engine.py
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    shutil.copy2(engine_file, os.path.join(backup_dir, "enhanced_trajectory_engine.py.bak"))
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar el método set_concentration
    concentration_fix = '''    def set_concentration(self, macro_id: str, factor: float, animate: bool = False, 
                         duration: float = 2.0, curve: str = 'linear'):
        """Establecer factor de concentración para un macro"""
        if macro_id not in self.macros:
            logger.warning(f"Macro {macro_id} no encontrado")
            return
            
        concentration = self.spatial_effects['concentration']
        concentration.set_factor(macro_id, factor)
        
        if animate:
            concentration.start_animation(
                macro_id=macro_id,
                target_factor=factor,
                duration=duration,
                curve=curve
            )
        
        logger.info(f"Concentración establecida para {macro_id}: factor={factor}")
        
        # FORZAR ACTUALIZACIÓN INMEDIATA
        self._force_immediate_update(macro_id)'''
    
    # Reemplazar el método existente
    import re
    pattern = r'def set_concentration\(self.*?logger\.info\(f"Concentración establecida.*?\)'
    content = re.sub(pattern, concentration_fix.strip(), content, flags=re.DOTALL)
    
    # Agregar método para forzar actualización si no existe
    if "_force_immediate_update" not in content:
        force_update_method = '''
    def _force_immediate_update(self, macro_id: str):
        """Forzar actualización inmediata de todas las fuentes del macro"""
        if macro_id not in self.macros:
            return
            
        macro = self.macros[macro_id]
        for source_id in macro.source_ids:
            if source_id in self.sources:
                # Forzar recálculo de posición
                source = self.sources[source_id]
                source._last_update_time = 0  # Resetear tiempo
                
                # Obtener posición actual y enviar
                position = self.get_source_position(source_id)
                if position is not None and self.bridge:
                    self.bridge.send_position(source_id, position)'''
        
        # Insertar antes del método update
        content = content.replace("    def update(self, dt: float):", 
                                  force_update_method + "\n\n    def update(self, dt: float):")
    
    # Fix similar para rotación algorítmica
    algo_rotation_fix = '''    def set_algorithmic_rotation(self, target_id: str, pattern: str, 
                                 speed: float = 1.0, amplitude: float = 1.0,
                                 is_macro: bool = True):
        """Configurar rotación algorítmica"""
        rotation = self.spatial_effects['algorithmic_rotation']
        rotation.set_pattern(target_id, pattern, speed, amplitude, is_macro)
        
        logger.info(f"Rotación algorítmica '{pattern}' aplicada al {'macro' if is_macro else 'source'} {target_id}")
        
        # FORZAR ACTUALIZACIÓN INMEDIATA
        if is_macro:
            self._force_immediate_update(target_id)
        else:
            # Para fuente individual
            position = self.get_source_position(target_id)
            if position is not None and self.bridge:
                self.bridge.send_position(target_id, position)'''
    
    # Reemplazar el método de rotación algorítmica
    pattern = r'def set_algorithmic_rotation\(self.*?logger\.info\(f"Rotación algorítmica.*?\)'
    content = re.sub(pattern, algo_rotation_fix.strip(), content, flags=re.DOTALL)
    
    # Guardar cambios
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ Fix aplicado en enhanced_trajectory_engine.py")
    
    # 2. Fix en source_motion.py para asegurar que update() siempre calcule cambios
    motion_file = "trajectory_hub/motion/source_motion.py"
    shutil.copy2(motion_file, os.path.join(backup_dir, "source_motion.py.bak"))
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar el método update y modificar el umbral
    content = content.replace("if dt < 0.001:", "if dt < 0.0001:")  # Reducir umbral
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ Fix aplicado en source_motion.py")
    print(f"📁 Backup guardado en: {backup_dir}")
    print("\n🎯 Los cambios ahora se enviarán inmediatamente a Spat")

if __name__ == "__main__":
    fix_osc_updates()
    print("\n✨ Fix completado. Reinicia el controller para probar.")