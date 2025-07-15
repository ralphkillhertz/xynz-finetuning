# === add_macro_rotation_clean.py ===
# 🔧 Añadir MacroRotation al proyecto actual
# ⚡ Implementación limpia basada en análisis completo
# 🎯 Tiempo: 2 minutos

from pathlib import Path
import datetime

def add_macro_rotation():
    """Añade MacroRotation correctamente al sistema"""
    
    print("🔧 Añadiendo MacroRotation al sistema...")
    
    # 1. Añadir MacroRotation a motion_components.py
    motion_components_path = Path("trajectory_hub/core/motion_components.py")
    
    if not motion_components_path.exists():
        print("❌ No se encontró motion_components.py")
        return False
        
    content = motion_components_path.read_text()
    
    # Verificar si ya existe
    if "class MacroRotation" in content:
        print("⚠️ MacroRotation ya existe, eliminando versión anterior...")
        # Eliminar versión anterior
        start = content.find("class MacroRotation")
        end = content.find("\nclass ", start + 1)
        if end == -1:
            end = len(content)
        content = content[:start] + content[end:]
    
    # Buscar dónde insertar (después de MacroTrajectory)
    insert_pos = content.find("class MacroTrajectory")
    if insert_pos == -1:
        print("❌ No se encontró MacroTrajectory")
        return False
    
    # Encontrar el final de MacroTrajectory
    next_class = content.find("\nclass ", insert_pos + 1)
    if next_class == -1:
        next_class = len(content)
    
    # Código de MacroRotation CORRECTO y COMPLETO
    macro_rotation_code = '''

class MacroRotation(MotionComponent):
    """Rotación algorítmica para grupos de fuentes - Sistema de deltas"""
    
    def __init__(self):
        super().__init__()
        self.component_type = 'macro_rotation'
        self.enabled = False
        
        # Centro de rotación
        self.center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        
        # Velocidades de rotación (rad/s) - SIEMPRE float
        self.speed_x = 0.0
        self.speed_y = 0.0  
        self.speed_z = 0.0
        
        # Ángulos actuales
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        
    def set_rotation(self, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configura velocidades de rotación"""
        # CRÍTICO: Convertir a float SIEMPRE para evitar arrays
        self.speed_x = float(speed_x) if speed_x is not None else 0.0
        self.speed_y = float(speed_y) if speed_y is not None else 0.0
        self.speed_z = float(speed_z) if speed_z is not None else 0.0
        
        if center is not None:
            self.center = np.array(center, dtype=np.float32).flatten()[:3]
        
        # Verificar si está habilitado - usar lista para evitar problemas con 'or'
        speeds_active = [
            abs(self.speed_x) > 0.001,
            abs(self.speed_y) > 0.001,
            abs(self.speed_z) > 0.001
        ]
        self.enabled = any(speeds_active)
        
    def calculate_delta(self, state, current_time, dt):
        """Calcula delta de rotación para sistema de deltas"""
        if not self.enabled or dt <= 0:
            return MotionDelta()
            
        # Convertir dt a float por seguridad
        dt = float(dt)
            
        # Actualizar ángulos
        self.angle_x += self.speed_x * dt
        self.angle_y += self.speed_y * dt
        self.angle_z += self.speed_z * dt
        
        # Posición relativa al centro
        pos = state.position - self.center
        
        # Matrices de rotación (orden: Z, Y, X)
        cx, sx = np.cos(self.angle_x), np.sin(self.angle_x)
        cy, sy = np.cos(self.angle_y), np.sin(self.angle_y)
        cz, sz = np.cos(self.angle_z), np.sin(self.angle_z)
        
        # Rotación Z
        x1 = pos[0] * cz - pos[1] * sz
        y1 = pos[0] * sz + pos[1] * cz
        z1 = pos[2]
        
        # Rotación Y
        x2 = x1 * cy + z1 * sy
        y2 = y1
        z2 = -x1 * sy + z1 * cy
        
        # Rotación X
        x3 = x2
        y3 = y2 * cx - z2 * sx
        z3 = y2 * sx + z2 * cx
        
        # Nueva posición absoluta
        new_pos = np.array([x3, y3, z3], dtype=np.float32) + self.center
        
        # Crear delta
        delta = MotionDelta()
        delta.position = new_pos - state.position
        
        return delta
        
    def get_state(self):
        """Obtiene el estado actual"""
        return {
            'enabled': self.enabled,
            'center': self.center.tolist(),
            'speed_x': self.speed_x,
            'speed_y': self.speed_y,
            'speed_z': self.speed_z,
            'angle_x': self.angle_x,
            'angle_y': self.angle_y,
            'angle_z': self.angle_z
        }
'''
    
    # Insertar el código
    content = content[:next_class] + macro_rotation_code + content[next_class:]
    
    # Guardar con backup
    backup_path = motion_components_path.with_suffix(f'.backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')
    motion_components_path.rename(backup_path)
    motion_components_path.write_text(content)
    
    print(f"✅ MacroRotation añadida a motion_components.py")
    print(f"   Backup: {backup_path}")
    
    # 2. Añadir set_macro_rotation a enhanced_trajectory_engine.py
    engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
    
    if not engine_path.exists():
        print("❌ No se encontró enhanced_trajectory_engine.py")
        return False
        
    engine_content = engine_path.read_text()
    
    # Verificar si ya existe
    if "def set_macro_rotation" in engine_content:
        print("⚠️ set_macro_rotation ya existe, actualizando...")
        # Eliminar versión anterior
        start = engine_content.find("def set_macro_rotation")
        # Retroceder para incluir la indentación
        while start > 0 and engine_content[start-1] in ' \t':
            start -= 1
        end = engine_content.find("\n    def ", start + 1)
        if end == -1:
            end = engine_content.find("\nclass ", start)
            if end == -1:
                end = len(engine_content)
        engine_content = engine_content[:start] + engine_content[end:]
    
    # Buscar dónde insertar
    insert_pos = engine_content.find("def set_macro_trajectory")
    if insert_pos == -1:
        # Buscar create_macro como alternativa
        insert_pos = engine_content.find("def create_macro")
        if insert_pos == -1:
            print("❌ No se encontró punto de inserción adecuado")
            return False
    
    # Encontrar el final del método
    next_def = engine_content.find("\n    def ", insert_pos + 1)
    if next_def == -1:
        next_def = len(engine_content)
    
    set_rotation_code = '''
    
    def set_macro_rotation(self, macro_name, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configura rotación algorítmica para un macro con sistema de deltas"""
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return False
            
        macro = self._macros[macro_name]
        source_ids = list(macro.source_ids)
        
        # Centro por defecto es el centroide del macro
        if center is None:
            positions = []
            for sid in source_ids:
                if sid < len(self._positions):
                    positions.append(self._positions[sid].copy())
            if positions:
                center = np.mean(positions, axis=0)
            else:
                center = np.array([0.0, 0.0, 0.0])
        
        # Convertir center a array numpy si no lo es
        center = np.array(center, dtype=np.float32)
        
        # Configurar rotación para cada fuente del macro
        configured = 0
        for sid in source_ids:
            if sid in self.motion_states:
                motion = self.motion_states[sid]
                
                # Crear componente si no existe
                if 'macro_rotation' not in motion.active_components:
                    rotation = MacroRotation()
                    motion.active_components['macro_rotation'] = rotation
                else:
                    rotation = motion.active_components['macro_rotation']
                
                # Configurar rotación
                rotation.set_rotation(
                    speed_x=speed_x,
                    speed_y=speed_y,
                    speed_z=speed_z,
                    center=center
                )
                configured += 1
        
        if configured > 0:
            print(f"✅ Rotación configurada para '{macro_name}'")
            print(f"   Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
            print(f"   Velocidades: X={float(speed_x):.2f}, Y={float(speed_y):.2f}, Z={float(speed_z):.2f} rad/s")
            print(f"   Fuentes: {configured}/{len(source_ids)}")
            return True
        
        return False
'''
    
    # Insertar el método
    engine_content = engine_content[:next_def] + set_rotation_code + engine_content[next_def:]
    
    # Guardar con backup
    engine_backup = engine_path.with_suffix(f'.backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')
    engine_path.rename(engine_backup)
    engine_path.write_text(engine_content)
    
    print(f"✅ set_macro_rotation añadido a enhanced_trajectory_engine.py")
    print(f"   Backup: {engine_backup}")
    
    # 3. Verificar imports necesarios
    if "from trajectory_hub.core.motion_components import MacroRotation" not in engine_content:
        print("\n⚠️ Nota: Puede necesitar añadir import en enhanced_trajectory_engine.py:")
        print("   from trajectory_hub.core.motion_components import MacroRotation")
    
    print("\n✅ Implementación completa")
    print("\n📝 Próximo paso: python test_rotation_simple.py")
    
    return True

if __name__ == "__main__":
    add_macro_rotation()