#!/usr/bin/env python3
"""
Demostración de controles en tiempo real para movimiento de macros
"""
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController

def main():
    print("=== DEMOSTRACIÓN DE CONTROLES EN TIEMPO REAL ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro de prueba
    print("1. Creando macro de demostración...")
    macro_id = engine.create_macro(
        name="demo_realtime",
        source_count=12,
        formation="sphere",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Crear controlador interactivo
    controller = InteractiveController(engine)
    
    print("\n2. Iniciando modo de movimiento interactivo...")
    print("   Los controles responden inmediatamente a las teclas:")
    print("   - Q/A: Mover en X")
    print("   - W/S: Mover en Z") 
    print("   - E/D: Mover en Y")
    print("   - +/-: Cambiar tamaño del paso")
    print("   - R: Reset a origen")
    print("   - ENTER: Confirmar")
    print("   - ESC/X: Cancelar\n")
    
    # Ejecutar movimiento interactivo
    start_pos = engine.get_macro_center(macro_id)
    result = controller._interactive_movement(macro_id, start_pos)
    
    if result is not None:
        print(f"\n✅ Nueva posición confirmada: X={result[0]:.2f}, Y={result[1]:.2f}, Z={result[2]:.2f}")
    else:
        print("\n❌ Movimiento cancelado")
    
    print("\n✨ Demostración completada")

if __name__ == "__main__":
    main()