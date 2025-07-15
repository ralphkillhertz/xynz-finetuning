#!/usr/bin/env python3
"""
🔧 Fix: Corregir orden de parámetros en update() para concentración
⚡ Problema: IndividualTrajectory recibe (time, dt, state) pero espera (state, current_time, dt)
🎯 Impacto: ALTO - Sistema de concentración no funcional
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_update_call_order():
    """Corregir el orden de llamada en enhanced_trajectory_engine.py"""
    
    print("🔧 Corrigiendo orden de parámetros en engine.update()...")
    
    # Leer enhanced_trajectory_engine.py
    try:
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el punto donde se llama a motion.update()
        # El problema está en cómo engine.update() llama a motion.update()
        
        # Patrón actual incorrecto: motion.update(current_time, dt, state)
        # Patrón correcto: motion.update(state, current_time, dt)
        
        # Buscar la línea específica en el método update del engine
        import re
        
        # Buscar todas las llamadas a motion.update
        pattern = r'motion\.update\s*\(\s*current_time\s*,\s*dt\s*,\s*state\s*\)'
        replacement = 'motion.update(state, current_time, dt)'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            print("✅ Encontrado y corregido: motion.update(current_time, dt, state) → motion.update(state, current_time, dt)")
        else:
            # Buscar variantes
            pattern2 = r'motion\.update\s*\([^)]+\)'
            matches = re.findall(pattern2, content)
            print(f"⚠️ Patrón exacto no encontrado. Llamadas encontradas: {matches[:3]}")
            
            # Buscar en el método update del engine específicamente
            update_method_match = re.search(r'def update\(self[^:]*:\s*\n(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
            if update_method_match:
                update_content = update_method_match.group(1)
                # Buscar motion.update dentro del método
                if 'motion.update(' in update_content:
                    # Reemplazar manualmente
                    lines = content.split('\n')
                    fixed = False
                    for i, line in enumerate(lines):
                        if 'motion.update(' in line and 'current_time' in line and 'dt' in line and 'state' in line:
                            # Detectar el orden actual
                            if 'current_time' in line and line.index('current_time') < line.index('state'):
                                # Orden incorrecto, corregir
                                lines[i] = line.replace('motion.update(current_time, dt, state)', 'motion.update(state, current_time, dt)')
                                print(f"✅ Corregido en línea {i+1}: {lines[i].strip()}")
                                fixed = True
                                break
                    
                    if fixed:
                        content = '\n'.join(lines)
        
        # Guardar cambios
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ enhanced_trajectory_engine.py actualizado")
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return False
    
    return True

def test_concentration():
    """Test rápido del sistema de concentración corregido"""
    print("\n🧪 TEST DE CONCENTRACIÓN")
    print("="*50)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        from trajectory_hub.core.osc_bridge import SpatOSCBridge
        
        # Crear engine y bridge
        bridge = SpatOSCBridge(spat_host="127.0.0.1", spat_port=9800)
        engine = EnhancedTrajectoryEngine(bridge)
        
        # Crear macro con fuentes
        macro_id = engine.create_macro("test_concentration", 5)
        
        # Configurar trayectorias individuales
        engine.set_individual_trajectories(
            macro_id,
            {i: 'circle' for i in range(5)},
            movement_mode='velocity',
            movement_speed=1.0
        )
        
        # Test de update
        print("\n📊 Estado inicial:")
        for i in range(5):
            motion = engine._source_motions.get(i)
            if motion and 'individual_trajectory' in motion.components:
                traj = motion.components['individual_trajectory']
                print(f"  Fuente {i}: fase={traj.position_on_trajectory:.3f}, enabled={traj.enabled}")
        
        # Ejecutar update
        print("\n⏯️ Ejecutando engine.update()...")
        engine.update()
        
        print("\n📊 Estado después de update:")
        success = False
        for i in range(5):
            motion = engine._source_motions.get(i)
            if motion and 'individual_trajectory' in motion.components:
                traj = motion.components['individual_trajectory']
                print(f"  Fuente {i}: fase={traj.position_on_trajectory:.3f}, enabled={traj.enabled}")
                if traj.position_on_trajectory > 0:
                    success = True
        
        if success:
            print("\n✅ ¡ÉXITO! Las trayectorias ahora avanzan correctamente")
        else:
            print("\n⚠️ Las fases aún no avanzan, puede haber otro problema")
            
        # Test de concentración
        print("\n🎯 Activando concentración...")
        engine.set_concentration_factor(macro_id, 0.0)  # Totalmente concentrado
        
        print("\n✅ Test completado")
        
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 FIX DE CONCENTRACIÓN - ORDEN DE PARÁMETROS")
    print("="*60)
    
    # Aplicar corrección
    if fix_update_call_order():
        print("\n✅ Corrección aplicada")
        
        # Ejecutar test
        test_concentration()
    else:
        print("\n❌ No se pudo aplicar la corrección")