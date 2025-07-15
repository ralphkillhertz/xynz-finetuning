#!/usr/bin/env python3
"""
Script de prueba para verificar formación esfera
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_sphere_formation():
    """Probar creación de macro con formación esfera"""
    print("=== Prueba de formación ESFERA ===\n")
    
    # Crear motor
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Crear IDs de fuentes
    source_ids = list(range(50))
    
    # Crear macro con formación esfera
    print("Creando macro con formación esfera...")
    try:
        macro_id = engine.create_macro(
            name="test_sphere",
            source_count=50,
            formation="sphere",
            spacing=None  # Probar con None para verificar el fix
        )
        print(f"✅ Macro creado exitosamente: {macro_id}")
        
        # Verificar posiciones
        print("\nPrimeras 5 posiciones:")
        for i in range(min(5, len(source_ids))):
            if source_ids[i] < len(engine._positions):
                pos = engine._positions[source_ids[i]]
                print(f"  Fuente {source_ids[i]}: x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.3f}")
                
        # Calcular estadísticas
        positions = []
        for sid in source_ids:
            if sid < len(engine._positions):
                positions.append(engine._positions[sid].copy())
                
        if positions:
            positions = np.array(positions)
            distances = np.linalg.norm(positions, axis=1)
            print(f"\nEstadísticas de distancias al origen:")
            print(f"  Min: {distances.min():.3f}")
            print(f"  Max: {distances.max():.3f}")
            print(f"  Media: {distances.mean():.3f}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sphere_formation()