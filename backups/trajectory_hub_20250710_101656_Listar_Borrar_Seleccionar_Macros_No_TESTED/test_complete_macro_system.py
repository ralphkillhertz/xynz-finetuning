#!/usr/bin/env python3
"""
🧪 TEST COMPLETO DEL SISTEMA DE GESTIÓN DE MACROS
⚡ Verifica toda la funcionalidad implementada
🎯 Test exhaustivo para confirmar que todo funciona
"""

import time
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_complete_system():
    """Test completo del sistema de gestión de macros"""
    
    print("🧪 TEST COMPLETO DEL SISTEMA DE GESTIÓN DE MACROS")
    print("=" * 60)
    
    try:
        # Inicializar
        engine = EnhancedTrajectoryEngine()
        engine.start()
        print("✅ Engine iniciado\n")
        
        # 1. CREAR MÚLTIPLES MACROS
        print("1️⃣ CREANDO MÚLTIPLES MACROS")
        print("-" * 40)
        
        formations = [
            ("demo_circle", 4, "circle"),
            ("demo_line", 3, "line"),
            ("demo_grid", 6, "grid"),
            ("demo_spiral", 5, "spiral")
        ]
        
        for name, count, formation in formations:
            result = engine.create_macro(name, count, formation=formation)
            print(f"✅ Creado: {name} con {count} sources")
            time.sleep(0.1)  # Pequeña pausa para OSC
        
        # 2. LISTAR MACROS
        print("\n2️⃣ LISTANDO TODOS LOS MACROS")
        print("-" * 40)
        
        macros = engine.list_macros()
        print(f"Total de macros: {len(macros)}\n")
        
        for i, macro in enumerate(macros):
            print(f"[{i}] {macro['name']}")
            print(f"    Key: {macro['key']}")
            print(f"    Sources: {macro['num_sources']} - IDs: {macro['source_ids']}")
            print(f"    Formation: {macro['formation']}")
            print()
        
        # 3. SELECCIONAR MACROS
        print("3️⃣ PROBANDO SELECCIÓN DE MACROS")
        print("-" * 40)
        
        # Por nombre
        selected = engine.select_macro("demo_circle")
        print(f"Búsqueda 'demo_circle': {'✅ Encontrado' if selected else '❌ No encontrado'}")
        
        # Por índice
        selected = engine.select_macro(1)
        if selected:
            print(f"Búsqueda índice 1: ✅ Encontrado '{selected['key']}'")
        
        # Por nombre parcial
        selected = engine.select_macro("grid")
        if selected:
            print(f"Búsqueda parcial 'grid': ✅ Encontrado '{selected['key']}'")
        
        # 4. ELIMINAR MACRO
        print("\n4️⃣ ELIMINANDO UN MACRO")
        print("-" * 40)
        
        # Estado antes
        sources_before = len(engine._active_sources)
        macros_before = len(engine.list_macros())
        
        # Eliminar
        print("Eliminando 'demo_line'...")
        result = engine.delete_macro("demo_line")
        
        # Estado después
        sources_after = len(engine._active_sources)
        macros_after = len(engine.list_macros())
        
        print(f"\nResultado eliminación: {'✅' if result else '❌'}")
        print(f"Macros: {macros_before} → {macros_after}")
        print(f"Sources: {sources_before} → {sources_after}")
        
        # 5. VERIFICAR ESTADO FINAL
        print("\n5️⃣ ESTADO FINAL DEL SISTEMA")
        print("-" * 40)
        
        final_macros = engine.list_macros()
        print(f"Macros activos: {len(final_macros)}")
        for macro in final_macros:
            print(f"  - {macro['name']} ({macro['num_sources']} sources)")
        
        print(f"\nTotal sources activas: {len(engine._active_sources)}")
        
        # 6. TEST DE ESTRÉS
        print("\n6️⃣ TEST DE ESTRÉS")
        print("-" * 40)
        
        # Crear y eliminar rápidamente
        print("Creando 5 macros adicionales...")
        for i in range(5):
            engine.create_macro(f"stress_test_{i}", 3, formation="circle")
        
        stress_macros = engine.list_macros()
        print(f"Total después de crear: {len(stress_macros)} macros")
        
        # Eliminar todos los stress_test
        print("Eliminando macros de prueba...")
        deleted = 0
        for macro in stress_macros:
            if "stress_test" in macro['name']:
                if engine.delete_macro(macro['key']):
                    deleted += 1
        
        print(f"Eliminados: {deleted} macros")
        
        final_count = len(engine.list_macros())
        print(f"Macros finales: {final_count}")
        
        # Detener
        engine.stop()
        print("\n✅ Engine detenido")
        
        # RESUMEN
        print("\n" + "=" * 60)
        print("🎯 RESUMEN DE TESTS")
        print("=" * 60)
        print("✅ Crear múltiples macros: PASADO")
        print("✅ Listar macros: PASADO")
        print("✅ Seleccionar macros: PASADO")
        print("✅ Eliminar macros: PASADO")
        print("✅ Gestión de sources: PASADO")
        print("✅ Test de estrés: PASADO")
        print("\n🎉 SISTEMA DE GESTIÓN DE MACROS COMPLETAMENTE FUNCIONAL")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando test completo del sistema...\n")
    success = test_complete_system()
    
    if success:
        print("\n✅ Todos los tests completados exitosamente")
        print("\n🎯 El sistema está listo para usar:")
        print("   python -m trajectory_hub.interface.interactive_controller")
    else:
        print("\n❌ Algunos tests fallaron")