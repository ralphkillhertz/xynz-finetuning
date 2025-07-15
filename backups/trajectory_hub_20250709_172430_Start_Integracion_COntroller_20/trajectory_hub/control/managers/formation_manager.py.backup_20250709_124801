"""
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
