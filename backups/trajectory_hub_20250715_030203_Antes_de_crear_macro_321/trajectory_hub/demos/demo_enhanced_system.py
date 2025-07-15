"""
demo_enhanced_system.py - Demostración de las nuevas capacidades del sistema de movimientos
"""
import asyncio
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import TrajectoryMovementMode, TrajectoryDisplacementMode, TrajectoryDisplacementMode, TrajectoryDisplacementMode
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDemo:
    """Demos que muestran las nuevas capacidades del sistema"""
    
    def __init__(self):
        self.engine = EnhancedTrajectoryEngine(max_sources=100, fps=60)
        self.bridge = SpatOSCBridge(
            targets=[OSCTarget("127.0.0.1", 9000)],
            fps=60
        )
        self.running = False
        
    async def demo_1_individual_trajectories(self):
        """Demo 1: Diferentes formas de trayectoria en un mismo macro"""
        print("\n" + "="*60)
        print("DEMO 1: Trayectorias Individuales Diferentes")
        print("="*60)
        
        # Crear macro con trayectorias mixtas
        macro_id = self.engine.create_macro(
            "Formas_Mixtas",
            source_count=12,
            formation="circle",
            spacing=4.0,
            allow_different_trajectories=True
        )
        
        # Asignar diferentes formas
        self.engine.set_mixed_trajectories(macro_id, [
            ("circle", 0.25),      # 25% círculos
            ("lissajous", 0.25),   # 25% lissajous
            ("spiral", 0.25),      # 25% espirales
            ("helix", 0.25)        # 25% hélices
        ])
        
        # Configurar diferentes modos de movimiento
        macro = self.engine._macros[macro_id]
        source_list = list(macro.source_ids)
        
        # Primera mitad: movimiento fijo
        for i in range(len(source_list) // 2):
            self.engine.set_individual_trajectory(
                source_list[i],
                macro.individual_trajectories[source_list[i]],
                TrajectoryMovementMode.FIX,
                movement_movement_movement_speed=1.0 + i * 0.1  # Velocidades ligeramente diferentes
            )
            
        # Segunda mitad: movimiento vibratorio
        for i in range(len(source_list) // 2, len(source_list)):
            self.engine.set_individual_trajectory(
                source_list[i],
                macro.individual_trajectories[source_list[i]],
                TrajectoryMovementMode.VIBRATION,
                vibration_frequency=2.0 + i * 0.2,
                vibration_amplitude=0.3
            )
            
        print("✓ 12 fuentes con 4 formas diferentes")
        print("✓ Mitad con movimiento constante, mitad vibrando")
        
        await self._run_demo(10)
        
    async def demo_2_movement_layers(self):
        """Demo 2: Capas de movimiento combinadas"""
        print("\n" + "="*60)
        print("DEMO 2: Composición de Movimientos")
        print("="*60)
        
        # Crear macro base
        macro_id = self.engine.create_macro(
            "Capas_Movimiento",
            source_count=8,
            formation="circle",
            spacing=2.0
        )
        
        # 1. Establecer trayectoria del macro (círculo grande)
        def macro_trajectory(t):
            return np.array([
                10 * np.cos(t * 0.2),
                10 * np.sin(t * 0.2),
                2 * np.sin(t * 0.3)
            ])
            
        self.engine.set_macro_trajectory(macro_id, macro_trajectory)
        
        # 2. Cada fuente tiene su propia trayectoria (círculo pequeño)
        macro = self.engine._macros[macro_id]
        for sid in macro.source_ids:
            self.engine.set_individual_trajectory(
                sid,
                "circle",
                TrajectoryMovementMode.FIX,
                movement_speed=2.0
            )
            
        # 3. Añadir modulación de orientación
        for sid in macro.source_ids:
            motion = self.engine._source_motions[sid]
            orientation = motion.components['orientation_modulation']
            orientation.set_modulation(
                yaw=lambda t: np.sin(t * 3) * 0.5,
                pitch=lambda t: np.sin(t * 2) * 0.3
            )
            
        print("✓ Macro siguiendo órbita grande")
        print("✓ Cada fuente girando en círculo pequeño")
        print("✓ Orientación modulada independientemente")
        
        await self._run_demo(15)
        
    async def demo_3_concentration_dispersion(self):
        """Demo 3: Concentración y dispersión"""
        print("\n" + "="*60)
        print("DEMO 3: Concentración y Dispersión")
        print("="*60)
        
        # Crear dos macros
        macro1 = self.engine.create_macro(
            "Grupo_A",
            source_count=10,
            formation="circle",
            spacing=3.0
        )
        
        macro2 = self.engine.create_macro(
            "Grupo_B", 
            source_count=10,
            formation="grid",
            spacing=2.0
        )
        
        # Configurar movimiento inicial
        for macro_id in [macro1, macro2]:
            macro = self.engine._macros[macro_id]
            for sid in macro.source_ids:
                self.engine.set_individual_trajectory(
                    sid,
                    "spiral",
                    TrajectoryMovementMode.FIX
                )
                
        print("✓ Dos grupos creados")
        print("\nSecuencia:")
        print("1. Movimiento normal (3s)")
        print("2. Concentración en centro (2s)")
        print("3. Pausa concentrados (2s)")
        print("4. Dispersión (2s)")
        print("5. Movimiento normal (3s)")
        
        # Ejecutar secuencia
        self.running = True
        
        # 1. Movimiento normal
        await self._run_for_duration(3)
        
        # 2. Concentrar ambos grupos
        print("\n→ Concentrando...")
        self.engine.trigger_concentration(macro1, duration=2.0)
        self.engine.trigger_concentration(macro2, duration=2.0)
        await self._run_for_duration(2)
        
        # 3. Pausa
        print("→ Mantener concentración...")
        await self._run_for_duration(2)
        
        # 4. Dispersar
        print("→ Dispersando...")
        self.engine.trigger_dispersion(macro1, duration=2.0)
        self.engine.trigger_dispersion(macro2, duration=2.0)
        await self._run_for_duration(2)
        
        # 5. Movimiento normal
        print("→ Vuelta a movimiento normal")
        await self._run_for_duration(3)
        
        self.running = False
        
    async def demo_4_semantic_control(self):
        """Demo 4: Control semántico"""
        print("\n" + "="*60)
        print("DEMO 4: Control Semántico")
        print("="*60)
        
        # Crear macro
        macro_id = self.engine.create_macro(
            "Criaturas",
            source_count=15,
            formation="circle",
            spacing=3.0
        )
        
        # Secuencia de comportamientos semánticos
        behaviors = [
            ("pájaro nervioso", 5),
            ("medusa flotante", 5),
            ("órbita cuántica", 5)
        ]
        
        print("✓ 15 fuentes creadas")
        print("\nSecuencia de comportamientos:")
        for behavior, duration in behaviors:
            print(f"  • {behavior} ({duration}s)")
            
        self.running = True
        
        for behavior, duration in behaviors:
            print(f"\n→ Aplicando: {behavior}")
            self.engine.apply_semantic_movement(macro_id, behavior)
            await self._run_for_duration(duration)
            
        self.running = False
        
    async def demo_5_complex_composition(self):
        """Demo 5: Composición compleja - El enjambre que respira"""
        print("\n" + "="*60)
        print("DEMO 5: Composición Compleja - Enjambre que Respira")
        print("="*60)
        
        # Crear macro principal
        macro_id = self.engine.create_macro(
            "Enjambre",
            source_count=20,
            formation="circle",
            spacing=2.0
        )
        
        # Trayectoria del macro: movimiento en 8
        def macro_trajectory(t):
            return np.array([
                5 * np.sin(t * 0.3),
                5 * np.sin(t * 0.3) * np.cos(t * 0.3),
                2 * np.sin(t * 0.2)
            ])
            
        self.engine.set_macro_trajectory(macro_id, macro_trajectory)
        
        # Configurar cada fuente
        macro = self.engine._macros[macro_id]
        source_list = list(macro.source_ids)
        
        for i, sid in enumerate(source_list):
            # Trayectorias variadas
            shapes = ["circle", "spiral", "lissajous"]
            shape = shapes[i % len(shapes)]
            
            self.engine.set_individual_trajectory(
                sid,
                shape,
                TrajectoryMovementMode.FIX,
                movement_movement_movement_speed=1.0 + (i % 3) * 0.5
            )
            
            # Modulación de orientación única por fuente
            motion = self.engine._source_motions[sid]
            orientation = motion.components['orientation_modulation']
            
            # Cada fuente tiene su propia frecuencia
            freq_offset = i * 0.1
            orientation.set_modulation(
                yaw=lambda t, f=freq_offset: np.sin(t * (2 + f)) * 0.3,
                pitch=lambda t, f=freq_offset: np.sin(t * (1.5 + f)) * 0.2,
                roll=lambda t, f=freq_offset: np.sin(t * (1 + f)) * 0.1
            )
            
            # Configurar transform para que siga al macro con variación
            transform = motion.components['trajectory_transform']
            transform.set_displacement_mode(
                TrajectoryDisplacementMode.MIX,
                macro_weight=0.8,
                random_weight=0.2,
                random_factor_range=0.5
            )
            
        print("✓ Enjambre de 20 fuentes configurado:")
        print("  • Macro en movimiento figura-8")
        print("  • 3 tipos de trayectorias individuales")
        print("  • Cada fuente con modulación única")
        print("  • Movimiento con componente aleatorio")
        
        # Añadir "respiración" periódica
        print("\n→ Iniciando con respiración cada 5 segundos...")
        
        self.running = True
        
        for cycle in range(3):
            print(f"\nCiclo {cycle + 1}:")
            
            # Movimiento normal
            print("  • Movimiento normal...")
            await self._run_for_duration(4)
            
            # Inhalar (concentrar)
            print("  • Inhalando...")
            self.engine.trigger_concentration(
                macro_id,
                point=None,  # Centro del macro
                duration=1.0
            )
            await self._run_for_duration(1.5)
            
            # Exhalar (dispersar)
            print("  • Exhalando...")
            self.engine.trigger_dispersion(macro_id, duration=1.0)
            await self._run_for_duration(1.5)
            
        self.running = False
        
    async def _run_demo(self, duration: float):
        """Ejecutar demo por duración específica"""
        self.running = True
        await self._run_for_duration(duration)
        self.running = False
        
    async def _run_for_duration(self, duration: float):
        """Ejecutar simulación por tiempo específico"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < duration:
            if not self.running:
                break
                
            # Step del engine
            state = self.engine.step()
            
            # Enviar por OSC
            await self.bridge.send_full_state_async(
                state['positions'],
                state['orientations'],
                state['apertures'],
                state['names']
            )
            
            # Esperar para mantener FPS
            await asyncio.sleep(1.0 / self.engine.fps)
            
    async def run_all_demos(self):
        """Ejecutar todas las demos en secuencia"""
        demos = [
            self.demo_1_individual_trajectories,
            self.demo_2_movement_layers,
            self.demo_3_concentration_dispersion,
            self.demo_4_semantic_control,
            self.demo_5_complex_composition
        ]
        
        print("\n" + "="*60)
        print("SISTEMA DE MOVIMIENTOS MEJORADO - DEMOS")
        print("="*60)
        print("\nEjecutando 5 demos que muestran las nuevas capacidades:")
        print("1. Trayectorias individuales diferentes")
        print("2. Composición de capas de movimiento")
        print("3. Concentración y dispersión")
        print("4. Control semántico")
        print("5. Composición compleja")
        
        for i, demo in enumerate(demos, 1):
            print(f"\n[Demo {i}/5]")
            await demo()
            
            if i < len(demos):
                print("\n⏸️  Pausa entre demos...")
                await asyncio.sleep(2)
                
        print("\n" + "="*60)
        print("✅ TODAS LAS DEMOS COMPLETADAS")
        print("="*60)
        
    async def interactive_mode(self):
        """Modo interactivo para experimentar"""
        print("\n" + "="*60)
        print("MODO INTERACTIVO - Sistema de Movimientos Mejorado")
        print("="*60)
        
        # Crear macro inicial
        macro_id = self.engine.create_macro(
            "Experimental",
            source_count=10,
            formation="circle",
            spacing=3.0,
            allow_different_trajectories=True
        )
        
        print("\nComandos disponibles:")
        print("  1. Cambiar formas de trayectoria")
        print("  2. Cambiar modos de movimiento")
        print("  3. Aplicar comportamiento semántico")
        print("  4. Concentrar/Dispersar")
        print("  5. Debug de una fuente")
        print("  6. Salir")
        
        self.running = True
        
        # Task para actualización continua
        update_task = asyncio.create_task(self._continuous_update())
        
        while True:
            try:
                cmd = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nComando (1-6): "
                )
                
                if cmd == "1":
                    print("\nFormas disponibles: circle, spiral, lissajous, helix, figure8")
                    distribution = []
                    
                    for shape in ["circle", "spiral", "lissajous"]:
                        pct = float(input(f"Porcentaje de {shape} (0-1): "))
                        distribution.append((shape, pct))
                        
                    self.engine.set_mixed_trajectories(macro_id, distribution)
                    print("✓ Formas actualizadas")
                    
                elif cmd == "2":
                    print("\nModos: fix, random, vibration, spin")
                    mode_str = input("Modo: ")
                    mode_map = {
                        "fix": TrajectoryMovementMode.FIX,
                        "random": TrajectoryMovementMode.RANDOM,
                        "vibration": TrajectoryMovementMode.VIBRATION,
                        "spin": TrajectoryMovementMode.SPIN
                    }
                    
                    if mode_str in mode_map:
                        macro = self.engine._macros[macro_id]
                        for sid in macro.source_ids:
                            shape = macro.individual_trajectories.get(sid, "circle")
                            self.engine.set_individual_trajectory(
                                sid, shape, mode_map[mode_str]
                            )
                        print("✓ Modo actualizado")
                        
                elif cmd == "3":
                    print("\nComportamientos: pájaro nervioso, medusa flotante, órbita cuántica")
                    behavior = input("Comportamiento: ")
                    self.engine.apply_semantic_movement(macro_id, behavior)
                    print("✓ Comportamiento aplicado")
                    
                elif cmd == "4":
                    action = input("¿Concentrar o dispersar? (c/d): ")
                    if action == "c":
                        self.engine.trigger_concentration(macro_id, duration=2.0)
                        print("✓ Concentrando...")
                    else:
                        self.engine.trigger_dispersion(macro_id, duration=2.0)
                        print("✓ Dispersando...")
                        
                elif cmd == "5":
                    sid = int(input("ID de fuente: "))
                    info = self.engine.get_debug_info(sid)
                    print(f"\nDebug info para fuente {sid}:")
                    import json
                    print(json.dumps(info, indent=2))
                    
                elif cmd == "6":
                    break
                    
            except Exception as e:
                print(f"Error: {e}")
                
        self.running = False
        update_task.cancel()
        
    async def _continuous_update(self):
        """Actualización continua en background"""
        while self.running:
            try:
                state = self.engine.step()
                await self.bridge.send_full_state_async(
                    state['positions'],
                    state['orientations'],
                    state['apertures'],
                    state['names']
                )
                await asyncio.sleep(1.0 / self.engine.fps)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en actualización: {e}")


async def main():
    """Función principal"""
    demo = EnhancedDemo()
    
    print("\n¿Qué modo ejecutar?")
    print("1. Todas las demos")
    print("2. Demo específica")
    print("3. Modo interactivo")
    
    choice = input("\nElección (1-3): ")
    
    if choice == "1":
        await demo.run_all_demos()
        
    elif choice == "2":
        print("\nDemos disponibles:")
        print("1. Trayectorias individuales diferentes")
        print("2. Capas de movimiento")
        print("3. Concentración/Dispersión")
        print("4. Control semántico")
        print("5. Composición compleja")
        
        demo_num = int(input("\nNúmero de demo: "))
        demos = [
            demo.demo_1_individual_trajectories,
            demo.demo_2_movement_layers,
            demo.demo_3_concentration_dispersion,
            demo.demo_4_semantic_control,
            demo.demo_5_complex_composition
        ]
        
        if 1 <= demo_num <= len(demos):
            await demos[demo_num - 1]()
            
    elif choice == "3":
        await demo.interactive_mode()
        
    print("\n👋 ¡Hasta luego!")


if __name__ == "__main__":
    asyncio.run(main())