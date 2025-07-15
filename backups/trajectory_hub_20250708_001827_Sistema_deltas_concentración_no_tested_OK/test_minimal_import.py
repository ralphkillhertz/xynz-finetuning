# Test mínimo de importación
import sys
import os

# Añadir el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Path de Python:")
for p in sys.path[:5]:
    print(f"  {p}")

print("\nIntentando import directo...")
try:
    import trajectory_hub.core.motion_components as mc
    print("✅ Módulo importado")
    
    # Ver qué contiene
    print("\nContenido del módulo:")
    for item in dir(mc):
        if not item.startswith('_'):
            print(f"  - {item}")
            
    # Intentar acceder a MotionState
    if hasattr(mc, 'MotionState'):
        print("\n✅ MotionState está en el módulo")
        ms = mc.MotionState()
        print(f"   Creado: {type(ms)}")
    else:
        print("\n❌ MotionState NO está en el módulo")
        
except Exception as e:
    print(f"❌ Error al importar: {e}")
    
    # Intentar import más específico
    print("\nIntentando import desde trajectory_hub...")
    try:
        from trajectory_hub.core.motion_components import MotionState
        print("✅ MotionState importado directamente")
    except Exception as e2:
        print(f"❌ Error: {e2}")
