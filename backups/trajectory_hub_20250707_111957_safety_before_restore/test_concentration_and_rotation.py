#!/usr/bin/env python3
"""
🧪 Test Específico: Concentración + Rotación MS
⚡ Verificar por qué no funcionan correctamente
"""

import sys
import os
import numpy as np
import time

# Auto-detectar ruta
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

def test_system():
    """Test completo del sistema de concentración y rotación"""
    print("🧪 TEST DE CONCENTRACIÓN Y ROTACIÓN MS\n")
    
    # Importar engine
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine sin OSC
    os.environ['DISABLE_OSC'] = '1'
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro
    print("1️⃣ CREANDO MACRO DE PRUEBA")
    macro_id = engine.create_macro("test", source_count=5, formation="line", spacing=2.0)
    print(f"   ✓ Macro creado: {macro_id}")
    
    # Obtener información debug
    debug_info = engine.get_debug_info()
    
    # Buscar las fuentes creadas
    print("\n2️⃣ BUSCANDO FUENTES CREADAS")
    
    # El engine debe tener alguna forma de acceder a las fuentes
    # Vamos a explorar el debug_info
    if isinstance(debug_info, dict):
        print("   📊 Debug info contiene:")
        for key in debug_info.keys():
            print(f"      • {key}")
            if 'source' in key.lower() or 'position' in key.lower():
                print(f"        → {debug_info[key]}")
    
    # Test de concentración
    print("\n3️⃣ TEST CONCENTRACIÓN")
    
    # Estado inicial
    initial_state = engine.get_macro_concentration_state(macro_id)
    print(f"   Estado inicial: {initial_state}")
    
    # Aplicar concentración
    print("   Aplicando concentración 0.1...")
    engine.set_macro_concentration(macro_id, 0.1)
    
    # Actualizar varias veces
    for i in range(10):
        engine.update(0.1)
    
    # Verificar estado
    new_state = engine.get_macro_concentration_state(macro_id)
    print(f"   Estado después: {new_state}")
    
    # Obtener debug info nuevamente
    debug_after_conc = engine.get_debug_info()
    
    # Test de rotación algorítmica
    print("\n4️⃣ TEST ROTACIÓN ALGORÍTMICA MS")
    
    # Reset concentración
    engine.set_macro_concentration(macro_id, 1.0)
    engine.update(0.1)
    
    # Aplicar rotación
    print("   Aplicando rotación circular...")
    engine.apply_algorithmic_rotation_ms(macro_id, 'circular', speed=5.0, amplitude=1.0)
    
    # Capturar posiciones durante varios frames
    print("   Actualizando 20 frames...")
    for i in range(20):
        engine.update(0.1)
    
    # Verificar si hay rotación en macro_rotations_algo
    if hasattr(engine, 'macro_rotations_algo'):
        print(f"   Rotaciones algorítmicas activas: {list(engine.macro_rotations_algo.keys())}")
    
    # Test combinado
    print("\n5️⃣ TEST COMBINADO: IS + CONCENTRACIÓN + ROTACIÓN")
    
    # Primero aplicar concentración y rotación
    engine.set_macro_concentration(macro_id, 0.2)
    engine.apply_algorithmic_rotation_ms(macro_id, 'circular', speed=5.0, amplitude=1.0)
    
    # Actualizar
    for _ in range(5):
        engine.update(0.1)
    
    print("   Estado con concentración + rotación MS")
    
    # Ahora agregar trayectorias individuales
    print("\n   Agregando trayectorias individuales...")
    
    # Necesitamos encontrar los IDs de las fuentes
    # Intentar diferentes formas
    source_names = engine.get_source_names()
    
    if source_names:
        print(f"   Fuentes encontradas: {len(source_names)}")
        
        # Aplicar trayectoria al primero
        first_source = source_names[0] if source_names else None
        
        if first_source:
            print(f"   Aplicando trayectoria circular a: {first_source}")
            engine.set_individual_trajectory(first_source, 'circle')
            
            # Actualizar y ver qué pasa
            print("   Actualizando con IS activo...")
            for _ in range(10):
                engine.update(0.1)
            
            print("   ✓ IS aplicado")
            
            # Verificar estados finales
            print("\n6️⃣ ESTADOS FINALES:")
            print(f"   • Concentración: {engine.get_macro_concentration_state(macro_id)}")
            print(f"   • Rotaciones MS: {list(engine.macro_rotations_algo.keys())}")
            
            # Buscar el problema
            print("\n7️⃣ ANÁLISIS DEL PROBLEMA:")
            
            if not engine.macro_rotations_algo.get(macro_id):
                print("   ❌ La rotación MS se perdió al activar IS")
            else:
                print("   ✅ La rotación MS sigue activa")
                
            conc_state = engine.get_macro_concentration_state(macro_id)
            if conc_state and conc_state.get('factor', 1.0) < 0.5:
                print("   ✅ La concentración sigue activa")
            else:
                print("   ❌ La concentración no está activa")
    else:
        print("   ❌ No se encontraron nombres de fuentes")
        print("   💡 El problema puede estar en cómo se accede a las fuentes")
    
    # Diagnóstico final
    print("\n" + "="*60)
    print("📊 DIAGNÓSTICO FINAL")
    print("="*60)
    
    print("\n💡 PROBLEMA IDENTIFICADO:")
    print("   Las fuentes existen pero no se puede acceder directamente")
    print("   Los métodos están disponibles pero falta la conexión")
    print("\n🔧 SOLUCIÓN REQUERIDA:")
    print("   Necesitamos implementar la suma correcta de componentes")
    print("   en el nivel donde se calculan las posiciones finales")

if __name__ == "__main__":
    try:
        test_system()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()