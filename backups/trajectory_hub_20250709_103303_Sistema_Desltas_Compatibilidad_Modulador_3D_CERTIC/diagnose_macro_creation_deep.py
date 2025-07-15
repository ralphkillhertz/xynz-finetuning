# === diagnose_macro_creation_deep.py ===
# 🔍 Diagnóstico profundo del sistema de creación de macros
# ⚡ Identifica problemas estructurales en el engine

import inspect
import ast
from trajectory_hub.core import EnhancedTrajectoryEngine

def diagnose_macro_system():
    """Diagnóstico completo del sistema de macros"""
    
    print("🔍 DIAGNÓSTICO PROFUNDO - SISTEMA DE MACROS")
    print("=" * 70)
    
    # 1. Analizar la firma de create_macro
    print("\n1️⃣ ANALIZANDO MÉTODO create_macro...")
    
    try:
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        
        # Inspeccionar el método
        create_macro_method = getattr(engine, 'create_macro', None)
        if create_macro_method:
            print(f"   ✅ Método existe")
            
            # Ver la firma
            sig = inspect.signature(create_macro_method)
            print(f"   📋 Firma: {sig}")
            
            # Ver el código fuente si es posible
            try:
                source = inspect.getsource(create_macro_method)
                print(f"   📄 Primeras líneas del código:")
                for i, line in enumerate(source.split('\n')[:10]):
                    print(f"      {line}")
                    
                # Buscar qué retorna
                if 'return' in source:
                    return_lines = [line.strip() for line in source.split('\n') if 'return' in line]
                    print(f"\n   🔄 Sentencias return encontradas:")
                    for ret in return_lines:
                        print(f"      {ret}")
            except:
                print("   ⚠️ No se puede obtener el código fuente")
        else:
            print("   ❌ Método create_macro NO EXISTE")
    
    except Exception as e:
        print(f"   ❌ Error al inspeccionar: {e}")
    
    # 2. Test de creación básica
    print("\n2️⃣ TEST DE CREACIÓN DE MACRO...")
    
    try:
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        
        # Intentar crear un macro
        print("   🔧 Llamando create_macro('test', 3)...")
        result = engine.create_macro('test', 3)
        
        print(f"   📦 Tipo retornado: {type(result)}")
        print(f"   📋 Valor: {result}")
        
        if isinstance(result, str):
            print("   ❌ ERROR: Retorna string en lugar de objeto")
            
            # Verificar si el macro se creó internamente
            if hasattr(engine, '_macros'):
                print(f"\n   🔍 Verificando _macros...")
                print(f"      Contenido: {engine._macros}")
                
                if 'test' in engine._macros:
                    macro_obj = engine._macros['test']
                    print(f"      ✅ Macro SÍ existe en _macros")
                    print(f"      Tipo: {type(macro_obj)}")
                    if hasattr(macro_obj, 'source_ids'):
                        print(f"      source_ids: {macro_obj.source_ids}")
                else:
                    print(f"      ❌ Macro NO existe en _macros")
        else:
            print(f"   ✅ Retorna objeto tipo: {type(result).__name__}")
            
    except Exception as e:
        print(f"   ❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Analizar el estado de las fuentes
    print("\n3️⃣ ANALIZANDO SISTEMA DE FUENTES...")
    
    try:
        # Verificar atributos relacionados con fuentes
        attrs_to_check = ['motion_states', '_source_motions', '_active_sources', 
                          '_positions', 'sources']
        
        for attr in attrs_to_check:
            if hasattr(engine, attr):
                value = getattr(engine, attr)
                print(f"   ✅ {attr}: {type(value)} - {len(value) if hasattr(value, '__len__') else 'N/A'} elementos")
            else:
                print(f"   ❌ {attr}: NO EXISTE")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Buscar el problema en el archivo
    print("\n4️⃣ ANALIZANDO ARCHIVO enhanced_trajectory_engine.py...")
    
    try:
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
            content = f.read()
            
        # Buscar el método create_macro
        import re
        create_macro_match = re.search(r'def create_macro\(.*?\):(.*?)(?=\n    def|\n\s*$)', 
                                      content, re.DOTALL)
        
        if create_macro_match:
            method_body = create_macro_match.group(1)
            
            # Contar returns
            returns = re.findall(r'return\s+(.+)', method_body)
            print(f"   📋 Sentencias return en create_macro: {len(returns)}")
            for i, ret in enumerate(returns):
                print(f"      {i+1}. return {ret.strip()}")
                
            # Verificar si retorna el nombre o el objeto
            if any('name' in ret and 'self._macros' not in ret for ret in returns):
                print("   ⚠️ PROBLEMA: Parece retornar el nombre en lugar del objeto")
    
    except Exception as e:
        print(f"   ❌ Error analizando archivo: {e}")
    
    # 5. Propuesta de solución
    print("\n5️⃣ ANÁLISIS DE CAUSA RAÍZ...")
    
    print("""
   📊 DIAGNÓSTICO:
   1. create_macro probablemente retorna el nombre (string) en lugar del objeto macro
   2. Esto rompe todo el flujo porque el test espera un objeto con 'source_ids'
   3. Las fuentes se crean pero posiblemente en una estructura diferente
   4. El modulador no encuentra las fuentes porque busca en el lugar equivocado
   
   🔧 SOLUCIÓN PROPUESTA:
   1. Modificar create_macro para que retorne el objeto macro
   2. Verificar que las fuentes se registren correctamente
   3. Sincronizar motion_states con el sistema de fuentes
   """)
    
    # 6. Verificar otros métodos que podrían tener el mismo problema
    print("\n6️⃣ VERIFICANDO OTROS MÉTODOS...")
    
    methods_to_check = ['get_macro', 'list_macros', 'delete_macro']
    for method_name in methods_to_check:
        if hasattr(engine, method_name):
            print(f"   ✅ {method_name} existe")
        else:
            print(f"   ⚠️ {method_name} NO existe")

if __name__ == "__main__":
    diagnose_macro_system()