#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO PROFUNDO - Rastrear el flujo real
⚡ Encontrar por qué los cambios no funcionan
"""

import sys
import os

# Auto-detectar ruta
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

def trace_execution_flow():
    """Rastrear exactamente qué está pasando"""
    print("🔍 DIAGNÓSTICO PROFUNDO - RASTREO DE EJECUCIÓN\n")
    
    # 1. Verificar que los cambios están en el archivo
    print("1️⃣ VERIFICANDO CAMBIOS EN motion_components.py")
    print("-" * 60)
    
    motion_file = "trajectory_hub/core/motion_components.py"
    if os.path.exists(motion_file):
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Buscar indicadores de la nueva arquitectura
        indicators = {
            'concentration_offset': 'concentration_offset' in content,
            'macro_rotation_offset': 'macro_rotation_offset' in content,
            'trajectory_offset': 'trajectory_offset' in content,
            'get_position suma offsets': 'self.base_position +' in content,
            '_combine_components': '_combine_components' in content
        }
        
        print("Verificando indicadores de arquitectura de deltas:")
        for indicator, found in indicators.items():
            print(f"   {'✅' if found else '❌'} {indicator}")
        
        # Buscar el método get_position
        import re
        get_pos_match = re.search(r'def get_position\(self.*?\n(?:.*?\n)*?return.*?\n', content, re.DOTALL)
        if get_pos_match:
            print("\n📄 Método get_position encontrado:")
            print("-" * 40)
            print(get_pos_match.group(0)[:300] + "...")
    
    # 2. Test en vivo con el engine
    print("\n\n2️⃣ TEST EN VIVO - CREANDO INSTANCIAS")
    print("-" * 60)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        os.environ['DISABLE_OSC'] = '1'
        engine = EnhancedTrajectoryEngine()
        print("✅ Engine creado")
        
        # Crear macro
        macro_id = engine.create_macro("test", source_count=3, formation="line", spacing=2.0)
        print(f"✅ Macro creado: {macro_id}")
        
        # Obtener una fuente para inspeccionar
        source_names = engine.get_source_names()
        if source_names:
            first_source = source_names[0]
            print(f"✅ Primera fuente: {first_source}")
            
            # Intentar acceder directamente a la fuente
            # Buscar en diferentes lugares posibles
            source = None
            
            # Opción 1: engine.sources
            if hasattr(engine, 'sources'):
                source = engine.sources.get(first_source)
            
            # Opción 2: engine._sources
            if not source and hasattr(engine, '_sources'):
                source = engine._sources.get(first_source)
            
            # Opción 3: buscar en otros atributos
            if not source:
                for attr_name in dir(engine):
                    attr = getattr(engine, attr_name)
                    if isinstance(attr, dict) and first_source in attr:
                        source = attr[first_source]
                        print(f"   📍 Fuente encontrada en: engine.{attr_name}")
                        break
            
            if source:
                print("\n3️⃣ INSPECCIONANDO FUENTE")
                print("-" * 60)
                
                # Ver qué tiene la fuente
                print("Atributos de la fuente:")
                for attr in ['motion', 'position', 'base_position', 'get_position']:
                    if hasattr(source, attr):
                        print(f"   ✅ {attr}")
                    else:
                        print(f"   ❌ {attr}")
                
                # Si tiene motion, inspeccionar
                if hasattr(source, 'motion'):
                    motion = source.motion
                    print("\nAtributos de motion:")
                    
                    offset_attrs = ['concentration_offset', 'macro_rotation_offset', 
                                   'trajectory_offset', 'algorithmic_rotation_offset']
                    
                    for attr in offset_attrs:
                        if hasattr(motion, attr):
                            value = getattr(motion, attr)
                            print(f"   ✅ {attr}: {value}")
                        else:
                            print(f"   ❌ {attr} NO EXISTE")
                    
                    # Verificar si tiene el método update correcto
                    if hasattr(motion, 'update'):
                        import inspect
                        update_source = inspect.getsource(motion.update)
                        if 'concentration_offset' in update_source:
                            print("\n   ✅ update() tiene código de deltas")
                        else:
                            print("\n   ❌ update() NO tiene código de deltas")
                    
                    # TEST CRÍTICO: Ver si get_position suma offsets
                    if hasattr(motion, 'get_position'):
                        get_pos_source = inspect.getsource(motion.get_position)
                        if '+' in get_pos_source and 'offset' in get_pos_source:
                            print("   ✅ get_position() suma offsets")
                        else:
                            print("   ❌ get_position() NO suma offsets")
                            print("\n   📄 Código actual de get_position:")
                            print("-" * 40)
                            print(get_pos_source)
                
                # Test de concentración
                print("\n4️⃣ TEST DE CONCENTRACIÓN")
                print("-" * 60)
                
                # Posición inicial
                if hasattr(source, 'get_position'):
                    initial_pos = source.get_position()
                    print(f"Posición inicial: {initial_pos}")
                
                # Aplicar concentración
                engine.set_macro_concentration(macro_id, 0.1)
                print("✅ Concentración aplicada (factor 0.1)")
                
                # Update
                engine.update()
                
                # Posición después
                if hasattr(source, 'get_position'):
                    final_pos = source.get_position()
                    print(f"Posición después: {final_pos}")
                    
                    import numpy as np
                    if np.allclose(initial_pos, final_pos):
                        print("\n❌ LA POSICIÓN NO CAMBIÓ")
                        
                        # Diagnóstico adicional
                        if hasattr(source, 'motion'):
                            motion = source.motion
                            if hasattr(motion, 'concentration_offset'):
                                print(f"   concentration_offset: {motion.concentration_offset}")
                            if hasattr(motion, 'components'):
                                print(f"   components: {list(motion.components.keys())}")
                                if 'concentration' in motion.components:
                                    conc = motion.components['concentration']
                                    print(f"   concentration.enabled: {getattr(conc, 'enabled', '?')}")
                                    print(f"   concentration.factor: {getattr(conc, 'factor', '?')}")
                    else:
                        print("\n✅ LA POSICIÓN CAMBIÓ")
                
            else:
                print("\n❌ No se pudo acceder a la fuente directamente")
    
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Diagnóstico final
    print("\n\n5️⃣ DIAGNÓSTICO FINAL")
    print("=" * 60)
    
    print("\n🔍 POSIBLES CAUSAS:")
    print("1. Los cambios están en motion_components.py pero no se están usando")
    print("2. El engine está usando otra clase/implementación")
    print("3. Los offsets se calculan pero no se suman en get_position()")
    print("4. La concentración no está creando el componente correctamente")
    
    print("\n💡 NECESITAMOS:")
    print("1. Verificar qué clase realmente se usa para las fuentes")
    print("2. Asegurar que get_position() realmente suma los offsets")
    print("3. Agregar logs para rastrear el flujo")

if __name__ == "__main__":
    trace_execution_flow()