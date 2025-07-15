#!/usr/bin/env python3
"""Test limpio sin imports problemáticos"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🧪 TEST LIMPIO\n")

# Test 1: Import directo de clases base
print("1️⃣ Importando clases base directamente...")
try:
    # Import directo, no a través de __init__.py
    import trajectory_hub.core.motion_components
    
    # Acceder a las clases
    MotionState = trajectory_hub.core.motion_components.MotionState
    MotionDelta = trajectory_hub.core.motion_components.MotionDelta
    SourceMotion = trajectory_hub.core.motion_components.SourceMotion
    
    print("✅ Clases importadas correctamente")
    
    # Crear instancias
    ms = MotionState()
    print(f"   MotionState position: {ms.position}")
    
    md = MotionDelta()
    print(f"   MotionDelta source: '{md.source}'")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Import del engine
print("\n2️⃣ Importando EnhancedTrajectoryEngine...")
try:
    import trajectory_hub.core.enhanced_trajectory_engine
    EnhancedTrajectoryEngine = trajectory_hub.core.enhanced_trajectory_engine.EnhancedTrajectoryEngine
    
    print("✅ Engine importado")
    
    # Crear instancia
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    print(f"   Engine creado: max_sources={engine.max_sources}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Test completado!")
