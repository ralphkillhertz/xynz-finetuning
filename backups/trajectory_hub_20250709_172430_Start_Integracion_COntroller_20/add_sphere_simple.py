import os
from datetime import datetime
import shutil

def add_sphere_simple():
    """Añadir sphere de la forma más simple posible"""
    print("🔧 AÑADIENDO SPHERE AL MENÚ")
    print("="*60)
    
    cli_file = "trajectory_hub/control/interfaces/cli_interface.py"
    
    # Backup
    backup = f"{cli_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(cli_file, backup)
    print(f"📦 Backup: {backup}")
    
    with open(cli_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la línea exacta
    old_line = 'formations = ["circle", "line", "grid", "spiral", "random"]'
    new_line = 'formations = ["circle", "line", "grid", "spiral", "random", "sphere"]'
    
    if old_line in content:
        print("✅ Encontrada lista de formaciones")
        content = content.replace(old_line, new_line)
        
        with open(cli_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Sphere añadido al menú")
        
        # Verificar FormationManager
        verify_formation_manager()
        
        return True
    else:
        # Buscar variante con espacios o saltos de línea
        print("\n🔍 Buscando formato alternativo...")
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'formations' in line and '=' in line and '[' in line:
                if 'random' in line and 'sphere' not in line:
                    print(f"✅ Encontrado en línea {i+1}: {line.strip()}")
                    
                    # Reemplazar random"] con random", "sphere"]
                    new_line = line.replace('random"]', 'random", "sphere"]')
                    lines[i] = new_line
                    
                    with open(cli_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    print("✅ Sphere añadido al menú")
                    verify_formation_manager()
                    return True
        
        print("❌ No se encontró la lista de formaciones")
        return False

def verify_formation_manager():
    """Asegurar que FormationManager tenga sphere"""
    print("\n📐 Verificando FormationManager...")
    
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if not os.path.exists(fm_file):
        print("❌ No existe FormationManager")
        return
    
    with open(fm_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '_create_sphere_formation' in content:
        print("✅ FormationManager ya tiene sphere")
        return
    
    print("⚠️ FormationManager no tiene sphere, añadiendo...")
    
    # Backup
    backup = f"{fm_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(fm_file, backup)
    
    # Buscar self.formations = {
    import re
    pattern = r'(self\.formations\s*=\s*\{[^}]+\})'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_dict = match.group(1)
        
        # Añadir sphere
        new_dict = old_dict.rstrip('}').rstrip()
        if not new_dict.endswith(','):
            new_dict += ','
        new_dict += '\n            "sphere": self._create_sphere_formation\n        }'
        
        content = content.replace(old_dict, new_dict)
        
        # Añadir método
        sphere_method = '''
    def _create_sphere_formation(self, source_ids, center=(0, 0, 0), radius=2.0):
        """Crear formación esférica con distribución uniforme"""
        import numpy as np
        
        positions = {}
        n = len(source_ids)
        
        if n == 0:
            return positions
        
        # Espiral de Fibonacci para distribución uniforme
        golden_angle = np.pi * (3.0 - np.sqrt(5.0))
        
        for i, sid in enumerate(source_ids):
            y = 1 - (i / float(n - 1)) * 2 if n > 1 else 0
            radius_at_y = np.sqrt(1 - y * y)
            theta = golden_angle * i
            
            x = np.cos(theta) * radius_at_y
            z = np.sin(theta) * radius_at_y
            
            positions[sid] = (
                center[0] + x * radius,
                center[1] + y * radius,
                center[2] + z * radius
            )
        
        return positions
'''
        
        # Insertar antes del final de la clase
        insert_pos = content.rfind('\n\n')
        if insert_pos > 0:
            content = content[:insert_pos] + sphere_method + content[insert_pos:]
        
        with open(fm_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Sphere añadido a FormationManager")

if __name__ == "__main__":
    if add_sphere_simple():
        print("\n🎉 SPHERE AÑADIDO EXITOSAMENTE")
        print("\n🚀 Ahora ejecuta:")
        print("python main.py --interactive")
        print("→ Crear macro → Verás sphere como opción 6")
    else:
        print("\n❌ No se pudo añadir sphere")
        print("\n💡 Añade manualmente en cli_interface.py:")
        print('Cambia: formations = ["circle", "line", "grid", "spiral", "random"]')
        print('Por:     formations = ["circle", "line", "grid", "spiral", "random", "sphere"]')