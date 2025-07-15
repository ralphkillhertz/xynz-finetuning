#!/usr/bin/env python3
"""
verify_and_fix_concentration.py - Verifica y corrige la integración de concentración
"""

import os
import inspect

def check_engine_methods():
    """Verificar qué métodos tiene realmente EnhancedTrajectoryEngine"""
    print("🔍 VERIFICANDO MÉTODOS DEL ENGINE...\n")
    
    try:
        from trajectory_hub import EnhancedTrajectoryEngine
        
        engine = EnhancedTrajectoryEngine()
        
        # Listar todos los métodos
        methods = [method for method in dir(engine) if not method.startswith('_')]
        
        print("Métodos públicos disponibles:")
        for method in sorted(methods):
            print(f"  - {method}")
        
        # Buscar métodos de concentración
        concentration_methods = [m for m in methods if 'concentration' in m.lower()]
        
        if concentration_methods:
            print(f"\n✅ Métodos de concentración encontrados: {concentration_methods}")
        else:
            print("\n❌ No se encontraron métodos de concentración")
            
        # Verificar set_macro_trajectory
        if hasattr(engine, 'set_macro_trajectory'):
            sig = inspect.signature(engine.set_macro_trajectory)
            print(f"\n📝 Firma de set_macro_trajectory: {sig}")
        
        return concentration_methods
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def check_file_content():
    """Verificar el contenido del archivo enhanced_trajectory_engine.py"""
    print("\n\n🔍 VERIFICANDO CONTENIDO DEL ARCHIVO...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar métodos de concentración
    if "def set_macro_concentration" in content:
        print("✅ set_macro_concentration ESTÁ en el archivo")
        
        # Encontrar la posición
        pos = content.find("def set_macro_concentration")
        # Mostrar contexto
        start = max(0, pos - 100)
        end = min(len(content), pos + 500)
        print("\nContexto:")
        print("-" * 60)
        print(content[start:end])
        print("-" * 60)
    else:
        print("❌ set_macro_concentration NO está en el archivo")
        
    # Buscar la clase
    class_start = content.find("class EnhancedTrajectoryEngine")
    if class_start != -1:
        # Ver cuántos métodos hay después de los de concentración
        conc_pos = content.find("def set_macro_concentration")
        if conc_pos > class_start:
            print(f"\n📍 Posiciones:")
            print(f"   - Clase empieza en: {class_start}")
            print(f"   - Métodos de concentración en: {conc_pos}")
            
            # Verificar si está dentro de la clase
            next_class = content.find("\nclass ", class_start + 1)
            if next_class == -1 or conc_pos < next_class:
                print("   ✅ Los métodos están dentro de la clase")
            else:
                print("   ❌ Los métodos están FUERA de la clase")

def fix_method_indentation():
    """Corregir la indentación de los métodos si es necesario"""
    print("\n\n🔧 VERIFICANDO INDENTACIÓN...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar los métodos de concentración
    concentration_start = -1
    for i, line in enumerate(lines):
        if "def set_macro_concentration" in line:
            concentration_start = i
            break
    
    if concentration_start != -1:
        # Verificar indentación
        indent = len(lines[concentration_start]) - len(lines[concentration_start].lstrip())
        print(f"Indentación encontrada: {indent} espacios")
        
        if indent == 0:
            print("❌ Los métodos no tienen indentación - están fuera de la clase")
            print("✅ Corrigiendo indentación...")
            
            # Encontrar donde termina la clase (antes del siguiente class o al final)
            class_end = len(lines)
            for i in range(concentration_start, len(lines)):
                if lines[i].startswith("class ") or (i > concentration_start and lines[i].strip() and not lines[i].startswith(" ")):
                    class_end = i
                    break
            
            # Indentar todos los métodos de concentración
            for i in range(concentration_start, class_end):
                if lines[i].strip():  # No indentar líneas vacías
                    lines[i] = "    " + lines[i]
            
            # Guardar
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            print("✅ Indentación corregida")
        elif indent == 4:
            print("✅ La indentación es correcta (4 espacios)")
        else:
            print(f"⚠️  Indentación inusual: {indent} espacios")

def create_working_test():
    """Crear un test que funcione con los métodos disponibles"""
    print("\n\n📝 CREANDO TEST FUNCIONAL...\n")
    
    test_code = '''#!/usr/bin/env python3
"""
test_concentration_working.py - Test adaptado a los métodos disponibles
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

def test_concentration():
    print("🧪 TEST ADAPTADO DEL SISTEMA DE CONCENTRACIÓN\\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro
    print("1. Creando macro...")
    macro_id = engine.create_macro("test_concentration", 10, 
                                   formation="circle", spacing=2.0)
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Verificar métodos disponibles
    print("\\n2. Métodos disponibles:")
    methods = [m for m in dir(engine) if 'concentration' in m.lower()]
    if methods:
        for m in methods:
            print(f"   - {m}")
    else:
        print("   ❌ No hay métodos de concentración")
        print("\\n   Intentando acceso directo a componentes...")
        
        # Acceso directo a los componentes
        if hasattr(engine, '_source_motions'):
            print("   ✅ Acceso a _source_motions disponible")
            
            # Obtener las fuentes del macro
            if hasattr(engine, '_macros') and macro_id in engine._macros:
                macro = engine._macros[macro_id]
                if hasattr(macro, 'source_ids'):
                    print(f"   ✅ Macro tiene {len(macro.source_ids)} fuentes")
                    
                    # Configurar concentración manualmente
                    from trajectory_hub.core.motion_components import ConcentrationComponent
                    
                    for sid in list(macro.source_ids)[:3]:  # Solo las primeras 3 para test
                        if sid in engine._source_motions:
                            motion = engine._source_motions[sid]
                            
                            # Agregar componente si no existe
                            if 'concentration' not in motion.components:
                                motion.components['concentration'] = ConcentrationComponent()
                            
                            # Configurar
                            conc = motion.components['concentration']
                            conc.enabled = True
                            conc.factor = 0.5
                            conc.target_point = np.array([0.0, 0.0, 0.0])
                            
                            print(f"   ✅ Concentración configurada para fuente {sid}")
    
    # Intentar actualizar
    print("\\n3. Probando updates...")
    try:
        for i in range(5):
            engine.update()
        print("   ✅ Updates ejecutados sin errores")
    except Exception as e:
        print(f"   ❌ Error en update: {e}")
    
    print("\\n✅ TEST COMPLETADO")
    print("\\nNOTA: Los métodos de concentración pueden no estar disponibles.")
    print("Verifica que enhanced_trajectory_engine.py tiene los métodos correctamente indentados.")

if __name__ == "__main__":
    test_concentration()
'''
    
    with open("test_concentration_working.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ test_concentration_working.py creado")

def main():
    print("="*60)
    print("🔍 VERIFICACIÓN Y CORRECCIÓN DE CONCENTRACIÓN")
    print("="*60)
    
    # Verificar métodos
    methods = check_engine_methods()
    
    # Verificar archivo
    check_file_content()
    
    # Corregir si es necesario
    if not methods:
        fix_method_indentation()
        
        print("\n🔄 Verificando nuevamente después de la corrección...")
        methods = check_engine_methods()
        
        if methods:
            print("\n✅ CORRECCIÓN EXITOSA")
        else:
            print("\n⚠️  Los métodos siguen sin estar disponibles")
            print("Puede ser necesario reiniciar Python o revisar manualmente")
    
    # Crear test funcional
    create_working_test()
    
    print("\n" + "="*60)
    print("PRÓXIMOS PASOS:")
    print("1. Si los métodos no aparecen, reinicia Python")
    print("2. Ejecuta: python test_concentration_working.py")
    print("3. Revisa manualmente enhanced_trajectory_engine.py")

if __name__ == "__main__":
    main()