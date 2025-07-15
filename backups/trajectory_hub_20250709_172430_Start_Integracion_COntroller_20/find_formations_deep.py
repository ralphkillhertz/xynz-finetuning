import os
import re
from pathlib import Path
import json

def search_all_files():
    """Buscar formaciones en TODOS los archivos del proyecto"""
    print("🔍 BÚSQUEDA PROFUNDA EN TODA LA ARQUITECTURA")
    print("="*60)
    
    # Archivos a buscar
    search_paths = [
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/interface/interactive_controller.py",
        "trajectory_hub/control/processors/command_processor.py",
        "trajectory_hub/control/managers/formation_manager.py",
        "trajectory_hub/control/interfaces/cli_interface.py",
        "trajectory_hub/core/macro_behaviors.py"
    ]
    
    formations_found = {}
    formation_keywords = ["circle", "line", "grid", "spiral", "random", "sphere"]
    
    for filepath in search_paths:
        if os.path.exists(filepath):
            print(f"\n📂 Analizando: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Buscar patrones de formaciones
            patterns = [
                r'formation[s]?\s*=\s*[\[{].*?[\]}]',  # Listas o dicts
                r'create_macro.*formation',              # Llamadas
                r'["\'](circle|line|grid|spiral|random|sphere)["\']',  # Strings
                r'def.*formation',                       # Métodos
                r'case.*formation',                      # Switch/case
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    context_start = max(0, line_num - 3)
                    context_end = min(len(lines), line_num + 3)
                    
                    print(f"\n   ✅ Patrón encontrado en línea {line_num}:")
                    for i in range(context_start, context_end):
                        if i < len(lines):
                            marker = ">>>" if i == line_num - 1 else "   "
                            print(f"   {marker} {i+1}: {lines[i][:100]}")
                    
                    if filepath not in formations_found:
                        formations_found[filepath] = []
                    formations_found[filepath].append((line_num, match.group(0)))
    
    # Buscar específicamente create_macro
    print("\n\n🎯 BUSCANDO MÉTODO create_macro...")
    
    for filepath in search_paths:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Buscar create_macro con contexto amplio
            create_match = re.search(
                r'(def create_macro.*?)(?=\n    def|\n\nclass|\nif __name__|$)', 
                content, 
                re.DOTALL
            )
            
            if create_match:
                print(f"\n✅ create_macro encontrado en: {filepath}")
                method = create_match.group(1)
                
                # Buscar si tiene formaciones definidas
                if any(formation in method for formation in ["circle", "line", "grid"]):
                    print("   ✅ Contiene definiciones de formación")
                    
                    # Verificar si sphere está
                    if "sphere" not in method:
                        print("   ⚠️ NO tiene 'sphere'")
                        add_sphere_to_file(filepath, method)
                    else:
                        print("   ✅ Ya tiene 'sphere'")
    
    return formations_found

def add_sphere_to_file(filepath, method_content):
    """Añadir sphere a las formaciones"""
    print(f"\n🔧 Añadiendo sphere a {filepath}...")
    
    with open(filepath, 'r') as f:
        full_content = f.read()
    
    # Buscar dónde añadir sphere
    # Patrón 1: En lista de opciones
    pattern1 = r'(["\'"]5["\'"]:\s*["\'"]random["\'"])'
    match1 = re.search(pattern1, method_content)
    
    if match1:
        new_method = method_content.replace(
            match1.group(1),
            match1.group(1) + ',\n            "6": "sphere"'
        )
        full_content = full_content.replace(method_content, new_method)
    
    # Patrón 2: En FormationManager
    if "FormationManager" in filepath:
        pattern2 = r'(self\.formations\s*=\s*\{[^}]+\})'
        match2 = re.search(pattern2, full_content)
        
        if match2 and '"sphere"' not in match2.group(1):
            old_dict = match2.group(1)
            new_dict = old_dict.rstrip('}') + ',\n            "sphere": self._create_sphere_formation\n        }'
            full_content = full_content.replace(old_dict, new_dict)
            
            # Añadir método _create_sphere_formation
            if "_create_sphere_formation" not in full_content:
                sphere_method = '''
    def _create_sphere_formation(self, source_ids, center=(0, 0, 0), radius=2.0):
        """Crear formación esférica"""
        import numpy as np
        
        positions = {}
        n = len(source_ids)
        
        # Algoritmo de distribución uniforme en esfera
        golden_angle = np.pi * (3 - np.sqrt(5))  # Ángulo dorado
        
        for i, sid in enumerate(source_ids):
            y = 1 - (i / float(n - 1)) * 2  # y va de 1 a -1
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
                # Insertar antes del último }
                insert_pos = full_content.rfind('\n\n')
                full_content = full_content[:insert_pos] + sphere_method + full_content[insert_pos:]
    
    # Guardar con backup
    from datetime import datetime
    import shutil
    
    backup = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(filepath, backup)
    
    with open(filepath, 'w') as f:
        f.write(full_content)
    
    print(f"   ✅ Archivo actualizado: {filepath}")
    print(f"   📦 Backup creado: {backup}")

def verify_integration():
    """Verificar que sphere esté integrado"""
    print("\n\n🧪 VERIFICACIÓN DE INTEGRACIÓN")
    print("="*60)
    
    # Test directo
    try:
        from trajectory_hub.control.managers.formation_manager import FormationManager
        fm = FormationManager()
        
        if hasattr(fm, 'formations') and 'sphere' in fm.formations:
            print("✅ FormationManager tiene 'sphere'")
        else:
            print("❌ FormationManager NO tiene 'sphere'")
            
    except Exception as e:
        print(f"⚠️ Error al verificar FormationManager: {e}")
    
    # Verificar en archivos
    files_to_check = [
        "trajectory_hub/control/managers/formation_manager.py",
        "trajectory_hub/control/processors/command_processor.py",
        "trajectory_hub/interface/interactive_controller.py"
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            sphere_count = content.count("sphere")
            if sphere_count > 0:
                print(f"✅ {filepath}: 'sphere' aparece {sphere_count} veces")
            else:
                print(f"❌ {filepath}: NO contiene 'sphere'")

if __name__ == "__main__":
    formations = search_all_files()
    verify_integration()
    
    print("\n\n🚀 PRÓXIMOS PASOS:")
    print("1. python main.py --interactive")
    print("2. Crear macro (opción 1)")
    print("3. Verificar que 'sphere' aparezca como opción 6")