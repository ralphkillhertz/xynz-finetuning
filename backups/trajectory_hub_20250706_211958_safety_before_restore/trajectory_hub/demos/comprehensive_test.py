"""
comprehensive_test.py - Test completo de todas las funcionalidades del sistema
"""
import asyncio
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine, SpatOSCBridge, OSCTarget
from trajectory_hub.core import (
    TrajectoryMovementMode, TrajectoryDisplacementMode,
    CompositeDeformer, BlendMode
)
from trajectory_hub.core.distance_controller import TrajectoryDistanceAdjuster
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveTest:
    """Test completo del sistema de trayectorias"""
    
    def __init__(self):
        self.engine = EnhancedTrajectoryEngine(max_sources=100, fps=60)
        self.bridge = SpatOSCBridge(
            targets=[OSCTarget("127.0.0.1", 9000)],
            fps=60
        )
        self.distance_adjuster = TrajectoryDistanceAdjuster(self.engine)
        self.running = False
        
        # IDs de los macros que crearemos
        self.macro_30 = None
        self.macro_10 = None
        
    async def run_test_sequence(self):
        """Ejecutar secuencia completa de tests"""
        print("\n" + "="*80)
        print("TEST COMPLETO DEL SISTEMA DE TRAYECTORIAS")
        print("="*80)
        
        # Iniciar actualización en background
        self.running = True
        update_task = asyncio.create_task(self._update_loop())
        
        try:
            # Test 1: Crear los dos macros
            await self.test_1_create_macros()
            await self._wait_and_observe(5)
            
            # Test 2: Diferentes formaciones
            await self.test_2_formations()
            await self._wait_and_observe(5)
            
            # Test 3: Trayectorias individuales
            await self.test_3_individual_trajectories()
            await self._wait_and_observe(10)
            
            # Test 4: Modos de movimiento
            await self.test_4_movement_modes()
            await self._wait_and_observe(10)
            
            # Test 5: Control de distancias
            await self.test_5_distance_control()
            await self._wait_and_observe(10)
            
            # Test 6: Deformaciones
            await self.test_6_deformations()
            await self._wait_and_observe(10)
            
            # Test 7: Interacción entre macros
            await self.test_7_macro_interaction()
            await self._wait_and_observe(10)
            
            # Test 8: Comportamientos complejos
            await self.test_8_complex_behaviors()
            await self._wait_and_observe(10)
            
            print("\n✅ TODOS LOS TESTS COMPLETADOS")
            
        finally:
            self.running = False
            update_task.cancel()
            
    async def test_1_create_macros(self):
        """Test 1: Crear dos macros con diferentes tamaños"""
        print("\n" + "-"*60)
        print("TEST 1: Creación de Macros")
        print("-"*60)
        
        # Crear macro grande (30 fuentes)
        self.macro_30 = self.engine.create_macro(
            name="Enjambre_Grande",
            source_count=30,
            formation="circle",
            spacing=1.5,
            allow_different_trajectories=True
        )
        print(f"✓ Macro 'Enjambre_Grande' creado con 30 fuentes")
        
        # Crear macro pequeño (10 fuentes)
        self.macro_10 = self.engine.create_macro(
            name="Nucleo_Pequeño",
            source_count=10,
            formation="circle",
            spacing=0.8,
            allow_different_trajectories=True
        )
        print(f"✓ Macro 'Nucleo_Pequeño' creado con 10 fuentes")
        
        # Posicionar los macros en diferentes lugares
        self._offset_macro(self.macro_30, np.array([5, 0, 0]))
        self._offset_macro(self.macro_10, np.array([-5, 0, 0]))
        
        print("\nMacros creados y posicionados:")
        print("  • Enjambre_Grande: 30 fuentes a la derecha")
        print("  • Nucleo_Pequeño: 10 fuentes a la izquierda")
        
    async def test_2_formations(self):
        """Test 2: Probar diferentes formaciones"""
        print("\n" + "-"*60)
        print("TEST 2: Formaciones")
        print("-"*60)
        
        formations = ["circle", "line", "grid", "spiral"]
        
        for formation in formations:
            print(f"\n→ Cambiando Enjambre_Grande a formación '{formation}'")
            self._change_formation(self.macro_30, formation)
            await self._wait_and_observe(3)
            
        # Volver a círculo
        self._change_formation(self.macro_30, "circle")
        print("\n✓ Formaciones probadas")
        
    async def test_3_individual_trajectories(self):
        """Test 3: Diferentes tipos de trayectorias individuales"""
        print("\n" + "-"*60)
        print("TEST 3: Trayectorias Individuales")
        print("-"*60)
        
        # Asignar trayectorias mixtas al macro grande
        print("\n→ Asignando trayectorias mixtas a Enjambre_Grande:")
        self.engine.set_mixed_trajectories(self.macro_30, [
            ("circle", 0.25),
            ("lissajous", 0.25),
            ("spiral", 0.25),
            ("helix", 0.25)
        ])
        print("  • 25% círculos")
        print("  • 25% lissajous")
        print("  • 25% espirales")
        print("  • 25% hélices")
        
        # Configurar velocidades diferentes
        macro = self.engine._macros[self.macro_30]
        source_list = list(macro.source_ids)
        
        print("\n→ Configurando velocidades variadas:")
        for i, sid in enumerate(source_list):
            shape = macro.individual_trajectories.get(sid, "circle")
            speed = 0.5 + (i / len(source_list)) * 2.0  # De 0.5 a 2.5
            
            self.engine.set_individual_trajectory(
                sid, 
                shape,
                TrajectoryMovementMode.FIX,
                movement_speed=speed
            )
            
        print("  • Velocidades de 0.5 a 2.5 rad/s")
        
        # El macro pequeño con trayectorias uniformes
        print("\n→ Núcleo_Pequeño con trayectorias uniformes (círculos)")
        for sid in self.engine._macros[self.macro_10].source_ids:
            self.engine.set_individual_trajectory(
                sid,
                "circle",
                TrajectoryMovementMode.FIX,
                movement_speed=1.0
            )
            
    async def test_4_movement_modes(self):
        """Test 4: Diferentes modos de movimiento"""
        print("\n" + "-"*60)
        print("TEST 4: Modos de Movimiento")
        print("-"*60)
        
        modes = [
            (TrajectoryMovementMode.FIX, "Velocidad fija"),
            (TrajectoryMovementMode.VIBRATION, "Vibración"),
            (TrajectoryMovementMode.RANDOM, "Aleatorio"),
            (TrajectoryMovementMode.SPIN, "Giro rápido")
        ]
        
        for mode, description in modes:
            print(f"\n→ Aplicando modo '{description}' a Núcleo_Pequeño")
            
            for sid in self.engine._macros[self.macro_10].source_ids:
                shape = self.engine._macros[self.macro_10].individual_trajectories.get(sid, "circle")
                
                if mode == TrajectoryMovementMode.VIBRATION:
                    self.engine.set_individual_trajectory(
                        sid, shape, mode,
                        vibration_frequency=3.0,
                        vibration_amplitude=0.5
                    )
                elif mode == TrajectoryMovementMode.SPIN:
                    self.engine.set_individual_trajectory(
                        sid, shape, mode,
                        spin_speed=15.0
                    )
                else:
                    self.engine.set_individual_trajectory(sid, shape, mode)
                    
            await self._wait_and_observe(3)
            
        # Volver a FIX
        for sid in self.engine._macros[self.macro_10].source_ids:
            self.engine.set_individual_trajectory(
                sid, "circle", TrajectoryMovementMode.FIX
            )
            
    async def test_5_distance_control(self):
        """Test 5: Control de distancias"""
        print("\n" + "-"*60)
        print("TEST 5: Control de Distancias")
        print("-"*60)
        
        distance_specs = [
            ("íntima", "0.5-2m"),
            ("cercana", "2-5m"),
            ("media", "4-10m"),
            ("lejana", "8-20m"),
            ("entre 3 y 15 metros", "3-15m"),
            ("envolvente", "1-15m amplio")
        ]
        
        for spec, description in distance_specs:
            print(f"\n→ Ajustando Enjambre_Grande a distancia '{spec}' ({description})")
            self.distance_adjuster.adjust_macro_distance(self.macro_30, spec)
            
            # Mostrar distancias actuales
            distances = self.distance_adjuster.get_current_distances(self.macro_30)
            print(f"  • Resultado: {distances['min']:.1f}m - {distances['max']:.1f}m (media: {distances['mean']:.1f}m)")
            
            await self._wait_and_observe(3)
            
        # Dejar en distancia media
        self.distance_adjuster.adjust_macro_distance(self.macro_30, "media")
        
    async def test_6_deformations(self):
        """Test 6: Sistema de deformaciones"""
        print("\n" + "-"*60)
        print("TEST 6: Deformaciones")
        print("-"*60)
        
        # Establecer trayectorias base para los macros
        def circular_trajectory(t):
            return np.array([
                5 * np.cos(t * 0.3),
                5 * np.sin(t * 0.3),
                0
            ])
            
        def figure8_trajectory(t):
            return np.array([
                3 * np.sin(t * 0.5),
                3 * np.sin(t * 0.5) * np.cos(t * 0.5),
                0
            ])
            
        print("\n→ Estableciendo trayectorias macro")
        self.engine.set_macro_trajectory(self.macro_30, circular_trajectory, enable_deformation=True)
        self.engine.set_macro_trajectory(self.macro_10, figure8_trajectory, enable_deformation=True)
        self.engine.enable_deformation(self.macro_30, True)
        self.engine.enable_deformation(self.macro_10, True)
        
        # Test 6.1: Respiración
        print("\n→ Aplicando respiración")
        self.engine.apply_breathing(period=4.0, amplitude=1.0, macro_id=self.macro_30)
        self.engine.apply_breathing(period=3.0, amplitude=0.5, macro_id=self.macro_10)
        await self._wait_and_observe(5)
        
        # Test 6.2: Campos de fuerza
        print("\n→ Añadiendo campos de fuerza")
        self.engine.apply_force_field(
            position=np.array([0, 0, 0]),
            strength=-3.0,  # Repulsor
            radius=4.0,
            falloff="smooth",
            macro_id=self.macro_30
        )
        
        self.engine.apply_force_field(
            position=np.array([3, 3, 0]),
            strength=2.0,  # Atractor
            radius=5.0,
            falloff="inverse_square",
            macro_id=self.macro_10
        )
        await self._wait_and_observe(5)
        
        # Test 6.3: Deformación caótica
        print("\n→ Añadiendo caos sutil")
        deformer_30 = self.engine.get_deformer(self.macro_30)
        chaotic = deformer_30.get_deformer('chaotic')
        chaotic.system_type = "lorenz"
        chaotic.scale = np.array([0.1, 0.1, 0.05])
        chaotic.speed = 0.3
        deformer_30.enable_deformer('chaotic', weight=0.3)
        await self._wait_and_observe(5)
        
    async def test_7_macro_interaction(self):
        """Test 7: Interacción entre macros"""
        print("\n" + "-"*60)
        print("TEST 7: Interacción entre Macros")
        print("-"*60)
        
        print("\n→ Configurando el macro pequeño para seguir al grande")
        
        # Obtener referencia al macro grande
        macro_30_center = self.engine._macros[self.macro_30].center_source_id
        
        # Crear función que sigue al centro del macro grande
        def follow_large_macro(t):
            if macro_30_center is not None and macro_30_center < len(self.engine._positions):
                target_pos = self.engine._positions[macro_30_center].copy()
                # Añadir offset y movimiento propio
                offset = np.array([3 * np.cos(t), 3 * np.sin(t), 1])
                return target_pos + offset
            return np.array([0, 0, 0])
            
        self.engine.set_macro_trajectory(self.macro_10, follow_large_macro)
        print("  • Núcleo_Pequeño ahora orbita alrededor de Enjambre_Grande")
        
        await self._wait_and_observe(8)
        
    async def test_8_complex_behaviors(self):
        """Test 8: Comportamientos complejos y combinados"""
        print("\n" + "-"*60)
        print("TEST 8: Comportamientos Complejos")
        print("-"*60)
        
        # Test 8.1: Cambiar comportamientos
        print("\n→ Cambiando comportamientos de los macros")
        behaviors = [
            ("flock", "Bandada natural"),
            ("rigid", "Formación rígida"),
            ("elastic", "Formación elástica"),
            ("swarm", "Enjambre independiente")
        ]
        
        for behavior, description in behaviors:
            print(f"\n  • Enjambre_Grande → {description}")
            self.engine.set_macro_behavior(self.macro_30, behavior)
            await self._wait_and_observe(3)
            
        # Test 8.2: Concentración y dispersión
        print("\n→ Probando concentración y dispersión")
        print("  • Concentrando Enjambre_Grande...")
        self.engine.trigger_concentration(self.macro_30, duration=2.0)
        await self._wait_and_observe(3)
        
        print("  • Dispersando...")
        self.engine.trigger_dispersion(self.macro_30, duration=2.0)
        await self._wait_and_observe(3)
        
        # Test 8.3: Movimientos semánticos
        print("\n→ Aplicando movimientos semánticos")
        semantic_movements = [
            ("pájaro nervioso", 4),
            ("medusa flotante", 4),
            ("órbita cuántica", 4)
        ]
        
        for movement, duration in semantic_movements:
            print(f"  • Aplicando '{movement}' a Núcleo_Pequeño")
            self.engine.apply_semantic_movement(self.macro_10, movement)
            await self._wait_and_observe(duration)
            
        # Test 8.4: Composición final
        print("\n→ Composición final: todo junto")
        print("  • Enjambre_Grande: bandada con respiración y caos")
        print("  • Núcleo_Pequeño: órbita cuántica siguiendo al grande")
        print("  • Distancias optimizadas para percepción")
        
        # Configuración final óptima
        self.engine.set_macro_behavior(self.macro_30, "flock")
        self.engine.apply_semantic_movement(self.macro_10, "órbita cuántica")
        self.distance_adjuster.adjust_macro_distance(self.macro_30, "media")
        self.distance_adjuster.adjust_macro_distance(self.macro_10, "cercana")
        
        await self._wait_and_observe(10)
        
    # Métodos auxiliares
    
    def _offset_macro(self, macro_id: str, offset: np.ndarray):
        """Desplazar todas las fuentes de un macro"""
        macro = self.engine._macros[macro_id]
        for sid in macro.source_ids:
            if sid in self.engine._source_motions:
                self.engine._source_motions[sid].state.position += offset
                
    def _change_formation(self, macro_id: str, formation: str):
        """Cambiar formación de un macro (simplificado)"""
        macro = self.engine._macros[macro_id]
        macro.formation_type = formation
        # Re-inicializar posiciones
        self.engine._initialize_macro_formation(macro_id)
        
    async def _wait_and_observe(self, seconds: float):
        """Esperar y mostrar progreso"""
        print(f"\n⏱️  Observando por {seconds} segundos...", end="", flush=True)
        for i in range(int(seconds)):
            await asyncio.sleep(1)
            print(".", end="", flush=True)
        print(" ✓")
        
    async def _update_loop(self):
        """Loop de actualización en background"""
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
                
    async def interactive_menu(self):
        """Menú interactivo para control manual durante el test"""
        print("\n" + "="*60)
        print("MODO INTERACTIVO")
        print("="*60)
        print("\nComandos disponibles durante el test:")
        print("  p - Pausar/Reanudar")
        print("  d - Cambiar distancias")
        print("  c - Cambiar comportamiento")
        print("  i - Ver información")
        print("  s - Saltar al siguiente test")
        print("  q - Salir")
        print("-"*60)
        
        # Aquí iría la lógica del menú interactivo
        # Por ahora, ejecutamos la secuencia completa
        await self.run_test_sequence()


async def main():
    """Función principal"""
    test = ComprehensiveTest()
    
    print("\n🎯 TEST COMPLETO DEL SISTEMA DE TRAYECTORIAS")
    print("\nEste test ejercitará todas las funcionalidades:")
    print("1. Creación de macros (30 y 10 fuentes)")
    print("2. Formaciones (círculo, línea, grid, espiral)")
    print("3. Trayectorias individuales mixtas")
    print("4. Modos de movimiento (fix, vibration, random, spin)")
    print("5. Control de distancias (íntima a lejana)")
    print("6. Deformaciones (respiración, fuerzas, caos)")
    print("7. Interacción entre macros")
    print("8. Comportamientos complejos")
    
    print("\n¿Comenzar el test? (s/n): ", end="")
    
    try:
        # Para modo automático, asumimos 's'
        # En modo interactivo real, esperaríamos input del usuario
        await test.interactive_menu()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por usuario")
    except Exception as e:
        logger.error(f"Error en test: {e}")
        raise
        
    print("\n✨ Test finalizado")


if __name__ == "__main__":
    asyncio.run(main())