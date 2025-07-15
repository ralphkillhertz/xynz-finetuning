#!/usr/bin/env python3
"""
🔧 Reconstrucción: Rebuild de clases problemáticas
⚡ Objetivo: Reemplazar clases corruptas con versiones limpias
🎯 Foco: OrientationModulation y ConcentrationComponent
"""

def rebuild_orientation_modulation():
    """Reconstruye la clase OrientationModulation"""
    
    code = """
class OrientationModulation(MotionComponent):
    """Modulación de orientación con formas predefinidas"""
    
    def __init__(self):
        super().__init__()
        self.yaw_func = None
        self.pitch_func = None
        self.roll_func = None
        self.aperture_func = None
        self.time = 0.0
        
    def set_functions(self, 
                      yaw: Optional[Callable] = None,
                      pitch: Optional[Callable] = None,
                      roll: Optional[Callable] = None):
        """Configurar funciones de modulación"""
        if yaw:
            self.yaw_func = yaw
        if pitch:
            self.pitch_func = pitch
        if roll:
            self.roll_func = roll
            
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualizar orientación"""
        self.time += dt
        
        if self.yaw_func:
            state.orientation[2] = self.yaw_func(self.time)
        if self.pitch_func:
            state.orientation[0] = self.pitch_func(self.time)
        if self.roll_func:
            state.orientation[1] = self.roll_func(self.time)
            
        return state
"""
    return code

def rebuild_concentration_component():
    """Reconstruye ConcentrationComponent con sistema de deltas"""
    
    code = """
class ConcentrationComponent(MotionComponent):
    """Componente para concentrar/dispersar fuentes"""
    
    def __init__(self, macro=None):
        super().__init__()
        self.macro = macro
        self.concentration_factor = 0.0
        self.enabled = False
        self.macro_center = np.zeros(3)
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta para concentración"""
        if not self.enabled or self.concentration_factor == 0:
            return MotionDelta(source="concentration")
        
        # Calcular centro
        center = self.macro_center
        
        # Vector hacia el centro
        to_center = center - state.position
        distance = np.linalg.norm(to_center)
        
        if distance > 0.001:
            direction = to_center / distance
            movement = direction * distance * self.concentration_factor * dt
            
            return MotionDelta(
                position=movement,
                weight=abs(self.concentration_factor),
                source="concentration"
            )
        
        return MotionDelta(source="concentration")
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Versión legacy - actualiza estado directamente"""
        if not self.enabled or self.concentration_factor == 0:
            return state
            
        delta = self.calculate_delta(state, current_time, dt)
        state.position += delta.position
        
        return state
        
    def set_factor(self, factor: float):
        """Establecer factor de concentración"""
        self.concentration_factor = max(0.0, min(1.0, factor))
        
    def update_macro_center(self, positions: List[np.ndarray]):
        """Actualizar centro del macro"""
        if positions:
            self.macro_center = np.mean(positions, axis=0)
"""
    return code

if __name__ == "__main__":
    print("🔧 SCRIPTS DE RECONSTRUCCIÓN GENERADOS")
    
    with open("rebuild_classes.py", "w") as f:
        f.write(__doc__)
        f.write("\n\n")
        f.write("# CÓDIGO PARA REEMPLAZAR:\n\n")
        f.write(rebuild_orientation_modulation())
        f.write("\n\n")
        f.write(rebuild_concentration_component())
    
    print("✅ Archivo creado: rebuild_classes.py")
    print("\nPasos siguientes:")
    print("1. Revisar rebuild_classes.py")
    print("2. Reemplazar las clases problemáticas manualmente")
    print("3. O usar un script automatizado para el reemplazo")
