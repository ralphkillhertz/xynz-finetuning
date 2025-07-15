"""
Command Processor - Procesa comandos semánticos y coordina la ejecución
"""
from typing import Dict, Any, Optional
import logging
from ..semantic.semantic_command import SemanticCommand, CommandResult, IntentType
from ...core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from ..managers.formation_manager import FormationManager


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
                "optional": ["formation", "spacing", "custom_function"],
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
            # Usar spacing del params si existe, sino usar default
            spacing = params.get("spacing", 2.0)
            
            # Preparar kwargs para incluir custom_function si existe
            create_kwargs = {}
            if "custom_function" in params and params["custom_function"]:
                create_kwargs["custom_function"] = params["custom_function"]
            
            macro_id = self.engine.create_macro(
                name=params["name"],
                source_count=params["source_count"],
                formation=params.get("formation", "circle"),
                spacing=spacing,
                **create_kwargs
            )
            
            return CommandResult(
                success=True,
                message=f"Macro '{params['name']}' creado con {params['source_count']} fuentes",
                data={"macro_id": macro_id, "sources": params["source_count"]}
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
        trajectory_params = params.get("trajectory_params", {})
        
        try:
            # Determinar si es macro o fuente individual
            if target in self.engine._macros:
                # Pasar el tipo de trayectoria como string y los parámetros separados
                self.engine.set_macro_trajectory(
                    target,
                    trajectory,  # Ahora acepta string
                    **trajectory_params  # Incluye speed y otros parámetros
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
                    **trajectory_params
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
                    # Rotación manual instantánea
                    instant = rotation_params.get("instant", True)
                    interpolation_speed = 1000.0 if instant else rotation_params.get("speed", 0.5)
                    
                    self.engine.set_manual_macro_rotation(
                        target,
                        yaw=rotation_params.get("yaw", 0),
                        pitch=rotation_params.get("pitch", 0),
                        roll=rotation_params.get("roll", 0),
                        interpolation_speed=interpolation_speed
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
