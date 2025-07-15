"""
macro_system.py - Sistema de macros para Trajectory Hub
"""
from enum import Enum
from typing import List, Set

class MacroState(Enum):
    """Estados posibles de un macro"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    RECORDING = "recording"

class Macro:
    """Clase que representa un macro de fuentes"""
    def __init__(self, name: str, source_ids: Set[int], behavior_name: str = "static"):
        self.name = name
        self.source_ids = source_ids
        self.behavior_name = behavior_name
        self.state = MacroState.STOPPED
        self.parameters = {}
        
    def __repr__(self):
        return f"Macro('{self.name}', {len(self.source_ids)} sources, {self.state.value})"
