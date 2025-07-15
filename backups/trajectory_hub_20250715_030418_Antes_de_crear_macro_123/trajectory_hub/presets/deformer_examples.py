"""
deformer_examples.py - Ejemplos artísticos de uso de los deformadores
"""
import numpy as np
import asyncio
from trajectory_hub.core.trajectory_deformers import (
    CompositeDeformer, ForceFieldDeformation, WaveDeformation,
    ChaoticDeformation, GestureDeformation, BlendMode
)
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import TrajectoryMovementMode
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeformerShowcase:
    """Ejemplos de uso artístico de los deformadores"""
    
    def __init__(self):
        self.engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
        self.deformer = CompositeDeformer()
        
    def example_1_magnetic_field(self):
        """Campo magnético con atractores y repulsores"""
        print("\n" + "="*60)
        print("EJEMPLO 1: Campo Magnético")
        print("="*60)
        
        # Obtener deformador de campo de fuerza
        force_field = self.deformer.get_deformer('force_field')
        
        # Crear atractores en los vértices de un triángulo
        triangle_points = [
            np.array([5, 0, 0]),
            np.array([-2.5, 4.33, 0]),
            np.array([-2.5, -4.33, 0])
        ]
        
        # Atractores que rotan
        for i, point in enumerate(triangle_points):
            def rotating_attractor(t, center=point, phase=i*2*np.pi/3):
                angle = t * 0.5 + phase
                return center * np.cos(angle)
                
            force_field.add_attractor(
                position=point,
                strength=3.0 if i % 2 == 0 else -2.0,  # Alternar atracción/repulsión
                radius=8.0,
                falloff="smooth",
                is_dynamic=True,
                trajectory=rotating_attractor
            )
            
        # Añadir vórtice central
        force_field.create_vortex(
            center=np.array([0, 0, 0]),
            axis=np.array([0, 0, 1]),
            strength=0.5,
            radius=10.0
        )
        
        # Activar deformador
        self.deformer.enable_deformer('force_field', weight=0.3)
        
        # Crear trayectoria base (círculo)
        def base_trajectory(t):
            return np.array([
                8 * np.cos(t),
                8 * np.sin(t),
                0
            ])
            
        return base_trajectory
        
    def example_2_breathing_ocean(self):
        """Ondas que simulan respiración oceánica"""
        print("\n" + "="*60)
        print("EJEMPLO 2: Océano que Respira")
        print("="*60)
        
        wave_deformer = self.deformer.get_deformer('wave')
        
        # Onda principal de respiración
        wave_deformer.add_breathing_wave(
            period=4.0,      # Respiración cada 4 segundos
            amplitude=2.0    # Expansión de 2 unidades
        )
        
        # Ondas secundarias para textura
        for i in range(3):
            wave_deformer.add_wave(
                frequency=0.5 + i * 0.3,
                amplitude=0.3 / (i + 1),
                wavelength=2.0 + i,
                direction="radial",
                phase=i * np.pi / 3
            )
            
        # Onda viajera tangencial
        wave_deformer.add_traveling_wave(
            speed=2.0,
            amplitude=0.5,
            wavelength=3.0
        )
        
        # Activar con modo de interferencia
        wave_deformer.interference_mode = "linear"
        self.deformer.enable_deformer('wave', weight=1.0)
        
        # Trayectoria base (espiral)
        def base_trajectory(t):
            r = 5 + 0.5 * t
            return np.array([
                r * np.cos(t * 2),
                r * np.sin(t * 2),
                0.3 * t
            ])
            
        return base_trajectory
        
    def example_3_chaotic_butterfly(self):
        """Atractor de Lorenz creando vuelo de mariposa"""
        print("\n" + "="*60)
        print("EJEMPLO 3: Mariposa Caótica")
        print("="*60)
        
        chaotic = self.deformer.get_deformer('chaotic')
        
        # Configurar sistema de Lorenz
        chaotic.system_type = "lorenz"
        chaotic.set_parameters(sigma=10, rho=28, beta=8/3)
        
        # Escala diferente por eje para forma de mariposa
        chaotic.scale = np.array([0.15, 0.1, 0.2])
        chaotic.speed = 0.5  # Velocidad media
        chaotic.smoothing = 0.15  # Suavizado moderado
        
        self.deformer.enable_deformer('chaotic', weight=1.0)
        
        # Trayectoria base (figura 8)
        def base_trajectory(t):
            return np.array([
                6 * np.sin(t),
                3 * np.sin(t) * np.cos(t),
                0
            ])
            
        return base_trajectory
        
    def example_4_calligraphy_gesture(self):
        """Gesto caligráfico grabado"""
        print("\n" + "="*60)
        print("EJEMPLO 4: Caligrafía Espacial")
        print("="*60)
        
        gesture = self.deformer.get_deformer('gesture')
        
        # Crear gesto caligráfico parametrizado
        def calligraphy_stroke(t):
            # Trazo elegante con variación
            return np.array([
                2 * np.sin(t * 2) * (1 - t/4),
                3 * np.cos(t * 3) * np.exp(-t/4),
                0.5 * np.sin(t * 5)
            ])
            
        gesture.add_parametric_gesture(
            func=calligraphy_stroke,
            duration=4.0,
            samples=200,
            loop=True,
            weight=1.0
        )
        
        # Añadir gesto lemniscata
        gesture.add_lemniscate_gesture(scale=1.5, duration=3.0)
        
        # Variación de velocidad
        gesture.playback_speed = 0.8
        
        self.deformer.enable_deformer('gesture', weight=0.7)
        
        # Trayectoria base simple
        def base_trajectory(t):
            return np.array([
                4 * np.cos(t * 0.5),
                4 * np.sin(t * 0.5),
                0
            ])
            
        return base_trajectory
        
    def example_5_composite_ecosystem(self):
        """Ecosistema complejo con todos los deformadores"""
        print("\n" + "="*60)
        print("EJEMPLO 5: Ecosistema Vivo")
        print("="*60)
        
        # 1. Campo de fuerza: Corrientes submarinas
        force_field = self.deformer.get_deformer('force_field')
        
        # Corriente circular principal
        def ocean_current(point, time):
            # Corriente que gira alrededor del origen
            r = np.sqrt(point[0]**2 + point[1]**2)
            if r > 0.1 and r < 15:
                theta = np.arctan2(point[1], point[0])
                tangent = np.array([-np.sin(theta), np.cos(theta), 0])
                strength = 0.3 * (1 - r/15) * np.sin(time * 0.2)
                return tangent * strength
            return np.zeros(3)
            
        force_field.set_ambient_force(ocean_current)
        
        # Zonas de turbulencia (repulsores suaves)
        for i in range(3):
            angle = i * 2 * np.pi / 3
            pos = 7 * np.array([np.cos(angle), np.sin(angle), 0])
            force_field.add_attractor(
                position=pos,
                strength=-1.5,
                radius=3.0,
                falloff="smooth"
            )
            
        # 2. Ondas: Pulso vital
        wave = self.deformer.get_deformer('wave')
        
        # Latido principal
        wave.add_breathing_wave(period=3.0, amplitude=0.8)
        
        # Microondas de superficie
        for freq in [2.1, 3.7, 5.3]:
            wave.add_wave(
                frequency=freq,
                amplitude=0.1,
                wavelength=1.5,
                direction="normal",
                damping=0.05
            )
            
        # 3. Caos: Comportamiento impredecible
        chaotic = self.deformer.get_deformer('chaotic')
        chaotic.system_type = "rossler"
        chaotic.scale = np.array([0.05, 0.05, 0.1])
        chaotic.speed = 0.3
        
        # 4. Gesto: Patrón de migración
        gesture = self.deformer.get_deformer('gesture')
        
        # Patrón de migración en espiral
        def migration_pattern(t):
            phase = t * 2 * np.pi / 8  # Ciclo de 8 segundos
            r = 2 + 0.5 * np.sin(phase * 3)
            return np.array([
                r * np.cos(phase),
                r * np.sin(phase),
                0.3 * np.sin(phase * 2)
            ])
            
        gesture.add_parametric_gesture(
            func=migration_pattern,
            duration=8.0,
            loop=True
        )
        
        # Activar todos con pesos balanceados
        self.deformer.enable_deformer('force_field', weight=0.4)
        self.deformer.enable_deformer('wave', weight=0.3)
        self.deformer.enable_deformer('chaotic', weight=0.2)
        self.deformer.enable_deformer('gesture', weight=0.3)
        
        # Modo de mezcla promediado para suavidad
        self.deformer.global_blend_mode = BlendMode.AVERAGE
        
        # Trayectoria base: órbita elíptica
        def base_trajectory(t):
            return np.array([
                10 * np.cos(t * 0.3),
                6 * np.sin(t * 0.3),
                2 * np.sin(t * 0.6)
            ])
            
        return base_trajectory
        
    async def visualize_deformation(self, base_trajectory, duration: float = 20.0):
        """Visualizar deformación en tiempo real"""
        print("\nVisualizando deformación...")
        print("Presiona Ctrl+C para detener\n")
        
        # Crear macro para visualización
        macro_id = self.engine.create_macro(
            "Deformación",
            source_count=1,
            formation="circle"
        )
        
        # Configurar trayectoria con deformación
        def deformed_trajectory(t):
            return self.deformer.deform_trajectory(base_trajectory, t)
            
        self.engine.set_macro_trajectory(macro_id, deformed_trajectory)
        
        # Simular
        start_time = asyncio.get_event_loop().time()
        
        try:
            while asyncio.get_event_loop().time() - start_time < duration:
                state = self.engine.step()
                
                # Aquí normalmente enviarías por OSC
                # Por ahora, solo mostrar posición
                pos = state['positions'][0]
                print(f"\rPosición: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]", end="")
                
                await asyncio.sleep(1.0 / self.engine.fps)
                
        except KeyboardInterrupt:
            print("\n\nDetenido por usuario")
            
        print("\n✓ Visualización completada")
        
    async def run_all_examples(self):
        """Ejecutar todos los ejemplos"""
        examples = [
            (self.example_1_magnetic_field, "Campo Magnético"),
            (self.example_2_breathing_ocean, "Océano que Respira"),
            (self.example_3_chaotic_butterfly, "Mariposa Caótica"),
            (self.example_4_calligraphy_gesture, "Caligrafía Espacial"),
            (self.example_5_composite_ecosystem, "Ecosistema Vivo")
        ]
        
        for example_func, name in examples:
            # Limpiar deformadores previos
            self.deformer.active_deformers.clear()
            
            # Configurar ejemplo
            base_trajectory = example_func()
            
            # Visualizar
            await self.visualize_deformation(base_trajectory, duration=10.0)
            
            # Pausa entre ejemplos
            await asyncio.sleep(2)
            
    def create_artistic_preset(self, name: str) -> Dict:
        """Crear presets artísticos predefinidos"""
        presets = {
            "underwater_dream": lambda: self._setup_underwater_dream(),
            "cosmic_dance": lambda: self._setup_cosmic_dance(),
            "organic_growth": lambda: self._setup_organic_growth(),
            "digital_glitch": lambda: self._setup_digital_glitch()
        }
        
        if name in presets:
            presets[name]()
            return self.deformer.create_preset(name)
            
    def _setup_underwater_dream(self):
        """Preset: Sueño submarino"""
        # Limpiar
        self.deformer.active_deformers.clear()
        
        # Ondas suaves
        wave = self.deformer.get_deformer('wave')
        wave.waves.clear()
        wave.add_breathing_wave(period=5.0, amplitude=1.2)
        wave.add_wave(frequency=0.3, amplitude=0.4, wavelength=4.0, direction="radial")
        
        # Campo de corrientes suaves
        force = self.deformer.get_deformer('force_field')
        force.attractors.clear()
        
        def gentle_current(point, time):
            return np.array([
                0.2 * np.sin(time * 0.1),
                0.1 * np.cos(time * 0.15),
                0.05 * np.sin(time * 0.2)
            ])
        force.set_ambient_force(gentle_current)
        
        # Activar
        self.deformer.enable_deformer('wave', 0.7)
        self.deformer.enable_deformer('force_field', 0.3)
        
    def _setup_cosmic_dance(self):
        """Preset: Danza cósmica"""
        self.deformer.active_deformers.clear()
        
        # Atractores orbitales
        force = self.deformer.get_deformer('force_field')
        force.attractors.clear()
        
        # Sistema de 3 cuerpos
        for i in range(3):
            angle = i * 2 * np.pi / 3
            
            def orbiting_body(t, phase=angle):
                return 6 * np.array([
                    np.cos(t * 0.7 + phase),
                    np.sin(t * 0.7 + phase),
                    np.sin(t * 0.3)
                ])
                
            force.add_attractor(
                position=np.zeros(3),
                strength=2.0,
                radius=8.0,
                falloff="inverse_square",
                is_dynamic=True,
                trajectory=orbiting_body
            )
            
        # Caos sutil
        chaotic = self.deformer.get_deformer('chaotic')
        chaotic.system_type = "lorenz"
        chaotic.scale = np.array([0.08, 0.08, 0.05])
        chaotic.speed = 0.2
        
        self.deformer.enable_deformer('force_field', 0.6)
        self.deformer.enable_deformer('chaotic', 0.4)


