#!/usr/bin/env python3
"""
🔍 ANÁLISIS COMPLETO - Estructura real de SourceMotion
⚡ Ver qué tiene y cómo funciona realmente
"""

import os
import re

def analyze_source_motion():
    """Analizar la estructura completa de SourceMotion"""
    
    print("🔍 ANÁLISIS COMPLETO DE SourceMotion\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # 1. Encontrar la clase SourceMotion completa
    print("1️⃣ EXTRAYENDO CLASE SourceMotion...")
    
    class_pattern = r'(class SourceMotion[^:]*:.*?)(?=\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encontró SourceMotion")
        return
    
    class_content = class_match.group(1)
    
    # 2. Analizar __init__
    print("\n2️⃣ ANALIZANDO __init__...")
    
    init_pattern = r'def __init__\(self.*?\):\s*\n(.*?)(?=\n    def|\Z)'
    init_match = re.search(init_pattern, class_content, re.DOTALL)
    
    if init_match:
        init_body = init_match.group(1)
        
        # Extraer todas las asignaciones self.algo = 
        assignments = re.findall(r'self\.(\w+)\s*=\s*([^\n]+)', init_body)
        
        print("   Atributos inicializados:")
        for attr, value in assignments[:15]:  # Primeros 15
            print(f"   • self.{attr} = {value.strip()}")
    
    # 3. Buscar todos los métodos
    print("\n3️⃣ MÉTODOS DE LA CLASE:")
    
    methods = re.findall(r'def (\w+)\(self[^)]*\):', class_content)
    for method in methods:
        print(f"   • {method}()")
    
    # 4. Ver si hereda de algo
    print("\n4️⃣ HERENCIA:")
    
    class_def = re.search(r'class SourceMotion(\([^)]*\))?:', class_content)
    if class_def and class_def.group(1):
        print(f"   Hereda de: {class_def.group(1)}")
    else:
        print("   No hereda de ninguna clase")
    
    # 5. Buscar cómo obtiene/establece posición
    print("\n5️⃣ GESTIÓN DE POSICIÓN:")
    
    # Buscar métodos relacionados con posición
    position_methods = []
    for method in methods:
        if 'position' in method.lower() or 'pos' in method.lower():
            position_methods.append(method)
    
    if position_methods:
        print(f"   Métodos relacionados: {position_methods}")
    
    # Ver si usa algún patrón específico
    if 'state' in init_body.lower():
        print("   📍 Parece usar un sistema de estados")
    
    # 6. Crear test de exploración real
    print("\n6️⃣ CREANDO TEST DE EXPLORACIÓN...")
    
    test_script = '''#!/usr/bin/env python3
"""
🔍 Exploración real de SourceMotion
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=1)
    
    if hasattr(engine, '_source_motions') and engine._source_motions:
        motion = list(engine._source_motions.values())[0]
        
        print("🔍 EXPLORACIÓN DE SourceMotion\\n")
        print(f"Tipo: {type(motion).__name__}")
        
        # 1. Todos los atributos
        print("\\n📊 ATRIBUTOS:")
        attrs = [a for a in dir(motion) if not a.startswith('_')]
        
        # Agrupar por tipo
        methods = []
        properties = []
        
        for attr in attrs:
            try:
                value = getattr(motion, attr)
                if callable(value):
                    methods.append(attr)
                else:
                    properties.append((attr, type(value).__name__, str(value)[:50]))
            except:
                pass
        
        print("\\n📁 Propiedades:")
        for prop, type_name, value in sorted(properties):
            print(f"   • {prop}: {type_name} = {value}")
        
        print("\\n🔧 Métodos:")
        for method in sorted(methods):
            print(f"   • {method}()")
        
        # 2. Buscar cómo obtener posición
        print("\\n🎯 BUSCANDO CÓMO OBTENER POSICIÓN:")
        
        # Probar diferentes formas
        position_attrs = ['position', 'pos', 'location', 'state', 'transform']
        
        for attr in position_attrs:
            if hasattr(motion, attr):
                value = getattr(motion, attr)
                print(f"   ✅ {attr}: {type(value).__name__}")
                
                # Si es un objeto, ver qué tiene
                if hasattr(value, 'position'):
                    print(f"      → {attr}.position: {getattr(value, 'position')}")
        
        # 3. Ver si tiene componentes
        if hasattr(motion, 'components'):
            print(f"\\n📦 COMPONENTES: {list(motion.components.keys())}")
        
        # 4. Intentar actualizar
        print("\\n🔄 INTENTANDO ACTUALIZAR:")
        
        # Ver qué parámetros necesita update
        if hasattr(motion, 'update'):
            import inspect
            sig = inspect.signature(motion.update)
            print(f"   update{sig}")
            
            # Intentar llamar con diferentes parámetros
            try:
                motion.update(0.1)
                print("   ✅ update(0.1) funcionó")
            except TypeError as e:
                print(f"   ❌ update(0.1) falló: {e}")
                
                # Ver qué necesita
                params = list(sig.parameters.keys())
                print(f"   Parámetros esperados: {params}")
        
        # 5. Cómo se integra con el engine
        print("\\n🔗 INTEGRACIÓN CON ENGINE:")
        
        # Ver si el engine tiene métodos para obtener posición
        if hasattr(engine, 'get_source_position'):
            try:
                pos = engine.get_source_position(0)  # ID 0
                print(f"   ✅ engine.get_source_position(0): {pos}")
            except:
                pass
        
        # Ver métodos del engine relacionados
        engine_methods = [m for m in dir(engine) if 'position' in m.lower() or 'source' in m.lower()]
        print(f"\\n   Métodos del engine relevantes:")
        for method in engine_methods[:10]:
            if not method.startswith('_'):
                print(f"   • {method}")
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("explore_source_motion.py", 'w') as f:
        f.write(test_script)
    
    print("   ✅ Script creado: explore_source_motion.py")
    
    # 7. Conclusiones preliminares
    print("\n" + "="*60)
    print("📊 ANÁLISIS PRELIMINAR")
    print("="*60)
    
    if 'get_position' not in methods:
        print("\n⚠️  SourceMotion NO tiene get_position()")
        print("   → Puede que use otro sistema para posiciones")
    
    if 'time' not in [attr for attr, _ in assignments]:
        print("\n⚠️  SourceMotion NO tiene atributo time")
        print("   → Puede que el tiempo se maneje externamente")
    
    print("\n💡 HIPÓTESIS:")
    print("   SourceMotion podría ser solo un contenedor de componentes")
    print("   La posición real podría manejarse en otro lugar")
    print("   Necesitamos ver cómo el engine obtiene las posiciones")

if __name__ == "__main__":
    analyze_source_motion()
    
    print("\n🚀 EJECUTA LA EXPLORACIÓN:")
    print("   python explore_source_motion.py")
    print("\n📊 Esto nos dirá exactamente cómo funciona SourceMotion")