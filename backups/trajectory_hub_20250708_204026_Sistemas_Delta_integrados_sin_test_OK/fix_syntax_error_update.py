import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_syntax_error():
    """Corrige el error de sintaxis en la línea 1285"""
    print("🔧 CORRIGIENDO ERROR DE SINTAXIS")
    print("=" * 60)
    
    filepath = 'trajectory_hub/core/motion_components.py'
    
    # Leer el archivo línea por línea
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Archivo: {filepath}")
    print(f"   Total líneas: {len(lines)}")
    
    # Buscar la línea problemática (1285 = índice 1284)
    if len(lines) > 1284:
        problem_line = lines[1284]
        print(f"\n❌ Línea 1285 actual:")
        print(f"   {problem_line.rstrip()}")
        
        # Corregir la línea
        correct_line = "    def update(self, current_time: float, dt: float, state: 'MotionState') -> 'MotionState':\n"
        lines[1284] = correct_line
        
        print(f"\n✅ Línea 1285 corregida:")
        print(f"   {correct_line.rstrip()}")
        
        # Mostrar contexto
        print(f"\n📋 Contexto (líneas 1283-1287):")
        for i in range(max(0, 1282), min(len(lines), 1287)):
            marker = ">>>" if i == 1284 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Guardar el archivo
    print(f"\n💾 Guardando archivo...")
    
    # Backup
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'{filepath}.backup_{timestamp}'
    shutil.copy(filepath, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Archivo corregido y guardado")
    
    # Verificar que se puede importar
    print(f"\n🧪 Verificando sintaxis...")
    try:
        import py_compile
        py_compile.compile(filepath, doraise=True)
        print("✅ Sintaxis correcta")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Todavía hay errores de sintaxis: {e}")
        return False

def test_rotation_after_fix():
    """Test rápido después del fix"""
    print("\n\n🧪 TEST DESPUÉS DEL FIX:")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear sistema
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        print("✅ Sistema creado")
        
        # Configurar rotación
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0
        )
        print(f"✅ Rotación configurada: {success}")
        
        # Verificar valores
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"\n📊 Componente configurado:")
                print(f"   Target yaw: {np.degrees(comp.target_yaw):.1f}°")
                print(f"   Enabled: {comp.enabled}")
                
                # Test update manual
                print(f"\n🔄 Test update manual:")
                print(f"   Current yaw antes: {np.degrees(comp.current_yaw):.1f}°")
                
                # Llamar update
                state = comp.update(0.0, 0.1, motion.state)
                
                print(f"   Current yaw después: {np.degrees(comp.current_yaw):.1f}°")
                print(f"   ¿Se actualizó?: {comp.current_yaw > 0}")
                
                # Test calculate_delta
                delta = comp.calculate_delta(motion.state, 0.1, 0.1)
                if delta:
                    print(f"\n📐 Delta calculado:")
                    print(f"   Position: {delta.position}")
                    print(f"   ¿Es movimiento?: {not np.allclose(delta.position, 0)}")
        
        print("\n✅ Sistema funcional")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_syntax_error():
        test_rotation_after_fix()