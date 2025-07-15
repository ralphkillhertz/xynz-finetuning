#!/usr/bin/env python3
"""
🔧 Fix: Añadir formación sphere 3D
⚡ Archivo: trajectory_hub/core/enhanced_trajectory_engine.py
🎯 Impacto: BAJO - Solo añade caso sphere
"""

import sys
import os

def apply_sphere_fix():
    """Aplica el fix para sphere en enhanced_trajectory_engine.py"""
    
    # Ruta al archivo
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print(f"❌ Error: No se encuentra {engine_path}")
        print("Asegúrate de ejecutar desde la raíz del proyecto")
        return False
    
    # Leer el archivo
    with open(engine_path, 'r') as f:
        content = f.read()
    
    # 1. Verificar si FormationManager está importado
    if "from trajectory_hub.control.managers.formation_manager import FormationManager" not in content:
        # Buscar dónde añadir el import (después de otros imports de trajectory_hub)
        import_pos = content.find("from trajectory_hub")
        if import_pos != -1:
            # Encontrar el final de la línea
            line_end = content.find("\n", import_pos)
            # Insertar el nuevo import
            new_import = "\nfrom trajectory_hub.control.managers.formation_manager import FormationManager"
            content = content[:line_end] + new_import + content[line_end:]
            print("✅ Import FormationManager añadido")
        else:
            print("❌ No se pudo añadir el import automáticamente")
            return False
    
    # 2. Encontrar dónde añadir el caso sphere
    # Buscar el elif para spiral (último caso antes del else)
    spiral_pos = content.find('elif formation == "spiral":')
    if spiral_pos == -1:
        print("❌ No se encontró el caso spiral")
        return False
    
    # Encontrar el final del bloque spiral
    # Buscar el siguiente elif o else
    search_pos = spiral_pos
    while True:
        next_elif = content.find("\n        elif", search_pos + 1)
        next_else = content.find("\n        else:", search_pos + 1)
        
        if next_else != -1 and (next_elif == -1 or next_else < next_elif):
            # Insertar antes del else
            insert_pos = next_else
            break
        elif next_elif != -1:
            search_pos = next_elif
        else:
            print("❌ No se encontró dónde insertar sphere")
            return False
    
    # 3. Código para sphere
    sphere_code = '''
        elif formation == "sphere":
            # Solución temporal - Engine usa FormationManager
            if not hasattr(self, '_fm'):
                self._fm = FormationManager()
            positions = self._fm.calculate_formation("sphere", self.config['n_sources'])
            print(f"🌐 Sphere 3D: {len(positions)} sources")
            
            # Aplicar las posiciones
            for i, pos in enumerate(positions):
                if i < len(sources):
                    sources[i]['x'] = pos[0]
                    sources[i]['y'] = pos[1] 
                    sources[i]['z'] = pos[2]
'''
    
    # Insertar el código
    content = content[:insert_pos] + sphere_code + content[insert_pos:]
    
    # 4. Hacer backup
    backup_path = f"{engine_path}.backup_before_sphere_{os.getpid()}"
    with open(backup_path, 'w') as f:
        f.write(content[:insert_pos] + content[insert_pos:])
    print(f"📦 Backup creado: {backup_path}")
    
    # 5. Escribir el archivo modificado
    with open(engine_path, 'w') as f:
        f.write(content)
    
    print("✅ Sphere fix aplicado exitosamente")
    print("\n🧪 Para probar:")
    print("1. python -m trajectory_hub.interface.interactive_controller")
    print("2. Seleccionar: 1 (Macro Management) → 1 (Create Macro)")
    print("3. Formation: sphere")
    
    return True

if __name__ == "__main__":
    print("🔧 Aplicando fix para formación sphere 3D...")
    print("=" * 50)
    
    if apply_sphere_fix():
        print("\n✅ Fix completado. Sistema listo para usar sphere.")
    else:
        print("\n❌ Error al aplicar el fix. Revisa los mensajes anteriores.")