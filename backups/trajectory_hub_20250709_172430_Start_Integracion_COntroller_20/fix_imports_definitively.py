#!/usr/bin/env python3
"""
🔧 Fix definitivo de imports
⚡ Limpia todos los imports problemáticos
"""

import os
import re

def fix_imports():
    """Arregla imports en enhanced_trajectory_engine.py"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    print("🔍 Analizando imports...")
    
    # Leer archivo
    with open(engine_path, 'r') as f:
        content = f.read()
    
    # 1. Primero, verificar qué existe realmente en motion_components
    motion_path = "trajectory_hub/core/motion_components.py"
    available_imports = []
    
    if os.path.exists(motion_path):
        with open(motion_path, 'r') as f:
            motion_content = f.read()
            
        # Buscar todas las clases y funciones definidas
        class_pattern = r'^class\s+(\w+)'
        func_pattern = r'^def\s+(\w+)'
        
        for line in motion_content.split('\n'):
            class_match = re.match(class_pattern, line)
            func_match = re.match(func_pattern, line)
            
            if class_match:
                available_imports.append(class_match.group(1))
            elif func_match:
                available_imports.append(func_match.group(1))
        
        print(f"✅ Encontrados en motion_components: {len(available_imports)} elementos")
        print(f"   Incluye: {', '.join(available_imports[:5])}...")
    
    # 2. Arreglar el bloque de imports de motion_components
    # Buscar el bloque completo
    import_pattern = r'from trajectory_hub\.core\.motion_components import \(([\s\S]*?)\)'
    match = re.search(import_pattern, content)
    
    if match:
        import_block = match.group(1)
        imports = [imp.strip() for imp in import_block.split(',') if imp.strip()]
        
        print(f"\n📋 Imports actuales: {len(imports)}")
        
        # Filtrar solo los que existen
        valid_imports = []
        removed_imports = []
        
        for imp in imports:
            imp_name = imp.strip()
            if imp_name in available_imports:
                valid_imports.append(imp_name)
            else:
                removed_imports.append(imp_name)
        
        if removed_imports:
            print(f"\n❌ Removiendo imports inexistentes:")
            for imp in removed_imports:
                print(f"   - {imp}")
        
        # Reconstruir el import
        if valid_imports:
            new_import = "from trajectory_hub.core.motion_components import (\n"
            for i, imp in enumerate(valid_imports):
                if i < len(valid_imports) - 1:
                    new_import += f"    {imp},\n"
                else:
                    new_import += f"    {imp}\n"
            new_import += ")"
            
            # Reemplazar
            old_import = match.group(0)
            content = content.replace(old_import, new_import)
            
            print(f"\n✅ Import actualizado con {len(valid_imports)} elementos válidos")
    
    # 3. Quitar cualquier import de FormationManager mal ubicado
    # (debe estar en línea separada, no dentro de otro import)
    content = re.sub(
        r'from trajectory_hub\.control\.managers\.formation_manager import FormationManager\s*\n\s*\w+',
        lambda m: m.group(0).replace('from trajectory_hub.control.managers.formation_manager import FormationManager\n', ''),
        content
    )
    
    # 4. Guardar
    with open(engine_path, 'w') as f:
        f.write(content)
    
    print("\n✅ Imports arreglados")
    
    # 5. Verificar sintaxis
    print("\n🧪 Verificando sintaxis...")
    import py_compile
    try:
        py_compile.compile(engine_path, doraise=True)
        print("✅ Sintaxis correcta")
        
        # Test import
        print("\n🧪 Probando import...")
        os.system(f"cd {os.path.dirname(engine_path)} && python -c 'from enhanced_trajectory_engine import EnhancedTrajectoryEngine; print(\"✅ Import exitoso\")'")
        
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Error de sintaxis: {e}")
        return False

def verify_system():
    """Verifica que el sistema pueda arrancar"""
    print("\n🔍 Verificando sistema...")
    
    # Test básico
    test_code = """
import sys
sys.path.insert(0, '.')
try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    print("✅ Engine importa correctamente")
    
    from trajectory_hub.interface.interactive_controller import InteractiveController
    print("✅ Controller importa correctamente")
    
    print("\\n✅ SISTEMA LISTO PARA USAR")
except Exception as e:
    print(f"❌ Error: {e}")
"""
    
    with open("_test_system.py", 'w') as f:
        f.write(test_code)
    
    os.system("python _test_system.py")
    os.remove("_test_system.py")

if __name__ == "__main__":
    print("🔧 FIX DEFINITIVO DE IMPORTS")
    print("=" * 50)
    
    if fix_imports():
        verify_system()
        
        print("\n🎯 Para ejecutar el sistema:")
        print("   python -m trajectory_hub.interface.interactive_controller")
    else:
        print("\n❌ No se pudieron arreglar los imports")
        print("   Revisa los mensajes de error arriba")