async def main():
    """Demostración principal"""
    showcase = DeformerShowcase()
    
    print("\n" + "="*60)
    print("SISTEMA DE DEFORMACIÓN DE TRAYECTORIAS")
    print("="*60)
    
    print("\n¿Qué deseas ver?")
    print("1. Todos los ejemplos")
    print("2. Ejemplo específico")
    print("3. Preset artístico")
    
    choice = input("\nElección (1-3): ")
    
    if choice == "1":
        await showcase.run_all_examples()
        
    elif choice == "2":
        print("\nEjemplos disponibles:")
        print("1. Campo Magnético")
        print("2. Océano que Respira")
        print("3. Mariposa Caótica")
        print("4. Caligrafía Espacial")
        print("5. Ecosistema Vivo")
        
        example_num = int(input("\nNúmero: "))
        examples = [
            showcase.example_1_magnetic_field,
            showcase.example_2_breathing_ocean,
            showcase.example_3_chaotic_butterfly,
            showcase.example_4_calligraphy_gesture,
            showcase.example_5_composite_ecosystem
        ]
        
        if 1 <= example_num <= len(examples):
            showcase.deformer.active_deformers.clear()
            base_trajectory = examples[example_num - 1]()
            await showcase.visualize_deformation(base_trajectory, 20.0)
            
    elif choice == "3":
        print("\nPresets artísticos:")
        print("1. Sueño Submarino")
        print("2. Danza Cósmica")
        
        preset_num = int(input("\nNúmero: "))
        presets = ["underwater_dream", "cosmic_dance"]
        
        if 1 <= preset_num <= len(presets):
            preset = showcase.create_artistic_preset(presets[preset_num - 1])
            print(f"\nPreset '{preset['name']}' aplicado")
            
            # Visualizar con trayectoria circular simple
            def circle(t):
                return 8 * np.array([np.cos(t), np.sin(t), 0])
                
            await showcase.visualize_deformation(circle, 20.0)
            
    print("\n✨ ¡Gracias por explorar las deformaciones!")


if __name__ == "__main__":
    asyncio.run(main())