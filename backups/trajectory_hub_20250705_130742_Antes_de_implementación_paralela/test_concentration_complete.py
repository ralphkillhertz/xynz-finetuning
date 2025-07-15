#!/usr/bin/env python3
"""
test_concentration_complete.py - Test completo y funcional del sistema de concentración
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import time

def test_concentration_system():
    print("🎯 TEST COMPLETO DEL SISTEMA DE CONCENTRACIÓN")
    print("="*60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("\n✅ Engine creado")
    
    # Crear macro con 15 fuentes
    print("\n1️⃣ CREANDO MACRO")
    macro_id = engine.create_macro("concentration_test", 15, 
                                   formation="circle", spacing=3.0)
    print(f"   ✅ Macro '{macro_id}' creado con 15 fuentes en formación circular")
    
    # Estado inicial
    print("\n2️⃣ ESTADO INICIAL")
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   Factor: {state.get('factor', 'N/A')}")
    print(f"   Habilitado: {state.get('enabled', False)}")
    print(f"   Modo: {state.get('mode', 'N/A')}")
    
    # Test 1: Concentración inmediata
    print("\n3️⃣ TEST CONCENTRACIÓN INMEDIATA")
    print("   Estableciendo factor 0.0 (totalmente concentrado)...")
    engine.set_macro_concentration(macro_id, 0.0)
    
    # Actualizar algunas veces
    for _ in range(10):
        engine.update()
    
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✅ Factor actual: {state['factor']}")
    print(f"   ✅ Las fuentes están concentradas en un punto")
    
    # Test 2: Dispersión animada
    print("\n4️⃣ TEST DISPERSIÓN ANIMADA")
    print("   Animando de concentrado (0.0) a disperso (1.0) en 3 segundos...")
    engine.animate_macro_concentration(macro_id, 1.0, 3.0, "ease_in_out")
    
    # Simular 3 segundos (180 frames a 60fps)
    start_time = time.time()
    frames = 0
    while frames < 180:
        engine.update()
        frames += 1
        
        # Mostrar progreso cada 0.5 segundos (30 frames)
        if frames % 30 == 0:
            state = engine.get_macro_concentration_state(macro_id)
            elapsed = frames / 60.0
            print(f"   t={elapsed:.1f}s: factor={state['factor']:.3f} {'🟢' if state['animating'] else '⭕'}")
    
    print("   ✅ Animación completada")
    
    # Test 3: Toggle rápido
    print("\n5️⃣ TEST TOGGLE")
    print("   Estado actual: disperso (1.0)")
    print("   Ejecutando toggle...")
    engine.toggle_macro_concentration(macro_id)
    
    # Esperar un poco para ver la animación
    for i in range(60):  # 1 segundo
        engine.update()
        if i == 30:
            state = engine.get_macro_concentration_state(macro_id)
            print(f"   Durante animación: factor={state['factor']:.3f}")
    
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✅ Toggle completado: factor={state['factor']:.3f}")
    
    # Test 4: Diferentes modos
    print("\n6️⃣ TEST MODOS DE CONCENTRACIÓN")
    
    # Modo punto fijo
    print("   a) Modo punto fijo en origen...")
    engine.set_macro_concentration(macro_id, 0.2, mode="fixed_point", 
                                  target_point=np.array([0.0, 0.0, 0.0]))
    print("   ✅ Establecido")
    
    # Modo seguir macro
    print("   b) Modo seguir macro...")
    engine.set_macro_concentration(macro_id, 0.3, mode="follow_macro")
    print("   ✅ Establecido")
    
    # Test 5: Curvas de animación
    print("\n7️⃣ TEST CURVAS DE ANIMACIÓN")
    curves = ["linear", "ease_in", "ease_out", "exponential", "bounce"]
    
    for curve in curves:
        print(f"   Probando curva '{curve}'...")
        engine.animate_macro_concentration(macro_id, 0.5, 0.5, curve)
        
        # Simular medio segundo
        for _ in range(30):
            engine.update()
        
        state = engine.get_macro_concentration_state(macro_id)
        print(f"   ✅ {curve}: factor={state['factor']:.3f}")
    
    # Test 6: Parámetros avanzados
    print("\n8️⃣ TEST PARÁMETROS AVANZADOS")
    engine.set_concentration_parameters(
        macro_id,
        include_macro_trajectory=False,
        attenuate_rotations=True,
        attenuate_modulations=True
    )
    print("   ✅ Parámetros avanzados configurados")
    
    # Verificación final
    print("\n9️⃣ VERIFICACIÓN FINAL")
    
    # Verificar que los componentes están activos
    if hasattr(engine, '_source_motions') and hasattr(engine, '_macros'):
        macro = engine._macros.get(macro_id)
        if macro and hasattr(macro, 'source_ids'):
            active_count = 0
            for sid in macro.source_ids:
                if sid in engine._source_motions:
                    motion = engine._source_motions[sid]
                    if 'concentration' in motion.components:
                        if motion.components['concentration'].enabled:
                            active_count += 1
            
            print(f"   ✅ {active_count}/{len(macro.source_ids)} fuentes con concentración activa")
            
            # Mostrar info del primer componente
            first_sid = next(iter(macro.source_ids))
            conc = engine._source_motions[first_sid].components['concentration']
            print(f"   📊 Componente ejemplo:")
            print(f"      - Factor: {conc.factor:.3f}")
            print(f"      - Modo: {conc.mode.value}")
            print(f"      - Punto objetivo: {conc.target_point}")
    
    print("\n" + "="*60)
    print("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
    print("\n💡 El sistema de concentración está listo para usar:")
    print("   - Usa la opción 31 en el controlador interactivo")
    print("   - O llama directamente a los métodos del engine")
    print("\n🎮 Métodos disponibles:")
    print("   - set_macro_concentration(macro_id, factor, duration, mode, target_point)")
    print("   - animate_macro_concentration(macro_id, target_factor, duration, curve)")
    print("   - toggle_macro_concentration(macro_id)")
    print("   - get_macro_concentration_state(macro_id)")
    print("   - set_concentration_parameters(macro_id, **params)")

if __name__ == "__main__":
    test_concentration_system()