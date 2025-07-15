# === find_manual_individual_init.py ===
# 🔍 Buscar __init__ de ManualIndividualRotation
# ⚡ Ver cómo se inicializa correctamente

import re

print("🔍 BUSCANDO __init__ DE ManualIndividualRotation")
print("=" * 60)

try:
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    # Buscar la clase y su __init__
    class_match = re.search(r'class ManualIndividualRotation.*?(?=class|\Z)', content, re.DOTALL)
    
    if class_match:
        class_content = class_match.group(0)
        
        # Buscar __init__
        init_match = re.search(r'def __init__\(self.*?\):', class_content)
        if init_match:
            print("✅ Encontrado __init__:")
            print(f"   {init_match.group(0)}")
        else:
            print("⚠️ No tiene __init__ definido (usa el del padre)")
            
        # Buscar métodos set_
        set_methods = re.findall(r'def (set_\w+)\(.*?\):', class_content)
        if set_methods:
            print("\n📋 Métodos set_ disponibles:")
            for method in set_methods:
                print(f"   - {method}")
                
    # Buscar cómo se usa en el engine
    print("\n🔍 Buscando uso en engine...")
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        engine_content = f.read()
        
    # Buscar set_manual_individual_rotation
    manual_match = re.search(r'def set_manual_individual_rotation.*?(?=def|\Z)', engine_content, re.DOTALL)
    if manual_match:
        method = manual_match.group(0)
        print("\n📄 Método set_manual_individual_rotation:")
        print("-" * 60)
        lines = method.strip().split('\n')[:20]
        for line in lines:
            print(line)
            
except Exception as e:
    print(f"Error: {e}")

print("\n✅ Diagnóstico completo")