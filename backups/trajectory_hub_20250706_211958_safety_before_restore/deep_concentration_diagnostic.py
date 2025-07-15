#!/usr/bin/env python3
"""
🔍 Diagnóstico profundo del problema de concentración
⚡ Encuentra exactamente dónde está el error de orden de parámetros
"""

import sys
import os
import ast
import inspect
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_update_methods():
    """Analizar todas las firmas de métodos update() en el sistema"""
    print("🔍 ANÁLISIS DE MÉTODOS UPDATE")
    print("="*60)
    
    # 1. Analizar IndividualTrajectory.update()
    print("\n1️⃣ IndividualTrajectory.update():")
    try:
        from trajectory_hub.core.motion_components import IndividualTrajectory
        sig = inspect.signature(IndividualTrajectory.update)
        print(f"   Firma esperada: {sig}")
        print(f"   Parámetros: {list(sig.parameters.keys())}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Analizar SourceMotion.update()
    print("\n2️⃣ SourceMotion.update():")
    try:
        from trajectory_hub.core.motion_components import SourceMotion
        sig = inspect.signature(SourceMotion.update)
        print(f"   Firma: {sig}")
        print(f"   Parámetros: {list(sig.parameters.keys())}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Buscar cómo engine.update() llama a motion.update()
    print("\n3️⃣ Llamadas en enhanced_trajectory_engine.py:")
    try:
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar todas las líneas con motion.update
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'motion.update(' in line and not line.strip().startswith('#'):
                print(f"   Línea {i+1}: {line.strip()}")
                
                # Analizar contexto
                if i > 0:
                    print(f"   Contexto: {lines[i-1].strip()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def find_update_chain():
    """Rastrear la cadena completa de llamadas update()"""
    print("\n\n🔗 CADENA DE LLAMADAS UPDATE")
    print("="*60)
    
    try:
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r', encoding='utf-8') as f:
            engine_content = f.read()
        
        # Buscar el método update del engine
        import re
        update_match = re.search(r'def update\(self.*?\n((?:    .*\n)*)', engine_content, re.MULTILINE)
        
        if update_match:
            update_body = update_match.group(0)
            print("📄 EnhancedTrajectoryEngine.update():")
            print("-"*40)
            # Mostrar solo las líneas relevantes
            for line in update_body.split('\n'):
                if any(keyword in line for keyword in ['motion.update', 'state =', 'current_time', 'dt']):
                    print(f"   {line}")
    except Exception as e:
        print(f"❌ Error: {e}")

def create_minimal_test():
    """Crear test mínimo para verificar el problema"""
    print("\n\n🧪 TEST MÍNIMO DE PARÁMETROS")
    print("="*60)
    
    try:
        from trajectory_hub.core.motion_components import SourceMotion, IndividualTrajectory, MotionState
        import numpy as np
        
        # Crear componentes
        motion = SourceMotion(source_id=0)
        traj = IndividualTrajectory(
            trajectory_type='circle',
            center=np.array([0, 0, 0]),
            radius=1.0,
            movement_speed=1.0
        )
        motion.add_component('individual_trajectory', traj)
        
        # Crear estado
        state = MotionState(position=np.array([0, 0, 0]))
        current_time = 0.0
        dt = 0.016
        
        print("1. Test con orden correcto (state, current_time, dt):")
        try:
            motion.update(state, current_time, dt)
            print(f"   ✅ OK - fase después: {traj.position_on_trajectory:.3f}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n2. Test con orden incorrecto (current_time, dt, state):")
        try:
            motion.update(current_time, dt, state)
            print(f"   ⚠️ No debería funcionar pero funcionó")
        except TypeError as e:
            print(f"   ✅ Error esperado: {e}")
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

def suggest_fix():
    """Sugerir la corrección exacta"""
    print("\n\n💡 CORRECCIÓN SUGERIDA")
    print("="*60)
    
    print("El problema está en enhanced_trajectory_engine.py")
    print("Buscar la línea que dice:")
    print("   motion.update(current_time, dt, state)")
    print("\nY cambiarla por:")
    print("   motion.update(state, current_time, dt)")
    print("\nEsto alineará el orden de parámetros con lo que espera IndividualTrajectory")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO PROFUNDO - PROBLEMA DE CONCENTRACIÓN")
    print("="*70)
    
    analyze_update_methods()
    find_update_chain()
    create_minimal_test()
    suggest_fix()
    
    print("\n" + "="*70)
    print("✅ Diagnóstico completado")