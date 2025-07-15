#!/usr/bin/env python3
"""
🔍 Explorar métodos del engine en runtime
"""

import os
import sys

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine()
    
    print("🔍 MÉTODOS DEL ENGINE\n")
    
    # Todos los métodos
    methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
    
    # Categorizar
    print("📊 MÉTODOS DE ACTUALIZACIÓN:")
    for method in methods:
        if any(word in method.lower() for word in ['update', 'tick', 'step', 'process']):
            print(f"   • {method}()")
    
    print("\n📊 MÉTODOS DE FUENTES:")
    for method in methods:
        if 'source' in method.lower():
            print(f"   • {method}()")
    
    print("\n📊 MÉTODOS DE POSICIÓN:")
    for method in methods:
        if 'position' in method.lower():
            print(f"   • {method}()")
    
    # Ver si tiene update
    if hasattr(engine, 'update'):
        import inspect
        sig = inspect.signature(engine.update)
        print(f"\n✅ engine.update{sig}")
    else:
        print("\n❌ engine NO tiene método update()")
        
        # Buscar alternativas
        print("\n🔍 Buscando método principal de actualización...")
        
        # El controller debe llamar algo
        # Veamos qué métodos podrían ser
        candidates = []
        for method in methods:
            try:
                # Ver si acepta dt o no params
                sig = inspect.signature(getattr(engine, method))
                params = list(sig.parameters.keys())
                if len(params) <= 2:  # self y tal vez dt
                    if any(word in method.lower() for word in ['update', 'tick', 'step']):
                        candidates.append((method, sig))
            except:
                pass
        
        if candidates:
            print("\n   Candidatos:")
            for method, sig in candidates:
                print(f"   • {method}{sig}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
