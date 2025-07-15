"""
modulator_visualizer.py - Visualizador opcional del modulador 3D
Simula visualmente el comportamiento del Simulador Modulación.html
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import time
from typing import List, Tuple, Optional
from trajectory_hub.core.motion_components import AdvancedOrientationModulation, MotionState


class ModulatorVisualizer:
    """
    Visualizador 3D del sistema de modulación
    Muestra cómo el "foco" se mueve sobre la superficie de una esfera
    """
    
    def __init__(self, modulator: AdvancedOrientationModulation):
        self.modulator = modulator
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Configuración de la vista
        self.ax.set_xlim([-2, 2])
        self.ax.set_ylim([-2, 2])
        self.ax.set_zlim([-2, 2])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Esfera base (la fuente sonora)
        self.sphere_radius = 1.0
        self.draw_sphere()
        
        # Punto focal (representa el haz de radiación)
        self.focus_point = None
        self.focus_trail = []
        self.trail_max_points = 200
        
        # Estado de simulación
        self.start_time = time.time()
        self.motion_state = MotionState()
        
    def draw_sphere(self):
        """Dibujar la esfera que representa la fuente sonora"""
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = self.sphere_radius * np.outer(np.cos(u), np.sin(v))
        y = self.sphere_radius * np.outer(np.sin(u), np.sin(v))
        z = self.sphere_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Dibujar superficie semi-transparente
        self.ax.plot_surface(x, y, z, alpha=0.2, color='gray')
        
    def orientation_to_sphere_point(self, yaw: float, pitch: float, roll: float) -> Tuple[float, float, float]:
        """
        Convertir orientación (yaw, pitch, roll) a un punto sobre la superficie de la esfera
        Simula cómo el "foco" se mueve sobre la superficie
        """
        # Usar yaw y pitch para determinar la posición en la esfera
        # Roll puede afectar el color o tamaño del punto
        
        # Convertir a coordenadas esféricas
        # Yaw = azimuth (rotación horizontal)
        # Pitch = elevación (rotación vertical)
        
        # Normalizar ángulos
        azimuth = yaw
        elevation = pitch
        
        # Convertir a cartesianas sobre la esfera
        x = self.sphere_radius * np.cos(elevation) * np.cos(azimuth)
        y = self.sphere_radius * np.cos(elevation) * np.sin(azimuth)
        z = self.sphere_radius * np.sin(elevation)
        
        return x, y, z
        
    def get_focus_color(self) -> str:
        """Obtener color del foco basado en el modo de dibujo"""
        colors = {
            "circle": "red",
            "ellipse": "blue",
            "lissajous": "green",
            "spiral": "purple",
            "random": "orange",
            "pendulum": "cyan",
            "seismic": "yellow",
            "ocean": "teal",
            "mechanical": "brown"
        }
        return colors.get(self.modulator.modulation_shape, "red")
        
    def update_frame(self, frame):
        """Actualizar frame de la animación"""
        current_time = time.time() - self.start_time
        dt = 1/30.0  # 30 FPS
        
        # Actualizar estado con el modulador
        self.motion_state = self.modulator.update(current_time, dt, self.motion_state)
        
        # Obtener orientación actual
        yaw, pitch, roll = self.motion_state.orientation
        
        # Convertir a punto en la esfera
        x, y, z = self.orientation_to_sphere_point(yaw, pitch, roll)
        
        # Actualizar punto focal
        if self.focus_point:
            self.focus_point.remove()
        
        # Tamaño del foco basado en aperture
        focus_size = 100 * (0.5 + self.motion_state.aperture * 0.5)
        
        # Dibujar punto focal
        self.focus_point = self.ax.scatter(
            [x], [y], [z], 
            c=self.get_focus_color(), 
            s=focus_size,
            alpha=0.8,
            edgecolors='white',
            linewidth=2
        )
        
        # Añadir a la estela
        self.focus_trail.append((x, y, z))
        if len(self.focus_trail) > self.trail_max_points:
            self.focus_trail.pop(0)
            
        # Dibujar estela
        if len(self.focus_trail) > 1:
            # Limpiar estela anterior
            for artist in self.ax.lines:
                if hasattr(artist, '_trail_line'):
                    artist.remove()
                    
            # Dibujar nueva estela con gradiente de opacidad
            trail_array = np.array(self.focus_trail)
            segments = len(trail_array) - 1
            
            for i in range(segments):
                alpha = (i / segments) * 0.5  # Gradiente de transparencia
                line = self.ax.plot(
                    trail_array[i:i+2, 0],
                    trail_array[i:i+2, 1],
                    trail_array[i:i+2, 2],
                    color=self.get_focus_color(),
                    alpha=alpha,
                    linewidth=2
                )[0]
                line._trail_line = True  # Marcar como línea de estela
                
        # Actualizar título con información
        self.ax.set_title(
            f"Modulador 3D - {self.modulator.modulation_shape}\n"
            f"LFO: {self.modulator.lfo_frequency:.2f} Hz | "
            f"Intensidad: {self.modulator.intensity:.0%} | "
            f"Apertura: {self.motion_state.aperture:.2f}"
        )
        
        # Rotar vista para mejor visualización
        self.ax.view_init(elev=20, azim=frame * 0.5)
        
    def animate(self, duration: float = 30.0, save_as: Optional[str] = None):
        """
        Animar el modulador
        
        Args:
            duration: Duración de la animación en segundos
            save_as: Si se especifica, guarda la animación como GIF
        """
        frames = int(duration * 30)  # 30 FPS
        
        anim = FuncAnimation(
            self.fig, 
            self.update_frame, 
            frames=frames,
            interval=33,  # ~30 FPS
            repeat=True
        )
        
        if save_as:
            print(f"Guardando animación como {save_as}...")
            anim.save(save_as, writer='pillow', fps=30)
            print("¡Animación guardada!")
        else:
            plt.show()
            
    def compare_presets(self, preset_names: List[str], duration: float = 5.0):
        """
        Comparar múltiples presets en una sola visualización
        """
        n_presets = len(preset_names)
        fig = plt.figure(figsize=(15, 5))
        
        for idx, preset_name in enumerate(preset_names):
            ax = fig.add_subplot(1, n_presets, idx + 1, projection='3d')
            
            # Configurar modulador con preset
            modulator = AdvancedOrientationModulation()
            modulator.apply_preset(preset_name)
            
            # Simular trayectoria completa
            trail = []
            state = MotionState()
            dt = 1/60.0
            
            for t in np.linspace(0, duration, int(duration * 60)):
                state = modulator.update(t, dt, state)
                x, y, z = self.orientation_to_sphere_point(*state.orientation)
                trail.append((x, y, z))
                
            # Dibujar esfera
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 15)
            x_sphere = np.outer(np.cos(u), np.sin(v))
            y_sphere = np.outer(np.sin(u), np.sin(v))
            z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
            ax.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.1, color='gray')
            
            # Dibujar trayectoria
            if trail:
                trail_array = np.array(trail)
                ax.plot(trail_array[:, 0], trail_array[:, 1], trail_array[:, 2],
                       color=self.get_focus_color(), linewidth=2, alpha=0.8)
                
            # Configurar vista
            ax.set_xlim([-1.5, 1.5])
            ax.set_ylim([-1.5, 1.5])
            ax.set_zlim([-1.5, 1.5])
            ax.set_title(f"{preset_name}\nLFO: {modulator.lfo_frequency} Hz")
            
        plt.tight_layout()
        plt.show()


def demo_visualizer():
    """Demostración del visualizador"""
    # Crear modulador
    modulator = AdvancedOrientationModulation()
    
    # Aplicar un preset
    modulator.apply_preset("lissajous")
    modulator.set_intensity(0.8)
    
    # Crear visualizador
    viz = ModulatorVisualizer(modulator)
    
    # Animar
    print("Mostrando animación del modulador...")
    print("Cierra la ventana para continuar")
    viz.animate(duration=20.0)
    
    # Comparar presets
    print("\nComparando diferentes presets...")
    viz.compare_presets(
        ["circle", "ellipse", "lissajous", "spiral"],
        duration=3.0
    )
    
    
def create_modulator_gif(preset_name: str, output_file: str = "modulator_demo.gif"):
    """Crear un GIF animado del modulador"""
    modulator = AdvancedOrientationModulation()
    modulator.apply_preset(preset_name)
    
    viz = ModulatorVisualizer(modulator)
    viz.animate(duration=5.0, save_as=output_file)
    

if __name__ == "__main__":
    # Ejecutar demo
    demo_visualizer()
    
    # Opcional: crear GIF
    # create_modulator_gif("spiral", "spiral_modulation.gif")