#!/usr/bin/env python3
"""
🧪 TEST FASE 1: Validación de Concentration en modo dual
"""

import sys
import numpy as np
import json

sys.path.insert(0, 'trajectory_hub')

from trajectory_hub.core.compatibility import compat

def test_concentration_dual_mode():
    """Test que concentration funciona en ambos modos"""
    print("\n🧪 TEST: CONCENTRATION MODO DUAL")
    print("-" * 60)
    
    results = {}
    
    try:
        # Test 1: Modo original
        print("\n1️⃣ Probando modo ORIGINAL...")
        
        # Asegurar modo original
        compat.config['CONCENTRATION_DUAL_MODE'] = False
        
        from trajectory_hub.interface.interactive_controller import InteractiveController
        controller = InteractiveController()
        
        if 'concentration' in controller.engine.modules:
            conc = controller.engine.modules['concentration']
            conc.enabled = True
            conc.factor = 0.0  # Max concentration
            
            # Get initial positions
            initial_pos = controller.engine._positions[0].copy()
            
            # Update
            controller.engine.update()
            
            # Check movement
            final_pos = controller.engine._positions[0]
            moved = not np.allclose(initial_pos, final_pos)
            
            results['original_mode'] = "✅ PASS" if moved else "❌ FAIL - No movement"
            print(f"   Posición inicial: {initial_pos}")
            print(f"   Posición final: {final_pos}")
            print(f"   Resultado: {results['original_mode']}")
        
        # Test 2: Modo dual
        print("\n2️⃣ Probando modo DUAL...")
        
        # Activar modo dual
        compat.config['CONCENTRATION_DUAL_MODE'] = True
        compat.load_config()  # Recargar
        
        # Reset positions
        controller = InteractiveController()
        
        if 'concentration' in controller.engine.modules:
            conc = controller.engine.modules['concentration']
            conc.enabled = True
            conc.factor = 0.0
            
            # Check that deltas are being calculated
            motion = controller.engine._source_motions[0]
            
            # Clear any previous deltas
            if hasattr(motion, '_position_deltas'):
                motion._position_deltas = []
            
            # Apply concentration
            conc.apply(motion)
            
            # Check deltas
            has_deltas = hasattr(motion, '_position_deltas') and len(motion._position_deltas) > 0
            
            results['dual_mode_deltas'] = "✅ PASS" if has_deltas else "❌ FAIL - No deltas"
            
            if has_deltas:
                print(f"   Deltas calculados: {len(motion._position_deltas)}")
                for name, delta in motion._position_deltas:
                    print(f"     - {name}: {delta}")
        
        # Test 3: No interferencia con IS
        print("\n3️⃣ Probando independencia de IS...")
        
        # Desactivar IS, activar concentration
        if 'individual_trajectory' in controller.engine.modules:
            controller.engine.modules['individual_trajectory'].enabled = False
        
        conc.enabled = True
        
        # Should work without IS
        initial = controller.engine._positions[0].copy()
        controller.engine.update()
        final = controller.engine._positions[0]
        
        works_without_is = not np.allclose(initial, final)
        results['independent_of_is'] = "✅ PASS" if works_without_is else "❌ FAIL"
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS:")
    
    passed = sum(1 for r in results.values() if "PASS" in str(r))
    total = len(results)
    
    for test, result in results.items():
        print(f"  {test}: {result}")
    
    print(f"\nRESULTADO: {passed}/{total} tests pasados")
    
    return passed == total

if __name__ == "__main__":
    success = test_concentration_dual_mode()
    
    if success:
        print("\n✅ FASE 1 COMPLETADA CON ÉXITO")
        print("Concentration funciona en modo dual")
        print("Puedes proceder a la siguiente fase")
    else:
        print("\n❌ FASE 1 REQUIERE AJUSTES")
        print("Revisa los errores antes de continuar")
