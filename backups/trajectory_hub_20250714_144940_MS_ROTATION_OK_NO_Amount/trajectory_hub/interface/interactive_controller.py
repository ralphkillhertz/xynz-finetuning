"""
Interactive Controller - Interfaz CLI simplificada
Versión 2.0 - Arquitectura Orquestador
"""
import logging
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any
from ..control import CommandProcessor, SemanticCommand, IntentType, CLIInterface
from ..core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from ..core.spat_osc_bridge import SpatOSCBridge, OSCTarget


logger = logging.getLogger(__name__)


class InteractiveController:
    """
    Controlador interactivo simplificado.
    Solo maneja navegación de menús y delega toda la lógica al CommandProcessor.
    """
    
    def __init__(self, engine: EnhancedTrajectoryEngine):
        self.engine = engine
        self.engine.start()  # Iniciar loop
        self.command_processor = CommandProcessor(self.engine)
        self.ui = CLIInterface()
        self.current_menu = "main"
        self.selected_macro = None
        
        # Estado de sesión
        self.session_active = True
        self.command_history = []
        
        logger.info("InteractiveController v2.0 inicializado")
    
    # ========== NAVEGACIÓN PRINCIPAL ==========
    
    def run(self):
        """Loop principal del controlador"""
        self.ui.clear_screen()
        self.ui.show_header("TRAJECTORY HUB - Control Interactivo v2.0")
        
        while self.session_active:
            try:
                self._show_current_menu()
                choice = self.ui.get_input().lower()
                
                if choice == 'q':
                    if self._confirm_exit():
                        break
                elif choice == 'b':
                    self._navigate_back()
                else:
                    self._process_choice(choice)
                    
            except KeyboardInterrupt:
                if self._confirm_exit():
                    break
            except Exception as e:
                logger.error(f"Error en loop principal: {e}")
                self.ui.show_error(f"Error inesperado: {str(e)}")
    
    def _show_current_menu(self):
        """Muestra el menú actual"""
        menu_handlers = {
            "main": self._show_main_menu,
            "movement": self._show_movement_menu,
            "delta": self._show_delta_menu,
            "modulation": self._show_modulation_menu,
            "presets": self._show_presets_menu,
            "system": self._show_system_menu,
            "macros": self._show_macros_menu
        }
        
        if self.current_menu in menu_handlers:
            menu_handlers[self.current_menu]()
        else:
            self.ui.show_error(f"Menú desconocido: {self.current_menu}")
            self.current_menu = "main"
    
    def _navigate_back(self):
        """Navega al menú anterior"""
        nav_map = {
            "movement": "main",
            "delta": "main",
            "modulation": "main",
            "presets": "main",
            "system": "main",
            "macros": "main"
        }
        self.current_menu = nav_map.get(self.current_menu, "main")
    
    def _process_choice(self, choice: str):
        """Procesa la elección del usuario según el menú actual"""
        processors = {
            "main": self._process_main_choice,
            "movement": self._process_movement_choice,
            "delta": self._process_delta_choice,
            "modulation": self._process_modulation_choice,
            "presets": self._process_presets_choice,
            "system": self._process_system_choice,
            "macros": self._process_macros_choice
        }
        
        if self.current_menu in processors:
            processors[self.current_menu](choice)
    
    # ========== MENÚS ==========
    
    def _show_main_menu(self):
        """Menú principal"""
        options = [
            ("1", "🎯 Crear Macro/Grupo"),
            ("2", "🌀 Sistema de Movimiento"),
            ("3", "🎵 Modulador 3D"),
            ("4", "🎨 Presets Artísticos"),
            ("5", "📊 Gestión de Macros"),
            ("6", "ℹ️  Sistema e Información"),
            ("-", ""),
            ("q", "Salir")
        ]
        
        self.ui.show_menu("MENÚ PRINCIPAL", options)
        
        if self.selected_macro:
            self.ui.show_info(f"Macro activo: {self.selected_macro}")
    
    def _show_movement_menu(self):
        """Menú del sistema de movimiento"""
        options = [
            ("1", "📍 Concentración/Dispersión"),
            ("2", "🔄 Trayectorias Macro"),
            ("3", "🎯 Trayectorias Individuales"),
            ("4", "🌀 Rotaciones Macro"),
            ("5", "🔸 Rotaciones Individuales"),
            ("6", "🏃 Modos de Movimiento"),
            ("7", "✏️ Editar Rotaciones Activas"),
            ("-", ""),
            ("b", "Volver"),
            ("q", "Salir")
        ]
        
        self.ui.show_menu("SISTEMA DE MOVIMIENTO", options)
    
    def _show_delta_menu(self):
        """Menú del sistema de movimiento"""
        options = [
            ("== TRANSFORMACIONES ==", ""),
            ("1", "📍 Concentración/Dispersión"),
            ("", ""),
            ("== TRAYECTORIAS ==", ""),
            ("2", "🔄 Trayectorias de Macro (MS)"),
            ("3", "🚶 Trayectorias Individuales (IS)"),
            ("", ""),
            ("== ROTACIONES ==", ""),
            ("4", "📐 Rotación Manual de Macro"),
            ("5", "🌀 Rotación Algorítmica de Macro"),
            ("6", "📐 Rotación Manual Individual"),
            ("7", "🔸 Rotación Algorítmica Individual"),
            ("", ""),
            ("== ORIENTACIÓN ==", ""),
            ("8", "🎛️  Modulación 3D"),
            ("", ""),
            ("9", "✏️  Editar Movimientos Activos"),
            ("-", ""),
            ("b", "Volver"),
            ("q", "Salir")
        ]
        
        self.ui.show_menu("SISTEMA DE MOVIMIENTO", options)
    
    def _show_modulation_menu(self):
        """Menú del modulador 3D"""
        options = [
            ("1", "🎭 Aplicar Preset de Modulación"),
            ("2", "🎚️ Ajustar Intensidad Global"),
            ("3", "⚡ Configurar Velocidad (LFO)"),
            ("4", "🔀 Interpolar entre Presets"),
            ("5", "🛑 Desactivar Modulación"),
            ("-", ""),
            ("b", "Volver"),
            ("q", "Salir")
        ]
        
        self.ui.show_menu("MODULADOR 3D", options)
    
    def _show_presets_menu(self):
        """Menú de presets artísticos"""
        options = [
            ("1", "🌌 Galaxia Rotante"),
            ("2", "🌊 Océano Respirante"),
            ("3", "⚡ Enjambre Nervioso"),
            ("4", "🌀 Vórtice Hipnótico"),
            ("5", "🎭 Composición Aleatoria"),
            ("-", ""),
            ("b", "Volver"),
            ("q", "Salir")
        ]
        
        self.ui.show_menu("PRESETS ARTÍSTICOS", options)
    
    def _show_system_menu(self):
        """Menú de sistema e información"""
        options = [
            ("1", "📊 Estado del Sistema"),
            ("2", "📋 Listar Macros Activos"),
            ("3", "🔍 Información de Macro"),
            ("4", "📡 Estado OSC"),
            ("5", "💾 Guardar Configuración"),
            ("6", "📂 Cargar Configuración"),
            ("7", "🗑️ Eliminar Macro"),
            ("-", ""),
            ("b", "Volver"),
            ("q", "Salir")
        ]
        
        self.ui.show_menu("SISTEMA E INFORMACIÓN", options)
    
    # ========== PROCESADORES DE OPCIONES ==========
    
    def _show_macros_menu(self):
        """Menú de gestión de macros"""
        options = [
            ("1", "📋 Listar Macros Activos"),
            ("2", "✅ Seleccionar Macro Activo"),
            ("3", "🔍 Información Detallada"),
            ("4", "📏 Ajustar Distancia (Spacing)"),
            ("5", "📍 Mover Posición del Macro"),
            ("6", "⏸️ Activar/Desactivar Macro"),
            ("7", "🗑️ Eliminar Macro"),
            ("-", ""),
            ("b", "Volver"),
            ("q", "Salir")
        ]
        
        # Mostrar macro seleccionado actual
        if self.selected_macro:
            macro_info = self.engine.select_macro(self.selected_macro)
            if macro_info:
                print(f"\n  Macro activo: {macro_info['key'].split('_')[2]} ({macro_info['num_sources']} sources)")
        
        self.ui.show_menu("GESTIÓN DE MACROS", options)

    def _process_macros_choice(self, choice: str):
        """Procesa las opciones del menú de macros"""
        if choice == "1":
            self._list_active_macros()
        elif choice == "2":
            self._select_macro()
        elif choice == "3":
            self._show_macro_info()
        elif choice == "4":
            self._adjust_macro_spacing()
        elif choice == "5":
            self._move_macro_position()
        elif choice == "6":
            self._toggle_macro_enabled()
        elif choice == "7":
            self._delete_macro()

    def _process_main_choice(self, choice: str):
        """Procesa opciones del menú principal"""
        if choice == "1":
            self._create_macro_wizard()
        elif choice == "2":
            self.current_menu = "delta"
        elif choice == "3":
            self.current_menu = "modulation"
        elif choice == "4":
            self.current_menu = "presets"
        elif choice == "5":
            self.current_menu = "macros"
        elif choice == "6":
            self.current_menu = "system"
    
    def _process_movement_choice(self, choice: str):
        """Procesa opciones del menú de movimiento"""
        if not self._ensure_macro_selected():
            return
            
        if choice == "7":
            self._edit_active_rotations()
            return
            
        commands = {
            "1": self._create_concentration_command,
            "2": self._create_macro_trajectory_command,
            "3": self._create_individual_trajectory_command,
            "4": self._create_macro_rotation_command,
            "5": self._create_individual_rotation_command,
            "6": self._configure_movement_modes
        }
        
        if choice in commands:
            command = commands[choice]()
            if command:
                self._execute_command(command)
    
    def _process_delta_choice(self, choice: str):
        """Procesa opciones del menú de movimiento"""
        if not self._ensure_macro_selected():
            return
            
        if choice == "8":
            self.current_menu = "modulation"
            return
        elif choice == "9":
            self._edit_active_rotations()
            return
            
        # Mapear las opciones del menú plano a los comandos
        commands = {
            "1": self._create_concentration_command,  # Concentración/Dispersión
            "2": self._create_macro_trajectory_command,  # Trayectorias de Macro (MS)
            "3": self._create_individual_trajectory_command,  # Trayectorias Individuales (IS)
            "4": lambda: self._create_macro_rotation_command(manual=True),  # Rotación Manual de Macro
            "5": lambda: self._create_macro_rotation_command(algorithmic=True),  # Rotación Algorítmica de Macro
            "6": lambda: self._create_individual_rotation_command(manual=True),  # Rotación Manual Individual
            "7": lambda: self._create_individual_rotation_command(algorithmic=True),  # Rotación Algorítmica Individual
        }
        
        if choice in commands:
            command = commands[choice]()
            if command:
                self._execute_command(command)
    
    def _process_modulation_choice(self, choice: str):
        """Procesa opciones del menú de modulación"""
        if not self._ensure_macro_selected():
            return
            
        if choice == "1":
            self._apply_modulation_preset()
        elif choice == "2":
            self._adjust_modulation_intensity()
        elif choice == "3":
            self._configure_modulation_lfo()
        elif choice == "4":
            self._interpolate_modulation_presets()
        elif choice == "5":
            self._toggle_modulation()
    
    def _process_presets_choice(self, choice: str):
        """Procesa opciones del menú de presets"""
        preset_map = {
            "1": "rotating_galaxy",
            "2": "breathing_ocean",
            "3": "nervous_swarm",
            "4": "hypnotic_vortex",
            "5": "random_composition"
        }
        
        if choice in preset_map:
            command = SemanticCommand(
                intent=IntentType.LOAD_PRESET,
                parameters={"preset_name": preset_map[choice]},
                source="interactive_cli"
            )
            self._execute_command(command)
    
    def _process_system_choice(self, choice: str):
        """Procesa opciones del menú de sistema"""
        if choice == "1":
            self._show_system_status()
        elif choice == "2":
            self._list_active_macros()
        elif choice == "3":
            self._show_macro_info()
        elif choice == "4":
            self._show_osc_status()
        elif choice == "5":
            self._save_configuration()
        elif choice == "6":
            self._load_configuration()
    
    # ========== WIZARDS DE CREACIÓN ==========
    
    def _create_macro_wizard(self):
        """Wizard para crear un macro"""
        config = self.ui.get_macro_config()
        if not config:
            return
            
        command = SemanticCommand(
            intent=IntentType.CREATE_MACRO,
            parameters=config,
            source="interactive_cli"
        )
        
        result = self._execute_command(command)
        if result.success:
            # Obtener el macro_id del resultado
            if 'data' in result.__dict__ and 'macro_id' in result.data:
                self.selected_macro = result.data['macro_id']
            else:
                # Si no está en data, intentar buscar por nombre
                macros = self.engine.list_macros()
                for macro in macros:
                    if macro['name'] == config["name"]:
                        self.selected_macro = macro['key']
                        break
            self.ui.show_success(f"Macro '{config['name']}' seleccionado")
    
    def _create_concentration_command(self) -> Optional[SemanticCommand]:
        """Crea comando de concentración"""
        factor = self.ui.get_numeric_input(
            "Factor de concentración (0=disperso, 1=concentrado): ",
            0.0, 1.0
        )
        
        if factor is None:
            return None
            
        return SemanticCommand(
            intent=IntentType.APPLY_CONCENTRATION,
            parameters={
                "target": self.selected_macro,
                "factor": factor
            },
            source="interactive_cli"
        )
    
    def _create_macro_trajectory_command(self) -> Optional[SemanticCommand]:
        """Crea comando de trayectoria macro"""
        config = self.ui.get_movement_config()
        if not config:
            return None
            
        return SemanticCommand(
            intent=IntentType.SET_TRAJECTORY,
            parameters={
                "target": self.selected_macro,
                "trajectory_type": config["trajectory_type"],
                "trajectory_params": {"speed": config["speed"]}
            },
            source="interactive_cli"
        )
    
    def _create_individual_trajectory_command(self) -> Optional[SemanticCommand]:
        """Crea comando de trayectorias individuales"""
        self.ui.show_info("Configuración de trayectorias individuales")
        
        modes = [
            "Todas iguales",
            "Formas mixtas",
            "Velocidades diferentes",
            "Configuración completa"
        ]
        
        mode_idx = self.ui.get_choice_from_list(modes, "Modo de configuración:")
        if mode_idx is None:
            return None
            
        # Simplificado por ahora
        return SemanticCommand(
            intent=IntentType.SET_INDIVIDUAL_MOVEMENT,
            parameters={
                "target": self.selected_macro,
                "mode": modes[mode_idx],
                "config": {}  # TODO: Expandir según modo
            },
            source="interactive_cli"
        )
    
    def _create_macro_rotation_command(self, algorithmic=False, manual=False) -> Optional[SemanticCommand]:
        """Crea comando de rotación macro"""
        self.ui.show_info("Configuración de rotación de macro")
        
        # Si se especifica el tipo directamente, usarlo
        if algorithmic:
            rotation_type = 0
        elif manual:
            rotation_type = 1
        else:
            # Si no se especifica, preguntar
            rotation_type = self.ui.get_choice_from_list(
                ["Algorítmica (continua)", "Manual (posición específica)"],
                "Tipo de rotación:"
            )
            
            if rotation_type is None:
                return None
            
        if rotation_type == 0:  # Algorítmica
            # Opciones de configuración
            config_options = [
                "🎯 Usar preset",
                "📐 Función personalizada"
            ]
            
            config_choice = self.ui.get_choice_from_list(
                config_options,
                "Seleccione método de configuración:"
            )
            
            if config_choice is None:
                return None
                
            # Variables para las velocidades base
            base_speed_x = 0.0
            base_speed_y = 0.0
            base_speed_z = 0.0
                
            if config_choice == 0:  # Presets
                # Presets geométricos claros y funciones de biblioteca integradas
                presets = [
                    # Formas básicas
                    ("⭕ Circle - Círculo perfecto XY", {"speed_x": 0.0, "speed_y": 0.0, "speed_z": 1.0}),
                    ("🔄 Spiral - Espiral expansiva", {"speed_x": 0.3, "speed_y": 0.3, "speed_z": 0.5}),
                    ("∞ Lissajous - Figura de 8", {"speed_x": 0.66, "speed_y": 1.0, "speed_z": 0.0}),
                    ("📦 Cube - Rotación cúbica", {"speed_x": 0.5, "speed_y": 0.5, "speed_z": 0.5}),
                    
                    # Funciones de biblioteca
                    ("🌊 Wave - Onda sinusoidal", {"speed_x": 0.0, "speed_y": 0.8, "speed_z": 0.2}),
                    ("💫 Helix - Hélice 3D", {"speed_x": 0.0, "speed_y": 0.7, "speed_z": 1.0}),
                    ("🌀 Vortex - Vórtice toroidal", {"speed_x": 1.0, "speed_y": 0.5, "speed_z": 0.3}),
                    ("🎯 Pendulum - Péndulo simple", {"speed_x": 0.0, "speed_y": 1.0, "speed_z": 0.0}),
                    
                    # Movimientos complejos
                    ("🦋 Butterfly - Atractor de Lorenz", {"speed_x": 0.4, "speed_y": 0.6, "speed_z": 0.8}),
                    ("🎭 Rose - Rosa matemática", {"speed_x": 0.33, "speed_y": 0.5, "speed_z": 0.0}),
                    ("🌐 Sphere - Rotación esférica", {"speed_x": 0.5, "speed_y": 0.7, "speed_z": 0.3}),
                    ("🎪 Carousel - Carrusel horizontal", {"speed_x": 0.0, "speed_y": 0.0, "speed_z": 1.2})
                ]
                
                preset_names = [name for name, _ in presets]
                preset_idx = self.ui.get_choice_from_list(preset_names, "Seleccione preset:")
                
                if preset_idx is None:
                    return None
                    
                _, speeds = presets[preset_idx]
                base_speed_x = speeds["speed_x"]
                base_speed_y = speeds["speed_y"]
                base_speed_z = speeds["speed_z"]
                
            elif config_choice == 1:  # Función personalizada - Acceso directo a escribir expresión
                print("\n📝 FUNCIÓN PERSONALIZADA")
                print("\nEscriba expresiones matemáticas para cada eje.")
                print("Variables: t (tiempo), theta (ángulo), pi, e")
                print("Funciones: sin, cos, tan, exp, log, sqrt, abs, min, max")
                print("\nEjemplos de expresiones:")
                print("  • Circle: X=sin(t), Y=cos(t), Z=0")
                print("  • Spiral: X=t*cos(5*t), Y=t*sin(5*t), Z=t*0.5")
                print("  • Lissajous: X=sin(3*t), Y=sin(2*t), Z=sin(4*t)*0.5")
                print("  • Wave: X=t, Y=sin(t*4), Z=cos(t*2)*0.5")
                
                expr_x = input("\nExpresión para velocidad X [sin(t)]: ").strip() or "sin(t)"
                expr_y = input("Expresión para velocidad Y [cos(t)]: ").strip() or "cos(t)"
                expr_z = input("Expresión para velocidad Z [0]: ").strip() or "0"
                
                # Crear función temporal y evaluar
                try:
                    from ..core.custom_motion_functions import CustomMotionFunction
                    temp_func = CustomMotionFunction(
                        "temp",
                        expr_x, expr_y, expr_z,
                        "Función temporal"
                    )
                    
                    # Evaluar en t=0.5 para obtener velocidades base
                    result = temp_func.evaluate(0.5)
                    base_speed_x = float(result[0])
                    base_speed_y = float(result[1])
                    base_speed_z = float(result[2])
                    
                    self.ui.show_success("✅ Expresiones válidas")
                    
                except Exception as e:
                    self.ui.show_error(f"Error en expresión: {e}")
                    return None
            
            # AJUSTE DE VELOCIDAD Y PROFUNDIDAD (aplicado a cualquier método)
            print("\n🎚️ AJUSTE DE INTENSIDAD")
            speed_multiplier = self.ui.get_numeric_input("Velocidad de rotación (-10.0-10.0): ", -10.0, 10.0) or 1.0
            depth = self.ui.get_numeric_input("Profundidad/Magnitud (0-100%): ", 0, 100) or 100
            
            # Aplicar ajustes
            depth_factor = depth / 100.0
            speed_x = base_speed_x * speed_multiplier * depth_factor
            speed_y = base_speed_y * speed_multiplier * depth_factor
            speed_z = base_speed_z * speed_multiplier * depth_factor
            
            return SemanticCommand(
                intent=IntentType.APPLY_ROTATION,
                parameters={
                    "target": self.selected_macro,
                    "rotation_params": {
                        "type": "algorithmic",
                        "speed_x": speed_x,
                        "speed_y": speed_y,
                        "speed_z": speed_z
                    }
                },
                source="interactive_cli"
            )
        else:  # Manual
            yaw = self.ui.get_numeric_input("Yaw (grados): ", -180, 180) or 0
            pitch = self.ui.get_numeric_input("Pitch (grados): ", -90, 90) or 0
            roll = self.ui.get_numeric_input("Roll (grados): ", -180, 180) or 0
            
            import math
            return SemanticCommand(
                intent=IntentType.APPLY_ROTATION,
                parameters={
                    "target": self.selected_macro,
                    "rotation_params": {
                        "type": "manual",
                        "yaw": math.radians(yaw),
                        "pitch": math.radians(pitch),
                        "roll": math.radians(roll),
                        "instant": True  # Rotación instantánea sin interpolación
                    }
                },
                source="interactive_cli"
            )
    
    def _create_individual_rotation_command(self, algorithmic=False, manual=False) -> Optional[SemanticCommand]:
        """Crea comando de rotación individual"""
        self.ui.show_info("Configuración de rotación individual")
        
        # Si se especifica el tipo directamente, usarlo
        if algorithmic:
            rotation_type = 0
        elif manual:
            rotation_type = 1
        else:
            # Si no se especifica, preguntar
            rotation_type = self.ui.get_choice_from_list(
                ["Algorítmica (continua)", "Manual (posición específica)"],
                "Tipo de rotación:"
            )
            
            if rotation_type is None:
                return None
        
        # TODO: Implementar la lógica completa similar a macro rotation
        self.ui.show_warning("Rotación individual en desarrollo")
        return None
    
    def _configure_movement_modes(self):
        """Configura modos de movimiento"""
        self.ui.show_info("Modos de movimiento")
        modes = ["stop", "fix", "random", "vibration", "spin"]
        mode_idx = self.ui.get_choice_from_list(modes, "Seleccione modo:")
        
        if mode_idx is not None:
            self.ui.show_success(f"Modo '{modes[mode_idx]}' aplicado")
            # TODO: Implementar comando real
    
    # ========== MODULACIÓN 3D ==========
    
    def _apply_modulation_preset(self):
        """Aplica preset de modulación"""
        presets = [
            "respiración_suave",
            "nervioso_aleatorio",
            "espiral_cósmica",
            "lissajous_complejo",
            "péndulo_hipnótico"
        ]
        
        preset_idx = self.ui.get_choice_from_list(presets, "Seleccione preset:")
        if preset_idx is None:
            return
            
        command = SemanticCommand(
            intent=IntentType.APPLY_MODULATION,
            parameters={
                "target": self.selected_macro,
                "preset": presets[preset_idx]
            },
            source="interactive_cli"
        )
        
        self._execute_command(command)
    
    def _adjust_modulation_intensity(self):
        """Ajusta intensidad de modulación"""
        intensity = self.ui.get_numeric_input(
            "Intensidad (0-100%): ", 0, 100
        )
        
        if intensity is not None:
            command = SemanticCommand(
                intent=IntentType.SET_MODULATION_INTENSITY,
                parameters={
                    "target": self.selected_macro,
                    "intensity": intensity / 100.0
                },
                source="interactive_cli"
            )
            self._execute_command(command)
    
    def _configure_modulation_lfo(self):
        """Configura LFO de modulación"""
        lfo = self.ui.get_numeric_input(
            "Frecuencia LFO (Hz): ", 0.1, 10
        )
        
        if lfo is not None:
            # TODO: Crear comando apropiado
            self.ui.show_success(f"LFO configurado a {lfo} Hz")
    
    def _interpolate_modulation_presets(self):
        """Interpola entre presets de modulación"""
        self.ui.show_warning("Interpolación de presets en desarrollo")
    
    def _toggle_modulation(self):
        """Activa/desactiva modulación"""
        # TODO: Implementar toggle real
        self.ui.show_success("Modulación toggle")
    
    def _edit_active_rotations(self):
        """Edita las rotaciones activas del macro seleccionado"""
        if not self.selected_macro:
            self.ui.show_error("No hay macro seleccionado")
            return
            
        # Obtener información del macro
        macro_info = self.engine.select_macro(self.selected_macro)
        if not macro_info:
            self.ui.show_error("Macro no encontrado")
            return
            
        # Buscar rotaciones activas en las fuentes del macro
        active_rotations = []
        
        for source_id in macro_info['sources']:
            if source_id in self.engine.motion_states:
                motion = self.engine.motion_states[source_id]
                
                # Verificar rotación algorítmica de macro
                if 'macro_rotation' in motion.active_components:
                    rotation = motion.active_components['macro_rotation']
                    if rotation.enabled:
                        active_rotations.append({
                            'type': 'algorítmica',
                            'component': rotation,
                            'source_id': source_id
                        })
                        break  # Solo necesitamos una referencia
                        
                # Verificar rotación manual de macro
                if 'manual_macro_rotation' in motion.active_components:
                    rotation = motion.active_components['manual_macro_rotation']
                    if rotation.enabled:
                        active_rotations.append({
                            'type': 'manual',
                            'component': rotation,
                            'source_id': source_id
                        })
                        break
        
        if not active_rotations:
            self.ui.show_info("No hay rotaciones activas en este macro")
            return
            
        # Mostrar rotaciones activas
        self.ui.show_info("\n🌀 Rotaciones activas en el macro:")
        options = []
        
        for i, rot_info in enumerate(active_rotations):
            rotation = rot_info['component']
            if rot_info['type'] == 'algorítmica':
                desc = f"Algorítmica - Velocidades: X={rotation.speed_x:.2f}, Y={rotation.speed_y:.2f}, Z={rotation.speed_z:.2f} rad/s"
            else:
                desc = f"Manual - Interpolando hacia objetivo"
            options.append((str(i+1), desc))
            
        options.extend([
            ("-", ""),
            ("b", "Volver")
        ])
        
        choice = self.ui.get_choice_from_list([opt[1] for opt in options if opt[0] != "-"], "Seleccione rotación a editar:")
        
        if choice is None or choice >= len(active_rotations):
            return
            
        # Editar la rotación seleccionada
        rot_info = active_rotations[choice]
        rotation = rot_info['component']
        
        if rot_info['type'] == 'algorítmica':
            self._edit_algorithmic_rotation(rotation)
        else:
            self.ui.show_info("La edición de rotaciones manuales no está implementada aún")
    
    def _edit_algorithmic_rotation(self, rotation):
        """Edita una rotación algorítmica activa"""
        self.ui.show_info("\n📝 Editar velocidades de rotación (Enter para mantener valor actual)")
        
        # Mostrar valores actuales
        print(f"\n  Valores actuales:")
        print(f"  X: {rotation.speed_x:.3f} rad/s")
        print(f"  Y: {rotation.speed_y:.3f} rad/s")
        print(f"  Z: {rotation.speed_z:.3f} rad/s")
        
        # Pedir nuevos valores
        new_x = self.ui.get_numeric_input(f"Nueva velocidad X [{rotation.speed_x:.3f}]: ", -5, 5)
        if new_x is None:
            new_x = rotation.speed_x
            
        new_y = self.ui.get_numeric_input(f"Nueva velocidad Y [{rotation.speed_y:.3f}]: ", -5, 5)
        if new_y is None:
            new_y = rotation.speed_y
            
        new_z = self.ui.get_numeric_input(f"Nueva velocidad Z [{rotation.speed_z:.3f}]: ", -5, 5)
        if new_z is None:
            new_z = rotation.speed_z
        
        # Actualizar la rotación usando el método del engine
        self.engine.set_macro_rotation(
            self.selected_macro,
            speed_x=new_x,
            speed_y=new_y,
            speed_z=new_z
        )
        
        self.ui.show_success(f"✅ Velocidades actualizadas: X={new_x:.3f}, Y={new_y:.3f}, Z={new_z:.3f}")
    
    # ========== UTILIDADES ==========
    
    def _execute_command(self, command: SemanticCommand) -> Any:
        """Ejecuta un comando y muestra el resultado"""
        self.command_history.append(command)
        
        result = self.command_processor.execute(command)
        
        if result.success:
            self.ui.show_success(result.message)
        else:
            self.ui.show_error(result.message)
            if result.error:
                logger.error(f"Error detalle: {result.error}")
                
        return result
    
    def _ensure_macro_selected(self) -> bool:
        """Verifica que haya un macro seleccionado"""
        if not self.selected_macro:
            self.ui.show_warning("Primero debe crear o seleccionar un macro")
            
            # Ofrecer crear uno rápido
            if self.ui.get_yes_no("¿Desea crear un macro ahora?"):
                self._create_macro_wizard()
                
        return self.selected_macro is not None
    
    def _confirm_exit(self) -> bool:
        """Confirma salida del programa"""
        return self.ui.get_yes_no("¿Está seguro que desea salir?")
    
    # ========== INFORMACIÓN DEL SISTEMA ==========
    
    def _show_system_status(self):
        """Muestra estado del sistema"""
        self.ui.show_header("ESTADO DEL SISTEMA")
        
        info = [
            f"Motor: {self.engine.__class__.__name__}",
            f"Fuentes máximas: {self.engine.max_sources}",
            f"FPS objetivo: {self.engine.fps}",
            f"Macros activos: {len(self.engine._macros)}",
            f"Sistema de deltas: ✅ Activo",
            f"Modulador 3D: {'✅ Activo' if hasattr(self.engine, 'enable_modulator') else '❌ Inactivo'}"
        ]
        
        for line in info:
            print(f"  {line}")
            
        self.ui.pause()
    
    def _list_active_macros(self):
        """Lista macros activos usando engine.list_macros()"""
        self.ui.show_header("MACROS ACTIVOS")
        
        macros = self.engine.list_macros()
        
        if not macros:
            self.ui.show_info("No hay macros activos")
        else:
            print(f"\n  Total: {len(macros)} macros\n")
            for i, macro in enumerate(macros):
                status = "✅" if macro['key'] == self.selected_macro else "  "
                print(f"  {status} [{i+1}] {macro['name']}")
                print(f"       Sources: {macro['num_sources']} | Formation: {macro['formation']}")
                
        self.ui.pause()
    
    def _show_macro_info(self):
        """Muestra información detallada del macro seleccionado"""
        self.ui.show_header("INFORMACIÓN DEL MACRO")
        
        if not self.selected_macro:
            self.ui.show_info("No hay ningún macro seleccionado")
            self.ui.show_info("Use 'Seleccionar Macro' primero")
            self.ui.pause()
            return
            
        # Obtener información del macro
        macros = self.engine.list_macros()
        macro_info = None
        
        for macro in macros:
            if macro['key'] == self.selected_macro:
                macro_info = macro
                break
                
        if not macro_info:
            self.ui.show_error(f"Macro '{self.selected_macro}' no encontrado")
            self.ui.pause()
            return
            
        # Mostrar información detallada
        print(f"\n  📋 Macro: {macro_info['name']}")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n  ID Interno: {macro_info['key']}")
        print(f"  Formación: {macro_info['formation'].upper()}")
        print(f"  Comportamiento: {macro_info['behavior']}")
        print(f"  Número de sources: {macro_info['num_sources']}")
        
        if macro_info['source_ids']:
            print(f"\n  Sources IDs: {', '.join(map(str, macro_info['source_ids'][:10]))}")
            if len(macro_info['source_ids']) > 10:
                print(f"  ... y {len(macro_info['source_ids']) - 10} más")
                
        # Obtener estado de componentes activos si es posible
        try:
            # Intentar obtener información adicional del engine
            if hasattr(self.engine, 'get_macro_state'):
                state = self.engine.get_macro_state(self.selected_macro)
                if state:
                    print(f"\n  Estado: {state.get('status', 'Activo')}")
                    if 'components' in state:
                        print(f"  Componentes activos: {len(state['components'])}")
        except:
            pass
            
        print("\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.pause()
    
    def _adjust_macro_spacing(self):
        """Ajusta el spacing de un macro existente"""
        if not self._ensure_macro_selected():
            return
            
        self.ui.show_header("AJUSTAR DISTANCIA (SPACING)")
        
        # Obtener información del macro actual usando select_macro que acepta nombres
        macro_info = self.engine.select_macro(self.selected_macro)
        if not macro_info:
            self.ui.show_error("No se pudo obtener información del macro")
            return
            
        # Asegurarse de usar el key completo para adjust_macro_spacing
        macro_key = macro_info['key']
            
        print(f"\n  Macro: {macro_info['name']}")
        print(f"  Formación: {macro_info['formation']}")
        
        # Obtener el spacing actual si está disponible
        current_spacing = macro_info.get('spacing', 2.0)  # Usar el spacing del macro_info
            
        print(f"  Spacing actual: {current_spacing:.2f}")
        
        # Solicitar nuevo spacing según el tipo de formación
        formation = macro_info['formation']
        print(f"\n  Nuevo spacing para formación {formation.upper()}:")
        
        if formation == "circle":
            new_spacing = self.ui.get_numeric_input("  Radio del círculo (1-10): ", 1.0, 10.0)
        elif formation == "line":
            new_spacing = self.ui.get_numeric_input("  Separación entre fuentes (0.5-5): ", 0.5, 5.0)
        elif formation == "grid":
            new_spacing = self.ui.get_numeric_input("  Separación de la cuadrícula (0.5-5): ", 0.5, 5.0)
        elif formation == "spiral":
            new_spacing = self.ui.get_numeric_input("  Factor de expansión (0.5-5): ", 0.5, 5.0)
        elif formation == "sphere":
            new_spacing = self.ui.get_numeric_input("  Radio de la esfera (1-10): ", 1.0, 10.0)
        elif formation == "random":
            new_spacing = self.ui.get_numeric_input("  Concentración (0.5-5.0): ", 0.5, 5.0)
        else:  # custom u otros
            new_spacing = self.ui.get_numeric_input("  Factor de escala (0.5-5): ", 0.5, 5.0)
            
        if new_spacing is None:
            self.ui.show_info("Operación cancelada")
            return
            
        # Aplicar el nuevo spacing usando el key completo
        try:
            if self.engine.adjust_macro_spacing(macro_key, new_spacing):
                self.ui.show_success(f"Spacing ajustado a {new_spacing:.2f}")
            else:
                self.ui.show_error("No se pudo ajustar el spacing")
        except Exception as e:
            self.ui.show_error(f"Error al ajustar spacing: {str(e)}")
            
        self.ui.pause()
    
    def _move_macro_position(self):
        """Mueve la posición de un macro con interfaz intuitiva"""
        if not self._ensure_macro_selected():
            return
            
        self.ui.show_header("MOVER POSICIÓN DEL MACRO")
        
        # Obtener información del macro
        macro_info = self.engine.select_macro(self.selected_macro)
        if not macro_info:
            self.ui.show_error("No se pudo obtener información del macro")
            return
            
        macro_key = macro_info['key']
        
        # Obtener centro actual
        current_center = self.engine.get_macro_center(macro_key)
        if current_center is None:
            self.ui.show_error("No se pudo obtener la posición actual")
            return
            
        print(f"\n  Macro: {macro_info['name']}")
        print(f"  Posición actual: X={current_center[0]:.2f}, Y={current_center[1]:.2f}, Z={current_center[2]:.2f}")
        
        # Ir directamente al control interactivo unificado
        new_position = self._unified_interactive_movement(macro_key, current_center)
            
        # Aplicar la nueva posición si se obtuvo
        if new_position is not None:
            try:
                if self.engine.move_macro_center(macro_key, new_position):
                    self.ui.show_success(
                        f"Macro movido a: X={new_position[0]:.2f}, "
                        f"Y={new_position[1]:.2f}, Z={new_position[2]:.2f}"
                    )
                else:
                    self.ui.show_error("No se pudo mover el macro")
            except Exception as e:
                self.ui.show_error(f"Error al mover macro: {str(e)}")
                
        self.ui.pause()
    
    def _select_preset_position(self):
        """Selecciona una posición predefinida"""
        import numpy as np
        
        presets = [
            ("Centro", np.array([0.0, 0.0, 0.0])),
            ("Frente (5m)", np.array([0.0, 0.0, 5.0])),
            ("Atrás (5m)", np.array([0.0, 0.0, -5.0])),
            ("Izquierda (5m)", np.array([-5.0, 0.0, 0.0])),
            ("Derecha (5m)", np.array([5.0, 0.0, 0.0])),
            ("Arriba (3m)", np.array([0.0, 3.0, 0.0])),
            ("Esquina frontal-derecha", np.array([4.0, 0.0, 4.0])),
            ("Esquina frontal-izquierda", np.array([-4.0, 0.0, 4.0])),
            ("Órbita 1 (radio 8m)", np.array([8.0, 2.0, 0.0])),
            ("Órbita 2 (45°)", np.array([5.66, 2.0, 5.66])),
            ("Órbita 3 (90°)", np.array([0.0, 2.0, 8.0])),
            ("Órbita 4 (135°)", np.array([-5.66, 2.0, 5.66]))
        ]
        
        print("\n  POSICIONES PREDEFINIDAS:")
        for i, (name, _) in enumerate(presets):
            print(f"  {i+1:2}. {name}")
            
        choice = self.ui.get_numeric_input("\n  Selección (1-12): ", 1, 12)
        if choice is None:
            return None
            
        return presets[int(choice)-1][1]
    
    
    def _unified_interactive_movement(self, macro_key, start_position):
        """Control unificado con teclado numérico y presets"""
        import numpy as np
        
        print("\n  🎮 CONTROL DE POSICIÓN")
        print("\n  Movimiento (Teclado Numérico):")
        print("  4/6: ← → (X)    8/2: ↑ ↓ (Z)    7/9: ▲ ▼ (Y)    5: Reset")
        print("\n  Modos especiales (presionar para activar/desactivar):")
        print("  S: Activar modo esférico → 4/6: Azimut, 8/2: Distancia, 7/9: Elevación")
        print("  A: Activar ajuste fino (paso 0.1m)")
        print("\n  Presets Rápidos (P + número):")
        print("  P+1: Centro    P+2: Frente    P+3: Derecha    P+4: Atrás    P+5: Izquierda")
        print("  P+6: Arriba    P+7: Esq.FD    P+8: Esq.FI     P+9: Órbita    P+0: Lateral")
        print("\n  Otros:")
        print("  +/-: Cambiar paso    ENTER: Confirmar    ESC/X: Cancelar")
        
        # Intentar usar captura de teclas en tiempo real
        try:
            return self._realtime_unified_movement(macro_key, start_position)
        except ImportError:
            print("\n  ⚠️  Modo tiempo real no disponible")
            self.ui.show_info("Se requiere soporte de terminal para control interactivo")
            return None
    
    def _realtime_keyboard_movement(self, macro_key, start_position, initial_step):
        """Movimiento con captura de teclas en tiempo real"""
        import numpy as np
        
        # Intentar importar bibliotecas necesarias
        try:
            import sys
            import termios
            import tty
            import select
        except ImportError:
            raise ImportError("Bibliotecas de terminal no disponibles")
        
        position = start_position.copy()
        step_size = initial_step
        
        # Guardar configuración terminal
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            # Configurar terminal para captura inmediata
            tty.setraw(sys.stdin.fileno())
            
            # Mostrar posición inicial
            self._print_position_status(position, step_size)
            
            while True:
                # Verificar si hay tecla disponible
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    
                    # Procesar tecla
                    if key == '\n' or key == '\r':  # Enter
                        print("\n\n  ✅ Posición confirmada")
                        return position
                    elif key == '\x1b' or key.lower() == 'x':  # ESC o X
                        print("\n\n  ❌ Cancelado")
                        return None
                    elif key.lower() == 'q':  # Izquierda
                        position[0] -= step_size
                        self._update_and_show(macro_key, position, step_size)
                    elif key.lower() == 'a':  # Derecha
                        position[0] += step_size
                        self._update_and_show(macro_key, position, step_size)
                    elif key.lower() == 'w':  # Adelante
                        position[2] += step_size
                        self._update_and_show(macro_key, position, step_size)
                    elif key.lower() == 's':  # Atrás
                        position[2] -= step_size
                        self._update_and_show(macro_key, position, step_size)
                    elif key.lower() == 'e':  # Arriba
                        position[1] += step_size
                        self._update_and_show(macro_key, position, step_size)
                    elif key.lower() == 'd':  # Abajo
                        position[1] -= step_size
                        self._update_and_show(macro_key, position, step_size)
                    elif key == '+':
                        step_size = min(step_size * 2, 10.0)
                        self._print_position_status(position, step_size)
                    elif key == '-':
                        step_size = max(step_size / 2, 0.1)
                        self._print_position_status(position, step_size)
                    elif key.lower() == 'r':  # Reset
                        position = np.array([0.0, 0.0, 0.0])
                        self._update_and_show(macro_key, position, step_size)
                        
        finally:
            # Restaurar configuración terminal
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print()  # Nueva línea final
    
    def _command_based_movement(self, macro_key, start_position, initial_step):
        """Movimiento basado en comandos (fallback)"""
        import numpy as np
        
        position = start_position.copy()
        step_size = initial_step
        
        print("\n  (Presione una tecla + ENTER para mover)")
        
        while True:
            # Mostrar posición actual
            print(f"\n  Posición: X={position[0]:.2f} Y={position[1]:.2f} Z={position[2]:.2f}")
            print(f"  Paso: {step_size:.1f}m")
            
            # Obtener comando
            cmd = self.ui.get_input("\n  Tecla: ").lower()
            
            if not cmd:
                continue
                
            # Tomar solo el primer carácter
            char = cmd[0]
            
            if char == '\n' or char == '\r':
                if self.ui.get_yes_no("\n  ¿Confirmar esta posición?"):
                    return position
                else:
                    continue
            elif char == 'x':
                return None
            elif char == 'q':  # Izquierda
                position[0] -= step_size
            elif char == 'a':  # Derecha
                position[0] += step_size
            elif char == 'w':  # Adelante
                position[2] += step_size
            elif char == 's':  # Atrás
                position[2] -= step_size
            elif char == 'e':  # Arriba
                position[1] += step_size
            elif char == 'd':  # Abajo
                position[1] -= step_size
            elif char == '+':
                step_size = min(step_size * 2, 10.0)
            elif char == '-':
                step_size = max(step_size / 2, 0.1)
            elif char == 'r':  # Reset
                position = np.array([0.0, 0.0, 0.0])
                
            # Actualizar posición inmediatamente
            try:
                self.engine.move_macro_center(macro_key, position)
            except Exception as e:
                self.ui.show_error(f"Error al mover: {str(e)}")
    
    def _update_and_show(self, macro_key, position, step_size):
        """Actualiza la posición y muestra el estado"""
        try:
            self.engine.move_macro_center(macro_key, position)
            self._print_position_status(position, step_size)
        except Exception as e:
            print(f"\n  ❌ Error: {str(e)}")
    
    def _print_position_status(self, position, step_size):
        """Imprime el estado actual de la posición"""
        # Usar retorno de carro para sobrescribir la línea
        print(f"\r  Pos: X={position[0]:6.2f} Y={position[1]:6.2f} Z={position[2]:6.2f} | Paso: {step_size:4.1f}m", 
              end='', flush=True)
    
    def _realtime_unified_movement(self, macro_key, start_position):
        """Movimiento unificado con teclado numérico y presets"""
        import numpy as np
        import sys
        import termios
        import tty
        import select
        import time
        
        position = start_position.copy()
        step_size = 1.0
        
        # Para modo esférico
        current_distance = np.linalg.norm(position[[0, 2]])
        current_azimuth = np.degrees(np.arctan2(position[2], position[0])) if current_distance > 0 else 0
        current_elevation = position[1]
        
        # Estado de modificadores
        s_mode = False  # Modo esférico
        a_mode = False  # Ajuste fino
        p_mode = False  # Modo preset
        
        # Definir presets con todas las posiciones
        presets = [
            np.array([0.0, 0.0, 0.0]),      # 1: Centro
            np.array([0.0, 0.0, 5.0]),      # 2: Frente
            np.array([5.0, 0.0, 0.0]),      # 3: Derecha
            np.array([0.0, 0.0, -5.0]),     # 4: Atrás
            np.array([-5.0, 0.0, 0.0]),     # 5: Izquierda
            np.array([0.0, 3.0, 0.0]),      # 6: Arriba
            np.array([4.0, 0.0, 4.0]),      # 7: Esquina frontal-derecha
            np.array([-4.0, 0.0, 4.0]),     # 8: Esquina frontal-izquierda
            np.array([0.0, 2.0, 8.0]),      # 9: Órbita frontal
            np.array([8.0, 2.0, 0.0])       # 0: Órbita derecha
        ]
        
        # Guardar configuración terminal
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            # Configurar terminal para captura inmediata
            tty.setraw(sys.stdin.fileno())
            
            # Mostrar estado inicial
            self._print_position_info(position, step_size, False)
            
            while True:
                if select.select([sys.stdin], [], [], 0.01)[0]:  # Timeout más pequeño para respuesta rápida
                    char = sys.stdin.read(1)
                    
                    # Manejar ESC
                    if char == '\x1b':
                        print("\n\n  ❌ Cancelado")
                        return None
                    
                    # Enter - Confirmar
                    elif char == '\n' or char == '\r':
                        print("\n\n  ✅ Posición confirmada")
                        return position
                    
                    # Cancelar con X (sin importar mayúsculas)
                    elif char.lower() == 'x':
                        print("\n\n  ❌ Cancelado")
                        return None
                    
                    # Detectar modificadores (toggle on/off)
                    elif char.lower() == 's':
                        s_mode = not s_mode  # Toggle modo esférico
                        a_mode = False  # Desactivar ajuste fino
                        p_mode = False  # Desactivar modo preset
                        self._print_position_info(position, step_size, s_mode)
                        continue
                    elif char.lower() == 'a':
                        a_mode = not a_mode  # Toggle ajuste fino
                        s_mode = False  # Desactivar modo esférico
                        p_mode = False  # Desactivar modo preset
                        self._print_position_info(position, step_size, s_mode)
                        continue
                    elif char.lower() == 'p':
                        p_mode = not p_mode  # Toggle modo preset
                        s_mode = False  # Desactivar modo esférico
                        a_mode = False  # Desactivar ajuste fino
                        if p_mode:
                            print("\r  [MODO PRESET] Presiona 0-9 para seleccionar preset", end='', flush=True)
                        else:
                            self._print_position_info(position, step_size, s_mode)
                        continue
                    
                    # Presets con P + número
                    elif p_mode and char in '0123456789':
                        preset_idx = int(char)
                        # Mapear 0 a índice 9
                        if preset_idx == 0:
                            preset_idx = 9
                        else:
                            preset_idx -= 1  # Convertir 1-9 a índices 0-8
                            
                        if 0 <= preset_idx < len(presets):
                            position = presets[preset_idx].copy()
                            # Actualizar valores esféricos
                            current_distance = np.linalg.norm(position[[0, 2]])
                            current_azimuth = np.degrees(np.arctan2(position[2], position[0])) if current_distance > 0 else 0
                            current_elevation = position[1]
                            self._update_and_show(macro_key, position, step_size)
                            
                        # Desactivar modo preset después de usar
                        p_mode = False
                        self._print_position_info(position, step_size, s_mode)
                    
                    # Movimiento con teclado numérico
                    else:
                        # Determinar paso actual basado en el modo
                        current_step = 0.1 if a_mode else step_size
                        moved = False
                        
                        if s_mode:  # Modo esférico activo
                            if char == '4':  # Azimut izquierda
                                current_azimuth -= 10 * current_step
                                moved = True
                            elif char == '6':  # Azimut derecha
                                current_azimuth += 10 * current_step
                                moved = True
                            elif char == '8':  # Distancia aumentar
                                current_distance += current_step
                                moved = True
                            elif char == '2':  # Distancia disminuir
                                current_distance = max(0.1, current_distance - current_step)
                                moved = True
                            elif char == '7':  # Elevación arriba
                                current_elevation += current_step
                                moved = True
                            elif char == '9':  # Elevación abajo
                                current_elevation -= current_step
                                moved = True
                            
                            if moved:
                                new_pos = self._update_spherical(macro_key, current_distance, current_azimuth, current_elevation)
                                if new_pos is not None:
                                    position = new_pos
                                self._print_position_info(position, step_size, True)
                        
                        elif char in '4567892+-':  # Movimiento normal o con ajuste fino
                            if char == '4':  # Izquierda
                                position[0] -= current_step
                                moved = True
                            elif char == '6':  # Derecha
                                position[0] += current_step
                                moved = True
                            elif char == '8':  # Adelante
                                position[2] += current_step
                                moved = True
                            elif char == '2':  # Atrás
                                position[2] -= current_step
                                moved = True
                            elif char == '7':  # Arriba
                                position[1] += current_step
                                moved = True
                            elif char == '9':  # Abajo
                                position[1] -= current_step
                                moved = True
                            elif char == '5':  # Reset
                                position = np.array([0.0, 0.0, 0.0])
                                current_distance = 0
                                current_azimuth = 0
                                current_elevation = 0
                                moved = True
                            elif char == '+':
                                step_size = min(step_size * 2, 10.0)
                                self._print_position_info(position, step_size, s_mode)
                            elif char == '-':
                                step_size = max(step_size / 2, 0.1)
                                self._print_position_info(position, step_size, s_mode)
                            
                            if moved:
                                self._update_and_show(macro_key, position, current_step)
                                # Actualizar valores esféricos
                                current_distance = np.linalg.norm(position[[0, 2]])
                                current_azimuth = np.degrees(np.arctan2(position[2], position[0])) if current_distance > 0 else 0
                                current_elevation = position[1]
                        
                        # Si no se reconoció el carácter (solo en modo normal)
                        if not moved and char not in '+-' and not char.isspace() and not p_mode:
                            # Solo mostrar debug para caracteres realmente no esperados
                            if char not in 'sapSAP' and ord(char) > 32:  # Ignorar teclas de control
                                print(f"\n  [DEBUG] Tecla '{char}' (ord={ord(char)}) no reconocida")
                                
                        
        finally:
            # Restaurar configuración terminal
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print()
    
    def _print_position_info(self, position, step_size, spherical_mode):
        """Imprime información de posición actual"""
        import numpy as np
        
        if spherical_mode:
            distance = np.linalg.norm(position[[0, 2]])
            azimuth = np.degrees(np.arctan2(position[2], position[0])) if distance > 0 else 0
            print(f"\r  [ESFÉRICO] Dist: {distance:5.2f}m | Azimut: {azimuth:6.1f}° | Elev: {position[1]:5.2f}m | Paso: {step_size:4.1f}m", 
                  end='', flush=True)
        else:
            print(f"\r  [CARTESIANO] X: {position[0]:6.2f} Y: {position[1]:6.2f} Z: {position[2]:6.2f} | Paso: {step_size:4.1f}m", 
                  end='', flush=True)
    
    def _update_spherical(self, macro_key, distance, azimuth, elevation):
        """Actualiza posición desde coordenadas esféricas"""
        import numpy as np
        
        # Convertir a cartesianas
        azimuth_rad = np.radians(azimuth)
        x = distance * np.cos(azimuth_rad)
        z = distance * np.sin(azimuth_rad)
        position = np.array([x, elevation, z])
        
        try:
            self.engine.move_macro_center(macro_key, position)
            self._print_spherical_status(distance, azimuth, elevation)
            return position  # Retornar la posición actualizada
        except Exception as e:
            print(f"\n  ❌ Error: {str(e)}")
            return None
    
    def _print_unified_status(self, position, step_size, mode):
        """Imprime estado para control unificado"""
        if mode == "cartesian":
            print(f"\r  Pos: X={position[0]:6.2f} Y={position[1]:6.2f} Z={position[2]:6.2f} | Paso: {step_size:4.1f}m | Modo: Cartesiano", 
                  end='', flush=True)
        else:
            distance = np.linalg.norm(position[[0, 2]])
            azimuth = np.degrees(np.arctan2(position[2], position[0])) if distance > 0 else 0
            self._print_spherical_status(distance, azimuth, position[1])
    
    def _print_spherical_status(self, distance, azimuth, elevation):
        """Imprime estado en modo esférico"""
        print(f"\r  Dist: {distance:5.2f}m | Azimut: {azimuth:6.1f}° | Elev: {elevation:5.2f}m | Modo: Esférico", 
              end='', flush=True)
    
    def _delete_macro(self):
        """Elimina un macro seleccionado"""
        self.ui.show_header("ELIMINAR MACRO")
        
        # Obtener lista de macros
        macros = self.engine.list_macros()
        
        if not macros:
            self.ui.show_info("No hay macros para eliminar")
            self.ui.pause()
            return
        
        # Mostrar macros disponibles
        print("\n  Macros disponibles:\n")
        for i, macro in enumerate(macros):
            selected = "→" if macro['key'] == self.selected_macro else " "
            print(f"  {selected} [{i+1}] {macro['name']} ({macro['num_sources']} sources)")
        
        print("\n  [0] Cancelar")
        print("\n  Ingrese el número del macro a eliminar")
        
        # Solicitar selección
        try:
            choice = input("\n  Selección: ").strip()
            
            if choice == "0":
                self.ui.show_info("Eliminación cancelada")
                self.ui.pause()
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(macros):
                macro_to_delete = macros[idx]
                
                # Confirmar eliminación
                print(f"\n  ⚠️  CONFIRMAR ELIMINACIÓN")
                print(f"\n  Macro: {macro_to_delete['name']}")
                print(f"  Sources: {macro_to_delete['num_sources']}")
                print(f"  IDs: {macro_to_delete['source_ids'][:5]}{'...' if len(macro_to_delete['source_ids']) > 5 else ''}")
                
                confirm = input("\n  ¿Confirmar eliminación? (s/n): ").strip().lower()
                
                if confirm == 's':
                    # Eliminar usando el engine
                    if self.engine.delete_macro(macro_to_delete['key']):
                        self.ui.show_success(f"Macro '{macro_to_delete['name']}' eliminado correctamente")
                        
                        # Si era el macro seleccionado, limpiar selección
                        if self.selected_macro == macro_to_delete['key']:
                            self.selected_macro = None
                            self.ui.show_info("Selección de macro limpiada")
                    else:
                        self.ui.show_error("Error al eliminar el macro")
                else:
                    self.ui.show_info("Eliminación cancelada")
            else:
                self.ui.show_error("Número inválido")
                
        except ValueError:
            self.ui.show_error("Entrada inválida - debe ser un número")
        except Exception as e:
            self.ui.show_error(f"Error: {str(e)}")
        
        self.ui.pause()
    
    def _toggle_macro_enabled(self):
        """Activa o desactiva un macro"""
        if not self._ensure_macro_selected():
            return
        
        self.ui.show_header("ACTIVAR/DESACTIVAR MACRO")
        
        # Obtener información del macro
        macro_info = self.engine.select_macro(self.selected_macro)
        if not macro_info:
            self.ui.show_error("No se pudo obtener información del macro")
            return
        
        # Verificar estado actual
        is_enabled = self.engine.is_macro_enabled(self.selected_macro)
        status_actual = "ACTIVADO" if is_enabled else "DESACTIVADO"
        
        print(f"\n  Macro: {macro_info['name']}")
        print(f"  Fuentes: {macro_info['num_sources']}")
        print(f"  Estado actual: {status_actual}")
        
        # Preguntar acción
        if is_enabled:
            print("\n  Al desactivar:")
            print("  • Las fuentes se mutearán (sin audio)")
            print("  • Las fuentes se desactivarán en SPAT")
            print("  • Se guardará el estado actual")
            
            if self.ui.get_yes_no("\n  ¿Desactivar el macro?"):
                if self.engine.enable_macro(self.selected_macro, False):
                    self.ui.show_success("Macro desactivado y muteado")
                else:
                    self.ui.show_error("Error al desactivar el macro")
        else:
            print("\n  Al activar:")
            print("  • Las fuentes volverán a su posición guardada")
            print("  • Las fuentes se activarán en SPAT")
            print("  • El audio se desmuteará")
            
            if self.ui.get_yes_no("\n  ¿Activar el macro?"):
                if self.engine.enable_macro(self.selected_macro, True):
                    self.ui.show_success("Macro activado y desmuteado")
                else:
                    self.ui.show_error("Error al activar el macro")
        
        self.ui.pause()
    
    def _toggle_macro_mute(self):
        """Mutea o desmutea un macro en SPAT"""
        if not self._ensure_macro_selected():
            return
        
        self.ui.show_header("MUTEAR/DESMUTEAR MACRO")
        
        # Obtener información del macro
        macro_info = self.engine.select_macro(self.selected_macro)
        if not macro_info:
            self.ui.show_error("No se pudo obtener información del macro")
            return
        
        print(f"\n  Macro: {macro_info['name']}")
        print(f"  Fuentes: {macro_info['num_sources']}")
        print("\n  Opciones:")
        print("  1. Mutear (silenciar audio)")
        print("  2. Desmutear (activar audio)")
        print("  0. Cancelar")
        
        choice = self.ui.get_input("\n  Selección: ")
        
        if choice == "1":
            if self.engine.mute_macro(self.selected_macro, True):
                self.ui.show_success("Macro muteado")
            else:
                self.ui.show_error("Error al mutear el macro")
        elif choice == "2":
            if self.engine.mute_macro(self.selected_macro, False):
                self.ui.show_success("Macro desmuteado")
            else:
                self.ui.show_error("Error al desmutear el macro")
        else:
            self.ui.show_info("Operación cancelada")
        
        self.ui.pause()
    
    def _show_osc_status(self):
        """Muestra el estado de la conexión OSC"""
        self.ui.show_header("ESTADO OSC")
        
        # Obtener información del OSC bridge
        osc_bridge = self.engine.osc_bridge
        
        print(f"\n  🔌 Conexión OSC")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if osc_bridge:
            print(f"\n  Estado: {'✅ Conectado' if hasattr(osc_bridge, 'client') else '❌ Desconectado'}")
            print(f"  Host: {osc_bridge.host if hasattr(osc_bridge, 'host') else 'No configurado'}")
            print(f"  Puerto: {osc_bridge.port if hasattr(osc_bridge, 'port') else 'No configurado'}")
            print(f"\n  Targets configurados: {len(osc_bridge.targets) if hasattr(osc_bridge, 'targets') else 0}")
            
            if hasattr(osc_bridge, 'targets') and osc_bridge.targets:
                print("\n  Targets activos:")
                for target in osc_bridge.targets:
                    print(f"    • {target.name}: {target.host}:{target.port}")
                    
            # Estadísticas si están disponibles
            if hasattr(osc_bridge, 'message_count'):
                print(f"\n  Mensajes enviados: {osc_bridge.message_count}")
            if hasattr(osc_bridge, 'last_message_time'):
                print(f"  Último mensaje: {osc_bridge.last_message_time}")
        else:
            print("\n  ❌ OSC Bridge no inicializado")
            
        print("\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.pause()
    
    def _save_configuration(self):
        """Guarda la configuración actual"""
        self.ui.show_header("GUARDAR CONFIGURACIÓN")
        
        # Solicitar nombre para la configuración
        name = input("\n  Nombre de la configuración: ").strip()
        
        if not name:
            self.ui.show_error("Nombre no puede estar vacío")
            self.ui.pause()
            return
            
        try:
            # Crear diccionario de configuración
            config = {
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "selected_macro": self.selected_macro,
                "macros": self.engine.list_macros(),
                "engine_state": {
                    "total_sources": len(self.engine.sources),
                    "update_rate": self.engine.update_rate if hasattr(self.engine, 'update_rate') else 60
                }
            }
            
            # Guardar en archivo
            import json
            filename = f"config_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = f"saved_configs/{filename}"
            
            # Crear directorio si no existe
            import os
            os.makedirs("saved_configs", exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
                
            self.ui.show_success(f"Configuración guardada en: {filename}")
            
        except Exception as e:
            self.ui.show_error(f"Error al guardar configuración: {str(e)}")
            
        self.ui.pause()
    
    def _load_configuration(self):
        """Carga una configuración guardada"""
        self.ui.show_header("CARGAR CONFIGURACIÓN")
        
        try:
            import os
            import json
            
            # Listar configuraciones disponibles
            if not os.path.exists("saved_configs"):
                self.ui.show_info("No hay configuraciones guardadas")
                self.ui.pause()
                return
                
            configs = [f for f in os.listdir("saved_configs") if f.endswith('.json')]
            
            if not configs:
                self.ui.show_info("No hay configuraciones guardadas")
                self.ui.pause()
                return
                
            print("\n  Configuraciones disponibles:\n")
            for i, config in enumerate(configs):
                print(f"  [{i+1}] {config}")
                
            print("\n  [0] Cancelar")
            
            # Solicitar selección
            choice = input("\n  Selección: ").strip()
            
            if choice == "0":
                return
                
            idx = int(choice) - 1
            if 0 <= idx < len(configs):
                filepath = f"saved_configs/{configs[idx]}"
                
                with open(filepath, 'r') as f:
                    config = json.load(f)
                    
                self.ui.show_info(f"Cargando configuración: {config['name']}")
                self.ui.show_info(f"Creada: {config['timestamp']}")
                
                # Aplicar configuración
                if 'selected_macro' in config:
                    self.selected_macro = config['selected_macro']
                    self.ui.show_info(f"Macro seleccionado: {self.selected_macro}")
                    
                self.ui.show_success("Configuración cargada")
            else:
                self.ui.show_error("Selección inválida")
                
        except ValueError:
            self.ui.show_error("Entrada inválida")
        except Exception as e:
            self.ui.show_error(f"Error al cargar configuración: {str(e)}")
            
        self.ui.pause()

# ========== PUNTO DE ENTRADA ==========

def main():
    """Punto de entrada principal"""
    import sys
    import os
    
    # Añadir path del proyecto
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    from trajectory_hub.core.spat_osc_bridge import OSCTarget
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear engine
    print("🚀 Inicializando Trajectory Hub...")
    engine = EnhancedTrajectoryEngine(
        max_sources=100,
        fps=60,
        enable_modulator=True
    )
    
    # Configurar OSC
    target = OSCTarget(host="127.0.0.1", port=9000)
    # Verificar que osc_bridge existe
    if engine.osc_bridge is None:
        from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge
        engine.osc_bridge = SpatOSCBridge()
    # engine.osc_bridge.add_target(target)  # TEMPORALMENTE DESHABILITADO
    
    # Crear y ejecutar controlador
    controller = InteractiveController(engine)
    controller.run()
    
    print("\n👋 ¡Hasta luego!")


if __name__ == "__main__":
    main()
    def _select_macro(self):
        """Selecciona un macro activo"""
        self.ui.show_header("SELECCIONAR MACRO ACTIVO")
        
        # Obtener lista de macros
        macros = self.engine.list_macros()
        
        if not macros:
            self.ui.show_info("No hay macros disponibles")
            self.ui.pause()
            return
        
        # Mostrar macros
        print("\n  Macros disponibles:\n")
        for i, macro in enumerate(macros):
            current = "✅" if macro['key'] == self.selected_macro else "  "
            print(f"  {current} [{i+1}] {macro['name']} ({macro['num_sources']} sources)")
        
        print(f"\n  Macro actual: {self.selected_macro if self.selected_macro else 'Ninguno'}")
        print("\n  [0] Cancelar")
        
        try:
            choice = input("\n  Seleccionar macro (número): ").strip()
            
            if choice == "0":
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(macros):
                self.selected_macro = macros[idx]['key']
                self.ui.show_success(f"Macro '{macros[idx]['name']}' seleccionado")
            else:
                self.ui.show_error("Número inválido")
                
        except ValueError:
            self.ui.show_error("Entrada inválida")
        except Exception as e:
            self.ui.show_error(f"Error: {str(e)}")
        
        self.ui.pause()

