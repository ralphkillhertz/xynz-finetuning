#!/usr/bin/env python3
"""
Trajectory Hub - Punto de entrada principal
"""
import sys
import argparse
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController
from trajectory_hub.tools import install_engine_hooks, notify_info, notify_completion


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
    parser.add_argument('--no-backup', action='store_true',
                        help='Deshabilitar backups automáticos')
    parser.add_argument('--no-sound', action='store_true',
                        help='Deshabilitar notificaciones sonoras')
    
    args = parser.parse_args()
    
    if args.interactive:
        print("🎮 Iniciando modo interactivo...")
        
        # Configurar notificaciones si están habilitadas
        if args.no_sound:
            from trajectory_hub.tools.notifications import notifier
            notifier.disable()
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(
            max_sources=args.sources,
            fps=args.fps
        )
        
        # Instalar hooks de backup si están habilitados
        if not args.no_backup:
            install_engine_hooks(engine)
            notify_info("Sistema de backup automático activado")
        
        # Configurar OSC si es necesario
        if args.host != '127.0.0.1' or args.port != 9000:
            engine.osc_bridge.targets.clear()
            engine.osc_bridge.add_target(("Custom", args.host, args.port))
        
        # Crear controlador e iniciar
        controller = InteractiveController(engine)
        try:
            controller.run()
            notify_completion("Sesión finalizada correctamente")
        except KeyboardInterrupt:
            notify_info("Sesión interrumpida por el usuario")
        except Exception as e:
            from trajectory_hub.tools import notify_error
            notify_error(f"Error en la sesión: {e}")
            raise
    else:
        print("Trajectory Hub v1.0")
        print("Usa --interactive para iniciar el modo interactivo")
        print("Usa --help para ver todas las opciones")


if __name__ == "__main__":
    main()
