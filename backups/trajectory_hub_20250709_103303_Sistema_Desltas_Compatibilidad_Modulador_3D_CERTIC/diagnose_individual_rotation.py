# === diagnose_individual_rotation.py ===
# 🔍 Diagnóstico: Verificar firma de set_individual_rotation
# ⚡ Análisis rápido del método

import inspect
from trajectory_hub.core import EnhancedTrajectoryEngine

def diagnose():
    """Diagnosticar set_individual_rotation"""
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Verificar si existe el método
    if hasattr(engine, 'set_individual_rotation'):
        method = getattr(engine, 'set_individual_rotation')
        sig = inspect.signature(method)
        
        print("✅ Método encontrado!")
        print(f"📝 Firma: {sig}")
        print(f"🔧 Parámetros: {list(sig.parameters.keys())}")
        
        # Buscar en el código fuente
        try:
            source = inspect.getsource(method)
            # Buscar los primeros 200 caracteres
            print(f"\n📄 Inicio del método:")
            print(source[:300] + "...")
        except:
            pass
    else:
        print("❌ Método no encontrado")
        
    # Buscar métodos similares
    print("\n🔍 Métodos relacionados con rotation:")
    for attr in dir(engine):
        if 'rotation' in attr.lower() and 'individual' in attr.lower():
            print(f"   - {attr}")

if __name__ == "__main__":
    diagnose()