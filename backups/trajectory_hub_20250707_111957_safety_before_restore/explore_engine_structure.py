#!/usr/bin/env python3
"""
🔍 Explorador de Estructura del Engine
⚡ Descubre la estructura real sin asumir nada
"""

import sys
import os
import numpy as np

# Auto-detectar ruta
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

def explore_engine():
    """Explorar la estructura real del engine"""
    print("🔍 EXPLORADOR DE ESTRUCTURA DEL ENGINE\n")
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        print("✅ Engine importado\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Crear instancia
    os.environ['DISABLE_OSC'] = '1'
    engine = EnhancedTrajectoryEngine()
    
    # 1. Explorar atributos del engine
    print("📊 ATRIBUTOS DEL ENGINE:")
    attrs = [attr for attr in dir(engine) if not attr.startswith('_')]
    
    # Categorizar atributos
    methods = []
    properties = []
    
    for attr in attrs:
        try:
            value = getattr(engine, attr)
            if callable(value):
                methods.append(attr)
            else:
                properties.append((attr, type(value).__name__))
        except:
            pass
    
    print("\n📁 Propiedades:")
    for prop, type_name in sorted(properties):
        print(f"   • {prop}: {type_name}")
    
    print("\n🔧 Métodos principales:")
    # Filtrar métodos relevantes
    relevant_methods = [m for m in methods if any(keyword in m.lower() for keyword in 
                       ['create', 'macro', 'source', 'set', 'get', 'update', 'trajectory'])]
    
    for method in sorted(relevant_methods):
        print(f"   • {method}()")
    
    # 2. Intentar crear algo
    print("\n🧪 PRUEBA DE CREACIÓN:")
    
    # Buscar método de creación
    create_methods = [m for m in methods if 'create' in m.lower()]
    
    if create_methods:
        print(f"   Métodos de creación encontrados: {create_methods}")
        
        # Intentar el primero
        method_name = create_methods[0]
        method = getattr(engine, method_name)
        
        # Inspeccionar parámetros
        import inspect
        try:
            sig = inspect.signature(method)
            print(f"\n   📝 {method_name}{sig}")
            
            # Intentar llamar con parámetros básicos
            if 'macro' in method_name.lower():
                print("\n   🔄 Intentando crear macro...")
                try:
                    # Probar diferentes combinaciones
                    result = method("test", 3)  # nombre, cantidad
                    print(f"   ✅ Creado: {result}")
                except Exception as e1:
                    try:
                        result = method("test", source_count=3)
                        print(f"   ✅ Creado: {result}")
                    except Exception as e2:
                        try:
                            result = method(name="test", source_count=3)
                            print(f"   ✅ Creado: {result}")
                        except Exception as e3:
                            print(f"   ❌ No se pudo crear: {e3}")
        except:
            pass
    
    # 3. Buscar dónde se almacenan los datos
    print("\n📦 BUSCANDO ALMACENAMIENTO DE DATOS:")
    
    # Buscar diccionarios o listas
    storage_candidates = []
    for prop, type_name in properties:
        if type_name in ['dict', 'list', 'defaultdict']:
            storage_candidates.append(prop)
            value = getattr(engine, prop)
            if hasattr(value, '__len__'):
                print(f"   • {prop} ({type_name}): {len(value)} elementos")
            else:
                print(f"   • {prop} ({type_name})")
    
    # 4. Buscar métodos de espacialización
    print("\n🎯 MÉTODOS DE ESPACIALIZACIÓN:")
    
    spatial_methods = [m for m in methods if any(keyword in m.lower() for keyword in
                      ['concentration', 'spatial', 'distance', 'rotation', 'algorithmic'])]
    
    for method in sorted(spatial_methods):
        print(f"   • {method}()")
    
    # 5. Test rápido de concentración
    if 'set_concentration' in methods:
        print("\n🧪 TEST RÁPIDO DE CONCENTRACIÓN:")
        print("   ✅ Método set_concentration disponible")
        
        # Ver parámetros
        method = getattr(engine, 'set_concentration')
        sig = inspect.signature(method)
        print(f"   📝 set_concentration{sig}")
    
    # 6. Buscar el problema real
    print("\n🔍 DIAGNÓSTICO DEL PROBLEMA:")
    
    # Verificar si hay fuentes/sources
    source_attrs = [p for p, _ in properties if 'source' in p.lower()]
    if source_attrs:
        print(f"   ✅ Atributos de fuentes encontrados: {source_attrs}")
        
        # Verificar contenido
        for attr in source_attrs:
            container = getattr(engine, attr)
            if hasattr(container, '__len__'):
                print(f"      {attr}: {len(container)} elementos")
    
    # Verificar macros
    macro_attrs = [p for p, _ in properties if 'macro' in p.lower()]
    if macro_attrs:
        print(f"   ✅ Atributos de macros encontrados: {macro_attrs}")
    else:
        # Buscar alternativas
        print("   ⚠️  No se encontró 'macros', buscando alternativas...")
        possible_containers = ['groups', 'collections', 'sets', 'clusters']
        for prop, _ in properties:
            if any(c in prop.lower() for c in possible_containers):
                print(f"      Posible contenedor: {prop}")
    
    return engine

if __name__ == "__main__":
    try:
        engine = explore_engine()
        print("\n✨ Exploración completada")
        print("\n💡 Basado en la estructura encontrada, ejecutaré el fix apropiado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()