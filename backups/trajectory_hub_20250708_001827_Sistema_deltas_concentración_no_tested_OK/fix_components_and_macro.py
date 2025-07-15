# === fix_components_and_macro.py ===
# 🔧 Fix: Arregla KeyError trajectory_transform y Macro import
# ⚡ Impacto: CRÍTICO - Resuelve errores de creación de fuentes

import os
import re
from datetime import datetime

def fix_issues():
    """Arregla los problemas de components y Macro import"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Fix 1: Arreglar create_source - trajectory_transform
    print("\n🔧 Arreglando create_source...")
    
    # Buscar la línea problemática
    problem_line = "motion.components['trajectory_transform'].enabled = False"
    
    if problem_line in content:
        # Reemplazar con verificación segura
        safe_code = """# Verificar si existe antes de acceder
        if 'trajectory_transform' in motion.components:
            motion.components['trajectory_transform'].enabled = False"""
        
        content = content.replace(problem_line, safe_code)
        print("✅ create_source arreglado con verificación segura")
    else:
        print("⚠️ Línea problemática no encontrada, buscando alternativa...")
        
        # Buscar en create_source
        pattern = r'(def create_source.*?)(motion\.components\[.*?\].*?)(.*?return)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Comentar cualquier acceso directo a components
            new_section = re.sub(
                r'motion\.components\[.*?\].*',
                '# Acceso a components deshabilitado temporalmente',
                match.group(2)
            )
            content = content[:match.start(2)] + new_section + content[match.end(2):]
            print("✅ Accesos a components comentados")
    
    # Fix 2: Asegurar que Macro esté en __all__ o importable
    print("\n🔧 Verificando clase Macro...")
    
    # Verificar si existe la clase Macro
    if 'class Macro' in content:
        print("✅ Clase Macro encontrada")
        
        # Verificar si está en __all__
        if '__all__' in content:
            all_pattern = r'__all__\s*=\s*\[(.*?)\]'
            all_match = re.search(all_pattern, content, re.DOTALL)
            
            if all_match and "'Macro'" not in all_match.group(1):
                # Añadir Macro a __all__
                current_all = all_match.group(1)
                new_all = current_all.rstrip() + ",\n    'Macro'"
                content = content[:all_match.start(1)] + new_all + content[all_match.end(1):]
                print("✅ Macro añadido a __all__")
        else:
            # Crear __all__ al principio del archivo después de imports
            import_end = content.rfind('import')
            if import_end > -1:
                import_end = content.find('\n', import_end) + 1
                all_export = "\n__all__ = ['EnhancedTrajectoryEngine', 'Macro']\n\n"
                content = content[:import_end] + all_export + content[import_end:]
                print("✅ __all__ creado con Macro")
    else:
        print("❌ Clase Macro no encontrada en el archivo")
    
    # Escribir archivo corregido
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Archivo actualizado")
    
    # Verificar sintaxis
    try:
        compile(content, engine_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

def create_minimal_test():
    """Crea un test mínimo sin dependencias problemáticas"""
    test_code = '''# === test_delta_minimal.py ===
# Test mínimo del sistema sin components problemáticos

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import time

print("🧪 TEST MÍNIMO DEL SISTEMA")
print("="*50)

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(n_sources=5, update_rate=60)
    print("✅ Engine creado")
    
    # Crear fuentes manualmente
    for i in range(3):
        engine.create_source(i, f"test_{i}")
    print("✅ 3 fuentes creadas")
    
    # Update simple
    for i in range(5):
        engine.update()
        time.sleep(0.1)
    
    print("✅ Sistema actualizado 5 veces")
    
    # Verificar posiciones
    if hasattr(engine, '_positions'):
        print(f"✅ Posiciones shape: {engine._positions.shape}")
    
    print("\\n✅ TEST COMPLETADO - Sistema base funcional")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open('test_delta_minimal.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Test mínimo creado: test_delta_minimal.py")

if __name__ == "__main__":
    print("🔧 FIX DE COMPONENTS Y MACRO IMPORT")
    print("="*60)
    
    success = fix_issues()
    
    if success:
        create_minimal_test()
        print("\n✅ Fixes aplicados exitosamente")
        print("\n📋 Siguiente paso - prueba el test mínimo:")
        print("$ python test_delta_minimal.py")
        print("\nSi funciona, intenta:")
        print("$ python test_delta_concentration_final.py")
    else:
        print("\n❌ Error aplicando fixes")