#!/usr/bin/env python3
import sys
sys.path.insert(0, 'trajectory_hub')

try:
    from trajectory_hub.interface.interactive_controller import InteractiveController
    
    print("\n🧪 VERIFICANDO CONCENTRACIÓN...")
    controller = InteractiveController()
    
    # Verificar engine
    if hasattr(controller, 'engine'):
        engine = controller.engine
        
        # Verificar módulo concentration
        if hasattr(engine, 'modules') and 'concentration' in engine.modules:
            print("✅ Módulo concentration encontrado")
            
            # Activar y probar
            conc = engine.modules['concentration']
            conc.enabled = True
            conc.factor = 0.0  # Máxima concentración
            
            # Guardar posiciones iniciales
            if hasattr(engine, '_positions'):
                import numpy as np
                initial = [np.linalg.norm(pos) for pos in engine._positions]
                
                # Update varias veces
                for _ in range(10):
                    engine.update()
                
                final = [np.linalg.norm(pos) for pos in engine._positions]
                
                if all(f < i for f, i in zip(final, initial)):
                    print("✅ ¡CONCENTRACIÓN FUNCIONA!")
                else:
                    print("❌ Concentración no está funcionando")
                    
    print("\n⚡ Ahora ejecuta el controlador principal")
    
except Exception as e:
    print(f"Error: {e}")
