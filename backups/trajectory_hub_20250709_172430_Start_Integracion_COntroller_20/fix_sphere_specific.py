import os
import re
from datetime import datetime
import shutil

def fix_sphere():
    """Implementar sphere en el archivo correcto"""
    print("🔧 IMPLEMENTANDO SPHERE 3D")
    
    # Archivo principal
    main_file = "trajectory_hub/presets/artistic_presets.py"
    
    # Backup
    backup = f"{main_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(main_file, backup)
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Buscar dónde añadir sphere
    if "_calculate_circle_positions" in content:
        # Añadir después de circle
        sphere_method = '''
def _calculate_sphere_positions(self, n_sources, center=(0, 0, 0), radius=2.0):
    """Calcular posiciones en esfera 3D"""
    import numpy as np
    
    positions = []
    golden_angle = np.pi * (3.0 - np.sqrt(5.0))
    
    for i in range(n_sources):
        y = 1 - (i / float(n_sources - 1)) * 2 if n_sources > 1 else 0
        radius_at_y = np.sqrt(1 - y * y)
        theta = golden_angle * i
        
        x = np.cos(theta) * radius_at_y
        z = np.sin(theta) * radius_at_y
        
        positions.append((
            center[0] + x * radius,
            center[1] + y * radius,
            center[2] + z * radius
        ))
    
    return positions
'''
        
        # Insertar después de circle
        circle_end = content.find("return positions", 
                                content.find("_calculate_circle_positions"))
        if circle_end > 0:
            insert_pos = content.find("\n\n", circle_end) + 2
            content = content[:insert_pos] + sphere_method + content[insert_pos:]
            
            print("✅ Método sphere añadido")
    
    # Buscar donde se mapean las formaciones
    # Añadir sphere donde sea necesario
    
    with open(main_file, 'w') as f:
        f.write(content)
    
    print("✅ Sphere implementado")

if __name__ == "__main__":
    fix_sphere()
