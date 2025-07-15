# === diagnose_complete_system.py ===
# 🔍 Diagnóstico completo del sistema
# ⚡ Identifica TODOS los problemas estructurales

from trajectory_hub.core import EnhancedTrajectoryEngine
import inspect

def diagnose_complete():
    """Diagnóstico completo y propuesta de solución"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 70)
    
    # 1. Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
    
    # 2. Test completo de creación
    print("\n1️⃣ TEST DE CREACIÓN DE MACRO Y FUENTES...")
    
    # Crear macro
    print("   📦 Creando macro...")
    result = engine.create_macro('test_macro', 3)
    print(f"   Retorna: '{result}' (tipo: {type(result).__name__})")
    
    # Ver estado interno
    print(f"\n   📊 Estado interno:")
    print(f"   _macros keys: {list(engine._macros.keys())}")
    print(f"   motion_states: {list(engine.motion_states.keys())}")
    print(f"   _source_motions: {list(engine._source_motions.keys()) if hasattr(engine, '_source_motions') else 'NO EXISTE'}")
    print(f"   _active_sources: {engine._active_sources}")
    
    # 3. Obtener el macro real
    print("\n2️⃣ ACCEDIENDO AL MACRO...")
    
    # El macro está en _macros con la clave que retornó create_macro
    macro_key = result  # 'macro_0_test_macro'
    if macro_key in engine._macros:
        macro = engine._macros[macro_key]
        print(f"   ✅ Macro encontrado con clave: '{macro_key}'")
        print(f"   name: {macro.name}")
        print(f"   source_ids: {macro.source_ids}")
    else:
        print(f"   ❌ Macro NO encontrado con clave: '{macro_key}'")
    
    # 4. Verificar el problema del modulador
    print("\n3️⃣ DIAGNÓSTICO DEL MODULADOR...")
    
    # Ver qué busca create_orientation_modulator
    if hasattr(engine, 'create_orientation_modulator'):
        try:
            # Crear un modulador para la fuente 0
            print("   🔧 Intentando crear modulador para fuente 0...")
            
            # Ver qué busca el método
            source_code = inspect.getsource(engine.create_orientation_modulator)
            
            # Buscar la condición que falla
            print("\n   📄 Condiciones en create_orientation_modulator:")
            for line in source_code.split('\n'):
                if 'if' in line and ('motion_states' in line or '_source_motions' in line):
                    print(f"      {line.strip()}")
            
            # Intentar crear
            mod = engine.create_orientation_modulator(0)
            if mod:
                print("   ✅ Modulador creado")
            else:
                print("   ❌ Modulador NO creado")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 5. Solución propuesta
    print("\n4️⃣ ANÁLISIS Y SOLUCIÓN:")
    
    print("""
   📊 PROBLEMAS IDENTIFICADOS:
   
   1. create_macro retorna 'macro_X_nombre' pero el test espera el objeto
   2. El modulador busca en _source_motions que está vacío
   3. Los nombres de macro son inconsistentes (se guarda como 'macro_X_nombre')
   
   🔧 SOLUCIONES MÍNIMAS:
   
   FIX 1: Modificar create_macro para retornar el objeto
   FIX 2: Hacer que el modulador busque en motion_states
   FIX 3: Ajustar el test para manejar la API actual
   
   🎯 RECOMENDACIÓN:
   Podemos hacer FIX 3 (ajustar el test) como solución rápida
   o FIX 1+2 para corregir el diseño de raíz.
   """)
    
    # 6. Verificar si podemos trabajar con la API actual
    print("\n5️⃣ PRUEBA CON API ACTUAL...")
    
    # Usar la API como está diseñada actualmente
    macro_id = engine.create_macro('demo', 2)
    macro = engine._macros[macro_id]  # Acceder directamente
    
    print(f"   ✅ Con la API actual:")
    print(f"      macro_id = engine.create_macro('demo', 2)")
    print(f"      macro = engine._macros[macro_id]")
    print(f"      source_ids = macro.source_ids = {macro.source_ids}")
    
    return engine, macro_id, macro

if __name__ == "__main__":
    engine, macro_id, macro = diagnose_complete()
    
    print("\n" + "=" * 70)
    print("💡 DECISIÓN:")
    print("=" * 70)
    print("\n¿Qué prefieres?")
    print("A) Ajustar el test para trabajar con la API actual (más rápido)")
    print("B) Corregir create_macro y el modulador (más limpio)")
    print("\nRecomiendo opción B para tener un sistema más coherente.")