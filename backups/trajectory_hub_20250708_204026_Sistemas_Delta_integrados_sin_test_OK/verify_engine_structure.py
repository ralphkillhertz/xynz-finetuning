# === verify_engine_structure.py ===
# 🔍 Verificar cómo acceder a macros y componentes
# ⚡ Inspección completa del engine

import inspect
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def inspect_engine():
    """Inspeccionar estructura real del engine"""
    
    print("🔍 INSPECCIÓN DEL ENGINE")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    
    # 1. Listar todos los atributos
    print("\n1️⃣ ATRIBUTOS DEL ENGINE:")
    print("-" * 40)
    
    attrs = [attr for attr in dir(engine) if not attr.startswith('__')]
    for attr in sorted(attrs):
        try:
            value = getattr(engine, attr)
            if not callable(value):
                print(f"   {attr}: {type(value).__name__}")
                if attr in ['_macros', 'macros']:
                    print(f"      -> Contenido: {value}")
        except:
            pass
    
    # 2. Buscar dónde están los macros
    print("\n2️⃣ BUSCANDO MACROS:")
    print("-" * 40)
    
    # Posibles ubicaciones
    possible_attrs = ['macros', '_macros', 'macro_manager', 'groups', '_groups']
    for attr in possible_attrs:
        if hasattr(engine, attr):
            print(f"   ✅ Encontrado: {attr}")
            value = getattr(engine, attr)
            print(f"      Tipo: {type(value)}")
            print(f"      Contenido: {value}")
    
    # 3. Crear un macro y ver dónde se guarda
    print("\n3️⃣ CREANDO MACRO DE PRUEBA:")
    print("-" * 40)
    
    result = engine.create_macro("test", 3, formation="line")
    print(f"   Resultado create_macro: {result}")
    
    # Buscar el macro creado
    print("\n   Buscando el macro creado...")
    for attr in ['_macros', 'macros', '_groups']:
        if hasattr(engine, attr):
            container = getattr(engine, attr)
            if isinstance(container, dict) and "test" in container:
                print(f"   ✅ Macro encontrado en: {attr}")
                print(f"      Tipo del macro: {type(container['test'])}")
                if hasattr(container['test'], 'source_ids'):
                    print(f"      Source IDs: {container['test'].source_ids}")
    
    # 4. Verificar motion_states
    print("\n4️⃣ VERIFICANDO MOTION_STATES:")
    print("-" * 40)
    
    if hasattr(engine, 'motion_states'):
        print(f"   ✅ motion_states existe")
        print(f"   Tipo: {type(engine.motion_states)}")
        print(f"   Contenido: {list(engine.motion_states.keys())}")
    
    # 5. Test rápido de concentración manual
    print("\n5️⃣ TEST RÁPIDO:")
    print("-" * 40)
    
    # Intentar configurar concentración manualmente
    from trajectory_hub.core.motion_components import ConcentrationComponent
    
    if hasattr(engine, '_macros') and 'test' in engine._macros:
        macro = engine._macros['test']
        print(f"   Configurando concentración para macro 'test'")
        
        for sid in macro.source_ids:
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                motion.active_components['concentration'] = ConcentrationComponent(
                    concentration_factor=0.8,
                    macro=macro
                )
                print(f"   ✅ Concentración añadida a fuente {sid}")
    
    return engine

if __name__ == "__main__":
    engine = inspect_engine()
    
    print("\n" + "=" * 60)
    print("📝 CONCLUSIÓN:")
    print("   Use el atributo correcto encontrado arriba para acceder a macros")