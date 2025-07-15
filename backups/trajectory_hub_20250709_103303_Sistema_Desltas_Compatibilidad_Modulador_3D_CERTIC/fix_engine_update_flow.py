import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_engine_update():
    """Corrige engine.update() para que procese motion_states"""
    print("🔧 CORRIGIENDO ENGINE.UPDATE() PARA PROCESAR MOTION_STATES")
    print("=" * 60)
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Leer el archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    print("\n1️⃣ Buscando método update()...")
    update_start = content.find("def update(self):")
    if update_start == -1:
        print("❌ No se encontró update()")
        return False
    
    # Buscar el final del método
    next_method = content.find("\n    def ", update_start + 1)
    if next_method == -1:
        next_method = len(content)
    
    # Extraer el método actual
    current_update = content[update_start:next_method]
    print("✅ Método update() encontrado")
    
    # Verificar si ya procesa motion_states
    if "motion.update(" in current_update:
        print("✅ Ya procesa motion_states")
    else:
        print("⚠️ NO procesa motion_states, añadiendo código...")
        
        # Buscar dónde insertar el código
        # Buscar después del cálculo de dt
        insert_point = current_update.find("self._last_update_time = current_time")
        if insert_point == -1:
            insert_point = current_update.find("dt =")
            
        if insert_point != -1:
            # Encontrar el final de esa línea
            line_end = current_update.find("\n", insert_point)
            
            # Código a insertar
            motion_update_code = """
        
        # Actualizar motion states y aplicar deltas
        for source_id, motion in self.motion_states.items():
            if source_id not in self._positions:
                continue
                
            # Sincronizar posición del state con el engine
            motion.state.position = self._positions[source_id].copy()
            
            # Actualizar el motion (que actualiza sus componentes)
            updated_state = motion.update(self._time, dt)
            
            # Obtener deltas de todos los componentes activos
            deltas = motion.update_with_deltas(self._time, dt)
            
            # Aplicar deltas a la posición
            if deltas:
                for delta in deltas:
                    if delta and delta.position is not None:
                        self._positions[source_id] += delta.position * delta.weight
"""
            
            # Insertar el código
            current_update = current_update[:line_end+1] + motion_update_code + current_update[line_end+1:]
            
            # Reemplazar en el contenido original
            content = content[:update_start] + current_update + content[next_method:]
            
            print("✅ Código de procesamiento añadido")
    
    # 2. Verificar que self._time existe
    print("\n2️⃣ Verificando self._time...")
    if "self._time = 0" not in content:
        print("⚠️ Falta self._time, añadiendo...")
        # Buscar __init__
        init_start = content.find("def __init__(")
        if init_start != -1:
            # Buscar dónde añadir
            init_end = content.find("self._frame_count = 0", init_start)
            if init_end != -1:
                line_end = content.find("\n", init_end)
                content = content[:line_end+1] + "        self._time = 0.0\n" + content[line_end+1:]
                print("✅ self._time añadido")
    
    # 3. Guardar el archivo
    print("\n3️⃣ Guardando archivo...")
    
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'{engine_path}.backup_{timestamp}'
    shutil.copy(engine_path, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Archivo guardado")
    
    return True

def test_update_flow():
    """Test del flujo de actualización"""
    print("\n\n🧪 TEST DEL FLUJO DE ACTUALIZACIÓN:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear sistema
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        
        # Configurar rotación
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,
            pitch=0.0,
            roll=0.0,
            interpolation_speed=90.0  # Más rápido para test
        )
        print(f"✅ Rotación configurada: {success}")
        
        # Verificar estado inicial
        print(f"\n📊 Estado inicial:")
        print(f"   Posición: {engine._positions[0]}")
        
        motion = engine.motion_states[0]
        comp = motion.active_components['manual_individual_rotation']
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        
        # Hacer 5 updates
        print(f"\n🔄 Ejecutando 5 updates...")
        for i in range(5):
            pos_before = engine._positions[0].copy()
            engine.update()
            pos_after = engine._positions[0].copy()
            
            moved = not np.array_equal(pos_before, pos_after)
            print(f"   Update {i+1}: {'✅ SE MOVIÓ' if moved else '❌ NO se movió'}")
            if moved:
                delta = np.linalg.norm(pos_after - pos_before)
                print(f"      Delta: {delta:.3f}")
                print(f"      Posición: [{pos_after[0]:.3f}, {pos_after[1]:.3f}, {pos_after[2]:.3f}]")
        
        # Estado final
        print(f"\n📊 Estado final:")
        print(f"   Posición: {engine._positions[0]}")
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        
        if not np.array_equal(engine._positions[0], [3.0, 0.0, 0.0]):
            print("\n✅ ¡ENGINE.UPDATE() FUNCIONA CORRECTAMENTE!")
        else:
            print("\n❌ Engine.update() NO procesa los componentes")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_engine_update():
        test_update_flow()