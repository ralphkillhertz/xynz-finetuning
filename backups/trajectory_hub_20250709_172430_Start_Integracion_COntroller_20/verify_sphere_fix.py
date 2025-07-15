#!/usr/bin/env python3
"""
🧪 Verificador de sphere fix
⚡ Prueba que la formación sphere funcione correctamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.control.managers.formation_manager import FormationManager

def test_sphere():
    """Prueba la formación sphere"""
    print("🧪 Probando FormationManager sphere...")
    print("=" * 50)
    
    fm = FormationManager()
    
    # Probar con diferentes cantidades de sources
    test_counts = [4, 8, 16]
    
    for count in test_counts:
        print(f"\n📍 Probando con {count} sources:")
        positions = fm.calculate_formation("sphere", count)
        
        # Verificar que son 3D
        all_3d = all(len(pos) == 3 for pos in positions)
        print(f"  ✓ Todas las posiciones son 3D: {all_3d}")
        
        # Verificar que no todas están en el mismo plano
        z_values = [pos[2] for pos in positions]
        has_depth = len(set(z_values)) > 1
        print(f"  ✓ Tiene profundidad (diferentes Z): {has_depth}")
        
        # Mostrar algunas posiciones
        print(f"  📊 Primeras 3 posiciones:")
        for i, pos in enumerate(positions[:3]):
            print(f"     Source {i}: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")
        
        # Verificar distribución esférica
        # Todas deberían estar aproximadamente a la misma distancia del centro
        distances = []
        for pos in positions:
            dist = (pos[0]**2 + pos[1]**2 + pos[2]**2)**0.5
            distances.append(dist)
        
        avg_dist = sum(distances) / len(distances)
        max_deviation = max(abs(d - avg_dist) for d in distances)
        
        print(f"  ✓ Radio promedio: {avg_dist:.2f}")
        print(f"  ✓ Desviación máxima: {max_deviation:.4f} {'✅' if max_deviation < 0.01 else '⚠️'}")

def check_engine_integration():
    """Verifica que Engine tenga el código sphere"""
    print("\n\n🔍 Verificando integración en Engine...")
    print("=" * 50)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print(f"❌ No se encuentra {engine_path}")
        return False
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    checks = [
        ("Import FormationManager", "from trajectory_hub.control.managers.formation_manager import FormationManager" in content),
        ("Caso sphere", 'elif formation == "sphere":' in content),
        ("Uso de FormationManager", '_fm.calculate_formation("sphere"' in content)
    ]
    
    all_good = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🌐 VERIFICADOR DE SPHERE FIX")
    print("=" * 60)
    
    # Test FormationManager
    test_sphere()
    
    # Check Engine
    engine_ok = check_engine_integration()
    
    print("\n" + "=" * 60)
    if engine_ok:
        print("✅ SPHERE ESTÁ LISTO PARA USAR")
        print("\n🚀 Ejecuta el sistema con:")
        print("   python -m trajectory_hub.interface.interactive_controller")
    else:
        print("⚠️  SPHERE NO ESTÁ INTEGRADO EN ENGINE")
        print("\n💡 Ejecuta primero:")
        print("   python fix_sphere_in_engine.py")