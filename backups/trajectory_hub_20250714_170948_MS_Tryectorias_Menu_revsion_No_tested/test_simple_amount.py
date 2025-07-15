#!/usr/bin/env python3
"""
Test simple para verificar que el sistema de amounts está integrado
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import MacroRotation
from trajectory_hub.core.amount_system import IntensityAmount


def test_amount_integration():
    """Test de integración básico del sistema Amount"""
    print("=== TEST INTEGRACIÓN AMOUNT SYSTEM ===")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Crear un macro simple
    macro_id = engine.create_macro(
        name="test_macro",
        source_count=3,
        formation="circle",
        spacing=2.0
    )
    print(f"✅ Macro '{macro_id}' creado con 3 fuentes")
    
    # Obtener una fuente del macro para verificar los componentes
    macro = engine._macros[macro_id]
    source_id = list(macro.source_ids)[0]  # Convertir set a lista
    source = engine.motion_states[source_id]
    
    print(f"✅ Fuente {source_id} obtenida")
    print(f"   Componentes activos: {list(source.active_components.keys())}")
    
    # Aplicar rotación al macro
    engine.set_macro_rotation(
        macro_id,
        speed_x=0.5,
        speed_y=0.0,
        speed_z=1.0,
        magnitude=0.8
    )
    print("✅ Rotación aplicada al macro")
    
    # Verificar que el componente de rotación tiene el amount
    if 'macro_rotation' in source.active_components:
        rotation_component = source.active_components['macro_rotation']
        print(f"✅ Componente de rotación encontrado: {type(rotation_component).__name__}")
        
        # Verificar amounts
        print(f"   Amounts disponibles: {list(rotation_component.amounts.keys())}")
        
        if 'magnitude' in rotation_component.amounts:
            magnitude_amount = rotation_component.amounts['magnitude']
            print(f"   Magnitude amount: {magnitude_amount.value} (tipo: {type(magnitude_amount).__name__})")
            
            # Cambiar el valor del amount
            magnitude_amount.value = 0.5
            print(f"   Magnitude cambiado a: {magnitude_amount.value}")
            
            # Verificar que el cambio se refleja
            current_magnitude = rotation_component.get_amount_value('magnitude', 1.0)
            print(f"   Valor actual obtenido: {current_magnitude}")
            
            if abs(current_magnitude - 0.5) < 0.001:
                print("✅ Amount system funcionando correctamente")
            else:
                print("❌ Error: el valor no se actualizó correctamente")
        else:
            print("❌ Error: no se encontró el amount 'magnitude'")
    else:
        print("❌ Error: no se encontró el componente de rotación")
    
    print("\n=== TEST COMPLETADO ===")


if __name__ == "__main__":
    test_amount_integration()