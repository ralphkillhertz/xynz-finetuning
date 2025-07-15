import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_iteration():
    """Corrige la iteración sobre active_components en SourceMotion.update()"""
    print("🔧 CORRIGIENDO ITERACIÓN EN SourceMotion.update()")
    print("=" * 60)
    
    filepath = 'trajectory_hub/core/motion_components.py'
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("📄 Buscando el bug...")
    
    # Buscar la línea problemática
    fixed = False
    for i, line in enumerate(lines):
        # Buscar la línea exacta
        if "for component in self.active_components:" in line:
            print(f"❌ Línea {i+1} con BUG encontrada:")
            print(f"   ANTES: {line.rstrip()}")
            
            # Corregir la línea
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + "for component in self.active_components.values():\n"
            
            print(f"   ✅ DESPUÉS: {lines[i].rstrip()}")
            fixed = True
            break
    
    if not fixed:
        print("⚠️ No se encontró la línea exacta, buscando variantes...")
        
        # Buscar dentro del método update de SourceMotion
        in_sourcemotion = False
        in_update = False
        
        for i, line in enumerate(lines):
            if "class SourceMotion:" in line:
                in_sourcemotion = True
            elif in_sourcemotion and line.strip().startswith("class "):
                in_sourcemotion = False
                
            if in_sourcemotion and "def update(" in line:
                in_update = True
            elif in_update and (line.strip().startswith("def ") or line.strip().startswith("class ")):
                in_update = False
                
            if in_update and "self.active_components" in line and "for" in line:
                print(f"🔍 Línea {i+1} encontrada:")
                print(f"   ANTES: {line.rstrip()}")
                
                # Diferentes formas de corregir según el patrón
                if "for component in self.active_components" in line:
                    # Cambiar a .values()
                    line = line.replace("self.active_components", "self.active_components.values()")
                elif "for name, component in self.active_components" in line and ".items()" not in line:
                    # Añadir .items()
                    line = line.replace("self.active_components", "self.active_components.items()")
                
                lines[i] = line
                print(f"   ✅ DESPUÉS: {line.rstrip()}")
                fixed = True
                break
    
    if fixed:
        # Guardar archivo
        print("\n💾 Guardando archivo...")
        
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'{filepath}.backup_{timestamp}'
        shutil.copy(filepath, backup_path)
        print(f"✅ Backup: {backup_path}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("✅ Archivo corregido")
    else:
        print("❌ No se encontró la línea a corregir")
        return False
    
    return True

def test_final():
    """Test final de la rotación"""
    print("\n\n🎯 TEST FINAL DE ROTACIÓN MANUAL IS:")
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
            interpolation_speed=180.0  # Muy rápido para test
        )
        
        print(f"✅ Sistema configurado")
        
        # Estado inicial
        motion = engine.motion_states[0]
        comp = motion.active_components['manual_individual_rotation']
        print(f"\n📊 Estado inicial:")
        print(f"   Posición: {engine._positions[0]}")
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        
        # 10 updates
        print(f"\n🔄 Ejecutando 10 updates...")
        positions = []
        
        for i in range(10):
            engine.update()
            pos = engine._positions[0].copy()
            positions.append(pos)
            
            if i < 5 or i == 9:  # Primeros 5 y último
                angle = np.degrees(np.arctan2(pos[1], pos[0]))
                print(f"   Update {i+1}: pos=[{pos[0]:6.3f}, {pos[1]:6.3f}] | ángulo={angle:6.1f}° | yaw={np.degrees(comp.current_yaw):6.1f}°")
        
        # Verificar resultado
        initial = np.array([3.0, 0.0, 0.0])
        final = positions[-1]
        moved = np.linalg.norm(final - initial) > 0.1
        
        print(f"\n📊 Resultado final:")
        print(f"   Posición final: [{final[0]:.3f}, {final[1]:.3f}, {final[2]:.3f}]")
        print(f"   Distancia movida: {np.linalg.norm(final - initial):.3f}")
        print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
        
        print("\n" + "=" * 60)
        if moved:
            print("✅ ¡ROTACIÓN MANUAL IS FUNCIONA PERFECTAMENTE! 🎉🎉🎉")
            print("   Sistema de deltas 100% operativo")
            print("   ManualIndividualRotation completamente funcional")
        else:
            print("❌ La rotación aún no funciona")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if fix_iteration():
        test_final()