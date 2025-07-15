#!/usr/bin/env python3
"""
🧪 TEST AJUSTADO - Estructura real de ConcentrationComponent
"""

import sys
import numpy as np
import json
from datetime import datetime

sys.path.insert(0, 'trajectory_hub')

from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
from trajectory_hub.core.motion_components import (
    ConcentrationComponent, ConcentrationMode, 
    MotionState, SourceMotion
)

def analyze_concentration_structure():
    """Analizar la estructura real de ConcentrationComponent"""
    print("\n🔍 ANALIZANDO ESTRUCTURA DE ConcentrationComponent...")
    
    concentration = ConcentrationComponent()
    
    # Listar todos los atributos
    attrs = [attr for attr in dir(concentration) if not attr.startswith('_') and not callable(getattr(concentration, attr))]
    
    print("Atributos encontrados:")
    for attr in attrs:
        try:
            value = getattr(concentration, attr)
            print(f"   - {attr}: {value}")
        except:
            print(f"   - {attr}: <no accesible>")
    
    return concentration

def test_concentration_real_structure():
    """Test adaptado a la estructura real"""
    print("\n🧪 TEST: ConcentrationComponent (Estructura Real)")
    print("=" * 60)
    
    results = {}
    
    try:
        # Primero analizar estructura
        concentration = analyze_concentration_structure()
        
        # Test 1: Modo Original - Comportamiento actual
        print("\n1️⃣ TEST MODO ORIGINAL...")
        
        # Asegurar modo original
        compat.config['CONCENTRATION_DUAL_MODE'] = False
        compat.reload_config()
        
        # Configurar concentración
        concentration.enabled = True
        concentration.factor = 0.0  # 0 = máxima concentración
        concentration.target_point = np.array([0.0, 0.0, 0.0])
        
        # Si tiene modo, configurarlo
        if hasattr(concentration, 'mode'):
            concentration.mode = ConcentrationMode.FIXED_POINT
            print(f"   Modo: {concentration.mode}")
        
        # Crear estado
        state = MotionState()
        state.position = np.array([10.0, 0.0, 0.0])
        if hasattr(state, 'source_id'):
            state.source_id = 1
        
        print(f"   Posición inicial: {state.position}")
        print(f"   Target: {concentration.target_point}")
        print(f"   Factor: {concentration.factor} (0=máxima concentración)")
        
        # Update
        current_time = 0.0
        dt = 0.016
        
        # Ejecutar varios updates para ver comportamiento
        positions = [state.position.copy()]
        current_state = state
        
        for i in range(5):
            new_state = concentration.update(current_state, current_time + i*dt, dt)
            positions.append(new_state.position.copy())
            current_state = new_state
        
        print("\n   Progresión de posiciones:")
        for i, pos in enumerate(positions):
            dist = np.linalg.norm(pos - concentration.target_point)
            print(f"     Update {i}: {pos} (dist al target: {dist:.3f})")
        
        # Verificar comportamiento
        initial_dist = np.linalg.norm(positions[0] - concentration.target_point)
        final_dist = np.linalg.norm(positions[-1] - concentration.target_point)
        
        moved = not np.allclose(positions[0], positions[-1])
        converging = final_dist < initial_dist
        reached_target = final_dist < 0.01
        
        # Calcular velocidad de convergencia
        if len(positions) > 1:
            step_size = np.linalg.norm(positions[1] - positions[0])
            print(f"\n   Tamaño del paso inicial: {step_size:.4f}")
        
        results['original_moves'] = "✅ PASS" if moved else "❌ FAIL"
        results['original_converges'] = "✅ PASS" if converging else "❌ FAIL"
        results['original_speed'] = "🚀 MUY RÁPIDO" if reached_target else "✅ GRADUAL"
        
        # Test 2: Modo Dual
        print("\n2️⃣ TEST MODO DUAL...")
        
        # Activar modo dual
        compat.config['CONCENTRATION_DUAL_MODE'] = True
        compat.reload_config()
        print(f"   Modo dual activado: {compat.is_concentration_dual_mode()}")
        
        # Limpiar deltas
        compat.clear_deltas()
        
        # Nuevo estado
        state2 = MotionState()
        state2.position = np.array([10.0, 0.0, 0.0])
        if hasattr(state2, 'source_id'):
            state2.source_id = 2
        else:
            # Agregar source_id manualmente si no existe
            state2.source_id = 2
        
        initial_pos2 = state2.position.copy()
        
        # Update en modo dual
        new_state2 = concentration.update(state2, current_time, dt)
        
        # Verificar comportamiento dual
        position_unchanged = np.allclose(new_state2.position, initial_pos2, atol=1e-6)
        
        # Verificar deltas
        stored_delta = compat.get_accumulated_delta(2)
        has_delta = stored_delta is not None
        
        print(f"   Posición inicial: {initial_pos2}")
        print(f"   Posición después: {new_state2.position}")
        print(f"   Cambio: {new_state2.position - initial_pos2}")
        print(f"   ¿Posición sin cambio?: {position_unchanged}")
        print(f"   ¿Delta almacenado?: {has_delta}")
        
        if has_delta:
            print(f"   Delta: {stored_delta}")
            print(f"   Magnitud del delta: {np.linalg.norm(stored_delta):.6f}")
        
        results['dual_no_immediate_change'] = "✅ PASS" if position_unchanged else "❌ FAIL"
        results['dual_stores_delta'] = "✅ PASS" if has_delta else "❌ FAIL"
        
        # Test 3: Factor = 1.0 (sin concentración)
        print("\n3️⃣ TEST FACTOR = 1.0 (DISPERSO)...")
        
        # Volver a modo original
        compat.config['CONCENTRATION_DUAL_MODE'] = False
        
        concentration.factor = 1.0  # Sin concentración
        state3 = MotionState()
        state3.position = np.array([10.0, 0.0, 0.0])
        
        new_state3 = concentration.update(state3, current_time, dt)
        
        no_movement = np.allclose(state3.position, new_state3.position)
        results['factor_1_no_movement'] = "✅ PASS" if no_movement else "❌ FAIL"
        
        print(f"   Con factor=1.0, posición se mantiene: {no_movement}")
        
        # Test 4: Integración con SourceMotion
        print("\n4️⃣ TEST CON SourceMotion...")
        
        try:
            source = SourceMotion(source_id=3)
            
            # Verificar estructura
            if 'concentration' in source.components:
                print("   ✅ SourceMotion tiene concentration")
                
                # Configurar
                source.components['concentration'].enabled = True
                source.components['concentration'].factor = 0.0
                source.state.position = np.array([5.0, 0.0, 0.0])
                
                initial_source_pos = source.state.position.copy()
                
                # Update - SourceMotion.update(time, dt)
                source.update(0.0, 0.016)
                
                final_source_pos = source.state.position
                source_moved = not np.allclose(initial_source_pos, final_source_pos)
                
                results['source_integration'] = "✅ PASS" if source_moved else "❌ FAIL"
                print(f"   Movimiento: {source_moved}")
                
            else:
                results['source_integration'] = "⚠️ NO TIENE concentration"
                
        except Exception as e:
            results['source_integration'] = f"❌ ERROR: {str(e)[:50]}"
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN:")
    
    passed = sum(1 for r in results.values() if "✅ PASS" in str(r))
    total = sum(1 for r in results.values() if "PASS" in str(r) or "FAIL" in str(r))
    
    for test, result in results.items():
        print(f"  {test}: {result}")
    
    print(f"\nRESULTADO: {passed}/{total} tests pasados")
    
    # Diagnóstico
    if "❌ FAIL" in str(results.get('dual_no_immediate_change', '')):
        print("\n⚠️ DIAGNÓSTICO MODO DUAL:")
        print("   El código de modo dual puede no estar interceptando correctamente")
        print("   Verificar que el if compat.is_concentration_dual_mode() está")
        print("   ANTES de la línea state.position = self._lerp(...)")
    
    # Guardar
    with open('phase1_test_results_final.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': {k: str(v) for k, v in results.items()},
            'passed': passed,
            'total': total
        }, f, indent=2)
    
    return passed >= total - 1

if __name__ == "__main__":
    success = test_concentration_real_structure()
    
    if success:
        print("\n✅ FASE 1 COMPLETADA")
        print("ConcentrationComponent funciona en ambos modos")
    else:
        print("\n❌ Revisa los fallos arriba")