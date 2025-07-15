#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO DIRECTO - Sin modificar archivos
⚡ Verificar qué está pasando realmente
"""

import os
import sys

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🔍 DIAGNÓSTICO DIRECTO DEL SISTEMA\n")
print("="*60)

# 1. Verificar qué clases existen
print("\n1️⃣ VERIFICANDO CLASES EN motion_components.py")

motion_file = "trajectory_hub/core/motion_components.py"
if os.path.exists(motion_file):
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar clases
    import re
    classes = re.findall(r'class (\w+)', content)
    print(f"   Clases encontradas: {classes}")
    
    # Verificar SourceMotion
    if 'SourceMotion' in classes:
        print("   ✅ SourceMotion existe")
        
        # Buscar si tiene get_position
        source_motion_match = re.search(r'class SourceMotion.*?(?=\nclass|\Z)', content, re.DOTALL)
        if source_motion_match:
            sm_content = source_motion_match.group(0)
            if 'def get_position' in sm_content:
                print("   ✅ SourceMotion.get_position() existe")
                
                # Ver qué hace
                get_pos_match = re.search(r'def get_position.*?(?=\n    def|\nclass|\Z)', sm_content, re.DOTALL)
                if get_pos_match:
                    method = get_pos_match.group(0)
                    if '+' in method and 'offset' in method:
                        print("   ✅ get_position() suma offsets")
                    else:
                        print("   ❌ get_position() NO suma offsets")
            else:
                print("   ❌ SourceMotion NO tiene get_position()")

# 2. Verificar qué usa el engine
print("\n2️⃣ VERIFICANDO enhanced_trajectory_engine.py")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        engine_content = f.read()
    
    # Qué importa
    imports = re.findall(r'from trajectory_hub\.core\.motion_components import ([^\n]+)', engine_content)
    if imports:
        print(f"   Importa: {imports}")
    
    # Buscar create_source
    create_source_match = re.search(r'def create_source.*?\n.*?return.*?\n', engine_content, re.DOTALL)
    if create_source_match:
        create_method = create_source_match.group(0)
        
        # Ver qué tipo de objeto crea
        if 'TrajectorySource(' in create_method:
            print("   → create_source() crea objetos TrajectorySource")
        elif 'Source(' in create_method:
            print("   → create_source() crea objetos Source")
        else:
            print("   → create_source() tipo no claro")
    
    # Buscar si usa SourceMotion directamente
    if 'SourceMotion(' in engine_content:
        print("   ✅ Usa SourceMotion directamente")
    else:
        print("   ❌ NO usa SourceMotion directamente")

# 3. Test real con monkey patching
print("\n3️⃣ TEST REAL CON INTERCEPTACIÓN")
print("-"*60)

try:
    # Importar el engine
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Guardar referencias originales
    original_update = None
    original_get_position = None
    
    # Interceptar métodos para ver si se llaman
    calls_log = []
    
    def log_call(method_name):
        def wrapper(*args, **kwargs):
            calls_log.append(method_name)
            print(f"   🔍 {method_name} llamado")
            return None  # Por ahora solo registrar
        return wrapper
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Crear macro
    macro_id = engine.create_macro("test", source_count=2, formation="line")
    print(f"✅ Macro creado: {macro_id}")
    
    # Intentar obtener una fuente
    print("\n🔍 Buscando cómo acceder a las fuentes...")
    
    # Opción 1: sources
    if hasattr(engine, 'sources'):
        print("   → engine.sources existe")
        sources = engine.sources
        if sources:
            first_id = list(sources.keys())[0]
            source = sources[first_id]
            print(f"   ✅ Fuente obtenida: {first_id}")
            print(f"   Tipo: {type(source).__name__}")
            
            # Ver qué tiene
            if hasattr(source, 'motion'):
                print(f"   → source.motion: {type(source.motion).__name__}")
            if hasattr(source, 'get_position'):
                print("   → source.get_position() existe")
    
    # Opción 2: _sources
    elif hasattr(engine, '_sources'):
        print("   → engine._sources existe")
        sources = engine._sources
        if sources:
            first_id = list(sources.keys())[0]
            source = sources[first_id]
            print(f"   ✅ Fuente obtenida: {first_id}")
            print(f"   Tipo: {type(source).__name__}")
    
    # Opción 3: buscar en todos los atributos
    else:
        print("   ❌ No se encontró sources ni _sources")
        
        # Buscar cualquier dict que contenga fuentes
        for attr_name in dir(engine):
            if not attr_name.startswith('_'):
                attr = getattr(engine, attr_name)
                if isinstance(attr, dict) and len(attr) > 0:
                    # Ver si parece contener fuentes
                    first_key = list(attr.keys())[0]
                    if 'test' in str(first_key) or 'source' in str(first_key):
                        print(f"   → Posibles fuentes en: engine.{attr_name}")
    
    # Test de concentración
    print("\n4️⃣ TEST DE CONCENTRACIÓN")
    
    # Aplicar concentración
    engine.set_macro_concentration(macro_id, 0.1)
    print("✅ Concentración aplicada")
    
    # Update
    engine.update()
    print("✅ Update ejecutado")
    
    # Ver si algo cambió
    print(f"\nMétodos llamados: {calls_log}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("📊 CONCLUSIONES")
print("="*60)

print("""
NECESITAMOS SABER:
1. ¿Qué clase se usa para las fuentes? (Source, TrajectorySource, etc.)
2. ¿Esa clase usa SourceMotion internamente?
3. ¿El get_position() de esa clase suma los offsets?

El problema puede ser que:
- SourceMotion existe pero no se usa
- Se usa otra clase que no tiene la lógica de deltas
- Los offsets se calculan pero no se aplican
""")