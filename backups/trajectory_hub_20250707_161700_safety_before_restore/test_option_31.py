#!/usr/bin/env python3
"""
🧪 TEST DIRECTO OPCIÓN 31
⚡ Simula selección de concentración
"""

import os
import sys

# Agregar rutas
sys.path.insert(0, 'trajectory_hub')
sys.path.insert(0, '.')

print("=" * 60)
print("🧪 TEST OPCIÓN 31 - CONCENTRACIÓN")
print("=" * 60)

try:
    # Importar el controlador
    from trajectory_hub.interface.interactive_controller import InteractiveController
    print("✅ InteractiveController importado")
    
    # Crear instancia
    print("\n🚀 Creando controlador...")
    controller = InteractiveController()
    
    # Verificar si tiene el método de concentración
    methods = [attr for attr in dir(controller) if 'concentration' in attr.lower()]
    if methods:
        print(f"✅ Métodos de concentración encontrados: {methods}")
    
    # Buscar engine
    engine_attrs = ['engine', 'trajectory_engine', 'spatial_engine', 'system', 'hub']
    engine = None
    engine_name = None
    
    for attr in engine_attrs:
        if hasattr(controller, attr):
            engine = getattr(controller, attr)
            engine_name = attr
            print(f"✅ Engine encontrado: controller.{attr}")
            break
    
    if engine:
        # Verificar estado
        if hasattr(engine, '_positions'):
            print(f"✅ Engine tiene _positions: {len(engine._positions)} fuentes")
        elif hasattr(engine, 'positions'):
            print(f"✅ Engine tiene positions: {len(engine.positions)} fuentes")
        
        # Verificar módulos
        if hasattr(engine, 'modules'):
            if 'concentration' in engine.modules:
                print("✅ Módulo concentration existe")
                conc = engine.modules['concentration']
                print(f"   Enabled: {conc.enabled}")
                print(f"   Factor: {getattr(conc, 'factor', 'N/A')}")
            else:
                print("❌ Módulo concentration NO existe")
                print(f"   Módulos disponibles: {list(engine.modules.keys())}")
    
    # Intentar ejecutar opción 31
    print("\n🎯 SIMULANDO OPCIÓN 31...")
    
    # Buscar el método handle_option o process_command
    if hasattr(controller, 'handle_option'):
        print("✅ Método handle_option encontrado")
        try:
            controller.handle_option('31')
            print("✅ Opción 31 ejecutada")
        except Exception as e:
            print(f"❌ Error al ejecutar: {e}")
    
    elif hasattr(controller, 'process_command'):
        print("✅ Método process_command encontrado")
        try:
            controller.process_command('31')
            print("✅ Opción 31 ejecutada")
        except Exception as e:
            print(f"❌ Error al ejecutar: {e}")
    
    # Buscar método directo
    for method in methods:
        if 'test' in method:
            print(f"\n🧪 Ejecutando {method}()...")
            try:
                func = getattr(controller, method)
                func()
                print(f"✅ {method} ejecutado")
            except Exception as e:
                print(f"❌ Error: {e}")
    
except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("\n💡 Verifica que estés en el directorio correcto")
    print("   o que trajectory_hub esté en el PYTHONPATH")

except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Si este test falla, ejecuta directamente:")
print("   python trajectory_hub/interface/interactive_controller.py")
print("Y selecciona manualmente la opción 31")
print("=" * 60)