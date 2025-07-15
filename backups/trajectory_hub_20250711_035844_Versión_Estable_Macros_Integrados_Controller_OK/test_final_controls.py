#!/usr/bin/env python3
"""
Test del sistema de control final con P+número para presets
"""
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController
import numpy as np

def main():
    print("=== SISTEMA DE CONTROL FINAL ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro de prueba
    print("1. Creando macro de demostración...")
    macro_id = engine.create_macro(
        name="test_final",
        source_count=16,
        formation="sphere",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}\n")
    
    # Crear controlador
    controller = InteractiveController(engine)
    controller.selected_macro = macro_id
    
    print("2. CONTROLES FINALES:\n")
    
    print("   📍 MOVIMIENTO (Teclado Numérico):")
    print("   ┌───┬───┬───┐")
    print("   │ 7 │ 8 │ 9 │  7/9: Arriba/Abajo (Y)")
    print("   │ ▲ │ ↑ │ ▼ │  8/2: Adelante/Atrás (Z)")
    print("   ├───┼───┼───┤  4/6: Izquierda/Derecha (X)")
    print("   │ 4 │ 5 │ 6 │  5: Reset a origen")
    print("   │ ← │ ● │ → │")
    print("   ├───┼───┼───┤")
    print("   │   │ 2 │   │")
    print("   │   │ ↓ │   │")
    print("   └───┴───┴───┘")
    
    print("\n   🔄 MODOS ESPECIALES (presionar letra para activar/desactivar):")
    print("   • S = Modo ESFÉRICO")
    print("     - 4/6: Rotar (azimut)")
    print("     - 8/2: Acercar/Alejar (distancia)")
    print("     - 7/9: Subir/Bajar (elevación)")
    print("   • A = AJUSTE FINO (paso 0.1m)")
    print("   • P = MODO PRESET (luego presionar 0-9)")
    
    print("\n   ⚡ PRESETS (P + número):")
    print("   P+1: Centro (0,0,0)")
    print("   P+2: Frente (0,0,5)")
    print("   P+3: Derecha (5,0,0)")
    print("   P+4: Atrás (0,0,-5)")
    print("   P+5: Izquierda (-5,0,0)")
    print("   P+6: Arriba (0,3,0)")
    print("   P+7: Esquina frontal-derecha (4,0,4)")
    print("   P+8: Esquina frontal-izquierda (-4,0,4)")
    print("   P+9: Órbita frontal (0,2,8)")
    print("   P+0: Órbita lateral (8,2,0)")
    
    print("\n   📏 OTROS:")
    print("   • +: Aumentar paso")
    print("   • -: Reducir paso")
    print("   • ENTER: Confirmar")
    print("   • ESC/X: Cancelar")
    
    print("\n3. INDICADORES:")
    print("   • [CARTESIANO]: Modo normal activo")
    print("   • [ESFÉRICO]: Modo esférico activo (S)")
    print("   • [MODO PRESET]: Esperando número (P)")
    
    print("\n4. Iniciando control interactivo...\n")
    
    # Ejecutar el control
    controller._move_macro_position()
    
    # Mostrar posición final
    final_pos = engine.get_macro_center(macro_id)
    print(f"\n5. Posición final:")
    print(f"   X: {final_pos[0]:.2f}m")
    print(f"   Y: {final_pos[1]:.2f}m") 
    print(f"   Z: {final_pos[2]:.2f}m")
    
    print("\n✨ Control completado")

if __name__ == "__main__":
    main()