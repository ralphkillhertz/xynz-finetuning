"""
standalone_controller.py - Controlador mejorado con sistema de comportamientos
"""
import asyncio
import numpy as np
import logging
from typing import Dict, Any, Optional
import time

from trajectory_hub.core.extended_path_engine import ExtendedPathEngine
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget

# Intentar importar describe_behavior
try:
    from trajectory_hub.core.macro_behaviors import describe_behavior
    _BEHAVIORS_AVAILABLE = True
except ImportError:
    _BEHAVIORS_AVAILABLE = False
    def describe_behavior(name):
        return f"Comportamiento: {name}"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrajectoryController:
    """Controlador con sistema de comportamientos robusto"""
    
    def __init__(
        self,
        max_sources: int = 256,
        fps: int = 120,
        osc_host: str = "127.0.0.1",
        osc_port: int = 9000
    ):
        self.engine = ExtendedPathEngine(max_sources=max_sources, fps=fps)
        self.bridge = SpatOSCBridge(
            targets=[OSCTarget(osc_host, osc_port, use_bundles=False)],
            fps=fps
        )
        
        self.running = False
        self._simulation_task: Optional[asyncio.Task] = None
        self.fps = fps
        self.current_macro = None  # Macro actualmente seleccionado
        
        logger.info(f"TrajectoryController inicializado ({max_sources} fuentes @ {fps} fps)")
        
    def create_macro(
        self, 
        name: str, 
        source_count: int, 
        behavior: str = "flock",
        formation: str = "circle",
        spacing: float = 3.0
    ) -> str:
        """Crear un macro con comportamiento específico"""
        macro_id = self.engine.create_macro(
            name, 
            source_count,
            formation=formation,
            spacing=spacing
        )
        
        self.current_macro = macro_id
        logger.info(f"Macro '{name}' creado con comportamiento '{behavior}'")
        return macro_id
        
    def set_behavior(self, behavior: str, macro_id: Optional[str] = None):
        """Cambiar comportamiento de un macro"""
        if macro_id is None:
            macro_id = self.current_macro
            
        if macro_id is None:
            logger.error("No hay macro seleccionado")
            return
            
        self.engine.set_macro_behavior(macro_id, behavior)
        logger.info(f"Comportamiento cambiado a: {behavior}")
        
    def set_trajectory(self, description: str, target: Optional[str] = None):
        """Aplicar trayectoria desde descripción"""
        if target is None:
            target = self.current_macro
            
        if target is None:
            logger.error("No hay macro seleccionado")
            return
            
        # Parser de trayectorias
        trajectory_funcs = self._parse_trajectory(description)
        
        if target in self.engine._macros:
            self.engine.set_macro_trajectory(
                target,
                trajectory_funcs.get('position'),
                trajectory_funcs.get('orientation')
            )
            logger.info(f"Trayectoria aplicada a macro {target}")
        else:
            logger.error(f"Target {target} no encontrado")
            
    def _parse_trajectory(self, desc: str) -> Dict[str, Any]:
        """Parser mejorado de trayectorias"""
        funcs = {}
        desc_lower = desc.lower()
        
        # Posiciones
        if "circle" in desc_lower or "círculo" in desc_lower:
            import re
            r_match = re.search(r'r(\d+\.?\d*)', desc)
            radius = float(r_match.group(1)) if r_match else 5.0
            funcs['position'] = lambda t: np.array([
                radius * np.cos(t),
                radius * np.sin(t),
                0
            ])
            
        elif "spiral" in desc_lower or "espiral" in desc_lower:
            expand = "expand" in desc_lower or "expande" in desc_lower
            if expand:
                funcs['position'] = lambda t: np.array([
                    (2 + 0.1 * t) * np.cos(t),
                    (2 + 0.1 * t) * np.sin(t),
                    0.2 * t
                ])
            else:
                funcs['position'] = lambda t: np.array([
                    (5 - 0.1 * t) * np.cos(t),
                    (5 - 0.1 * t) * np.sin(t),
                    0.2 * t
                ])
            
        elif "lissajous" in desc_lower:
            funcs['position'] = lambda t: np.array([
                5 * np.sin(3 * t),
                5 * np.sin(4 * t + np.pi/4),
                2 * np.sin(5 * t)
            ])
            
        elif "helix" in desc_lower or "hélice" in desc_lower:
            funcs['position'] = lambda t: np.array([
                3 * np.cos(t),
                3 * np.sin(t),
                0.5 * t
            ])
            
        elif "figure8" in desc_lower or "ocho" in desc_lower:
            funcs['position'] = lambda t: np.array([
                5 * np.sin(t),
                5 * np.sin(t) * np.cos(t),
                0
            ])
            
        elif "random" in desc_lower or "aleatorio" in desc_lower:
            # Movimiento suave pseudo-aleatorio
            funcs['position'] = lambda t: np.array([
                4 * np.sin(0.3 * t) * np.cos(0.7 * t),
                4 * np.cos(0.5 * t) * np.sin(0.2 * t),
                2 * np.sin(0.4 * t)
            ])
            
        else:
            # Default: órbita simple
            funcs['position'] = lambda t: np.array([
                5 * np.cos(t * 0.5),
                5 * np.sin(t * 0.5),
                2 * np.sin(t)
            ])
            
        # Orientación
        if "rotate" in desc_lower or "rotar" in desc_lower or "gira" in desc_lower:
            if "yaw" in desc_lower:
                funcs['orientation'] = lambda t: np.array([t * 0.5, 0, 0])
            elif "pitch" in desc_lower:
                funcs['orientation'] = lambda t: np.array([0, np.sin(t) * 0.5, 0])
            elif "roll" in desc_lower:
                funcs['orientation'] = lambda t: np.array([0, 0, t * 0.3])
            else:
                # Rotación general
                funcs['orientation'] = lambda t: np.array([t * 0.5, 0, 0])
                
        # Aperture
        if "pulse" in desc_lower or "pulsar" in desc_lower:
            funcs['aperture'] = lambda t: 0.5 + 0.4 * np.sin(3 * t)
            
        return funcs
        
    async def start(self):
        """Iniciar simulación"""
        if self.running:
            return
            
        self.running = True
        self._simulation_task = asyncio.create_task(self._run_simulation())
        logger.info("Simulación iniciada")
        
    async def stop(self):
        """Detener simulación"""
        self.running = False
        if self._simulation_task:
            self._simulation_task.cancel()
            try:
                await self._simulation_task
            except asyncio.CancelledError:
                pass
        logger.info("Simulación detenida")
        
    async def _run_simulation(self):
        """Loop principal de simulación"""
        while self.running:
            try:
                state = self.engine.step()
                
                # Enviar estado completo
                await self.bridge.send_full_state_async(
                    state['positions'],
                    state['orientations'],
                    state['apertures'],
                    state['names']
                )
                
                await asyncio.sleep(1.0 / self.fps)
                
            except Exception as e:
                logger.error(f"Error en simulación: {e}")
                await asyncio.sleep(0.1)


