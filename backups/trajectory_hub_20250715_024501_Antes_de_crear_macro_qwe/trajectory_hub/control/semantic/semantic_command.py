"""
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
