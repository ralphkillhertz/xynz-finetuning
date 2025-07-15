"""
Static Orientation Component - Solo cambia la orientación sin movimiento
"""
import numpy as np
from .motion_components import MotionComponent, MotionDelta, MotionState

class StaticMacroOrientation(MotionComponent):
    """Orientación estática de macro - solo cambia PRY sin mover las posiciones"""
    
    def __init__(self):
        super().__init__("static_macro_orientation")
        
        # Orientación objetivo en radianes
        self.target_pitch = 0.0
        self.target_yaw = 0.0
        self.target_roll = 0.0
        
        # Flag para aplicar solo una vez
        self.orientation_applied = False
        self.enabled = True
    
    def set_orientation(self, pitch: float = None, yaw: float = None, roll: float = None):
        """Establece la orientación objetivo"""
        if pitch is not None:
            self.target_pitch = pitch
        if yaw is not None:
            self.target_yaw = yaw
        if roll is not None:
            self.target_roll = roll
        
        # Reset flag para aplicar la nueva orientación
        self.orientation_applied = False
        self.enabled = True
    
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Solo cambia orientación, no posición"""
        delta = MotionDelta()
        
        if not self.enabled or self.orientation_applied:
            # No hacer nada si ya se aplicó
            delta.position = np.array([0.0, 0.0, 0.0])
            delta.orientation = np.array([0.0, 0.0, 0.0])
            return delta
        
        # Solo cambiar orientación, no posición
        delta.position = np.array([0.0, 0.0, 0.0])  # Sin movimiento
        
        # Establecer nueva orientación (diferencia con la actual)
        current_orientation = np.array(state.orientation) if hasattr(state, 'orientation') else np.zeros(3)
        target_orientation = np.array([self.target_yaw, self.target_pitch, self.target_roll])
        
        delta.orientation = target_orientation - current_orientation
        
        # Marcar como aplicado
        self.orientation_applied = True
        
        return delta
    
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualiza solo la orientación del estado"""
        if not self.enabled or self.orientation_applied:
            return state
        
        # Establecer orientación directamente
        state.orientation = np.array([self.target_yaw, self.target_pitch, self.target_roll])
        
        # Marcar como aplicado
        self.orientation_applied = True
        
        # Desactivar después de aplicar
        self.enabled = False
        
        return state
    
    def reset(self):
        """Reset el componente"""
        self.orientation_applied = False
        self.enabled = True