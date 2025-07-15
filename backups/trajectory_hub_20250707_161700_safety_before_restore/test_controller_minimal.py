#!/usr/bin/env python3
"""
test_controller_minimal.py - Test mínimo del controlador
"""

import sys
import asyncio

print("🔍 TEST MÍNIMO DEL CONTROLADOR\n")

# Test 1: Importar
try:
    from trajectory_hub.interface.interactive_controller import InteractiveController
    print("✅ InteractiveController importado")
except Exception as e:
    print(f"❌ Error al importar: {e}")
    sys.exit(1)

# Test 2: Ver firma de __init__
import inspect
sig = inspect.signature(InteractiveController.__init__)
print(f"\nFirma de __init__: {sig}")

# Test 3: Crear instancia
try:
    # Intentar sin parámetros
    print("\nIntentando crear sin parámetros...")
    controller = InteractiveController()
    print("✅ Controlador creado sin parámetros")
except TypeError as e:
    print(f"❌ Error: {e}")
    
    # Intentar con engine
    try:
        print("\nIntentando crear con engine...")
        from trajectory_hub import EnhancedTrajectoryEngine
        engine = EnhancedTrajectoryEngine()
        controller = InteractiveController(engine)
        print("✅ Controlador creado con engine")
    except Exception as e2:
        print(f"❌ Error: {e2}")
        sys.exit(1)

# Test 4: Verificar que tiene engine
if hasattr(controller, 'engine'):
    print(f"\n✅ Controlador tiene engine: {type(controller.engine)}")
    
    # Test update
    try:
        controller.engine.update()
        print("✅ engine.update() funciona sin parámetros")
    except Exception as e:
        print(f"❌ Error en update: {e}")

print("\n✅ TESTS BÁSICOS COMPLETADOS")
