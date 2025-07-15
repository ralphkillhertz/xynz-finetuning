# === diagnose_source_system_deep.py ===
# 🔍 Diagnóstico de la sincronización de fuentes
# ⚡ Identifica por qué _source_motions está vacío

from trajectory_hub.core import EnhancedTrajectoryEngine
import inspect

def diagnose_source_synchronization():
    """Diagnóstico profundo del sistema de fuentes"""
    
    print("🔍 DIAGNÓSTICO PROFUNDO - SINCRONIZACIÓN DE FUENTES")
    print("=" * 70)
    
    # 1. Crear engine y examinar create_source
    print("\n1️⃣ ANALIZANDO create_source...")
    
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Ver qué hace create_source
    if hasattr(engine, 'create_source'):
        try:
            source = inspect.getsource(engine.create_source)
            print("   📄 Código de create_source:")
            
            # Buscar dónde se registra la fuente
            for i, line in enumerate(source.split('\n')):
                if 'motion_states' in line or '_source_motions' in line or 'SourceMotion' in line:
                    print(f"      L{i}: {line.strip()}")
        except:
            print("   ⚠️ No se puede obtener el código")
    
    # 2. Crear una fuente manualmente y ver qué pasa
    print("\n2️⃣ CREANDO FUENTE MANUALMENTE...")
    
    print("\n   Estado ANTES de create_source:")
    print(f"   motion_states: {len(engine.motion_states)} elementos")
    print(f"   _source_motions: {len(engine._source_motions) if hasattr(engine, '_source_motions') else 'NO EXISTE'}")
    print(f"   _active_sources: {len(engine._active_sources) if hasattr(engine, '_active_sources') else 'NO EXISTE'}")
    
    # Crear fuente
    engine.create_source(99)
    
    print("\n   Estado DESPUÉS de create_source:")
    print(f"   motion_states: {len(engine.motion_states)} elementos")
    print(f"   _source_motions: {len(engine._source_motions) if hasattr(engine, '_source_motions') else 'NO EXISTE'}")
    print(f"   _active_sources: {engine._active_sources if hasattr(engine, '_active_sources') else 'NO EXISTE'}")
    
    # Ver qué contiene motion_states[99]
    if 99 in engine.motion_states:
        motion = engine.motion_states[99]
        print(f"\n   📦 motion_states[99]:")
        print(f"      Tipo: {type(motion)}")
        print(f"      Atributos: {[attr for attr in dir(motion) if not attr.startswith('_')][:10]}")
    
    # 3. Analizar el problema del macro_id
    print("\n3️⃣ ANALIZANDO PROBLEMA DE NOMBRES DE MACRO...")
    
    # Crear un macro
    result = engine.create_macro('mi_macro', 2)
    print(f"\n   create_macro retorna: '{result}'")
    print(f"   Claves en _macros: {list(engine._macros.keys())}")
    
    # El problema es claro: retorna 'macro_X_nombre' pero deberíamos acceder con 'nombre'
    
    # 4. Ver la estructura del objeto macro
    if engine._macros:
        macro_key = list(engine._macros.keys())[0]
        macro = engine._macros[macro_key]
        print(f"\n   📦 Estructura del macro '{macro_key}':")
        print(f"      Tipo: {type(macro).__name__}")
        print(f"      name: {getattr(macro, 'name', 'NO TIENE')}")
        print(f"      source_ids: {getattr(macro, 'source_ids', 'NO TIENE')}")
        
        # Ver todos los atributos
        attrs = [attr for attr in dir(macro) if not attr.startswith('_')]
        print(f"      Atributos disponibles: {attrs[:10]}")
    
    # 5. Propuesta de correcciones
    print("\n5️⃣ CORRECCIONES NECESARIAS:")
    print("""
   🔧 FIX 1: create_macro debe retornar el objeto, no el string
      ACTUAL:    return macro_id
      CORRECTO:  return self._macros[macro_id]
   
   🔧 FIX 2: Sincronizar _source_motions con motion_states
      - Verificar si _source_motions es necesario
      - O eliminar referencias a _source_motions
      - O sincronizar ambos diccionarios
   
   🔧 FIX 3: Añadir método get_macro para acceso fácil
      def get_macro(self, name):
          # Buscar por nombre directo o por macro_X_nombre
          for key, macro in self._macros.items():
              if key == name or macro.name == name:
                  return macro
          return None
   """)
    
    # 6. Verificar el modulador
    print("\n6️⃣ VERIFICANDO SISTEMA DE MODULADORES...")
    
    if hasattr(engine, 'create_orientation_modulator'):
        print("   ✅ create_orientation_modulator existe")
        
        # Ver por qué no encuentra las fuentes
        try:
            source = inspect.getsource(engine.create_orientation_modulator)
            for line in source.split('\n'):
                if '_source_motions' in line or 'motion_states' in line:
                    print(f"      {line.strip()}")
        except:
            pass

if __name__ == "__main__":
    diagnose_source_synchronization()