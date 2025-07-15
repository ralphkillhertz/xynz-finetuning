# === fix_test_constructor.py ===
# 🔧 Fix: Corregir parámetros del constructor en el test
# ⚡ Error: n_sources no es válido, debe ser max_sources
# 🎯 Impacto: BAJO - Solo afecta al test

import os

def fix_test():
    """Corrige los parámetros del constructor en el test"""
    
    print("🔧 Corrigiendo test_update_fix.py...")
    
    # Leer el archivo
    with open("test_update_fix.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cambiar n_sources por max_sources
    content = content.replace(
        "engine = EnhancedTrajectoryEngine(n_sources=10, enable_modulator=False)",
        "engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)"
    )
    
    # También corregir el enable_modulator si existe
    content = content.replace("enable_modulator=False", "")
    
    # Guardar
    with open("test_update_fix.py", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Test corregido")
    
    # Crear un test diagnóstico para ver los parámetros correctos
    diag_code = '''# === diagnose_constructor.py ===
# Diagnostica los parámetros correctos del constructor

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import inspect

# Ver la firma del constructor
sig = inspect.signature(EnhancedTrajectoryEngine.__init__)
print("🔍 Parámetros del constructor:")
print(f"   {sig}")

# Intentar crear con parámetros básicos
try:
    engine = EnhancedTrajectoryEngine()
    print("\\n✅ Constructor sin parámetros funciona")
except Exception as e:
    print(f"\\n❌ Error sin parámetros: {e}")

# Probar con max_sources
try:
    engine = EnhancedTrajectoryEngine(max_sources=10)
    print("✅ Constructor con max_sources=10 funciona")
except Exception as e:
    print(f"❌ Error con max_sources: {e}")

# Probar con fps
try:
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Constructor con max_sources=10, fps=60 funciona")
except Exception as e:
    print(f"❌ Error con max_sources y fps: {e}")
'''
    
    with open("diagnose_constructor.py", 'w', encoding='utf-8') as f:
        f.write(diag_code)
    
    print("✅ Diagnóstico creado: diagnose_constructor.py")

if __name__ == "__main__":
    fix_test()
    print("\n📝 Ahora ejecuta:")
    print("1. python diagnose_constructor.py  # Para ver los parámetros correctos")
    print("2. python test_update_fix.py       # Para probar el fix")