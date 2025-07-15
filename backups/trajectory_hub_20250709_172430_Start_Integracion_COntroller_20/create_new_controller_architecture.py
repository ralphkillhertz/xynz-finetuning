# === create_new_controller_architecture.py ===
# 🏗️ Creación de la nueva arquitectura modular
# ⚡ Transformación completa del sistema de control

import os
import shutil
from datetime import datetime

print("🏗️ CREANDO NUEVA ARQUITECTURA DE CONTROL")
print("=" * 60)

# 1. Backup del controlador actual
backup_dir = f"backup_controller_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)

controller_file = "trajectory_hub/interface/interactive_controller.py"
if os.path.exists(controller_file):
    shutil.copy2(controller_file, os.path.join(backup_dir, "interactive_controller_original.py"))
    print(f"✅ Backup creado en: {backup_dir}")

# 2. Crear estructura de directorios
print("\n📁 Creando estructura de directorios...")
directories = [
    "trajectory_hub/control",
    "trajectory_hub/control/semantic",
    "trajectory_hub/control/processors",
    "trajectory_hub/control/interfaces",
    "trajectory_hub/control/managers"
]

for dir_path in directories:
    os.makedirs(dir_path, exist_ok=True)
    init_file = os.path.join(dir_path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('"""Control system components"""\n')
    print(f"  ✅ {dir_path}")

# 3. Crear SemanticCommand y estructuras base
print("\n📝 Creando componentes semánticos...")

# === semantic_command.py ===
semantic_command_content = '''"""
Semantic Command System - Representa intenciones de alto nivel
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class IntentType(Enum):
    """Tipos de intenciones disponibles"""
    # Creación
    CREATE_MACRO = "create_macro"
    CREATE_SOURCES = "create_sources"
    
    # Movimiento
    SET_TRAJECTORY = "set_trajectory"
    SET_INDIVIDUAL_MOVEMENT = "set_individual_movement"
    APPLY_ROTATION = "apply_rotation"
    APPLY_CONCENTRATION = "apply_concentration"
    
    # Modulación
    APPLY_MODULATION = "apply_modulation"
    SET_MODULATION_INTENSITY = "set_modulation_intensity"
    
    # Comportamiento
    SET_BEHAVIOR = "set_behavior"
    APPLY_DEFORMATION = "apply_deformation"
    
    # Presets
    LOAD_PRESET = "load_preset"
    CREATE_COMPOSITION = "create_composition"
    
    # Control
    START_TIMELINE = "start_timeline"
    STOP_ALL = "stop_all"


@dataclass
class SemanticCommand:
    """Representa un comando de alto nivel"""
    intent: IntentType
    parameters: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    source: str = "unknown"  # "mcp", "gesture", "cli"
    timestamp: Optional[float] = None
    
    def validate(self) -> bool:
        """Valida que el comando tenga los parámetros necesarios"""
        required_params = {
            IntentType.CREATE_MACRO: ["name", "source_count"],
            IntentType.SET_TRAJECTORY: ["target", "trajectory_type"],
            IntentType.APPLY_ROTATION: ["target", "rotation_params"],
            # ... más validaciones
        }
        
        if self.intent in required_params:
            for param in required_params[self.intent]:
                if param not in self.parameters:
                    return False
        return True


@dataclass
class CommandResult:
    """Resultado de la ejecución de un comando"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
'''

with open("trajectory_hub/control/semantic/semantic_command.py", 'w') as f:
    f.write(semantic_command_content)
print("  ✅ semantic_command.py")

# === command_processor.py ===
command_processor_content = '''"""
Command Processor - Procesa comandos semánticos y coordina la ejecución
"""
from typing import Dict, Any, Optional
import logging
from ..semantic.semantic_command import SemanticCommand, CommandResult, IntentType
from ...core.enhanced_trajectory_engine import EnhancedTrajectoryEngine


logger = logging.getLogger(__name__)


class CommandProcessor:
    """Procesa comandos semánticos y los ejecuta"""
    
    def __init__(self, engine: EnhancedTrajectoryEngine):
        self.engine = engine
        self.action_handlers = self._setup_handlers()
        self.validation_rules = self._setup_validation()
        
    def _setup_handlers(self) -> Dict[IntentType, Any]:
        """Mapea intenciones a handlers"""
        return {
            IntentType.CREATE_MACRO: self._handle_create_macro,
            IntentType.SET_TRAJECTORY: self._handle_set_trajectory,
            IntentType.APPLY_ROTATION: self._handle_apply_rotation,
            IntentType.APPLY_CONCENTRATION: self._handle_apply_concentration,
            IntentType.APPLY_MODULATION: self._handle_apply_modulation,
            IntentType.SET_BEHAVIOR: self._handle_set_behavior,
            IntentType.LOAD_PRESET: self._handle_load_preset,
            # Más handlers...
        }
    
    def _setup_validation(self) -> Dict[IntentType, Dict]:
        """Define reglas de validación para cada intención"""
        return {
            IntentType.CREATE_MACRO: {
                "required": ["name", "source_count"],
                "optional": ["formation", "spacing"],
                "defaults": {"formation": "circle", "spacing": 2.0}
            },
            # Más validaciones...
        }
    
    def execute(self, command: SemanticCommand) -> CommandResult:
        """Ejecuta un comando semántico"""
        logger.info(f"Ejecutando comando: {command.intent.value}")
        
        # Validar comando
        if not command.validate():
            return CommandResult(
                success=False,
                message="Comando inválido",
                error="Faltan parámetros requeridos"
            )
        
        # Aplicar defaults si es necesario
        self._apply_defaults(command)
        
        # Ejecutar handler correspondiente
        if command.intent in self.action_handlers:
            try:
                return self.action_handlers[command.intent](command)
            except Exception as e:
                logger.error(f"Error ejecutando {command.intent}: {str(e)}")
                return CommandResult(
                    success=False,
                    message="Error en ejecución",
                    error=str(e)
                )
        else:
            return CommandResult(
                success=False,
                message="Intención no implementada",
                error=f"No hay handler para {command.intent.value}"
            )
    
    def _apply_defaults(self, command: SemanticCommand):
        """Aplica valores por defecto a los parámetros"""
        if command.intent in self.validation_rules:
            defaults = self.validation_rules[command.intent].get("defaults", {})
            for key, value in defaults.items():
                if key not in command.parameters:
                    command.parameters[key] = value
    
    # === HANDLERS DE ACCIONES ===
    
    def _handle_create_macro(self, command: SemanticCommand) -> CommandResult:
        """Crea un macro con las especificaciones dadas"""
        params = command.parameters
        
        try:
            # Crear macro en el engine
            macro = self.engine.create_macro(
                name=params["name"],
                source_count=params["source_count"],
                formation=params.get("formation", "circle")
            )
            
            # Aplicar espaciado si se especificó
            if "spacing" in params:
                # TODO: Implementar lógica de espaciado
                pass
            
            return CommandResult(
                success=True,
                message=f"Macro '{params['name']}' creado con {params['source_count']} fuentes",
                data={"macro_id": params["name"], "sources": params["source_count"]}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message="Error al crear macro",
                error=str(e)
            )
    
    def _handle_set_trajectory(self, command: SemanticCommand) -> CommandResult:
        """Establece trayectoria para un macro o fuente"""
        params = command.parameters
        target = params["target"]
        trajectory = params["trajectory_type"]
        
        try:
            # Determinar si es macro o fuente individual
            if target in self.engine._macros:
                self.engine.set_macro_trajectory(
                    target,
                    trajectory,
                    **params.get("trajectory_params", {})
                )
                return CommandResult(
                    success=True,
                    message=f"Trayectoria '{trajectory}' aplicada a macro '{target}'"
                )
            else:
                # Asumir que es una fuente individual
                self.engine.set_individual_trajectory(
                    int(target),
                    shape=trajectory,
                    **params.get("trajectory_params", {})
                )
                return CommandResult(
                    success=True,
                    message=f"Trayectoria '{trajectory}' aplicada a fuente {target}"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                message="Error al establecer trayectoria",
                error=str(e)
            )
    
    def _handle_apply_rotation(self, command: SemanticCommand) -> CommandResult:
        """Aplica rotación a macro o fuente"""
        params = command.parameters
        target = params["target"]
        rotation_params = params["rotation_params"]
        
        try:
            if target in self.engine._macros:
                # Rotación de macro
                if rotation_params.get("type") == "manual":
                    self.engine.set_manual_macro_rotation(
                        target,
                        yaw=rotation_params.get("yaw", 0),
                        pitch=rotation_params.get("pitch", 0),
                        roll=rotation_params.get("roll", 0),
                        interpolation_speed=rotation_params.get("speed", 0.5)
                    )
                else:
                    self.engine.set_macro_rotation(
                        target,
                        speed_x=rotation_params.get("speed_x", 0),
                        speed_y=rotation_params.get("speed_y", 0),
                        speed_z=rotation_params.get("speed_z", 0)
                    )
                    
                return CommandResult(
                    success=True,
                    message=f"Rotación aplicada a macro '{target}'"
                )
            else:
                # Rotación individual
                # TODO: Implementar rotación individual
                return CommandResult(
                    success=False,
                    message="Rotación individual no implementada aún"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                message="Error al aplicar rotación",
                error=str(e)
            )
    
    def _handle_apply_concentration(self, command: SemanticCommand) -> CommandResult:
        """Aplica concentración/dispersión a un macro"""
        params = command.parameters
        
        try:
            self.engine.apply_concentration(
                params["target"],
                params.get("factor", 0.5)
            )
            
            return CommandResult(
                success=True,
                message=f"Concentración aplicada: factor {params.get('factor', 0.5)}"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message="Error al aplicar concentración",
                error=str(e)
            )
    
    def _handle_apply_modulation(self, command: SemanticCommand) -> CommandResult:
        """Aplica modulación 3D"""
        params = command.parameters
        
        try:
            if hasattr(self.engine, 'apply_orientation_preset'):
                self.engine.apply_orientation_preset(
                    params["target"],
                    params["preset"],
                    intensity=params.get("intensity", 1.0)
                )
                return CommandResult(
                    success=True,
                    message=f"Modulación '{params['preset']}' aplicada"
                )
            else:
                return CommandResult(
                    success=False,
                    message="Modulador 3D no disponible"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                message="Error al aplicar modulación",
                error=str(e)
            )
    
    def _handle_set_behavior(self, command: SemanticCommand) -> CommandResult:
        """Establece comportamiento de un macro"""
        # TODO: Implementar
        return CommandResult(
            success=False,
            message="Comportamientos no implementados aún"
        )
    
    def _handle_load_preset(self, command: SemanticCommand) -> CommandResult:
        """Carga un preset artístico"""
        # TODO: Implementar
        return CommandResult(
            success=False,
            message="Presets no implementados aún"
        )
'''

with open("trajectory_hub/control/processors/command_processor.py", 'w') as f:
    f.write(command_processor_content)
print("  ✅ command_processor.py")

# === cli_interface.py ===
cli_interface_content = '''"""
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
            self.last_input = input(f"\\n{prompt}").strip()
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
        print(f"\\n{prompt}")
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
        print(f"\\n{'=' * 60}")
        print(f"{title.center(60)}")
        print('=' * 60)
    
    def show_success(self, message: str):
        """Muestra mensaje de éxito"""
        print(f"\\n✅ {message}")
    
    def show_error(self, message: str):
        """Muestra mensaje de error"""
        print(f"\\n❌ ERROR: {message}")
    
    def show_warning(self, message: str):
        """Muestra advertencia"""
        print(f"\\n⚠️  ADVERTENCIA: {message}")
    
    def show_info(self, message: str):
        """Muestra información"""
        print(f"\\nℹ️  {message}")
    
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
        input(f"\\n{message}")
    
    def get_macro_config(self) -> Optional[Dict[str, Any]]:
        """Obtiene configuración para crear un macro"""
        print("\\n🔧 CONFIGURACIÓN DE MACRO")
        
        name = self.get_input("Nombre del macro: ")
        if not name or name == 'q':
            return None
            
        count = self.get_numeric_input("Número de fuentes: ", 1, 100)
        if count is None:
            return None
            
        formations = ["circle", "line", "grid", "spiral", "random"]
        formation_idx = self.get_choice_from_list(formations, "Formación inicial:")
        if formation_idx is None:
            return None
            
        return {
            "name": name,
            "source_count": int(count),
            "formation": formations[formation_idx]
        }
    
    def get_movement_config(self) -> Optional[Dict[str, Any]]:
        """Obtiene configuración de movimiento"""
        print("\\n🌀 CONFIGURACIÓN DE MOVIMIENTO")
        
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
'''

with open("trajectory_hub/control/interfaces/cli_interface.py", 'w') as f:
    f.write(cli_interface_content)
print("  ✅ cli_interface.py")

# 4. Crear __init__.py para los nuevos módulos
print("\n📝 Configurando imports...")

control_init = '''"""
Sistema de control modular para Trajectory Hub
"""
from .semantic.semantic_command import SemanticCommand, CommandResult, IntentType
from .processors.command_processor import CommandProcessor
from .interfaces.cli_interface import CLIInterface

__all__ = [
    'SemanticCommand',
    'CommandResult', 
    'IntentType',
    'CommandProcessor',
    'CLIInterface'
]
'''

with open("trajectory_hub/control/__init__.py", 'w') as f:
    f.write(control_init)

print("\n✅ ARQUITECTURA BASE CREADA")
print("\n📋 Siguientes pasos:")
print("  1. Refactorizar InteractiveController")
print("  2. Migrar lógica a CommandProcessor")
print("  3. Crear managers especializados")
print("\n🚀 Ejecuta: python create_refactored_controller.py")