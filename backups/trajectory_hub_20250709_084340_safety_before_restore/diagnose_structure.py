# === diagnose_structure.py ===
# 🔍 Diagnóstico de la estructura del sistema
# ⚡ Para entender las APIs correctas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import inspect

def diagnose_system():
    """Diagnosticar la estructura del sistema"""
    print("🔍 DIAGNÓSTICO DEL SISTEMA")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    
    # 1. Inspeccionar métodos disponibles
    print("\n📋 MÉTODOS PRINCIPALES:")
    methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
    for method in sorted(methods)[:20]:  # Primeros 20
        try:
            sig = inspect.signature(getattr(engine, method))
            print(f"  • {method}{sig}")
        except:
            print(f"  • {method}()")
    
    # 2. Verificar estructura de macros
    print("\n📦 ESTRUCTURA DE MACROS:")
    print(f"  • _macros exists: {hasattr(engine, '_macros')}")
    print(f"  • macros exists: {hasattr(engine, 'macros')}")
    
    # 3. Crear un macro y ver su estructura
    print("\n🧪 CREANDO MACRO DE PRUEBA:")
    try:
        macro_name = engine.create_macro("diagnose", 3, formation='line')
        print(f"  ✅ Macro creado: {macro_name}")
        
        # Ver estructura
        if hasattr(engine, '_macros'):
            macro = engine._macros.get(macro_name)
            if macro:
                print(f"  • Tipo: {type(macro)}")
                print(f"  • Atributos: {[a for a in dir(macro) if not a.startswith('_')][:10]}")
                if hasattr(macro, 'source_ids'):
                    print(f"  • Source IDs: {macro.source_ids}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 4. Verificar motion_states
    print("\n🔄 MOTION STATES:")
    print(f"  • motion_states exists: {hasattr(engine, 'motion_states')}")
    if hasattr(engine, 'motion_states'):
        print(f"  • Tipo: {type(engine.motion_states)}")
        print(f"  • Cantidad: {len(engine.motion_states)}")
        
        # Ver estructura de un motion state
        if engine.motion_states:
            sid = list(engine.motion_states.keys())[0]
            motion = engine.motion_states[sid]
            print(f"\n  📌 Motion State {sid}:")
            print(f"    • Tipo: {type(motion)}")
            if hasattr(motion, 'active_components'):
                print(f"    • active_components tipo: {type(motion.active_components)}")
                print(f"    • active_components contenido: {motion.active_components}")

if __name__ == "__main__":
    diagnose_system()
