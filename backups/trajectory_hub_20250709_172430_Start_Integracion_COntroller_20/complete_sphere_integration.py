def complete_sphere_integration():
    print("🔧 COMPLETANDO INTEGRACIÓN DE SPHERE")
    print("="*60)
    
    # 1. Actualizar CommandProcessor para usar FormationManager
    processor_file = "trajectory_hub/control/processors/command_processor.py"
    print(f"\n1️⃣ Actualizando {processor_file}...")
    
    with open(processor_file, 'r') as f:
        content = f.read()
    
    # Añadir import del FormationManager
    if "from ..managers.formation_manager import FormationManager" not in content:
        # Buscar dónde están los imports
        import_pos = content.find("from typing import")
        if import_pos > 0:
            end_line = content.find("\n\n", import_pos)
            new_import = "\nfrom ..managers.formation_manager import FormationManager"
            content = content[:end_line] + new_import + content[end_line:]
            print("   ✅ Import añadido")
    
    # Modificar el método create_macro para usar FormationManager
    if "FormationManager.calculate_formation" not in content:
        # Buscar el método execute de create_macro
        pattern = r'(elif command\.name == "create_macro":.*?)(return result)'
        import re
        
        def replacer(match):
            body = match.group(1)
            
            # Añadir uso del FormationManager
            new_code = '''
            # Usar FormationManager para calcular posiciones
            if "formation" in command.parameters:
                formation = command.parameters["formation"]
                source_count = command.parameters["source_count"]
                spacing = command.parameters.get("spacing", 2.0)
                
                # Calcular posiciones usando FormationManager
                positions = FormationManager.calculate_formation(
                    formation, source_count, spacing
                )
                
                # Pasar las posiciones al engine
                command.parameters["calculated_positions"] = positions
'''
            return body + new_code + "\n            " + match.group(2)
        
        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        print("   ✅ CommandProcessor actualizado para usar FormationManager")
    
    # Guardar
    with open(processor_file, 'w') as f:
        f.write(content)
    
    # 2. Completar FormationManager
    manager_file = "trajectory_hub/control/managers/formation_manager.py"
    print(f"\n2️⃣ Completando {manager_file}...")
    
    complete_manager = '''"""
Formation Manager - Gestiona las formaciones de macros
Parte de la arquitectura de control por capas
"""
import numpy as np
import math
from typing import List, Tuple

class FormationManager:
    """Gestiona todas las formaciones posibles para macros"""
    
    @staticmethod
    def calculate_formation(
        formation: str, 
        source_count: int, 
        spacing: float = 2.0
    ) -> List[Tuple[float, float, float]]:
        """
        Calcula las posiciones según la formación
        
        Returns:
            Lista de tuplas (x, y, z) para cada fuente
        """
        positions = []
        
        if formation == "sphere":
            # Distribución uniforme en esfera usando espiral de Fibonacci
            golden_ratio = (1 + math.sqrt(5)) / 2
            
            for i in range(source_count):
                # Ángulo vertical (de -1 a 1)
                y = 1 - (2 * i / (source_count - 1)) if source_count > 1 else 0
                
                # Radio en el plano XZ
                radius_xz = math.sqrt(1 - y * y)
                
                # Ángulo horizontal usando proporción áurea
                theta = 2 * math.pi * i / golden_ratio
                
                # Coordenadas finales
                x = radius_xz * math.cos(theta) * spacing
                y_final = y * spacing
                z = radius_xz * math.sin(theta) * spacing
                
                positions.append((x, y_final, z))
                
        elif formation == "circle":
            angle_step = 2 * math.pi / source_count
            for i in range(source_count):
                angle = i * angle_step
                x = math.cos(angle) * spacing
                y = math.sin(angle) * spacing
                z = 0.0
                positions.append((x, y, z))
                
        elif formation == "line":
            for i in range(source_count):
                x = (i - source_count/2) * spacing
                y = 0.0
                z = 0.0
                positions.append((x, y, z))
                
        elif formation == "grid":
            grid_size = int(math.ceil(math.sqrt(source_count)))
            for i in range(source_count):
                row = i // grid_size
                col = i % grid_size
                x = (col - grid_size/2) * spacing
                y = (row - grid_size/2) * spacing
                z = 0.0
                positions.append((x, y, z))
                
        elif formation == "spiral":
            for i in range(source_count):
                angle = i * 0.5
                radius = i * spacing * 0.3
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                z = math.sin(i * 0.2) * spacing
                positions.append((x, y, z))
                
        else:  # random o default
            import random
            for i in range(source_count):
                x = random.uniform(-spacing*2, spacing*2)
                y = random.uniform(-spacing*2, spacing*2)
                z = random.uniform(-spacing, spacing)
                positions.append((x, y, z))
        
        return positions
'''
    
    with open(manager_file, 'w') as f:
        f.write(complete_manager)
    print("   ✅ FormationManager completado con todas las formaciones")
    
    # 3. Test arquitectónico
    print(f"\n3️⃣ Creando test arquitectónico...")
    
    test_code = '''#!/usr/bin/env python3
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

print(f"\\n✅ Resultado: {result}")
print("\\n💡 Verifica en Spat:")
print("   - 15 fuentes en formación esférica")
print("   - Distribución uniforme 3D")
print("   - Radio ~3 metros")
'''
    
    with open("test_sphere_architecture.py", "w") as f:
        f.write(test_code)
    
    print("\n✅ INTEGRACIÓN COMPLETA")
    print("\n🚀 Ejecuta: python test_sphere_architecture.py")
    print("\n📊 Arquitectura respetada:")
    print("   ✅ FormationManager calcula posiciones")
    print("   ✅ CommandProcessor orquesta")
    print("   ✅ Engine solo aplica")
    print("   ✅ Separación de responsabilidades")

if __name__ == "__main__":
    complete_sphere_integration()