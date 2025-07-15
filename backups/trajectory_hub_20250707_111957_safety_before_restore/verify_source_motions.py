#!/usr/bin/env python3
"""
🔍 VERIFICAR - _source_motions es el contenedor
⚡ Confirmar que las fuentes están ahí y tienen la arquitectura correcta
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🔍 VERIFICACIÓN DE _source_motions\n")
print("="*60)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Verificar si existe _source_motions
    if hasattr(engine, '_source_motions'):
        print("✅ engine._source_motions existe")
    else:
        print("❌ engine._source_motions NO existe")
        
        # Buscar alternativas
        print("\n🔍 Buscando alternativas...")
        for attr in dir(engine):
            if 'source' in attr.lower() or 'motion' in attr.lower():
                value = getattr(engine, attr)
                if isinstance(value, dict):
                    print(f"   • {attr}: dict con {len(value)} elementos")
    
    # Crear macro
    print("\n1️⃣ CREANDO MACRO DE PRUEBA")
    macro_id = engine.create_macro("test", source_count=3, formation="line", spacing=2.0)
    print(f"   Macro: {macro_id}")
    
    # Verificar _source_motions después de crear macro
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        print(f"   _source_motions tiene {len(motions)} elementos")
        
        if motions:
            # Obtener la primera fuente
            first_id = list(motions.keys())[0]
            first_motion = motions[first_id]
            
            print(f"\n2️⃣ ANALIZANDO PRIMERA FUENTE: {first_id}")
            print(f"   Tipo: {type(first_motion).__name__}")
            
            # Verificar atributos de offset
            offset_attrs = [
                'concentration_offset',
                'macro_rotation_offset',
                'trajectory_offset',
                'algorithmic_rotation_offset'
            ]
            
            print("\n   Verificando offsets:")
            for attr in offset_attrs:
                if hasattr(first_motion, attr):
                    value = getattr(first_motion, attr)
                    print(f"   ✅ {attr}: {value}")
                else:
                    print(f"   ❌ {attr} NO existe")
            
            # Verificar get_position
            if hasattr(first_motion, 'get_position'):
                print("\n   ✅ get_position() existe")
                
                # Obtener posición inicial
                pos_initial = first_motion.get_position()
                print(f"   Posición inicial: {pos_initial}")
            
            # Test de concentración
            print("\n3️⃣ TEST DE CONCENTRACIÓN")
            
            # Aplicar concentración
            engine.set_macro_concentration(macro_id, 0.1)
            print("   Concentración aplicada (factor 0.1)")
            
            # Verificar si se creó el componente
            if hasattr(first_motion, 'components'):
                print(f"   Componentes: {list(first_motion.components.keys())}")
                
                if 'concentration' in first_motion.components:
                    conc = first_motion.components['concentration']
                    print(f"   ✅ Componente concentración existe")
                    print(f"      enabled: {getattr(conc, 'enabled', '?')}")
                    print(f"      factor: {getattr(conc, 'factor', '?')}")
            
            # Update manual del motion
            print("\n4️⃣ UPDATE MANUAL")
            first_motion.update(0.1)
            
            # Verificar offsets después del update
            print("\n   Offsets después del update:")
            if hasattr(first_motion, 'concentration_offset'):
                print(f"   concentration_offset: {first_motion.concentration_offset}")
            
            # Obtener posición final
            if hasattr(first_motion, 'get_position'):
                pos_final = first_motion.get_position()
                print(f"   Posición final: {pos_final}")
                
                # Verificar si cambió
                if not np.allclose(pos_initial, pos_final):
                    print("\n   ✅ ¡LA POSICIÓN CAMBIÓ!")
                else:
                    print("\n   ❌ La posición NO cambió")
            
            # Test del engine.update()
            print("\n5️⃣ TEST DE ENGINE.UPDATE()")
            
            # Resetear y probar con engine.update()
            engine.set_macro_concentration(macro_id, 0.2)
            
            # Capturar posición antes
            pos_before = first_motion.get_position()
            
            # Update del engine
            engine.update()
            
            # Posición después
            pos_after = first_motion.get_position()
            
            print(f"   Antes: {pos_before}")
            print(f"   Después: {pos_after}")
            
            if not np.allclose(pos_before, pos_after):
                print("\n   ✅ ENGINE.UPDATE() MUEVE LAS FUENTES")
            else:
                print("\n   ❌ ENGINE.UPDATE() NO MUEVE LAS FUENTES")
                
                # Diagnóstico adicional
                print("\n   🔍 Verificando el método update del engine...")
                
                # Ver si el engine llama a motion.update()
                import inspect
                if hasattr(engine, 'update'):
                    update_source = inspect.getsource(engine.update)
                    if 'motion.update' in update_source or '_source_motions' in update_source:
                        print("   ✅ engine.update() menciona _source_motions")
                    else:
                        print("   ❌ engine.update() NO menciona _source_motions")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("📊 CONCLUSIONES")
print("="*60)