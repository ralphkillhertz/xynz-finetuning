#!/usr/bin/env python3
"""
Test del sistema de control corregido
"""
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController
import numpy as np

def main():
    print("=== TEST DE CONTROLES CORREGIDOS ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro de prueba
    print("1. Creando macro de demostración...")
    macro_id = engine.create_macro(
        name="test_fixed",
        source_count=16,
        formation="sphere",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}\n")
    
    # Crear controlador
    controller = InteractiveController(engine)
    controller.selected_macro = macro_id
    
    print("2. CONTROLES ACTUALIZADOS:\n")
    
    print("   📍 MOVIMIENTO CARTESIANO:")
    print("   • Teclas solas del numpad:")
    print("     4/6: ← → (X)    8/2: ↑ ↓ (Z)    7/9: ▲ ▼ (Y)    5: Reset")
    
    print("\n   🌐 MOVIMIENTO ESFÉRICO:")
    print("   • Mantener S + tecla del numpad:")
    print("     S+4/6: Azimut    S+8/2: Distancia    S+7/9: Elevación")
    
    print("\n   🎯 AJUSTE FINO:")
    print("   • Mantener A + tecla = Paso de 0.1m")
    print("     Ejemplo: A+6 mueve 0.1m a la derecha")
    
    print("\n   ⚡ PRESETS RÁPIDOS:")
    print("   • Shift + número (símbolos):")
    print("     !: Centro      @: Frente     #: Derecha")
    print("     $: Atrás       %: Izquierda  ^: Arriba")
    print("     &: Esq. FD     *: Esq. FI    (: Órbita F")
    print("     ): Órbita D")
    
    print("\n   📏 OTROS:")
    print("   • +/-: Cambiar tamaño de paso")
    print("   • ENTER: Confirmar")
    print("   • ESC/X: Cancelar")
    
    print("\n3. NOTAS IMPORTANTES:")
    print("   • S y A deben mantenerse presionados mientras se pulsa la tecla numérica")
    print("   • Los presets son instantáneos con Shift+número")
    print("   • El modo se indica en la línea de estado: [CARTESIANO] o [ESFÉRICO]")
    
    print("\n4. Iniciando control interactivo...\n")
    
    # Ejecutar el control
    controller._move_macro_position()
    
    # Mostrar posición final
    final_pos = engine.get_macro_center(macro_id)
    print(f"\n5. Posición final del macro:")
    print(f"   Cartesianas: X={final_pos[0]:.2f}, Y={final_pos[1]:.2f}, Z={final_pos[2]:.2f}")
    
    # En coordenadas esféricas
    dist = np.linalg.norm(final_pos[[0, 2]])
    if dist > 0:
        azimut = np.degrees(np.arctan2(final_pos[2], final_pos[0]))
    else:
        azimut = 0
    print(f"   Esféricas: Dist={dist:.2f}m, Azimut={azimut:.1f}°, Elev={final_pos[1]:.2f}m")
    
    print("\n✨ Test completado")

if __name__ == "__main__":
    main()