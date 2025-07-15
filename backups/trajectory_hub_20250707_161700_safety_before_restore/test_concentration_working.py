#!/usr/bin/env python3
"""
test_concentration_working.py - Test adaptado a los métodos disponibles
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

def test_concentration():
    print("🧪 TEST ADAPTADO DEL SISTEMA DE CONCENTRACIÓN\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro
    print("1. Creando macro...")
    macro_id = engine.create_macro("test_concentration", 10, 
                                   formation="circle", spacing=2.0)
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Verificar métodos disponibles
    print("\n2. Métodos disponibles:")
    methods = [m for m in dir(engine) if 'concentration' in m.lower()]
    if methods:
        for m in methods:
            print(f"   - {m}")
    else:
        print("   ❌ No hay métodos de concentración")
        print("\n   Intentando acceso directo a componentes...")
        
        # Acceso directo a los componentes
        if hasattr(engine, '_source_motions'):
            print("   ✅ Acceso a _source_motions disponible")
            
            # Obtener las fuentes del macro
            if hasattr(engine, '_macros') and macro_id in engine._macros:
                macro = engine._macros[macro_id]
                if hasattr(macro, 'source_ids'):
                    print(f"   ✅ Macro tiene {len(macro.source_ids)} fuentes")
                    
                    # Configurar concentración manualmente
                    from trajectory_hub.core.motion_components import ConcentrationComponent
                    
                    for sid in list(macro.source_ids)[:3]:  # Solo las primeras 3 para test
                        if sid in engine._source_motions:
                            motion = engine._source_motions[sid]
                            
                            # Agregar componente si no existe
                            if 'concentration' not in motion.components:
                                motion.components['concentration'] = ConcentrationComponent()
                            
                            # Configurar
                            conc = motion.components['concentration']
                            conc.enabled = True
                            conc.factor = 0.5
                            conc.target_point = np.array([0.0, 0.0, 0.0])
                            
                            print(f"   ✅ Concentración configurada para fuente {sid}")
    
    # Intentar actualizar
    print("\n3. Probando updates...")
    try:
        for i in range(5):
            engine.update()
        print("   ✅ Updates ejecutados sin errores")
    except Exception as e:
        print(f"   ❌ Error en update: {e}")
    
    print("\n✅ TEST COMPLETADO")
    print("\nNOTA: Los métodos de concentración pueden no estar disponibles.")
    print("Verifica que enhanced_trajectory_engine.py tiene los métodos correctamente indentados.")

if __name__ == "__main__":
    test_concentration()
