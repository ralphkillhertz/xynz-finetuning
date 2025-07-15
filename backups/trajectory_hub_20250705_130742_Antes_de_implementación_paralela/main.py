#!/usr/bin/env python3
"""
main.py - Punto de entrada principal para Trajectory Hub
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from trajectory_hub.interface.interactive_controller import InteractiveController
from trajectory_hub.demos.demo_enhanced_system import EnhancedDemo


async def run_interactive():
    """Ejecutar modo interactivo"""
    controller = InteractiveController()
    await controller.start()

async def run_demo():
    """Ejecutar demo"""
    demo = EnhancedDemo()
    await demo.run_all_demos()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Trajectory Hub v2.0 - Sistema de Trayectorias 3D",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --interactive          # Modo interactivo completo
  python main.py --demo                 # Ejecutar demos
  python main.py --interactive --debug  # Con debug habilitado
        """
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Ejecutar en modo interactivo"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true", 
        help="Ejecutar demos automáticos"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Habilitar modo debug"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nivel de logging"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    log_level = getattr(logging, args.log_level)
    if args.debug:
        log_level = logging.DEBUG
        
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Información de bienvenida
    print("\n" + "="*60)
    print("TRAJECTORY HUB v2.0")
    print("Sistema de Trayectorias 3D Inteligentes para Spat Revolution")
    print("="*60)
    print("Ralph Killhertz (XYNZ) - ralph@xynz.org")
    
    # Ejecutar modo seleccionado
    try:
        if args.interactive:
            print("\n🎮 Iniciando modo interactivo...")
            asyncio.run(run_interactive())
        elif args.demo:
            print("\n🎯 Ejecutando demos...")
            asyncio.run(run_demo())
        else:
            # Sin argumentos, mostrar ayuda y preguntar qué hacer
            parser.print_help()
            print("\n¿Qué deseas hacer?")
            print("1. Modo interactivo")
            print("2. Ejecutar demos")
            print("3. Salir")
            
            try:
                choice = input("\nSelección (1-3): ").strip()
                if choice == "1":
                    asyncio.run(run_interactive())
                elif choice == "2":
                    asyncio.run(run_demo())
                else:
                    print("\n👋 ¡Hasta luego!")
            except KeyboardInterrupt:
                print("\n\n⚠️ Operación cancelada")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()