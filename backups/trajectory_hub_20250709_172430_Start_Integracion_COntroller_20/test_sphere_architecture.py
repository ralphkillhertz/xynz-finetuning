#!/usr/bin/env python3
"""Test de formación sphere siguiendo arquitectura correcta"""

from trajectory_hub.control.semantic.semantic_command import SemanticCommand
from trajectory_hub.control.processors.command_processor import CommandProcessor
from trajectory_hub import EnhancedTrajectoryEngine

print("🏗️ TEST ARQUITECTÓNICO - FORMACIÓN SPHERE")
print("="*60)

# 1. Crear engine
engine = EnhancedTrajectoryEngine(max_sources=20, fps=30)
processor = CommandProcessor(engine)

# 2. Crear comando semántico (como vendría del CLI)
command = SemanticCommand(
    name="create_macro",
    parameters={
        "name": "esfera_test",
        "source_count": 15,
        "formation": "sphere",
        "spacing": 3.0
    }
)

print("📋 Comando:", command.name)
print("📋 Parámetros:", command.parameters)

# 3. Ejecutar a través del processor
result = processor.execute(command)

print(f"\n✅ Resultado: {result}")
print("\n💡 Verifica en Spat:")
print("   - 15 fuentes en formación esférica")
print("   - Distribución uniforme 3D")
print("   - Radio ~3 metros")
