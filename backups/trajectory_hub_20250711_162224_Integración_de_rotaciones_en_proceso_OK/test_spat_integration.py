#!/usr/bin/env python3
"""
Test de integración con SPAT Revolution
Prueba las nuevas funcionalidades OSC
"""
import time
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_spat_integration():
    print("=== TEST DE INTEGRACIÓN CON SPAT ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # 1. Crear un macro con nombres personalizados
    print("1. Creando macro 'demo_spat' con 8 fuentes...")
    macro_id = engine.create_macro(
        name="demo_spat",
        source_count=8,
        formation="circle",
        spacing=3.0
    )
    print(f"   ✅ Macro creado: {macro_id}")
    print("   📝 Las fuentes deberían llamarse: demo_spat_1, demo_spat_2, ..., demo_spat_8")
    print("   🔗 Las fuentes deberían estar seleccionadas en SPAT (agrupadas visualmente)")
    
    time.sleep(2)
    
    # 2. Mover el macro
    print("\n2. Moviendo el macro a una nueva posición...")
    new_position = np.array([5.0, 2.0, 5.0])
    engine.move_macro_center(macro_id, new_position)
    print(f"   ✅ Macro movido a: X={new_position[0]}, Y={new_position[1]}, Z={new_position[2]}")
    
    time.sleep(2)
    
    # 3. Desactivar el macro
    print("\n3. Desactivando el macro...")
    print("   - Se mutearán las fuentes primero")
    print("   - Luego se desactivarán en SPAT")
    print("   - Se guardará el estado actual")
    engine.enable_macro(macro_id, False)
    print("   ⏸️ Macro desactivado y muteado")
    
    time.sleep(3)
    
    # 4. Reactivar el macro
    print("\n4. Reactivando el macro...")
    print("   - Se activarán las fuentes en SPAT")
    print("   - Se desmutearán automáticamente")
    print("   - Volverán a su última posición")
    engine.enable_macro(macro_id, True)
    print("   ▶️ Macro reactivado y desmuteado")
    
    time.sleep(2)
    
    # 5. Test de mute manual (opcional, ya integrado en desactivar)
    print("\n5. Test de mute manual (función disponible pero integrada en desactivar)...")
    engine.mute_macro(macro_id, True)
    print("   🔇 Macro muteado manualmente")
    
    time.sleep(2)
    
    engine.mute_macro(macro_id, False)
    print("   🔊 Macro desmuteado manualmente")
    
    time.sleep(2)
    
    # 7. Crear segundo macro para probar múltiples grupos
    print("\n7. Creando segundo macro 'test_group' con 6 fuentes...")
    macro_id2 = engine.create_macro(
        name="test_group",
        source_count=6,
        formation="line",
        spacing=2.0
    )
    print(f"   ✅ Segundo macro creado: {macro_id2}")
    print("   📝 Las fuentes deberían llamarse: test_group_1, test_group_2, ..., test_group_6")
    
    time.sleep(2)
    
    # 8. Verificar información de macros
    print("\n8. Listando todos los macros...")
    macros = engine.list_macros()
    for macro in macros:
        status = "ACTIVADO" if engine.is_macro_enabled(macro['key']) else "DESACTIVADO"
        print(f"   • {macro['name']}: {macro['num_sources']} fuentes, formación: {macro['formation']}, estado: {status}")
    
    print("\n✨ Test completado")
    print("\nVERIFICA EN SPAT:")
    print("1. Los nombres de las fuentes deben seguir el formato Macro_name_n")
    print("2. Las fuentes de cada macro deberían estar agrupadas visualmente")
    print("3. Al desactivar un macro:")
    print("   - Primero se mutean las fuentes (sin audio)")
    print("   - Luego se desactivan (desaparecen)")
    print("4. Al reactivar un macro:")
    print("   - Las fuentes vuelven a su última posición")
    print("   - Se activan y desmutean automáticamente")
    print("5. El mute ahora está integrado en la desactivación")

if __name__ == "__main__":
    test_spat_integration()