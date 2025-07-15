#!/usr/bin/env python3
"""Test de formación sphere - versión directa"""

from trajectory_hub import EnhancedTrajectoryEngine

print("🌐 TEST FORMACIÓN SPHERE - DIRECTO")
print("="*60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=20, fps=30)

# TEMPORAL: Actualizar directamente el engine para sphere
# (mientras completamos la arquitectura)
import numpy as np
import math

def apply_sphere_formation(engine, source_ids, spacing=2.0):
    """Aplicar formación esfera manualmente"""
    n = len(source_ids)
    golden_ratio = (1 + math.sqrt(5)) / 2
    
    for i, sid in enumerate(source_ids):
        # Ángulo vertical (de -1 a 1)
        y = 1 - (2 * i / (n - 1)) if n > 1 else 0
        
        # Radio en el plano XZ
        radius_xz = math.sqrt(1 - y * y)
        
        # Ángulo horizontal usando proporción áurea
        theta = 2 * math.pi * i / golden_ratio
        
        # Coordenadas finales
        x = radius_xz * math.cos(theta) * spacing
        y_final = y * spacing
        z = radius_xz * math.sin(theta) * spacing
        
        engine._positions[sid] = np.array([x, y_final, z])
        # Enviar a Spat
        engine.osc_bridge.send_position(sid, engine._positions[sid])

print("1. Creando macro...")
macro = engine.create_macro("esfera_test", 15, formation="circle")  # Temporal

print("2. Aplicando formación esfera...")
apply_sphere_formation(engine, macro.source_ids, spacing=3.0)

print("\n✅ Formación esfera aplicada")
print("\n💡 Verifica en Spat:")
print("   - 15 fuentes distribuidas en esfera")
print("   - Radio ~3 metros")
print("   - Distribución uniforme 3D")

# Stats
stats = engine.osc_bridge.get_stats()
print(f"\n📊 OSC: {stats['messages_sent']} mensajes enviados")
