#!/usr/bin/env python3
"""
Test del nuevo sistema de control con teclado numérico
"""
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController
import numpy as np

def main():
    print("=== TEST DE CONTROL CON TECLADO NUMÉRICO ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro de prueba
    print("1. Creando macro de demostración...")
    macro_id = engine.create_macro(
        name="test_numpad",
        source_count=20,
        formation="sphere",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}\n")
    
    # Crear controlador
    controller = InteractiveController(engine)
    controller.selected_macro = macro_id
    
    print("2. RESUMEN DE CONTROLES:\n")
    
    print("   📍 MOVIMIENTO BÁSICO (Teclado Numérico):")
    print("   ┌───┬───┬───┐")
    print("   │ 7 │ 8 │ 9 │  7/9: Arriba/Abajo (Y)")
    print("   │ ▲ │ ↑ │ ▼ │  8/2: Adelante/Atrás (Z)")
    print("   ├───┼───┼───┤  4/6: Izquierda/Derecha (X)")
    print("   │ 4 │ 5 │ 6 │  5: Reset a origen")
    print("   │ ← │ ● │ → │")
    print("   ├───┼───┼───┤")
    print("   │   │ 2 │   │")
    print("   │   │ ↓ │   │")
    print("   └───┴───┴───┘\n")
    
    print("   🌐 MODO ESFÉRICO (mantener Q):")
    print("   Q+4/6: Rotar (azimut)")
    print("   Q+8/2: Acercar/Alejar (distancia)")
    print("   Q+7/9: Subir/Bajar (elevación)\n")
    
    print("   ⚡ PRESETS RÁPIDOS (Shift + número):")
    print("   !: Centro    @: Frente    #: Derecha    $: Atrás    %: Izquierda")
    print("   ^: Arriba    &: Esquina FD    *: Esquina FI    (: Órbita F    ): Órbita D\n")
    
    print("   🎯 OTROS CONTROLES:")
    print("   A+tecla: Ajuste fino (paso 0.1m)")
    print("   +/-: Cambiar tamaño de paso")
    print("   ENTER: Confirmar    ESC/X: Cancelar\n")
    
    print("3. Iniciando control interactivo...\n")
    
    # Ejecutar el control
    controller._move_macro_position()
    
    # Mostrar posición final
    final_pos = engine.get_macro_center(macro_id)
    print(f"\n4. Posición final del macro:")
    print(f"   X: {final_pos[0]:.2f}m")
    print(f"   Y: {final_pos[1]:.2f}m")
    print(f"   Z: {final_pos[2]:.2f}m")
    
    # En coordenadas esféricas
    dist = np.linalg.norm(final_pos[[0, 2]])
    azimut = np.degrees(np.arctan2(final_pos[2], final_pos[0])) if dist > 0 else 0
    print(f"\n   Distancia: {dist:.2f}m")
    print(f"   Azimut: {azimut:.1f}°")
    print(f"   Elevación: {final_pos[1]:.2f}m")
    
    print("\n✨ Test completado")

if __name__ == "__main__":
    main()