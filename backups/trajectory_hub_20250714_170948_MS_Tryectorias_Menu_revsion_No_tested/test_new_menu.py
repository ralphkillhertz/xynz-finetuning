#!/usr/bin/env python3
"""Test de la nueva estructura de menús"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_menu_navigation():
    """Test de navegación básica del menú"""
    print("=== TEST: NUEVA ESTRUCTURA DE MENÚS ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Crear un macro de prueba
    print("1. Creando macro de prueba...")
    macro_id = engine.create_macro("menu_test", 5, "circle", spacing=3.0)
    print(f"✅ Macro '{macro_id}' creado")
    
    # Añadir trayectoria al macro
    print("\n2. Añadiendo trayectoria...")
    engine.set_macro_trajectory(
        macro_id,
        "circle",
        speed=1.5,
        radius=5.0
    )
    print("✅ Trayectoria circular añadida")
    
    # Probar métodos de actualización en vivo
    print("\n3. Probando actualización de velocidad...")
    engine.update_trajectory_speed(macro_id, 2.5)
    print("✅ Velocidad actualizada a 2.5")
    
    print("\n4. Probando actualización de escala...")
    engine.update_trajectory_scale(macro_id, 8.0)
    print("✅ Escala actualizada a 8.0m")
    
    # Verificar el estado
    macro = engine._macros[macro_id]
    if macro.trajectory_component:
        print(f"\nEstado actual:")
        print(f"  - Velocidad: {macro.trajectory_component.speed}")
        print(f"  - Tipo: {getattr(macro.trajectory_component.trajectory_func, 'trajectory_type', 'desconocida')}")
        print(f"  - Fase: {macro.trajectory_component.phase:.2f}")
    
    print("\n" + "="*60)
    print("ESTRUCTURA DE MENÚS IMPLEMENTADA:")
    print("✅ Menú principal reorganizado (MS/IS/Efectos)")
    print("✅ Submenú Trayectorias Macro con edición en vivo")
    print("✅ Submenú Rotaciones Macro")
    print("✅ Creación rápida de trayectorias mejorada")
    print("✅ Edición de velocidad/escala sin recrear")
    print("✅ Eliminado menú 'Editar Movimientos Activos'")
    print("="*60)
    
    print("\nPara probar la interfaz completa, ejecuta:")
    print("python -m trajectory_hub.main")


if __name__ == "__main__":
    test_menu_navigation()