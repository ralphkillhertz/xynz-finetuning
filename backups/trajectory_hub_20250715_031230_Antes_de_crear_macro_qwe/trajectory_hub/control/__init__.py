"""
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
