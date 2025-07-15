#!/usr/bin/env python3
"""
test_controller_run.py - Test del método run del controlador
"""

import asyncio
import sys

async def test_run():
    print("🔍 TEST DEL MÉTODO RUN\n")
    
    # Importar
    from trajectory_hub.interface.interactive_controller import InteractiveController
    
    # Crear controlador
    print("1. Creando controlador...")
    controller = InteractiveController()
    print("   ✅ Controlador creado")
    
    # Crear un macro para tener algo que actualizar
    print("\n2. Creando macro de prueba...")
    macro_id = controller.engine.create_macro("test", 5)
    controller.macros["Test"] = macro_id
    print("   ✅ Macro creado")
    
    # Simular parte del run loop
    print("\n3. Simulando bucle de actualización...")
    
    error_count = 0
    max_errors = 5
    
    for i in range(10):
        try:
            # Esto es lo que hace el controlador
            controller.engine.update()
            print(f"   ✓ Update {i+1} exitoso")
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error en update {i+1}: {e}")
            if error_count >= max_errors:
                print("   ❌ Demasiados errores, deteniendo")
                break
    
    if error_count == 0:
        print("\n✅ BUCLE DE ACTUALIZACIÓN FUNCIONA CORRECTAMENTE")
    else:
        print(f"\n❌ Hubo {error_count} errores")
    
    # Test del método step si existe
    if hasattr(controller, 'step'):
        print("\n4. Probando step()...")
        try:
            controller.step()
            print("   ✅ step() funciona")
        except Exception as e:
            print(f"   ❌ Error en step(): {e}")

if __name__ == "__main__":
    asyncio.run(test_run())
