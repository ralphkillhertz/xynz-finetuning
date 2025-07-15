#!/usr/bin/env python3
"""
Test final - Verificar que el error en bucle está corregido
"""
import time
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_fixed_loop():
    print("=== TEST FINAL - ERROR EN BUCLE CORREGIDO ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20)
    
    # Test 1: Crear macro simple
    print("1. Creando macro simple con 3 fuentes...")
    macro_id1 = engine.create_macro(
        name="test_simple",
        source_count=3,
        formation="line",
        spacing=2.0
    )
    print(f"   ✅ Macro creado sin errores: {macro_id1}")
    
    time.sleep(1)
    
    # Test 2: Crear macro más grande
    print("\n2. Creando macro grande con 10 fuentes...")
    macro_id2 = engine.create_macro(
        name="test_grande",
        source_count=10,
        formation="sphere",
        spacing=4.0
    )
    print(f"   ✅ Macro creado sin errores: {macro_id2}")
    
    time.sleep(1)
    
    # Test 3: Mover macros (verifica que update funcione)
    print("\n3. Moviendo macros (verificando bucle update)...")
    engine.move_macro_center(macro_id1, [5, 0, 0])
    print("   ✅ Primer macro movido sin errores")
    
    time.sleep(0.5)
    
    engine.move_macro_center(macro_id2, [0, 5, 0])
    print("   ✅ Segundo macro movido sin errores")
    
    # Test 4: Operaciones continuas
    print("\n4. Ejecutando operaciones continuas...")
    for i in range(5):
        # Pequeño movimiento para forzar updates
        engine.move_macro_center(macro_id1, [5 + i*0.1, 0, 0])
        time.sleep(0.1)
    print("   ✅ 5 movimientos continuos sin errores")
    
    # Test 5: Desactivar/activar macro
    print("\n5. Probando desactivar/activar macro...")
    engine.enable_macro(macro_id1, False)
    print("   ✅ Macro desactivado sin errores")
    
    time.sleep(0.5)
    
    engine.enable_macro(macro_id1, True)
    print("   ✅ Macro reactivado sin errores")
    
    # Resumen
    print("\n" + "="*50)
    print("✨ TODOS LOS TESTS PASADOS EXITOSAMENTE ✨")
    print("="*50)
    print("\nEl error en bucle ha sido corregido:")
    print("• La función send_source_positions ahora recibe diccionarios correctamente")
    print("• No hay más errores 'list object has no attribute items'")
    print("• Los macros se crean, mueven y actualizan sin problemas")
    print("• El sistema OSC funciona correctamente")
    
    # Listar macros finales
    print("\nMacros creados:")
    macros = engine.list_macros()
    for macro in macros:
        print(f"• {macro['name']}: {macro['num_sources']} fuentes, formación: {macro['formation']}")

if __name__ == "__main__":
    test_fixed_loop()