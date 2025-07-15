# === diagnose_create_source.py ===
# 🔍 Diagnóstico: Ver qué retorna create_source exactamente
# ⚡ Para entender el error de tipos

import os

def diagnose_create_source():
    """Ver el método create_source completo"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Buscando create_source...")
    
    in_method = False
    method_lines = []
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'def create_source' in line:
            in_method = True
            indent_level = len(line) - len(line.lstrip())
            print(f"\n✅ Encontrado en línea {i+1}")
            print("📋 Método completo:")
            print("-" * 60)
        
        if in_method:
            # Si encontramos otro método al mismo nivel, terminar
            if line.strip().startswith('def ') and len(line) - len(line.lstrip()) <= indent_level and 'def create_source' not in line:
                break
            
            # Imprimir línea
            print(f"{i+1:4d}: {line.rstrip()}")
            method_lines.append(line)
            
            # Buscar returns
            if 'return' in line:
                print(f"\n   ⚠️ RETURN encontrado: {line.strip()}")
    
    # Análisis
    print("\n" + "="*60)
    print("📊 ANÁLISIS:")
    
    # Buscar todos los returns
    returns = []
    for line in method_lines:
        if 'return' in line:
            returns.append(line.strip())
    
    print(f"\n🔍 Returns encontrados: {len(returns)}")
    for r in returns:
        print(f"   - {r}")
        if 'motion_states' in r:
            print("     ⚠️ Esto retorna un MotionState, no un ID")
        if 'source_id' in r and 'motion_states[source_id]' in r:
            print("     ❌ PROBLEMA: Retorna el objeto, no el ID")
    
    # Test rápido
    print("\n🧪 Test rápido:")
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from trajectory_hub import EnhancedTrajectoryEngine
        
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        result = engine.create_source("test")
        print(f"   create_source retornó: {result}")
        print(f"   Tipo: {type(result)}")
        print(f"   ¿Es MotionState?: {'motion_states' in str(type(result)).lower()}")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    diagnose_create_source()