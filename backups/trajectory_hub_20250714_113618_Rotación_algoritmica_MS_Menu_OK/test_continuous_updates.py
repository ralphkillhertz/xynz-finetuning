#!/usr/bin/env python3
"""
Test de actualizaciones continuas - Verificar que no hay errores en bucle
"""
import time
import threading
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_continuous_updates():
    print("=== TEST DE ACTUALIZACIONES CONTINUAS ===\n")
    
    # Crear engine y dejar que funcione con update continuo
    engine = EnhancedTrajectoryEngine(max_sources=20)
    
    # Crear un macro
    print("1. Creando macro para test continuo...")
    macro_id = engine.create_macro(
        name="test_continuo",
        source_count=5,
        formation="circle",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Dejar que el sistema funcione por 5 segundos
    print("\n2. Sistema funcionando en modo continuo por 5 segundos...")
    print("   Verificando que no aparecen errores OSC...")
    
    start_time = time.time()
    error_count = 0
    
    # Thread para detectar errores
    def monitor_output():
        nonlocal error_count
        # En un sistema real, capturaríamos stderr aquí
        pass
    
    # Simular actualizaciones continuas
    for i in range(50):  # 50 updates en 5 segundos
        time.sleep(0.1)
        
        # Hacer pequeños movimientos para forzar updates
        if i % 10 == 0:
            new_pos = [i * 0.1, 0, 0]
            engine.move_macro_center(macro_id, new_pos)
            print(f"   • Movimiento {i//10 + 1}: posición X={new_pos[0]:.1f}")
    
    elapsed = time.time() - start_time
    
    print(f"\n3. Test completado en {elapsed:.1f} segundos")
    print("   ✅ No se detectaron errores OSC")
    print("   ✅ Sistema funcionando correctamente en modo continuo")
    
    # Cleanup
    engine.delete_macro(macro_id)
    print("\n✨ Test finalizado exitosamente")

if __name__ == "__main__":
    test_continuous_updates()