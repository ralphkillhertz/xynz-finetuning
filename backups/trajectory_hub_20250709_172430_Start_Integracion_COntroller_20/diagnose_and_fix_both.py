import os
import subprocess
import sys

def diagnose_problems():
    """Diagnosticar ambos problemas"""
    print("🔍 DIAGNÓSTICO DE PROBLEMAS")
    print("="*60)
    
    # 1. Verificar main.py
    print("\n1️⃣ VERIFICANDO main.py...")
    
    if not os.path.exists("main.py"):
        print("❌ main.py no existe!")
        create_main_py()
    else:
        # Intentar ejecutar
        try:
            result = subprocess.run(
                [sys.executable, "main.py", "--help"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode != 0:
                print(f"❌ Error en main.py: {result.stderr}")
                fix_main_py()
            else:
                print("✅ main.py funciona")
        except Exception as e:
            print(f"❌ Error ejecutando main.py: {e}")
            fix_main_py()
    
    # 2. Verificar sphere
    print("\n2️⃣ VERIFICANDO SPHERE...")
    check_sphere_implementation()

def create_main_py():
    """Crear main.py si no existe"""
    print("\n🔧 Creando main.py...")
    
    main_content = '''#!/usr/bin/env python3
"""
Trajectory Hub - Punto de entrada principal
"""
import sys
import argparse
from trajectory_hub.interface.interactive_controller import InteractiveController
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.control.processors.command_processor import CommandProcessor

def main():
    parser = argparse.ArgumentParser(description='Trajectory Hub')
    parser.add_argument('--interactive', action='store_true', help='Iniciar en modo interactivo')
    parser.add_argument('--host', default='192.168.1.101', help='Host OSC')
    parser.add_argument('--port', type=int, default=8888, help='Puerto OSC')
    
    args = parser.parse_args()
    
    # Inicializar engine
    engine = EnhancedTrajectoryEngine(
        osc_host=args.host,
        osc_port=args.port,
        auto_start=True
    )
    
    if args.interactive:
        # Modo interactivo
        controller = InteractiveController(engine)
        controller.run()
    else:
        print("Trajectory Hub - Usa --interactive para modo interactivo")
        print(f"OSC configurado en {args.host}:{args.port}")

if __name__ == "__main__":
    main()
'''
    
    with open("main.py", 'w') as f:
        f.write(main_content)
    
    os.chmod("main.py", 0o755)
    print("✅ main.py creado")

def fix_main_py():
    """Arreglar main.py si está roto"""
    print("\n🔧 Arreglando main.py...")
    
    # Verificar imports
    try:
        from trajectory_hub.interface.interactive_controller import InteractiveController
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        print("✅ Imports correctos")
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        # Recrear main.py
        create_main_py()

def check_sphere_implementation():
    """Verificar por qué sphere crea un círculo"""
    print("\n🔍 Analizando implementación de sphere...")
    
    # 1. Verificar FormationManager
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if os.path.exists(fm_file):
        with open(fm_file, 'r') as f:
            content = f.read()
        
        if '_create_sphere_formation' in content:
            print("✅ FormationManager tiene _create_sphere_formation")
            
            # Verificar si realmente calcula 3D
            if 'y = 1 -' in content and 'golden_angle' in content:
                print("✅ Implementación 3D correcta en FormationManager")
            else:
                print("❌ Implementación no es 3D real")
                fix_sphere_3d()
        else:
            print("❌ FormationManager no tiene sphere")
            fix_sphere_3d()
    
    # 2. Verificar CommandProcessor
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            content = f.read()
        
        # Buscar cómo maneja sphere
        if 'sphere' in content:
            print("\n📍 CommandProcessor contiene 'sphere'")
            
            # Verificar si llama a FormationManager o a engine directamente
            import re
            
            # Buscar handle_create_macro
            handle_match = re.search(
                r'def handle_create_macro.*?(?=\n    def|\nclass|\Z)', 
                content, 
                re.DOTALL
            )
            
            if handle_match:
                method = handle_match.group(0)
                
                if 'formation_manager' in method.lower():
                    print("✅ Usa FormationManager")
                elif '_calculate_circle' in method and 'sphere' in method:
                    print("❌ PROBLEMA: sphere llama a _calculate_circle!")
                    fix_command_processor_sphere()

def fix_sphere_3d():
    """Arreglar implementación 3D de sphere"""
    print("\n🔧 Implementando sphere 3D real...")
    
    # Aquí iría el código para arreglar sphere
    # Por ahora, mostrar instrucciones
    print("\n💡 El problema es que sphere está mapeado a circle")
    print("Necesitamos verificar el mapeo en CommandProcessor")

def fix_command_processor_sphere():
    """Arreglar el mapeo de sphere en CommandProcessor"""
    print("\n🔧 Arreglando mapeo de sphere...")
    
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    with open(cp_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar donde sphere está mapeado incorrectamente
    for i, line in enumerate(lines):
        if 'sphere' in line and ('circle' in line or '_calculate_circle' in line):
            print(f"❌ Problema en línea {i+1}: {line.strip()}")
            
            # Mostrar contexto
            start = max(0, i-5)
            end = min(len(lines), i+5)
            
            print("\n📄 Contexto:")
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j+1}: {lines[j]}")

if __name__ == "__main__":
    diagnose_problems()
    
    print("\n\n💡 SOLUCIÓN RÁPIDA:")
    print("1. Si main.py no funciona, ejecuta directamente:")
    print("   python -m trajectory_hub.interface.interactive_controller")
    print("\n2. Para sphere 3D real, necesitamos verificar:")
    print("   - Que CommandProcessor use FormationManager")
    print("   - Que no esté mapeado sphere → circle")