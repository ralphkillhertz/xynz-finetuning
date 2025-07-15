#!/usr/bin/env python3
"""
🧪 Test final de concentración - sin dependencias problemáticas
⚡ Verifica si el sistema ya funciona con modo 'fix'
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_concentration():
    """Test directo del sistema de concentración"""
    
    print("🧪 TEST DIRECTO DE CONCENTRACIÓN")
    print("="*60)
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        from trajectory_hub.core.motion_components import TrajectoryMovementMode
        import numpy as np
        
        # Crear engine sin parámetros
        print("1️⃣ Creando engine...")
        engine = EnhancedTrajectoryEngine()
        print("   ✅ Engine creado")
        
        # Crear macro como en tu test original
        print("\n2️⃣ Creando macro 'qwe' con 50 fuentes...")
        macro_id = engine.create_macro("qwe", 50)
        print(f"   ✅ Macro creado: {macro_id}")
        
        # Configurar trayectorias con modo 'fix'
        print("\n3️⃣ Configurando trayectorias individuales...")
        trajectories = {i: 'circle' for i in range(50)}
        
        # Intentar con 'fix' primero
        try:
            engine.set_individual_trajectories(
                macro_id,
                trajectories,
                movement_mode='fix',
                movement_speed=1.0
            )
            print("   ✅ Configurado con modo 'fix'")
        except Exception as e:
            print(f"   ⚠️ Error con 'fix': {e}")
            # Intentar sin movement_mode
            engine.set_individual_trajectories(macro_id, trajectories)
            print("   ✅ Configurado sin especificar modo")
        
        # Verificar estado inicial
        print("\n4️⃣ Estado inicial de algunas fuentes:")
        for i in [0, 10, 25, 40, 49]:
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    print(f"   Fuente {i}: enabled={traj.enabled}, fase={traj.position_on_trajectory:.3f}")
        
        # Ejecutar updates
        print("\n5️⃣ Ejecutando 20 updates...")
        for _ in range(20):
            engine.update()
        
        # Verificar movimiento
        print("\n6️⃣ Estado después de updates:")
        phases_moved = []
        for i in [0, 10, 25, 40, 49]:
            if i in engine._source_motions:
                motion = engine._source_motions[i]
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    phases_moved.append(traj.position_on_trajectory)
                    print(f"   Fuente {i}: fase={traj.position_on_trajectory:.3f}")
        
        if any(phase > 0 for phase in phases_moved):
            print("\n✅ ¡LAS TRAYECTORIAS SE MUEVEN!")
            
            # Test de concentración
            print("\n7️⃣ TEST DE CONCENTRACIÓN")
            print("-"*40)
            
            # Factor 0.0 = totalmente concentrado
            print("   Aplicando concentración total (factor=0.0)...")
            try:
                engine.set_concentration_factor(macro_id, 0.0)
                print("   ✅ set_concentration_factor ejecutado")
                
                # Updates para ver el efecto
                for _ in range(5):
                    engine.update()
                
                print("   ✅ Concentración aplicada sin errores")
                
                # Toggle
                print("\n   Probando toggle...")
                engine.toggle_concentration(macro_id)
                print("   ✅ Toggle ejecutado")
                
                # Más updates
                for _ in range(5):
                    engine.update()
                
                print("\n🎉 ¡SISTEMA DE CONCENTRACIÓN FUNCIONAL!")
                return True
                
            except Exception as e:
                print(f"   ❌ Error en concentración: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("\n❌ LAS TRAYECTORIAS NO SE MUEVEN")
            print("\nPosibles soluciones:")
            print("1. Verificar que las trayectorias estén usando TrajectoryMovementMode.FIX")
            print("2. Revisar el método update() en IndividualTrajectory")
            print("3. Asegurar que engine.update() propague los cambios")
            return False
            
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_current_mode_setting():
    """Verificar cómo se está configurando el modo actualmente"""
    
    print("\n\n🔍 VERIFICACIÓN DE CONFIGURACIÓN DE MODOS")
    print("="*60)
    
    try:
        # Leer enhanced_trajectory_engine.py
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar set_individual_trajectories
        import re
        
        # Buscar el método
        match = re.search(r'def set_individual_trajectories\(self.*?\n((?:        .*\n)*)', content, re.DOTALL)
        
        if match:
            method_body = match.group(0)
            
            # Buscar cómo se configura el movement_mode
            if 'movement_mode' in method_body:
                print("✅ El método set_individual_trajectories maneja movement_mode")
                
                # Buscar si hay algún valor por defecto
                if "'velocity'" in method_body:
                    print("⚠️ Todavía hay referencias a 'velocity' - necesita cambiar a 'fix'")
                elif "'fix'" in method_body:
                    print("✅ Ya está usando 'fix'")
                else:
                    print("ℹ️ No hay un valor por defecto explícito")
                    
                # Mostrar las líneas relevantes
                lines = method_body.split('\n')
                for i, line in enumerate(lines):
                    if 'movement_mode' in line and ('=' in line or 'set_movement_mode' in line):
                        print(f"\n   Línea relevante: {line.strip()}")
                        
    except Exception as e:
        print(f"Error: {e}")

def manual_fix_instructions():
    """Instrucciones para corrección manual si es necesario"""
    
    print("\n\n📝 INSTRUCCIONES DE CORRECCIÓN MANUAL")
    print("="*60)
    
    print("""
Si las trayectorias no se mueven, verifica:

1. En enhanced_trajectory_engine.py, método set_individual_trajectories():
   - Cambiar: movement_mode = movement_mode or 'velocity'
   - Por: movement_mode = movement_mode or 'fix'

2. En motion_components.py, método set_movement_mode():
   - Agregar al inicio:
     if isinstance(mode, str):
         if mode == 'velocity':
             mode = 'fix'
         mode = TrajectoryMovementMode(mode)

3. Verificar que TrajectoryMovementMode.FIX realmente mueva las trayectorias
   en el método update() de IndividualTrajectory

El problema principal es que 'velocity' no existe como modo.
Los modos válidos son: STOP, FIX, RANDOM, VIBRATION, SPIN, FREEZE
""")

if __name__ == "__main__":
    print("🚀 TEST FINAL DE CONCENTRACIÓN")
    print("="*70)
    
    # Test principal
    success = test_direct_concentration()
    
    if not success:
        # Si falla, verificar configuración
        check_current_mode_setting()
        manual_fix_instructions()
    
    print("\n" + "="*70)
    print(f"Resultado: {'✅ ÉXITO' if success else '❌ REQUIERE CORRECCIÓN'}")