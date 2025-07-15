#!/usr/bin/env python3
"""
🧪 Test Simplificado: Concentración y Rotación
⚡ Ir directo al problema sin complicaciones
"""

import sys
import os

# Auto-detectar ruta
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

def simple_test():
    """Test minimalista del sistema"""
    print("🧪 TEST SIMPLIFICADO\n")
    
    # Importar engine
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine sin OSC
    os.environ['DISABLE_OSC'] = '1'
    engine = EnhancedTrajectoryEngine()
    
    # 1. Crear macro
    print("1️⃣ Creando macro...")
    macro_id = engine.create_macro("test", source_count=3, formation="line", spacing=2.0)
    print(f"   ✓ Macro: {macro_id}")
    
    # 2. Test concentración
    print("\n2️⃣ Test Concentración")
    print("   Estado inicial:")
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   → {state}")
    
    print("\n   Aplicando concentración 0.1...")
    engine.set_macro_concentration(macro_id, 0.1)
    
    # Actualizar
    for _ in range(10):
        engine.update()
    
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   → Estado actual: {state}")
    
    # 3. Test rotación MS
    print("\n3️⃣ Test Rotación MS")
    print("   Aplicando rotación circular...")
    engine.apply_algorithmic_rotation_ms(macro_id, 'circular', speed=5.0, amplitude=1.0)
    
    # Verificar
    if hasattr(engine, 'macro_rotations_algo'):
        active = list(engine.macro_rotations_algo.keys())
        print(f"   → Rotaciones activas: {active}")
    
    # 4. Test combinado con IS
    print("\n4️⃣ Test con IS")
    
    # Obtener nombres de fuentes
    source_names = engine.get_source_names()
    print(f"   Fuentes disponibles: {len(source_names)}")
    
    if source_names:
        # Aplicar IS a la primera fuente
        first = source_names[0]
        print(f"   Aplicando círculo a: {first}")
        engine.set_individual_trajectory(first, 'circle')
        
        # Actualizar
        for _ in range(5):
            engine.update()
        
        # Verificar estados
        print("\n5️⃣ VERIFICACIÓN FINAL:")
        
        # Concentración
        conc = engine.get_macro_concentration_state(macro_id)
        if conc and conc.get('factor', 1.0) < 1.0:
            print("   ✅ Concentración activa")
        else:
            print("   ❌ Concentración NO activa")
        
        # Rotación MS
        if hasattr(engine, 'macro_rotations_algo') and macro_id in engine.macro_rotations_algo:
            print("   ✅ Rotación MS activa")
        else:
            print("   ❌ Rotación MS NO activa")
        
        print("\n💡 DIAGNÓSTICO:")
        print("   El problema es que los componentes no se están sumando")
        print("   cuando IS está activo. Necesitamos verificar la ")
        print("   implementación de la arquitectura de deltas.")
    
    # 6. Buscar el código problemático
    print("\n6️⃣ BUSCANDO LA CAUSA:")
    
    # Verificar si existe apply_concentration
    if hasattr(engine, 'apply_concentration'):
        print("   ✅ apply_concentration existe")
    else:
        print("   ❌ apply_concentration NO existe")
    
    # Verificar métodos de aplicación
    methods = ['apply_algorithmic_rotation_ms', 'apply_concentration', 'apply_individual_trajectory']
    for method in methods:
        if hasattr(engine, method):
            print(f"   ✅ {method} disponible")
        else:
            print(f"   ⚠️  {method} no encontrado")

if __name__ == "__main__":
    try:
        simple_test()
        print("\n" + "="*60)
        print("🔧 SOLUCIÓN NECESARIA:")
        print("="*60)
        print("\n📝 El sistema necesita que todos los componentes")
        print("   (concentración, rotación MS, IS) se sumen en lugar")
        print("   de sobrescribirse. Ejecuta:")
        print("\n   python fix_component_combination.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()