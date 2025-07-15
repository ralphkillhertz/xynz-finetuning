# === diagnose_engine_structure.py ===
# 🔍 Diagnostica la estructura real del engine

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import inspect

def diagnose_engine():
    """Diagnostica la estructura y métodos del engine"""
    print("\n🔍 DIAGNÓSTICO DE ESTRUCTURA - EnhancedTrajectoryEngine")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado\n")
    
    # 1. Listar todos los atributos
    print("📋 ATRIBUTOS DEL ENGINE:")
    print("-" * 40)
    attrs = [attr for attr in dir(engine) if not attr.startswith('__')]
    
    # Agrupar por tipo
    macro_attrs = [a for a in attrs if 'macro' in a.lower()]
    motion_attrs = [a for a in attrs if 'motion' in a.lower()]
    trajectory_attrs = [a for a in attrs if 'trajectory' in a.lower() or 'traj' in a.lower()]
    source_attrs = [a for a in attrs if 'source' in a.lower()]
    
    print("\n🎯 Atributos relacionados con MACROS:")
    for attr in macro_attrs:
        try:
            value = getattr(engine, attr)
            print(f"  - {attr}: {type(value).__name__}")
            if isinstance(value, dict) and len(value) > 0:
                print(f"    Contenido: {list(value.keys())[:3]}...")
        except:
            print(f"  - {attr}: [No accesible]")
    
    print("\n🎯 Atributos relacionados con MOTION:")
    for attr in motion_attrs:
        try:
            value = getattr(engine, attr)
            print(f"  - {attr}: {type(value).__name__}")
        except:
            print(f"  - {attr}: [No accesible]")
    
    print("\n🎯 Atributos relacionados con TRAJECTORY:")
    for attr in trajectory_attrs:
        print(f"  - {attr}")
    
    print("\n🎯 Atributos relacionados con SOURCE:")
    for attr in source_attrs:
        print(f"  - {attr}")
    
    # 2. Métodos relevantes
    print("\n\n📋 MÉTODOS RELEVANTES:")
    print("-" * 40)
    
    methods = [m for m in dir(engine) if callable(getattr(engine, m)) and not m.startswith('_')]
    
    # Filtrar métodos relevantes
    relevant_keywords = ['macro', 'trajectory', 'source', 'motion', 'create', 'set', 'get']
    relevant_methods = []
    
    for method in methods:
        if any(keyword in method.lower() for keyword in relevant_keywords):
            relevant_methods.append(method)
    
    # Mostrar con firma
    for method in sorted(relevant_methods):
        try:
            func = getattr(engine, method)
            sig = inspect.signature(func)
            print(f"\n  {method}{sig}")
        except:
            print(f"\n  {method}()")
    
    # 3. Test de creación de macro
    print("\n\n🧪 TEST DE CREACIÓN DE MACRO:")
    print("-" * 40)
    
    try:
        # Intentar crear macro
        result = engine.create_macro("test", source_count=3)
        print("✅ create_macro() ejecutado")
        print(f"   Resultado: {result}")
        
        # Buscar dónde se guardó
        print("\n🔍 Buscando el macro creado...")
        
        # Probar diferentes ubicaciones
        possible_locations = ['_macros', 'macros', 'macro_sources', '_macro_sources']
        
        for loc in possible_locations:
            if hasattr(engine, loc):
                container = getattr(engine, loc)
                if isinstance(container, dict) and "test" in container:
                    print(f"✅ Encontrado en: engine.{loc}")
                    macro = container["test"]
                    print(f"   Tipo: {type(macro).__name__}")
                    if hasattr(macro, 'source_ids'):
                        print(f"   source_ids: {list(macro.source_ids)}")
                    break
        
    except Exception as e:
        print(f"❌ Error al crear macro: {e}")
    
    # 4. Test de motion_states
    print("\n\n🧪 TEST DE MOTION_STATES:")
    print("-" * 40)
    
    if hasattr(engine, 'motion_states'):
        ms = engine.motion_states
        print(f"✅ motion_states existe: {type(ms).__name__}")
        print(f"   Número de elementos: {len(ms)}")
        if len(ms) > 0:
            # Mostrar primeros elementos
            for i, (k, v) in enumerate(list(ms.items())[:3]):
                print(f"   - {k}: {type(v).__name__}")
    else:
        print("❌ No tiene atributo motion_states")
    
    # 5. Test de update
    print("\n\n🧪 TEST DE MÉTODO UPDATE:")
    print("-" * 40)
    
    if hasattr(engine, 'update'):
        sig = inspect.signature(engine.update)
        print(f"✅ update existe: {sig}")
        
        # Ver el código del update
        try:
            import dis
            print("\n📝 Primeras líneas del método update:")
            dis.dis(engine.update, depth=1)
        except:
            pass
    else:
        print("❌ No tiene método update")
    
    return engine

if __name__ == "__main__":
    engine = diagnose_engine()
    
    print("\n\n💡 RESUMEN:")
    print("=" * 60)
    print("Usa esta información para crear un test correcto")
    print("que use los atributos y métodos reales del engine.")