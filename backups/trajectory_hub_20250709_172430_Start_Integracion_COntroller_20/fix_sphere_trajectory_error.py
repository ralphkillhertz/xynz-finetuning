#!/usr/bin/env python3
"""
🔧 Fix: Error 'individual_trajectory' en sphere
⚡ Ajusta el código sphere en Engine
"""

import os

# Buscar y arreglar el problema en enhanced_trajectory_engine.py
engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_path, 'r') as f:
    content = f.read()

# Buscar el bloque de sphere
sphere_start = content.find('elif formation == "sphere"')
if sphere_start != -1:
    # Encontrar el final del bloque
    next_elif = content.find('\n        elif', sphere_start + 1)
    next_else = content.find('\n        else:', sphere_start + 1)
    
    if next_else != -1 and (next_elif == -1 or next_else < next_elif):
        sphere_end = next_else
    else:
        sphere_end = next_elif if next_elif != -1 else len(content)
    
    # Reemplazar el bloque sphere con código corregido
    new_sphere_code = '''elif formation == "sphere":
            # Solución temporal - Engine usa FormationManager
            if not hasattr(self, '_fm'):
                self._fm = FormationManager()
            positions = self._fm.calculate_formation("sphere", self.config['n_sources'])
            print(f"🌐 Sphere 3D: {len(positions)} sources")
            
            # Aplicar las posiciones - mismo formato que otras formaciones
            for i, pos in enumerate(positions):
                if i < len(sources):
                    sources[i]['x'] = pos[0]
                    sources[i]['y'] = pos[1] 
                    sources[i]['z'] = pos[2]
                    # Asegurar otros campos necesarios
                    if 'individual_trajectory' not in sources[i]:
                        sources[i]['individual_trajectory'] = None
                    if 'motion' not in sources[i]:
                        sources[i]['motion'] = None
        '''
    
    # Encontrar el inicio exacto del bloque
    block_start = content.rfind('\n', 0, sphere_start) + 1
    
    # Reemplazar
    content = content[:block_start] + new_sphere_code + content[sphere_end:]
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.write(content)
    
    print("✅ Código sphere actualizado con campos faltantes")
else:
    print("❌ No se encontró el bloque sphere")
    print("   Verificando estructura de sources...")
    
    # Buscar cómo se inicializan sources en otras formaciones
    circle_pos = content.find('elif formation == "circle"')
    if circle_pos != -1:
        # Extraer unas líneas para ver el patrón
        sample = content[circle_pos:circle_pos+500]
        print("\n📋 Patrón en circle:")
        lines = sample.split('\n')[:10]
        for line in lines:
            if 'sources[' in line:
                print(f"   {line.strip()}")