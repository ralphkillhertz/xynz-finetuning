#!/usr/bin/env python3
"""
🔍 Verifica implementación actual de gestión de macros
⚡ Diagnostica qué está implementado y qué falta
"""

import os
import sys
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def check_implementation():
    """Verifica qué métodos están implementados"""
    
    print("🔍 VERIFICANDO IMPLEMENTACIÓN ACTUAL")
    print("=" * 60)
    
    # Verificar Engine
    print("\n1️⃣ MÉTODOS EN ENGINE:")
    engine = EnhancedTrajectoryEngine()
    
    methods_to_check = ['list_macros', 'select_macro', 'delete_macro']
    for method in methods_to_check:
        if hasattr(engine, method):
            print(f"   ✅ {method}() - Implementado")
        else:
            print(f"   ❌ {method}() - NO encontrado")
    
    # Verificar Controller
    print("\n2️⃣ VERIFICANDO CONTROLLER:")
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    with open(controller_path, 'r') as f:
        content = f.read()
    
    # Buscar si tiene menú de macros
    has_macro_menu = 'show_macro_management' in content or 'Manage Macros' in content
    has_option_6 = '"6"' in content and 'main_menu' in content
    
    print(f"   {'✅' if has_macro_menu else '❌'} Menú de gestión de macros")
    print(f"   {'✅' if has_option_6 else '❌'} Opción 6 en menú principal")
    
    # Test rápido de funcionalidad
    print("\n3️⃣ TEST RÁPIDO:")
    try:
        engine.start()
        # Crear un macro de prueba
        result = engine.create_macro("test_check", 3, formation="circle")
        print(f"   ✅ create_macro() funciona")
        
        # Listar
        macros = engine.list_macros()
        print(f"   ✅ list_macros() retorna {len(macros)} macros")
        
        # Seleccionar
        if macros:
            selected = engine.select_macro(macros[0]['key'])
            print(f"   ✅ select_macro() funciona")
        
        engine.stop()
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📋 SIGUIENTE PASO:")
    if not has_macro_menu:
        print("   → Añadir menú de gestión al Controller")
    else:
        print("   → Sistema de gestión completo")
    
    print("\n✅ VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    check_implementation()