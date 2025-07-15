class ConcentrationComponent(MotionComponent):
    """
    Componente que maneja la concentración/dispersión de fuentes
    Se aplica como último paso después de todos los demás movimientos
    """
    
    def __init__(self):
        super().__init__("concentration")
        
        # Parámetros principales
        self.factor = 1.0  # 0=concentrado, 1=disperso
        self.target_point = np.zeros(3)
        self.mode = ConcentrationMode.FIXED_POINT
        
        # Control de animación
        self.animation_active = False
        self.animation_start_factor = 1.0
        self.animation_target_factor = 0.0
        self.animation_duration = 2.0
        self.animation_elapsed = 0.0
        self.animation_curve = ConcentrationCurve.EASE_IN_OUT
        
        # Parámetros avanzados
        self.include_macro_trajectory = True
        self.attenuate_rotations = True
        self.attenuate_modulations = True
        self.concentration_order = "uniform"
        
        # Cache
        self._macro_center = np.zeros(3)
        self._source_distances = {}
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualizar el componente de concentración"""
        if not self.enabled:
            return state
            
        # Actualizar animación
        if self.animation_active:
            self.animation_elapsed += dt
            progress = min(self.animation_elapsed / self.animation_duration, 1.0)
            
            # Aplicar curva
            curved_progress = self._apply_curve(progress, self.animation_curve)
            
            # Interpolar factor
            self.factor = self.animation_start_factor + \
                         (self.animation_target_factor - self.animation_start_factor) * curved_progress
            
            if progress >= 1.0:
                self.animation_active = False
                
        # No hacer nada si completamente disperso
        if abs(self.factor - 1.0) < 0.001:
            return state
            
        # Calcular punto objetivo
        if self.mode == ConcentrationMode.FOLLOW_MACRO:
            target = self._macro_center + self.target_point
        else:
            target = self.target_point
            
        # Aplicar concentración
        concentration_strength = 1.0 - self.factor
                if compat.is_concentration_dual_mode():
            # DUAL MODE: Calculate delta
            delta = compat.calculate_position_delta(state.position, target, concentration_strength)
            source_id = getattr(state, 'source_id', 0)
            compat.store_pending_delta(source_id, 'concentration', delta)
        else:
            # ORIGINAL MODE
            state.position = self._lerp(state.position, target, concentration_strength)
        
        # Atenuar velocidad
        state.velocity *= self.factor
        
        # Atenuar orientación si está habilitado
        if self.attenuate_rotations:
            state.orientation *= self.factor
            
        return state
        