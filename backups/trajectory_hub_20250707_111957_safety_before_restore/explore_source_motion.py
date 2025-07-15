#!/usr/bin/env python3
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
        
        print("🔍 EXPLORACIÓN DE SourceMotion\n")
        print(f"Tipo: {type(motion).__name__}")
        
        # 1. Todos los atributos
        print("\n📊 ATRIBUTOS:")
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
        
        print("\n📁 Propiedades:")
        for prop, type_name, value in sorted(properties):
            print(f"   • {prop}: {type_name} = {value}")
        
        print("\n🔧 Métodos:")
        for method in sorted(methods):
            print(f"   • {method}()")
        
        # 2. Buscar cómo obtener posición
        print("\n🎯 BUSCANDO CÓMO OBTENER POSICIÓN:")
        
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
            print(f"\n📦 COMPONENTES: {list(motion.components.keys())}")
        
        # 4. Intentar actualizar
        print("\n🔄 INTENTANDO ACTUALIZAR:")
        
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
        print("\n🔗 INTEGRACIÓN CON ENGINE:")
        
        # Ver si el engine tiene métodos para obtener posición
        if hasattr(engine, 'get_source_position'):
            try:
                pos = engine.get_source_position(0)  # ID 0
                print(f"   ✅ engine.get_source_position(0): {pos}")
            except:
                pass
        
        # Ver métodos del engine relacionados
        engine_methods = [m for m in dir(engine) if 'position' in m.lower() or 'source' in m.lower()]
        print(f"\n   Métodos del engine relevantes:")
        for method in engine_methods[:10]:
            if not method.startswith('_'):
                print(f"   • {method}")
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
