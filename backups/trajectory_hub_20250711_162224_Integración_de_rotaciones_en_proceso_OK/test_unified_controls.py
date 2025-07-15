#!/usr/bin/env python3
"""
Test del sistema de control unificado con flechas y modificadores
"""
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController
import numpy as np

def main():
    print("=== TEST DE CONTROL UNIFICADO ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro de prueba
    print("1. Creando macro de demostración...")
    macro_id = engine.create_macro(
        name="test_unified",
        source_count=16,
        formation="sphere",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Mover a posición inicial
    initial_pos = np.array([5.0, 2.0, 5.0])
    engine.move_macro_center(macro_id, initial_pos)
    print(f"\n2. Posición inicial: X={initial_pos[0]}, Y={initial_pos[1]}, Z={initial_pos[2]}")
    
    # Crear controlador
    controller = InteractiveController(engine)
    
    print("\n3. CONTROLES DISPONIBLES:")
    print("\n   Modo Cartesiano (sin modificadores):")
    print("   ← →     : Mover en X (izquierda/derecha)")
    print("   ↑ ↓     : Mover en Z (adelante/atrás)")
    print("   Shift+↑↓: Mover en Y (arriba/abajo)")
    
    print("\n   Modo Esférico (mantener Control):")
    print("   ← →     : Cambiar azimut (rotar alrededor del centro)")
    print("   ↑ ↓     : Cambiar distancia (acercar/alejar)")
    print("   Shift+↑↓: Cambiar elevación (subir/bajar)")
    
    print("\n   Ajuste fino:")
    print("   Cmd/Alt : Paso de 0.1m en lugar de 1m")
    print("   +/-     : Cambiar tamaño del paso")
    print("   R       : Reset a origen")
    print("   ENTER   : Confirmar posición")
    print("   ESC     : Cancelar\n")
    
    print("4. Iniciando control interactivo...")
    
    # Simular que el macro está seleccionado
    controller.selected_macro = macro_id
    
    # Ejecutar movimiento unificado
    result = controller._unified_interactive_movement(macro_id, engine.get_macro_center(macro_id))
    
    if result is not None:
        print(f"\n✅ Nueva posición: X={result[0]:.2f}, Y={result[1]:.2f}, Z={result[2]:.2f}")
        
        # Mostrar en coordenadas esféricas también
        dist = np.linalg.norm(result[[0, 2]])
        azimut = np.degrees(np.arctan2(result[2], result[0])) if dist > 0 else 0
        print(f"   En esféricas: Dist={dist:.2f}m, Azimut={azimut:.1f}°, Elevación={result[1]:.2f}m")
    else:
        print("\n❌ Movimiento cancelado")
    
    print("\n✨ Test completado")

if __name__ == "__main__":
    main()