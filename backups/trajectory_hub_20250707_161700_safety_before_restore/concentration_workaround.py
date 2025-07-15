#!/usr/bin/env python3
"""
concentration_workaround.py - Solución temporal para usar concentración
"""

from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

class ConcentrationEngine(EnhancedTrajectoryEngine):
    """Engine con soporte automático de concentración"""
    
    def create_source(self, source_id: int, name: str = None):
        """Override para agregar concentration automáticamente"""
        motion = super().create_source(source_id, name)
        
        # Agregar concentration si no existe
        if motion and 'concentration' not in motion.components:
            motion.components['concentration'] = ConcentrationComponent()
            
        return motion

# Usar esta clase en lugar de EnhancedTrajectoryEngine
if __name__ == "__main__":
    print("🎯 TEST DE CONCENTRACIÓN CON WORKAROUND\n")
    
    engine = ConcentrationEngine()
    
    # Crear macro
    macro_id = engine.create_macro("test", 5, formation="circle", spacing=3.0)
    
    print("Aplicando concentración...")
    engine.animate_macro_concentration(macro_id, 0.0, 3.0, "ease_in_out")
    
    # Simular
    for i in range(180):  # 3 segundos
        engine.update()
        if i % 60 == 0:
            state = engine.get_macro_concentration_state(macro_id)
            print(f"  t={i/60}s: factor={state['factor']:.2f}")
    
    print("\n✅ Concentración aplicada")
