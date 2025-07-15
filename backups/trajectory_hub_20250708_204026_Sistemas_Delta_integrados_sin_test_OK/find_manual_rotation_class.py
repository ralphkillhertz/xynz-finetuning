import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def find_class():
    """Busca la clase ManualIndividualRotation en todos los archivos"""
    
    print("🔍 BUSCANDO ManualIndividualRotation...")
    print("=" * 60)
    
    # Archivos donde buscar
    files_to_check = [
        'trajectory_hub/core/motion_components.py',
        'trajectory_hub/core/enhanced_trajectory_engine.py',
        'trajectory_hub/core/trajectory_deformers.py',
        'trajectory_hub/core/macro_behaviors.py'
    ]
    
    found = False
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"\n📄 Verificando: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Buscar variaciones del nombre
            searches = [
                "class ManualIndividualRotation",
                "ManualIndividualRotation(",
                "manual_individual_rotation",
                "set_manual_individual_rotation"
            ]
            
            for search in searches:
                if search in content:
                    print(f"   ✅ Encontrado: '{search}'")
                    # Mostrar contexto
                    index = content.find(search)
                    start = max(0, index - 100)
                    end = min(len(content), index + 200)
                    context = content[start:end]
                    print(f"   Contexto:\n   {'-'*50}")
                    for i, line in enumerate(context.split('\n')):
                        if search in line:
                            print(f"   >>> {line}")
                        else:
                            print(f"       {line}")
                    found = True
        else:
            print(f"\n❌ No existe: {filepath}")
    
    if not found:
        print("\n❌ No se encontró ManualIndividualRotation")
        print("\n🔍 Buscando rotaciones individuales en general...")
        
        # Buscar IndividualRotation
        for filepath in files_to_check:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "class IndividualRotation" in content:
                    print(f"\n✅ Encontrado IndividualRotation en: {filepath}")
                    # Contar clases
                    classes = []
                    for line in content.split('\n'):
                        if line.strip().startswith("class ") and ":" in line:
                            class_name = line.strip().split()[1].split("(")[0].rstrip(":")
                            classes.append(class_name)
                    
                    print(f"\n📋 Clases encontradas en {filepath}:")
                    for cls in classes:
                        if "Rotation" in cls or "Trajectory" in cls:
                            print(f"   - {cls}")
    
    # Verificar si está implementado en el engine
    print("\n🔍 Verificando métodos en el engine...")
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    if os.path.exists(engine_path):
        with open(engine_path, 'r', encoding='utf-8') as f:
            engine_content = f.read()
        
        rotation_methods = []
        for line in engine_content.split('\n'):
            if "def " in line and "rotation" in line.lower():
                method_name = line.strip().split("(")[0].replace("def ", "")
                rotation_methods.append(method_name)
        
        if rotation_methods:
            print(f"\n📋 Métodos de rotación en el engine:")
            for method in rotation_methods:
                print(f"   - {method}")

if __name__ == "__main__":
    find_class()