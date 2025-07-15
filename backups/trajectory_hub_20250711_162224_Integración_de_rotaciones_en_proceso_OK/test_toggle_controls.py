#!/usr/bin/env python3
"""
Test del sistema de control con toggles
"""
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController
import numpy as np

def main():
    print("=== TEST DE CONTROLES CON TOGGLE ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear un macro de prueba
    print("1. Creando macro de demostración...")
    macro_id = engine.create_macro(
        name="test_toggle",
        source_count=16,
        formation="sphere",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}\n")
    
    # Crear controlador
    controller = InteractiveController(engine)
    controller.selected_macro = macro_id
    
    print("2. SISTEMA DE CONTROL ACTUALIZADO:\n")
    
    print("   📍 MOVIMIENTO BÁSICO:")
    print("   • Usa el teclado numérico para moverte:")
    print("     4/6: Izquierda/Derecha (X)")
    print("     8/2: Adelante/Atrás (Z)")
    print("     7/9: Arriba/Abajo (Y)")
    print("     5: Reset a origen")
    
    print("\n   🔄 MODOS TOGGLE (presionar para activar/desactivar):")
    print("   • S: Activa/desactiva modo ESFÉRICO")
    print("     - En modo esférico: 4/6 = Azimut, 8/2 = Distancia, 7/9 = Elevación")
    print("   • A: Activa/desactiva AJUSTE FINO (paso 0.1m)")
    print("     - Los modos son mutuamente excluyentes")
    
    print("\n   ⚡ PRESETS INSTANTÁNEOS:")
    print("   • Usa Shift + número (aparecen como símbolos):")
    print("     Shift+1 = !  → Centro")
    print("     Shift+2 = @  → Frente")
    print("     Shift+3 = #  → Derecha")
    print("     Shift+4 = $  → Atrás")
    print("     Shift+5 = %  → Izquierda")
    print("     Shift+6 = ^  → Arriba")
    print("     Shift+7 = &  → Esquina frontal-derecha")
    print("     Shift+8 = *  → Esquina frontal-izquierda")
    print("     Shift+9 = (  → Órbita frontal")
    print("     Shift+0 = )  → Órbita derecha")
    
    print("\n   📏 CONTROL DE PASO:")
    print("   • +: Aumentar paso (máx 10m)")
    print("   • -: Reducir paso (mín 0.1m)")
    
    print("\n   ✅ FINALIZAR:")
    print("   • ENTER: Confirmar posición")
    print("   • ESC o X: Cancelar")
    
    print("\n3. INDICADORES:")
    print("   • La línea de estado muestra el modo activo:")
    print("     [CARTESIANO] = Modo normal")
    print("     [ESFÉRICO] = Modo esférico activo")
    print("   • El paso actual se muestra siempre")
    
    print("\n4. NOTAS:")
    print("   • Si un preset no funciona, se mostrará un mensaje de debug")
    print("   • Las teclas no reconocidas también mostrarán debug")
    
    print("\n5. Iniciando control interactivo...\n")
    
    # Ejecutar el control
    controller._move_macro_position()
    
    # Mostrar posición final
    final_pos = engine.get_macro_center(macro_id)
    print(f"\n6. Posición final del macro:")
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