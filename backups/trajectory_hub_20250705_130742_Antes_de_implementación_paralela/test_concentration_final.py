#!/usr/bin/env python3
"""
test_concentration_final.py - Test final del sistema de concentración
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

def test_concentration():
    print("🧪 TEST FINAL DEL SISTEMA DE CONCENTRACIÓN\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro
    print("1. Creando macro con 10 fuentes...")
    macro_id = engine.create_macro("test_concentration", 10, 
                                   formation="circle", spacing=2.0)
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Test concentración inmediata
    print("\n2. Test concentración inmediata (factor 0.5)")
    result = engine.set_macro_concentration(macro_id, 0.5)
    print(f"   ✅ Concentración aplicada: {result}")
    
    # Obtener estado
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   Factor: {state.get('factor', 'N/A')}")
    print(f"   Habilitado: {state.get('enabled', False)}")
    
    # Test animación
    print("\n3. Test animación (0.5 → 0.0 en 2s)")
    engine.animate_macro_concentration(macro_id, 0.0, 2.0, "ease_in_out")
    
    # Simular algunos frames
    print("\n4. Simulando updates...")
    for i in range(10):
        engine.update()
        if i % 5 == 0:
            state = engine.get_macro_concentration_state(macro_id)
            print(f"   Frame {i}: factor={state.get('factor', 'N/A'):.2f}")
    
    # Test toggle
    print("\n5. Test toggle")
    engine.toggle_macro_concentration(macro_id)
    print("   ✅ Toggle ejecutado")
    
    # Verificar componentes
    print("\n6. Verificando componentes...")
    if hasattr(engine, '_source_motions') and hasattr(engine, '_macros'):
        macro = engine._macros.get(macro_id)
        if macro and hasattr(macro, 'source_ids'):
            first_sid = next(iter(macro.source_ids))
            if first_sid in engine._source_motions:
                motion = engine._source_motions[first_sid]
                if 'concentration' in motion.components:
                    conc = motion.components['concentration']
                    print(f"   ✅ ConcentrationComponent activo")
                    print(f"   - Factor: {conc.factor:.2f}")
                    print(f"   - Enabled: {conc.enabled}")
                    print(f"   - Mode: {conc.mode.value}")
    
    print("\n✅ TODOS LOS TESTS COMPLETADOS")

if __name__ == "__main__":
    test_concentration()
