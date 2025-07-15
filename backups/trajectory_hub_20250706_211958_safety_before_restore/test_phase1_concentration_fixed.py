#!/usr/bin/env python3
"""
🧪 TEST FASE 1: ConcentrationComponent Modo Dual
"""

import sys
import numpy as np
import json

sys.path.insert(0, 'trajectory_hub')

from trajectory_hub.core.compatibility import compat
from trajectory_hub.core.motion_components import ConcentrationComponent, ConcentrationMode, MotionState

def test_concentration_modes():
    """Test concentration in both modes"""
    print("\n🧪 TEST: ConcentrationComponent MODO DUAL")
    print("=" * 60)
    
    results = {}
    
    try:
        # Create mock motion object
        class MockMotion:
            def __init__(self, source_id=0):
                self.source_id = source_id
                self.state = MotionState()
                self.state.position = np.array([5.0, 0.0, 0.0])
        
        # Test 1: Original Mode
        print("\n1️⃣ TEST MODO ORIGINAL...")
        
        # Ensure original mode
        compat.config['CONCENTRATION_DUAL_MODE'] = False
        
        motion = MockMotion(0)
        concentration = ConcentrationComponent()
        concentration.enabled = True
        concentration.factor = 1.0  # Max concentration
        concentration.target = np.array([0.0, 0.0, 0.0])
        concentration.speed = 0.1
        
        initial_pos = motion.state.position.copy()
        concentration.apply(motion)
        final_pos = motion.state.position
        
        moved = not np.allclose(initial_pos, final_pos)
        results['original_mode'] = "✅ PASS" if moved else "❌ FAIL"
        
        print(f"   Initial: {initial_pos}")
        print(f"   Final: {final_pos}")
        print(f"   Result: {results['original_mode']}")
        
        # Test 2: Dual Mode
        print("\n2️⃣ TEST MODO DUAL...")
        
        # Activate dual mode
        compat.config['CONCENTRATION_DUAL_MODE'] = True
        
        motion2 = MockMotion(1)
        compat.clear_deltas()  # Clear any previous deltas
        
        initial_pos2 = motion2.state.position.copy()
        concentration.apply(motion2)
        
        # In dual mode, position shouldn't change immediately
        immediate_change = not np.allclose(motion2.state.position, initial_pos2)
        
        # But delta should be stored
        deltas = compat.get_deltas(1)
        has_delta = len(deltas) > 0
        
        results['dual_mode_no_immediate'] = "✅ PASS" if not immediate_change else "❌ FAIL"
        results['dual_mode_stores_delta'] = "✅ PASS" if has_delta else "❌ FAIL"
        
        print(f"   Position unchanged: {not immediate_change}")
        print(f"   Delta stored: {has_delta}")
        if has_delta:
            print(f"   Delta value: {deltas[0]['position']}")
        
        # Test 3: Independence from IS
        print("\n3️⃣ TEST INDEPENDENCIA DE IS...")
        
        # This tests that concentration works without any IS reference
        motion3 = MockMotion(2)
        concentration.enabled = True
        
        # Should work in both modes without IS
        works_without_is = True
        try:
            concentration.apply(motion3)
        except Exception as e:
            works_without_is = False
            print(f"   Error: {e}")
        
        results['independent_from_is'] = "✅ PASS" if works_without_is else "❌ FAIL"
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS:")
    
    passed = sum(1 for r in results.values() if "PASS" in str(r))
    total = len(results)
    
    for test, result in results.items():
        print(f"  {test}: {result}")
    
    print(f"\nRESULTADO: {passed}/{total} tests pasados")
    
    # Save results
    with open('phase1_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'passed': passed,
            'total': total
        }, f, indent=2)
    
    return passed == total

if __name__ == "__main__":
    from datetime import datetime
    
    success = test_concentration_modes()
    
    if success:
        print("\n✅ FASE 1 VALIDADA EXITOSAMENTE")
        print("ConcentrationComponent funciona en ambos modos")
        print("\nPRÓXIMOS PASOS:")
        print("1. Activar modo dual en el controlador")
        print("2. Probar con opción 31 del menú")
        print("3. Si todo OK, proceder a Fase 2")
    else:
        print("\n❌ FASE 1 REQUIERE REVISIÓN")
        print("Revisa los errores antes de continuar")
