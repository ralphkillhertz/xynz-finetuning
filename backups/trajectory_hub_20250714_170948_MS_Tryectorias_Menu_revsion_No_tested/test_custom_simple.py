#!/usr/bin/env python3
"""
Prueba simple de formación personalizada
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_custom_rose():
    """Probar formación de rosa polar personalizada"""
    
    print("=== PRUEBA DE FORMACIÓN PERSONALIZADA ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Rosa polar con 4 pétalos
    print("Creando formación de rosa polar con función personalizada...")
    print("Función: r(t) = 2 + sin(4 * t * 2π)")
    print("         x(t) = r * cos(t * 2π)")
    print("         y(t) = r * sin(t * 2π)")
    print("         z(t) = t * 2 - 1\n")
    
    custom_func = {
        'r': '2 + sin(4 * t * 2 * pi)',
        'polar': True,
        'z': 't * 2 - 1'  # Variar Z de -1 a 1
    }
    
    try:
        macro = engine.create_macro(
            name="rosa_polar",
            source_count=32,
            formation="custom",
            spacing=1.5,
            custom_function=custom_func
        )
        
        print(f"✅ Macro 'rosa_polar' creado exitosamente con 32 fuentes")
        
        # Mostrar algunas posiciones para verificar
        print("\n📍 Primeras 8 posiciones:")
        for i in range(8):
            if i < len(engine._positions):
                pos = engine._positions[i]
                # Calcular radio real
                r = np.sqrt(pos[0]**2 + pos[1]**2)
                print(f"  Fuente {i}: x={pos[0]:6.3f}, y={pos[1]:6.3f}, z={pos[2]:6.3f}, r={r:.3f}")
        
        # Calcular estadísticas
        positions = []
        for i in range(32):
            if i < len(engine._positions):
                positions.append(engine._positions[i])
                
        if positions:
            positions = np.array(positions)
            radii = np.sqrt(positions[:, 0]**2 + positions[:, 1]**2)
            print(f"\n📊 Estadísticas:")
            print(f"  Radio mínimo: {radii.min():.3f}")
            print(f"  Radio máximo: {radii.max():.3f}")
            print(f"  Z mínimo: {positions[:, 2].min():.3f}")
            print(f"  Z máximo: {positions[:, 2].max():.3f}")
            
        print("\n✨ Formación personalizada creada exitosamente")
        print("   La forma debería verse como una rosa con 4 pétalos en SPAT")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_custom_rose()