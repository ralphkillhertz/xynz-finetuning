"""
CLI Interface Helper - Maneja entrada/salida de consola
"""
from typing import Optional, List, Dict, Any
import os


class CLIInterface:
    """Helper para interfaz de línea de comandos"""
    
    def __init__(self):
        self.last_input = None
        
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_input(self, prompt: str = "Selección: ") -> str:
        """Obtiene entrada del usuario"""
        try:
            self.last_input = input(f"\n{prompt}").strip()
            return self.last_input
        except KeyboardInterrupt:
            return 'q'
    
    def get_numeric_input(self, prompt: str, min_val: float = None, 
                         max_val: float = None) -> Optional[float]:
        """Obtiene entrada numérica con validación"""
        while True:
            value = self.get_input(prompt)
            if value.lower() == 'q':
                return None
                
            try:
                num = float(value)
                if min_val is not None and num < min_val:
                    self.show_error(f"Valor mínimo: {min_val}")
                    continue
                if max_val is not None and num > max_val:
                    self.show_error(f"Valor máximo: {max_val}")
                    continue
                return num
            except ValueError:
                self.show_error("Por favor ingrese un número válido")
    
    def get_choice_from_list(self, options: List[str], 
                           prompt: str = "Seleccione una opción:") -> Optional[int]:
        """Muestra lista y obtiene selección"""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        choice = self.get_numeric_input("Opción: ", 1, len(options))
        return int(choice) - 1 if choice else None
    
    def get_yes_no(self, prompt: str) -> bool:
        """Obtiene respuesta sí/no"""
        response = self.get_input(f"{prompt} (s/n): ").lower()
        return response in ['s', 'si', 'sí', 'y', 'yes']
    
    def show_header(self, title: str):
        """Muestra encabezado formateado"""
        print(f"\n{'=' * 60}")
        print(f"{title.center(60)}")
        print('=' * 60)
    
    def show_success(self, message: str):
        """Muestra mensaje de éxito"""
        print(f"\n✅ {message}")
    
    def show_error(self, message: str):
        """Muestra mensaje de error"""
        print(f"\n❌ ERROR: {message}")
    
    def show_warning(self, message: str):
        """Muestra advertencia"""
        print(f"\n⚠️  ADVERTENCIA: {message}")
    
    def show_info(self, message: str):
        """Muestra información"""
        print(f"\nℹ️  {message}")
    
    def show_menu(self, title: str, options: List[tuple]):
        """Muestra un menú formateado"""
        self.show_header(title)
        for key, description in options:
            if key == '-':
                print(f"{'-' * 60}")
            else:
                print(f"  {key:<4} {description}")
    
    def pause(self, message: str = "Presione ENTER para continuar..."):
        """Pausa la ejecución"""
        input(f"\n{message}")
    
    def get_macro_config(self) -> Optional[Dict[str, Any]]:
        """Obtiene configuración para crear un macro"""
        print("\n🔧 CONFIGURACIÓN DE MACRO")
        
        name = self.get_input("Nombre del macro: ")
        if not name or name == 'q':
            return None
            
        count = self.get_numeric_input("Número de fuentes: ", 1, 100)
        if count is None:
            return None
            
        formations = ["circle", "line", "grid", "spiral", "random", "sphere", "custom"]
        formation_idx = self.get_choice_from_list(formations, "Formación inicial:")
        if formation_idx is None:
            return None
        
        formation = formations[formation_idx]
        
        # Solicitar spacing para todas las formaciones
        spacing = None
        custom_function = None
        
        # Pedir spacing según el tipo de formación
        print("\n📏 DISTANCIA ENTRE FUENTES")
        if formation == "circle":
            print("  Define el radio del círculo")
            spacing = self.get_numeric_input("Radio del círculo (1-10): ", 1.0, 10.0)
        elif formation == "line":
            print("  Define la separación entre fuentes en la línea")
            spacing = self.get_numeric_input("Separación entre fuentes (0.5-5): ", 0.5, 5.0)
        elif formation == "grid":
            print("  Define la separación entre fuentes en la cuadrícula")
            spacing = self.get_numeric_input("Separación de la cuadrícula (0.5-5): ", 0.5, 5.0)
        elif formation == "spiral":
            print("  Define el factor de expansión de la espiral")
            spacing = self.get_numeric_input("Factor de expansión (0.5-5): ", 0.5, 5.0)
        elif formation == "sphere":
            print("  Define el radio de la esfera")
            spacing = self.get_numeric_input("Radio de la esfera (1-10): ", 1.0, 10.0)
        elif formation == "random":
            print("  Menor valor = más concentrado, mayor = más disperso")
            spacing = self.get_numeric_input("Concentración (0.5-5.0): ", 0.5, 5.0)
        elif formation == "custom":
            print("  Define la escala general de la formación")
            spacing = self.get_numeric_input("Factor de escala (0.5-5): ", 0.5, 5.0)
            
        # Valor por defecto si el usuario cancela
        if spacing is None:
            spacing = 2.0
                
        # Configuración adicional para formación personalizada
        if formation == "custom":
            print("\n🎨 FORMACIÓN PERSONALIZADA")
            print("  Defina la formación usando funciones matemáticas.")
            print("  Variables disponibles: i (índice), n (total), t (parámetro 0-1)")
            print("  Funciones: sin, cos, sqrt, pi")
            print("\n  Ejemplos:")
            print("  - Rosa polar: r = 2 + sin(4*t*2*pi)")
            print("  - Espiral 3D: x = r*cos(t*6*pi), y = r*sin(t*6*pi), z = t*4")
            
            custom_function = {}
            
            # Obtener expresiones para cada coordenada
            print("\nDefina las expresiones (Enter para usar default):")
            
            x_expr = self.get_input("  x(t) = ")
            custom_function['x'] = x_expr if x_expr else "2 * cos(t * 2 * pi)"
            
            y_expr = self.get_input("  y(t) = ")
            custom_function['y'] = y_expr if y_expr else "0"
            
            z_expr = self.get_input("  z(t) = ")
            custom_function['z'] = z_expr if z_expr else "2 * sin(t * 2 * pi)"
            
            # Opcionalmente, permitir definir r(t) para coordenadas polares
            use_polar = self.get_yes_no("\n¿Usar coordenadas polares (r, theta)? ")
            if use_polar:
                r_expr = self.get_input("  r(t) = ")
                custom_function['r'] = r_expr if r_expr else "2"
                custom_function['polar'] = True
            
        return {
            "name": name,
            "source_count": int(count),
            "formation": formation,
            "spacing": spacing,
            "custom_function": custom_function
        }
    
    def get_movement_config(self) -> Optional[Dict[str, Any]]:
        """Obtiene configuración de movimiento de trayectoria macro"""
        print("\n🌀 CONFIGURACIÓN DE TRAYECTORIA MACRO")
        
        # Tipos de trayectoria expandidos con descripción
        trajectory_options = [
            ("circle", "Círculo - Trayectoria circular en plano configurable"),
            ("spiral", "Espiral 3D - Helicoidal expansiva"),
            ("figure8", "Figura 8 - Lemniscata horizontal"),
            ("lissajous", "Lissajous 3D - Curva paramétrica compleja"),
            ("random", "Aleatorio - Movimiento suavizado aleatorio"),
            ("helix", "Hélice - Espiral vertical (ABIERTA)"),
            ("line", "Línea recta - Punto A a B (ABIERTA)"),
            ("wave", "Onda - Sinusoidal en 3D (ABIERTA)"),
            ("torus_knot", "Nudo toroidal - Trayectoria sobre toro"),
            ("rose", "Rosa - Pétalos matemáticos"),
            ("butterfly", "Mariposa - Curva compleja"),
            ("heart", "Corazón - Forma romántica")
        ]
        
        print("\nTipos de trayectoria disponibles:")
        print("\n  [CERRADAS] - El macro vuelve al punto inicial")
        cerradas_printed = False
        abiertas_printed = False
        
        for i, (key, desc) in enumerate(trajectory_options[:9], 1):
            if key in ["helix", "line", "wave"] and not abiertas_printed:
                print("\n  [ABIERTAS] - El macro no vuelve al inicio")
                abiertas_printed = True
            print(f"  {i}. {key:<12} - {desc}")
        
        type_idx = self.get_numeric_input("\nSeleccione tipo (1-12): ", 1, 12)
        if type_idx is None:
            return None
            
        trajectory_type = trajectory_options[int(type_idx)-1][0]
        
        # Configuración de velocidad con soporte para negativas
        print("\n⚡ CONFIGURACIÓN DE VELOCIDAD")
        print("  • Valores positivos: sentido normal")
        print("  • Valores negativos: sentido inverso")
        print("  • Mayor valor absoluto = más rápido")
        
        speed = self.get_numeric_input("Velocidad (-10 a 10): ", -10.0, 10.0)
        if speed is None:
            return None
            
        # Configuración de escala/tamaño
        print("\n📏 CONFIGURACIÓN DE ESCALA")
        print("  Define el tamaño de la trayectoria en metros")
        
        params = {
            "speed": speed
        }
        
        # Parámetros específicos según tipo
        if trajectory_type == "circle":
            params["radius"] = self.get_numeric_input("Radio del círculo (metros): ", 0.5, 20.0) or 5.0
            
            planes = ["xy", "xz", "yz"]
            plane_idx = self.get_choice_from_list(
                ["Horizontal (XY)", "Frontal (XZ)", "Lateral (YZ)"],
                "Plano de rotación:"
            )
            if plane_idx is not None:
                params["plane"] = planes[plane_idx]
                
        elif trajectory_type == "spiral":
            params["radius"] = self.get_numeric_input("Radio máximo (metros): ", 0.5, 20.0) or 5.0
            params["height"] = self.get_numeric_input("Altura total (metros): ", 1.0, 30.0) or 10.0
            params["turns"] = self.get_numeric_input("Número de vueltas: ", 0.5, 10.0) or 3.0
            
        elif trajectory_type in ["figure8", "lissajous"]:
            params["scale"] = self.get_numeric_input("Escala general (metros): ", 0.5, 20.0) or 5.0
            
            if trajectory_type == "lissajous":
                print("\n  Frecuencias para Lissajous 3D:")
                params["freq_x"] = self.get_numeric_input("  Frecuencia X: ", 1.0, 10.0) or 3.0
                params["freq_y"] = self.get_numeric_input("  Frecuencia Y: ", 1.0, 10.0) or 2.0
                params["freq_z"] = self.get_numeric_input("  Frecuencia Z: ", 1.0, 10.0) or 4.0
                
        elif trajectory_type == "random":
            params["scale"] = self.get_numeric_input("Rango de movimiento (metros): ", 0.5, 20.0) or 5.0
            params["seed"] = int(self.get_numeric_input("Semilla aleatoria: ", 0, 9999) or 42)
            params["num_points"] = int(self.get_numeric_input("Puntos de control: ", 5, 20) or 10)
            
        elif trajectory_type == "helix":
            params["radius"] = self.get_numeric_input("Radio (metros): ", 0.5, 20.0) or 5.0
            params["pitch"] = self.get_numeric_input("Paso vertical por vuelta: ", 0.5, 10.0) or 2.0
            params["turns"] = self.get_numeric_input("Número de vueltas: ", 0.5, 10.0) or 3.0
            
        elif trajectory_type == "line":
            print("\n  Punto inicial:")
            start_x = self.get_numeric_input("    X inicial: ", -50, 50) or 0.0
            start_y = self.get_numeric_input("    Y inicial: ", -50, 50) or 0.0
            start_z = self.get_numeric_input("    Z inicial: ", -50, 50) or 0.0
            params["start"] = np.array([start_x, start_y, start_z])
            
            print("\n  Punto final:")
            end_x = self.get_numeric_input("    X final: ", -50, 50) or 10.0
            end_y = self.get_numeric_input("    Y final: ", -50, 50) or 0.0
            end_z = self.get_numeric_input("    Z final: ", -50, 50) or 0.0
            params["end"] = np.array([end_x, end_y, end_z])
            
        elif trajectory_type == "wave":
            params["length"] = self.get_numeric_input("Longitud de onda (metros): ", 1.0, 50.0) or 20.0
            params["amplitude"] = self.get_numeric_input("Amplitud (metros): ", 0.5, 10.0) or 3.0
            params["frequency"] = self.get_numeric_input("Frecuencia: ", 0.5, 10.0) or 2.0
            
            axes = ["x", "y", "z"]
            axis_idx = self.get_choice_from_list(["Eje X", "Eje Y", "Eje Z"], "Dirección principal:")
            if axis_idx is not None:
                params["axis"] = axes[axis_idx]
                
            wave_axis_idx = self.get_choice_from_list(["Eje X", "Eje Y", "Eje Z"], "Eje de oscilación:")
            if wave_axis_idx is not None:
                params["wave_axis"] = axes[wave_axis_idx]
                
        elif trajectory_type == "torus_knot":
            params["major_radius"] = self.get_numeric_input("Radio mayor del toro: ", 1.0, 20.0) or 5.0
            params["minor_radius"] = self.get_numeric_input("Radio menor del toro: ", 0.5, 10.0) or 2.0
            params["p"] = int(self.get_numeric_input("Vueltas eje mayor (p): ", 1, 10) or 2)
            params["q"] = int(self.get_numeric_input("Vueltas eje menor (q): ", 1, 10) or 3)
            
        else:
            # Para rose, butterfly, heart, usar escala general
            params["scale"] = self.get_numeric_input("Escala (metros): ", 0.5, 20.0) or 5.0
            
        # Configuración del modo de reproducción
        print("\n🎮 MODO DE REPRODUCCIÓN")
        playback_modes = [
            ("fix", "Fix - Velocidad constante"),
            ("random", "Random - Velocidad y dirección aleatorias"),
            ("freeze", "Freeze - Congelable en cualquier momento"),
            ("vibration", "Vibration - Oscilación alrededor de la posición"),
            ("spin", "Spin - Rotación con variación sinusoidal")
        ]
        
        print("\nModos disponibles:")
        for i, (key, desc) in enumerate(playback_modes, 1):
            print(f"  {i}. {desc}")
            
        mode_idx = self.get_numeric_input("\nSeleccione modo (1-5): ", 1, 5)
        if mode_idx is None:
            playback_mode = "fix"
        else:
            playback_mode = playback_modes[int(mode_idx)-1][0]
            
        # Parámetros específicos del modo
        playback_params = {}
        
        if playback_mode == "random":
            print("\n  Configuración modo Random:")
            playback_params["change_interval"] = self.get_numeric_input(
                "    Intervalo de cambio (segundos): ", 0.5, 10.0
            ) or 2.0
            playback_params["speed_range"] = (
                self.get_numeric_input("    Velocidad mínima: ", 0.1, 5.0) or 0.1,
                self.get_numeric_input("    Velocidad máxima: ", 0.1, 5.0) or 3.0
            )
            
        elif playback_mode == "vibration":
            print("\n  Configuración modo Vibration:")
            playback_params["amplitude"] = self.get_numeric_input(
                "    Amplitud de vibración: ", 0.01, 0.2
            ) or 0.05
            playback_params["frequency"] = self.get_numeric_input(
                "    Frecuencia (Hz): ", 1.0, 50.0
            ) or 10.0
            
        elif playback_mode == "spin":
            print("\n  Configuración modo Spin:")
            playback_params["base_speed"] = self.get_numeric_input(
                "    Velocidad base: ", 0.1, 5.0
            ) or 1.0
            playback_params["variation"] = self.get_numeric_input(
                "    Variación (0-1): ", 0.0, 1.0
            ) or 0.5
            playback_params["frequency"] = self.get_numeric_input(
                "    Frecuencia de variación: ", 0.1, 2.0
            ) or 0.2
        
        return {
            "trajectory_type": trajectory_type,
            "speed": speed,
            "trajectory_params": params,
            "playback_mode": playback_mode,
            "playback_params": playback_params
        }
