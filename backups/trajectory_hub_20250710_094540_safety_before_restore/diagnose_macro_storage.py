#!/usr/bin/env python3
# 🔧 Diagnóstico: Cómo se almacenan los macros
# ⚡ Verificar estructuras de datos actuales
# 🎯 Impacto: ALTO

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def diagnose_macros():
    print("\n🔍 DIAGNÓSTICO DE ALMACENAMIENTO DE MACROS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear algunos macros de prueba
    print("\n1️⃣ Creando macros de prueba...")
    engine.create_macro("test_circle", 3, formation="circle")
    engine.create_macro("test_line", 3, formation="line")
    engine.create_macro("test_grid", 4, formation="grid")
    
    # Explorar estructuras
    print("\n2️⃣ Explorando estructuras de datos:")
    
    # Verificar atributos disponibles
    attrs = [attr for attr in dir(engine) if 'macro' in attr.lower()]
    print(f"\n   Atributos con 'macro': {attrs}")
    
    # Verificar _macros
    if hasattr(engine, '_macros'):
        print(f"\n   engine._macros type: {type(engine._macros)}")
        print(f"   Contenido: {engine._macros}")
        print(f"   Número de macros: {len(engine._macros)}")
        
        # Ver estructura de cada macro
        for name, macro in engine._macros.items():
            print(f"\n   📦 Macro '{name}':")
            print(f"      - Tipo: {type(macro)}")
            print(f"      - Sources: {len(macro.source_ids) if hasattr(macro, 'source_ids') else '?'}")
            if hasattr(macro, 'source_ids'):
                print(f"      - IDs: {macro.source_ids}")
    
    # Verificar _active_sources
    print(f"\n3️⃣ Sources activas totales: {len(engine._active_sources)}")
    
    # Verificar _sources
    if hasattr(engine, '_sources'):
        print(f"\n4️⃣ engine._sources:")
        for sid, source in list(engine._sources.items())[:5]:  # Solo primeras 5
            print(f"   Source {sid}: {source.name if hasattr(source, 'name') else '?'}")

if __name__ == "__main__":
    diagnose_macros()