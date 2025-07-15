# === diagnose_motion_components.py ===
# 🔧 Diagnóstico: Ver estructura exacta de motion_components.py
# ⚡ Impacto: Diagnóstico completo

import os

def diagnose_file():
    """Diagnostica la estructura del archivo"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    print("🔍 DIAGNÓSTICO DE motion_components.py\n")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Total líneas: {len(lines)}")
    print("\n📋 Clases encontradas (primeras 50 líneas):")
    
    for i, line in enumerate(lines[:50]):
        if "class " in line and not line.strip().startswith("#"):
            print(f"   L{i+1}: {line.strip()}")
    
    # Buscar específicamente MacroRotation y MotionComponent
    print("\n🔎 Buscando MacroRotation...")
    macro_line = None
    for i, line in enumerate(lines):
        if "class MacroRotation" in line:
            macro_line = i
            print(f"   Encontrado en línea {i+1}")
            break
    
    print("\n🔎 Buscando MotionComponent...")
    component_line = None
    for i, line in enumerate(lines):
        if "class MotionComponent" in line:
            component_line = i
            print(f"   Encontrado en línea {i+1}")
            break
    
    if macro_line and component_line:
        if macro_line < component_line:
            print("\n❌ PROBLEMA: MacroRotation está ANTES que MotionComponent")
        else:
            print("\n✅ OK: MotionComponent está antes que MacroRotation")
    elif not component_line:
        print("\n⚠️ MotionComponent NO EXISTE - usar otra estrategia")
    
    # Crear fix basado en diagnóstico
    print("\n💡 Creando solución...")
    
    if not component_line:
        # No hay MotionComponent, hacer MacroRotation independiente
        create_independent_rotation()
    else:
        # Mover MacroRotation al lugar correcto
        fix_class_order()

def create_independent_rotation():
    """Crea MacroRotation como clase independiente"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Leer contenido
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Eliminar la clase MacroRotation actual
    import re
    content = re.sub(
        r'class MacroRotation.*?(?=\nclass|\n@|\Z)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Crear nueva versión independiente
    new_macro_rotation = '''
@dataclass
class MacroRotation:
    """Rotación algorítmica del macro alrededor de su centro"""
    center: np.ndarray = field(default_factory=lambda: np.zeros(3))
    rotation_speed: np.ndarray = field(default_factory=lambda: np.zeros(3))  # rad/s
    current_angle: np.ndarray = field(default_factory=lambda: np.zeros(3))
    enabled: bool = False
    
    def calculate_delta(self, current_time: float, dt: float, state: MotionState) -> MotionDelta:
        """Calcula el delta de posición por rotación"""
        delta = MotionDelta()
        delta.source_id = state.source_id
        
        if not self.enabled or np.allclose(self.rotation_speed, 0):
            return delta
            
        # Actualizar ángulos
        self.current_angle += self.rotation_speed * dt
        
        # Posición relativa al centro
        rel_pos = state.position - self.center
        
        # Aplicar rotaciones (orden: Z, Y, X)
        # Rotación en Z
        if abs(self.rotation_speed[2]) > 0:
            cos_z = np.cos(self.rotation_speed[2] * dt)
            sin_z = np.sin(self.rotation_speed[2] * dt)
            new_x = rel_pos[0] * cos_z - rel_pos[1] * sin_z
            new_y = rel_pos[0] * sin_z + rel_pos[1] * cos_z
            rel_pos[0] = new_x
            rel_pos[1] = new_y
            
        # Rotación en Y
        if abs(self.rotation_speed[1]) > 0:
            cos_y = np.cos(self.rotation_speed[1] * dt)
            sin_y = np.sin(self.rotation_speed[1] * dt)
            new_x = rel_pos[0] * cos_y + rel_pos[2] * sin_y
            new_z = -rel_pos[0] * sin_y + rel_pos[2] * cos_y
            rel_pos[0] = new_x
            rel_pos[2] = new_z
            
        # Rotación en X
        if abs(self.rotation_speed[0]) > 0:
            cos_x = np.cos(self.rotation_speed[0] * dt)
            sin_x = np.sin(self.rotation_speed[0] * dt)
            new_y = rel_pos[1] * cos_x - rel_pos[2] * sin_x
            new_z = rel_pos[1] * sin_x + rel_pos[2] * cos_x
            rel_pos[1] = new_y
            rel_pos[2] = new_z
            
        # Nueva posición absoluta
        new_position = rel_pos + self.center
        
        # Delta es la diferencia
        delta.position = new_position - state.position
        
        return delta
        
    def set_rotation(self, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):
        """Configura la velocidad de rotación"""
        self.rotation_speed = np.array([speed_x, speed_y, speed_z])
        self.enabled = True
        
    def update_center(self, center: np.ndarray):
        """Actualiza el centro de rotación"""
        self.center = center.copy()
'''
    
    # Insertar después de MotionDelta
    insert_after = "class MotionState:"
    insert_pos = content.find(insert_after)
    if insert_pos > 0:
        content = content[:insert_pos] + new_macro_rotation + "\n\n" + content[insert_pos:]
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ MacroRotation creado como dataclass independiente")

def fix_class_order():
    """Mueve MacroRotation después de MotionComponent"""
    # Similar al fix anterior pero más robusto
    pass

if __name__ == "__main__":
    diagnose_file()
    print("\n🚀 Ejecutando test...")
    os.system("python test_macro_rotation.py")