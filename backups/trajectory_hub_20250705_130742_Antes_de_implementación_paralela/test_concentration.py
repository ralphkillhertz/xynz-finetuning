#!/usr/bin/env python3
"""
test_concentration.py - Prueba del sistema de concentración
"""

import asyncio
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

async def test_concentration():
    print("🧪 TEST DEL SISTEMA DE CONCENTRACIÓN\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro de prueba
    print("1. Creando macro con 10 fuentes...")
    macro_id = engine.create_macro("test_concentration", 10, 
                                   formation="circle", spacing=2.0)
    
    # Configurar movimiento
    print("2. Configurando trayectorias...")
    engine.set_macro_trajectory(macro_id, "circle", size=5.0)
    engine.set_trajectory_mode(macro_id, "fix", speed=1.0)
    
    # Test concentración inmediata
    print("\n3. Test concentración inmediata (factor 0.5)")
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Actualizar algunos frames
    for _ in range(30):
        engine.update()
        
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✓ Factor: {state['factor']}")
    print(f"   ✓ Habilitado: {state['enabled']}")
    
    # Test animación
    print("\n4. Test animación (0.5 → 0.0 en 2s)")
    engine.animate_macro_concentration(macro_id, 0.0, 2.0)
    
    # Simular 2 segundos
    for i in range(120):
        engine.update()
        if i % 60 == 0:
            state = engine.get_macro_concentration_state(macro_id)
            print(f"   - {i/60}s: factor={state['factor']:.2f}")
            
    # Test toggle
    print("\n5. Test toggle")
    engine.toggle_macro_concentration(macro_id)
    
    for _ in range(120):
        engine.update()
        
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✓ Factor después de toggle: {state['factor']}")
    
    print("\n✅ TESTS COMPLETADOS")

if __name__ == "__main__":
    asyncio.run(test_concentration())
