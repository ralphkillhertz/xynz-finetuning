# === fix_individual_trajectory_api.py ===
# 🔧 Fix: Usar la API correcta para trayectorias individuales
# ⚡ El problema es que solo hay macro_trajectory, no individual_trajectory
# 🎯 Impacto: ALTO - Sin esto no hay movimiento individual

import os
import re

def check_set_individual_trajectory():
    """Verifica la implementación de set_individual_trajectory"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("🔍 Analizando set_individual_trajectory...")
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método
    pattern = r'def set_individual_trajectory\(self[^)]+\):(.*?)(?=\n    def|\n\s*$|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("✅ Método encontrado")
        method_body = match.group(1)
        
        # Ver si espera macro_id
        if "macro_id" in match.group(0) or "macro_name" in match.group(0):
            print("✅ El método espera macro_id/macro_name como primer parámetro")
            
            # Extraer la firma completa
            sig_match = re.search(r'def set_individual_trajectory\([^)]+\):', content)
            if sig_match:
                print(f"\n📝 Firma actual: {sig_match.group(0)}")
        
        # Verificar si añade a active_components
        if "active_components" in method_body:
            print("✅ Parece añadir a active_components")
        else:
            print("❌ NO parece añadir a active_components")
            
        # Verificar si crea IndividualTrajectory
        if "IndividualTrajectory" in method_body:
            print("✅ Crea IndividualTrajectory")
        else:
            print("❌ NO crea IndividualTrajectory")
    
    return True

def create_working_test():
    """Crea un test que use la API correcta"""
    
    test_code = '''# === test_trajectory_working.py ===
# 🧪 Test con la API correcta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test_trajectory_with_correct_api():
    """Test usando la API correcta para trayectorias individuales"""
    print("\\n🧪 TEST: Trayectorias con API correcta")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=3)
    print(f"✅ Macro creado: '{macro_name}'")
    
    # Obtener los source_ids del macro
    if hasattr(engine, '_macros') and macro_name in engine._macros:
        macro = engine._macros[macro_name]
        source_ids = list(macro.source_ids)
    else:
        source_ids = [0, 1, 2]
    
    print(f"📍 Source IDs: {source_ids}")
    
    # OPCIÓN 1: Configurar trayectorias individuales con macro_id
    print("\\n🔧 Configurando trayectorias individuales...")
    
    # Primero, intentar con macro_name como primer parámetro
    for i, sid in enumerate(source_ids):
        try:
            # API posible 1: (macro_id, source_id, shape, mode, **params)
            engine.set_individual_trajectory(
                macro_name,  # macro_id primero
                sid,         # source_id
                shape="circle",
                mode="fix",
                shape_params={'radius': 2.0},
                speed=1.0
            )
            print(f"   ✅ Fuente {sid}: configurada con API (macro_id, source_id, ...)")
        except Exception as e1:
            # Si falla, probar sin macro_id
            try:
                # API posible 2: (source_id, shape, mode, **params)
                engine.set_individual_trajectory(
                    sid,
                    shape="circle", 
                    mode="fix",
                    shape_params={'radius': 2.0},
                    speed=1.0
                )
                print(f"   ✅ Fuente {sid}: configurada con API (source_id, ...)")
            except Exception as e2:
                print(f"   ❌ Fuente {sid}: Error con ambas APIs")
                print(f"      API 1: {e1}")
                print(f"      API 2: {e2}")
    
    # OPCIÓN 2: Si lo anterior falla, usar set_macro_trajectory + configuración manual
    print("\\n🔧 Alternativa: Configurar macro trajectory...")
    try:
        # Definir una trayectoria circular simple
        def circular_trajectory(t):
            radius = 3.0
            x = radius * np.cos(2 * np.pi * t)
            y = radius * np.sin(2 * np.pi * t)
            z = 0.0
            return np.array([x, y, z])
        
        engine.set_macro_trajectory(macro_name, circular_trajectory)
        print("   ✅ Macro trajectory configurada")
    except Exception as e:
        print(f"   ❌ Error configurando macro trajectory: {e}")
    
    # Verificar componentes después de configuración
    print("\\n🔍 Verificando componentes activos:")
    for sid in source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components'):
                components = list(motion.active_components.keys())
                print(f"   Fuente {sid}: {components}")
                
                # Ver detalles de cada componente
                for comp_name, comp in motion.active_components.items():
                    enabled = getattr(comp, 'enabled', 'N/A')
                    print(f"      - {comp_name}: enabled={enabled}")
    
    # Capturar posiciones iniciales
    initial_positions = {}
    for sid in source_ids:
        if sid < len(engine._positions):
            initial_positions[sid] = engine._positions[sid].copy()
    
    # Ejecutar updates
    print("\\n🔄 Ejecutando 30 updates...")
    for i in range(30):
        engine.update()
        time.sleep(0.03)
        
        # Debug cada 10 updates
        if i % 10 == 0:
            sid = source_ids[0]
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial_positions[sid])
            print(f"   Update {i}: Fuente {sid} distancia = {dist:.4f}")
    
    # Verificar resultados
    print("\\n📊 RESULTADOS FINALES:")
    print("-" * 40)
    
    any_moved = False
    for sid in source_ids:
        if sid < len(engine._positions):
            current_pos = engine._positions[sid]
            initial_pos = initial_positions[sid]
            distance = np.linalg.norm(current_pos - initial_pos)
            moved = distance > 0.01
            
            print(f"Fuente {sid}: distancia = {distance:.4f} {'✅ MOVIDA' if moved else '❌ NO MOVIDA'}")
            if moved:
                any_moved = True
    
    # Diagnóstico adicional si no se mueven
    if not any_moved:
        print("\\n🔍 DIAGNÓSTICO ADICIONAL:")
        
        # Verificar si hay deltas
        sid = source_ids[0]
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            
            # Llamar update_with_deltas manualmente
            current_time = time.time()
            deltas = motion.update_with_deltas(current_time, 0.1)
            print(f"\\nDeltas retornados: {deltas}")
            
            # Ver el estado interno
            if hasattr(motion, 'state'):
                state = motion.state
                print(f"\\nEstado del SourceMotion:")
                for attr in ['position', 'position_on_trajectory', 'velocity']:
                    if hasattr(state, attr):
                        value = getattr(state, attr)
                        print(f"  - {attr}: {value}")
    
    return any_moved

if __name__ == "__main__":
    success = test_trajectory_with_correct_api()
    
    if success:
        print("\\n✅ ¡ÉXITO! Las trayectorias funcionan")
    else:
        print("\\n❌ Las trayectorias aún no funcionan")
        print("\\n💡 Siguiente paso: Revisar la implementación de IndividualTrajectory")
'''
    
    with open("test_trajectory_working.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test creado: test_trajectory_working.py")

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO DE API - Trayectorias Individuales")
    print("=" * 50)
    
    check_set_individual_trajectory()
    create_working_test()
    
    print("\n📝 Ejecuta:")
    print("python test_trajectory_working.py")