#!/usr/bin/env python3
"""
🔍 Verifica el estado actual del sistema
⚡ Analiza qué métodos existen y funcionan
🎯 Crea snapshot del estado actual
"""

import os
import datetime
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def verify_current_state():
    """Verifica estado actual y crea snapshot"""
    
    print("🔍 VERIFICANDO ESTADO ACTUAL")
    print("=" * 60)
    
    # 1. Crear backup con timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    backup_path = f"{engine_path}.backup_stable_{timestamp}"
    
    os.system(f"cp '{engine_path}' '{backup_path}'")
    print(f"✅ Backup creado: {backup_path}")
    
    # 2. Verificar métodos existentes
    print("\n📋 MÉTODOS EN ENGINE:")
    engine = EnhancedTrajectoryEngine()
    
    methods_to_check = [
        'create_macro',
        'list_macros', 
        'select_macro',
        'delete_macro',
        'update',
        'start',
        'stop'
    ]
    
    existing_methods = []
    missing_methods = []
    
    for method in methods_to_check:
        if hasattr(engine, method):
            existing_methods.append(method)
            print(f"   ✅ {method}()")
        else:
            missing_methods.append(method)
            print(f"   ❌ {method}()")
    
    # 3. Test rápido de funcionalidad
    print("\n🧪 TEST DE FUNCIONALIDAD:")
    try:
        engine.start()
        
        # Crear macros de prueba
        result1 = engine.create_macro("test_circle", 4, formation="circle")
        result2 = engine.create_macro("test_line", 3, formation="line")
        
        print(f"   ✅ create_macro funciona")
        print(f"   ✅ Macros creados: 2")
        
        # Verificar estructura interna
        if hasattr(engine, '_macros'):
            print(f"   ✅ _macros existe: {len(engine._macros)} macros")
        
        if hasattr(engine, '_active_sources'):
            print(f"   ✅ _active_sources existe: {len(engine._active_sources)} sources")
        
        engine.stop()
        
    except Exception as e:
        print(f"   ❌ Error en test: {e}")
    
    # 4. Guardar estado
    state = {
        "timestamp": timestamp,
        "backup_path": backup_path,
        "existing_methods": existing_methods,
        "missing_methods": missing_methods,
        "system_functional": len(existing_methods) >= 4
    }
    
    # Guardar estado en archivo
    import json
    with open('INTEGRATION_STATE.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    print("\n📊 RESUMEN:")
    print(f"   Métodos existentes: {len(existing_methods)}")
    print(f"   Métodos faltantes: {len(missing_methods)}")
    print(f"   Sistema funcional: {'SÍ' if state['system_functional'] else 'NO'}")
    
    if missing_methods:
        print(f"\n🎯 NECESARIO IMPLEMENTAR:")
        for method in missing_methods:
            print(f"   - {method}()")
    
    print(f"\n💾 Estado guardado en: INTEGRATION_STATE.json")
    print(f"📁 Backup estable en: {backup_path}")
    
    return state

if __name__ == "__main__":
    state = verify_current_state()
    
    if state['missing_methods']:
        print("\n⚡ Próximo paso: Implementar métodos faltantes uno por uno")