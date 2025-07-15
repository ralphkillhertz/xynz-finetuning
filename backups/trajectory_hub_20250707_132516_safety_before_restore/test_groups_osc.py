#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST GRUPOS OSC\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print("\nCreando macro 'Pajaros' con 3 fuentes...")
macro_id = engine.create_macro("Pajaros", source_count=3, formation="triangle")

print("\n✅ VERIFICA EN SPAT OSC MONITOR:")
print("   Deberías ver:")
print("   - /group/new ['Pajaros']")
print("   - /source/0/group ['Pajaros']")
print("   - /source/1/group ['Pajaros']") 
print("   - /source/2/group ['Pajaros']")

print("\n🎯 En Spat, el grupo 'Pajaros' debería existir")
print("   con las fuentes 1, 2 y 3 dentro")
