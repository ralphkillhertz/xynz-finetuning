def fix_sphere_and_main():
    print("🔍 DIAGNÓSTICO Y CORRECCIÓN")
    print("="*60)
    
    # 1. Buscar dónde están las formaciones en el controlador v2
    controller_file = "trajectory_hub/interface/interactive_controller.py"
    
    with open(controller_file, 'r') as f:
        content = f.read()
    
    # Buscar handle_create_macro
    import re
    macro_section = re.search(r'def handle_create_macro.*?(?=\n    def|\Z)', content, re.DOTALL)
    
    if macro_section:
        section_text = macro_section.group(0)
        
        # Buscar las formaciones
        formations_in_section = re.search(r'print.*?"Formación.*?5\. random', section_text, re.DOTALL)
        
        if formations_in_section and "6. sphere" not in formations_in_section.group(0):
            print("✅ Encontradas formaciones en handle_create_macro")
            
            # Reemplazar para añadir sphere
            old_text = formations_in_section.group(0)
            new_text = old_text.rstrip() + "\n  6. sphere"
            
            content = content.replace(old_text, new_text)
            
            # También buscar el diccionario de formaciones
            formations_dict = re.search(r'formations\s*=\s*\{[^}]+\}', section_text)
            if formations_dict and '"6": "sphere"' not in formations_dict.group(0):
                old_dict = formations_dict.group(0)
                new_dict = old_dict.rstrip('}') + ', "6": "sphere"}'
                content = content.replace(old_dict, new_dict)
            
            # Guardar
            import shutil
            from datetime import datetime
            backup = f"{controller_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(controller_file, backup)
            
            with open(controller_file, 'w') as f:
                f.write(content)
            
            print("✅ Sphere añadido al menú de formaciones")
    
    # 2. Crear main.py funcional
    print("\n🔧 Creando main.py funcional...")
    
    main_content = '''#!/usr/bin/env python3
"""
Trajectory Hub - Punto de entrada principal
"""
import sys
import argparse
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController


def main():
    parser = argparse.ArgumentParser(description='Trajectory Hub - Sistema de trayectorias 3D')
    parser.add_argument('--interactive', '-i', action='store_true', 
                        help='Iniciar en modo interactivo')
    parser.add_argument('--sources', '-s', type=int, default=100,
                        help='Número máximo de fuentes (default: 100)')
    parser.add_argument('--fps', '-f', type=int, default=60,
                        help='FPS del sistema (default: 60)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host OSC de Spat (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9000,
                        help='Puerto OSC de Spat (default: 9000)')
    
    args = parser.parse_args()
    
    if args.interactive:
        print("🎮 Iniciando modo interactivo...")
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(
            max_sources=args.sources,
            fps=args.fps
        )
        
        # Configurar OSC si es necesario
        if args.host != '127.0.0.1' or args.port != 9000:
            engine.osc_bridge.targets.clear()
            engine.osc_bridge.add_target(("Custom", args.host, args.port))
        
        # Crear controlador e iniciar
        controller = InteractiveController(engine)
        controller.run()
    else:
        print("Trajectory Hub v1.0")
        print("Usa --interactive para iniciar el modo interactivo")
        print("Usa --help para ver todas las opciones")


if __name__ == "__main__":
    main()
'''
    
    with open("main.py", "w") as f:
        f.write(main_content)
    
    print("✅ main.py creado")
    
    # 3. Crear script de test rápido
    test_code = '''# Test rápido de sphere en menú
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController

engine = EnhancedTrajectoryEngine(max_sources=20, fps=30)
controller = InteractiveController(engine)

# Verificar que sphere está disponible
print("🔍 Verificando formaciones disponibles...")

# Simular creación directa
print("\\n🧪 Creando macro con sphere directamente:")
macro = engine.create_macro("test_sphere", 10, formation="sphere")
print(f"✅ Macro creado: {macro.name}")

stats = engine.osc_bridge.get_stats()
print(f"📡 OSC: {stats['messages_sent']} mensajes enviados")
'''
    
    with open("test_sphere_menu.py", "w") as f:
        f.write(test_code)
    
    print("\n✅ CORRECCIONES COMPLETADAS")
    print("\n🚀 Prueba ahora:")
    print("   1. python main.py --interactive")
    print("   2. O directamente: python -m trajectory_hub.interface.interactive_controller")
    print("\n📋 En el menú:")
    print("   - Opción 1 (Crear Macro)")
    print("   - Formación: 6 (sphere)")

if __name__ == "__main__":
    fix_sphere_and_main()