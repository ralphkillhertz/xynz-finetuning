# === implement_engine_methods_is.py ===
# 🔧 Añadir métodos de rotación IS a enhanced_trajectory_engine.py
# ⚡ Métodos para controlar rotaciones individuales

import os
import re
from datetime import datetime

def implement_engine_methods():
    """Añade métodos de rotación individual al engine"""
    
    print("🔧 AÑADIENDO MÉTODOS DE ROTACIÓN IS AL ENGINE")
    print("=" * 60)
    
    # Ruta del archivo
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra {file_path}")
        return False
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Métodos a añadir
    methods_code = '''
    
    def set_individual_rotation(self, source_id: int, 
                              speed_x: float = 0.0, speed_y: float = 0.0, speed_z: float = 0.0,
                              center: Optional[List[float]] = None) -> bool:
        """
        Configura rotación algorítmica continua para una fuente individual
        
        Args:
            source_id: ID de la fuente
            speed_x: Velocidad de rotación en X (rad/s)
            speed_y: Velocidad de rotación en Y (rad/s)
            speed_z: Velocidad de rotación en Z (rad/s)
            center: Centro de rotación (opcional, default: posición actual)
            
        Returns:
            True si se configuró correctamente
        """
        if source_id not in self.motion_states:
            print(f"❌ Fuente {source_id} no existe")
            return False
        
        motion = self.motion_states[source_id]
        
        # Determinar centro
        if center is None:
            center = self._positions[source_id].copy()
        else:
            center = np.array(center, dtype=np.float32)
        
        # Crear o actualizar componente
        from trajectory_hub.core.motion_components import IndividualRotation
        
        if 'individual_rotation' in motion.active_components:
            # Actualizar existente
            rotation = motion.active_components['individual_rotation']
            rotation.set_rotation_speeds(speed_x, speed_y, speed_z)
            rotation.center = center
        else:
            # Crear nuevo
            rotation = IndividualRotation(center=center, speed_x=speed_x, speed_y=speed_y, speed_z=speed_z)
            motion.active_components['individual_rotation'] = rotation
        
        print(f"✅ Rotación algorítmica configurada para fuente {source_id}")
        print(f"   Velocidades: X={speed_x:.3f}, Y={speed_y:.3f}, Z={speed_z:.3f} rad/s")
        
        return True
    
    def set_manual_individual_rotation(self, source_id: int,
                                     yaw: float = 0.0, pitch: float = 0.0, roll: float = 0.0,
                                     interpolation_speed: float = 0.1,
                                     center: Optional[List[float]] = None) -> bool:
        """
        Configura rotación manual con interpolación para una fuente individual
        
        Args:
            source_id: ID de la fuente
            yaw: Rotación objetivo en Y (radianes)
            pitch: Rotación objetivo en X (radianes)
            roll: Rotación objetivo en Z (radianes)
            interpolation_speed: Velocidad de interpolación (0.01 a 1.0)
            center: Centro de rotación (opcional, default: posición actual)
            
        Returns:
            True si se configuró correctamente
        """
        if source_id not in self.motion_states:
            print(f"❌ Fuente {source_id} no existe")
            return False
        
        motion = self.motion_states[source_id]
        
        # Determinar centro
        if center is None:
            center = self._positions[source_id].copy()
        else:
            center = np.array(center, dtype=np.float32)
        
        # Crear o actualizar componente
        from trajectory_hub.core.motion_components import ManualIndividualRotation
        
        if 'manual_individual_rotation' in motion.active_components:
            # Actualizar existente
            rotation = motion.active_components['manual_individual_rotation']
            rotation.center = center
            rotation.set_target_rotation(yaw, pitch, roll, interpolation_speed)
            # Sincronizar con estado actual
            rotation._sync_with_state(motion.state)
        else:
            # Crear nuevo
            rotation = ManualIndividualRotation(center=center)
            rotation.set_target_rotation(yaw, pitch, roll, interpolation_speed)
            rotation._sync_with_state(motion.state)
            motion.active_components['manual_individual_rotation'] = rotation
        
        print(f"✅ Rotación manual configurada para fuente {source_id}")
        print(f"   Objetivos: Yaw={math.degrees(yaw):.1f}°, Pitch={math.degrees(pitch):.1f}°, Roll={math.degrees(roll):.1f}°")
        
        return True
    
    def stop_individual_rotation(self, source_id: int, rotation_type: str = 'both') -> bool:
        """
        Detiene la rotación de una fuente individual
        
        Args:
            source_id: ID de la fuente
            rotation_type: 'algorithmic', 'manual', o 'both'
            
        Returns:
            True si se detuvo correctamente
        """
        if source_id not in self.motion_states:
            print(f"❌ Fuente {source_id} no existe")
            return False
        
        motion = self.motion_states[source_id]
        stopped = False
        
        if rotation_type in ['algorithmic', 'both']:
            if 'individual_rotation' in motion.active_components:
                motion.active_components['individual_rotation'].enabled = False
                print(f"✅ Rotación algorítmica detenida para fuente {source_id}")
                stopped = True
        
        if rotation_type in ['manual', 'both']:
            if 'manual_individual_rotation' in motion.active_components:
                motion.active_components['manual_individual_rotation'].enabled = False
                print(f"✅ Rotación manual detenida para fuente {source_id}")
                stopped = True
        
        return stopped
    
    def set_batch_individual_rotation(self, source_ids: List[int], 
                                    speed_x: float = 0.0, speed_y: float = 0.0, speed_z: float = 0.0,
                                    offset_factor: float = 0.0) -> int:
        """
        Configura rotación algorítmica para múltiples fuentes con desfase opcional
        
        Args:
            source_ids: Lista de IDs de fuentes
            speed_x: Velocidad base en X (rad/s)
            speed_y: Velocidad base en Y (rad/s)
            speed_z: Velocidad base en Z (rad/s)
            offset_factor: Factor de desfase entre fuentes (0.0 = sin desfase)
            
        Returns:
            Número de fuentes configuradas exitosamente
        """
        configured = 0
        
        for i, sid in enumerate(source_ids):
            # Aplicar desfase si se especifica
            factor = 1.0 + (i * offset_factor)
            sx = speed_x * factor
            sy = speed_y * factor
            sz = speed_z * factor
            
            if self.set_individual_rotation(sid, sx, sy, sz):
                configured += 1
        
        print(f"\n✅ Rotación configurada para {configured}/{len(source_ids)} fuentes")
        return configured'''
    
    # Buscar dónde insertar (después de set_manual_macro_rotation)
    print("\n🔍 Buscando lugar para insertar métodos...")
    
    # Buscar el final de set_manual_macro_rotation
    pattern = r'(def set_manual_macro_rotation.*?(?=\n    def |\n\s*#|\Z))'
    
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        
        # Insertar los métodos
        content = content[:insert_pos] + methods_code + content[insert_pos:]
        
        print("✅ Métodos de rotación IS añadidos")
    else:
        # Buscar alternativa - después de cualquier método set_
        pattern2 = r'(def set_.*?return.*?\n)(?=\n    def |\n\s*#|\Z)'
        match2 = re.search(pattern2, content, re.DOTALL)
        
        if match2:
            insert_pos = match2.end()
            content = content[:insert_pos] + methods_code + content[insert_pos:]
            print("✅ Métodos añadidos (ubicación alternativa)")
        else:
            print("❌ No se pudo encontrar lugar de inserción")
            return False
    
    # Añadir import si no existe
    if 'import math' not in content:
        import_pattern = r'(import.*?\n)'
        content = re.sub(import_pattern, r'\1import math\n', content, count=1)
    
    # Escribir el archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ enhanced_trajectory_engine.py actualizado con:")
    print("   - set_individual_rotation()")
    print("   - set_manual_individual_rotation()")
    print("   - stop_individual_rotation()")
    print("   - set_batch_individual_rotation()")
    
    return True

if __name__ == "__main__":
    implement_engine_methods()