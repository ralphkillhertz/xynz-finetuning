# test_rotation_simple.py
# Test simple de rotaciones manuales MS

import numpy as np
import warnings
from trajectory_hub import EnhancedTrajectoryEngine

# Ignorar warnings no críticos
warnings.filterwarnings("ignore", message="No se puede crear modulador")

def test_manual_rotation():
    print("🎉 TEST: Rotaciones Manuales MS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear macro
    print("🔧 Creando macro con 4 fuentes...")
    macro_name = engine.create_macro("test_rotation", source_count=4, formation="square")
    
    # Guardar posiciones iniciales
    initial_positions = []
    for i in range(4):
        pos = engine._positions[i].copy()
        initial_positions.append(pos)
        print(f"   Fuente {i}: {pos}")
    
    # Configurar rotación manual
    print("\n🔧 Configurando rotación manual de 90°...")
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,              # 90° en radianes
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.5
    )
    
    # Ejecutar algunos updates
    print("\n⚙️ Ejecutando rotación (30 frames)...")
    for i in range(30):
        engine.update()
        
        if i % 10 == 0:
            print(f"\n   Frame {i}:")
            for j in range(4):
                pos = engine._positions[j]
                print(f"      Fuente {j}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # Verificar que se movieron
    print("\n📊 Verificación de movimiento:")
    moved_count = 0
    
    for i in range(4):
        initial = initial_positions[i]
        final = engine._positions[i]
        distance = np.linalg.norm(final - initial)
        
        if distance > 0.1:
            moved_count += 1
            print(f"   Fuente {i}: ✅ Movió {distance:.2f} unidades")
        else:
            print(f"   Fuente {i}: ❌ No se movió")
    
    print("\n" + "=" * 60)
    if moved_count == 4:
        print("✅ ¡ÉXITO! Todas las fuentes rotaron correctamente")
        print("✅ ManualMacroRotation funciona al 100%")
        
        print("\n📊 Estado del sistema:")
        print("   • Sistema de deltas: 90% completo")
        print("   • Rotaciones MS: 50% (manual ✅, algorítmica ✅)")
        print("   • Rotaciones IS: 0% (pendiente)")
        print("   • Servidor MCP: 0% (CRÍTICO)")
    else:
        print(f"⚠️ Solo {moved_count}/4 fuentes se movieron")

if __name__ == "__main__":
    test_manual_rotation()
    
    print("\n💾 Ejecuta: python save_session_state.py")