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
        """Obtiene configuración de movimiento"""
        print("\n🌀 CONFIGURACIÓN DE MOVIMIENTO")
        
        types = ["circle", "spiral", "figure8", "lissajous", "random"]
        type_idx = self.get_choice_from_list(types, "Tipo de trayectoria:")
        if type_idx is None:
            return None
            
        speed = self.get_numeric_input("Velocidad (0.1-10): ", 0.1, 10)
        if speed is None:
            return None
            
        return {
            "trajectory_type": types[type_idx],
            "speed": speed
        }