async def demo_interactivo():
    """Demo interactivo mejorada"""
    controller = TrajectoryController(max_sources=100, fps=30)
    
    print("\n" + "="*60)
    print("  TRAJECTORY HUB - Sistema de Comportamientos")
    print("="*60)
    print("\nComandos disponibles:")
    print("  crear <nombre> <num> [comportamiento] [formación] - Crear macro")
    print("  trayectoria <descripción>                         - Aplicar trayectoria") 
    print("  comportamiento <nombre>                           - Cambiar comportamiento")
    print("  info [comportamiento]                             - Ver info de comportamiento")
    print("  start/stop                                        - Control de simulación")
    print("  status                                            - Ver estado")
    print("  demo                                              - Demo automática")
    print("  salir                                             - Salir")
    print("\n📌 Comportamientos disponibles:")
    print("  • flock    - Bandada natural")
    print("  • rigid    - Formación rígida")
    print("  • elastic  - Formación elástica")
    print("  • swarm    - Enjambre independiente")
    print("\n📌 Trayectorias disponibles:")
    print("  • circle r[radio]  • spiral        • lissajous")
    print("  • helix           • figure8       • random")
    print("  Añade 'rotar' para rotación")
    print("-"*60)
    
    async def handle_input():
        while True:
            try:
                cmd = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\n> "
                )
                
                parts = cmd.strip().split()
                if not parts:
                    continue
                    
                command = parts[0].lower()
                
                if command == "crear":
                    if len(parts) >= 3:
                        name = parts[1]
                        count = int(parts[2])
                        behavior = parts[3] if len(parts) > 3 else "flock"
                        formation = parts[4] if len(parts) > 4 else "circle"
                        
                        macro_id = controller.create_macro(
                            name, count, behavior, formation
                        )
                        print(f"✓ Macro '{name}' creado")
                        print(f"  • ID: {macro_id}")
                        print(f"  • {count} fuentes en formación {formation}")
                        print(f"  • Comportamiento: {behavior}")
                    else:
                        print("Uso: crear <nombre> <num> [comportamiento] [formación]")
                        
                elif command == "trayectoria":
                    if len(parts) >= 2:
                        desc = " ".join(parts[1:])
                        controller.set_trajectory(desc)
                        print(f"✓ Trayectoria aplicada: {desc}")
                    else:
                        print("Uso: trayectoria <descripción>")
                        
                elif command == "comportamiento":
                    if len(parts) >= 2:
                        behavior = parts[1]
                        controller.set_behavior(behavior)
                        print(f"✓ Comportamiento cambiado a: {behavior}")
                    else:
                        print("Uso: comportamiento <nombre>")
                        
                elif command == "info":
                    if len(parts) >= 2:
                        behavior_name = parts[1]
                        if _BEHAVIORS_AVAILABLE:
                            print(describe_behavior(behavior_name))
                        else:
                            print(f"Info de {behavior_name} no disponible")
                    else:
                        print("Comportamientos: flock, rigid, elastic, swarm")
                        
                elif command == "start":
                    await controller.start()
                    print("✓ Simulación iniciada")
                    
                elif command == "stop":
                    await controller.stop()
                    print("✓ Simulación detenida")
                    
                elif command == "status":
                    stats = controller.bridge.get_stats()
                    print(f"\n📊 Estado del sistema:")
                    print(f"  • Simulación: {'🟢 Activa' if controller.running else '🔴 Detenida'}")
                    print(f"  • Macros: {len(controller.engine._macros)}")
                    
                    if controller.engine._macros:
                        print("\n  📦 Macros activos:")
                        for mid, macro in controller.engine._macros.items():
                            print(f"    • {macro.name}:")
                            print(f"      - {len(macro.source_ids)} fuentes")
                            print(f"      - Comportamiento: {macro.behavior_name}")
                            print(f"      - Formación: {macro.formation_type}")
                    
                    print(f"\n  📡 OSC:")
                    print(f"    • Mensajes enviados: {stats['messages_sent']}")
                    print(f"    • Tasa: {stats['message_rate']:.1f} msg/s")
                    
                elif command == "demo":
                    print("\n🎬 Ejecutando demo...")
                    await run_demo(controller)
                    
                elif command == "salir":
                    await controller.stop()
                    break
                    
                else:
                    print(f"❌ Comando no reconocido: {command}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    await handle_input()
    print("\n👋 ¡Hasta luego!")


async def run_demo(controller):
    """Demo que muestra los 4 comportamientos"""
    # Detener si está corriendo
    await controller.stop()
    
    # Crear 4 demos
    demos = [
        ("Pajaros", 15, "flock", "circle", "Bandada natural"),
        ("Drones", 12, "rigid", "grid", "Formación rígida"),
        ("Medusas", 10, "elastic", "circle", "Formación elástica"),
        ("Particulas", 20, "swarm", "circle", "Enjambre independiente")
    ]
    
    print("\n🎯 Creando 4 grupos con diferentes comportamientos...")
    
    for nombre, count, behavior, formation, desc in demos:
        macro_id = controller.create_macro(nombre, count, behavior, formation)
        controller.set_trajectory("lissajous", macro_id)
        print(f"  ✓ {nombre}: {desc}")
        
    print("\n▶️  Iniciando simulación (20 segundos)...")
    await controller.start()
    
    # Esperar 20 segundos
    for i in range(20, 0, -1):
        print(f"\r  ⏱️  {i} segundos restantes...", end="")
        await asyncio.sleep(1)
        
    await controller.stop()
    print("\n✅ Demo completada!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Modo demo directo
        async def quick_demo():
            controller = TrajectoryController(max_sources=100, fps=30)
            await run_demo(controller)
            
        asyncio.run(quick_demo())
    else:
        # Modo interactivo
        asyncio.run(demo_interactivo())