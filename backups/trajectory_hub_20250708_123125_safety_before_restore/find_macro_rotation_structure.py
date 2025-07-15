# === find_macro_rotation_structure.py ===
# 🔍 Buscar estructura real de MacroRotation
# ⚡ Diagnóstico profundo
# 🎯 Impacto: DEBUG

import inspect

print("🔍 Analizando estructura de MacroRotation")
print("=" * 50)

try:
    from trajectory_hub.core.motion_components import MacroRotation
    
    print("✅ MacroRotation importado")
    
    # Listar todos los métodos y atributos
    print("\n📋 Métodos y atributos de MacroRotation:")
    members = inspect.getmembers(MacroRotation)
    
    methods = []
    attributes = []
    
    for name, obj in members:
        if not name.startswith('_'):
            if callable(obj):
                methods.append(name)
            else:
                attributes.append(name)
    
    print("\n🔧 Métodos públicos:")
    for method in sorted(methods):
        print(f"   - {method}")
        
    print("\n📊 Atributos:")
    for attr in sorted(attributes):
        print(f"   - {attr}")
    
    # Buscar el __init__
    print("\n🔍 Analizando __init__:")
    init_source = inspect.getsource(MacroRotation.__init__)
    print("```python")
    print(init_source[:500] + "..." if len(init_source) > 500 else init_source)
    print("```")
    
    # Buscar métodos relacionados con velocidad
    print("\n🔍 Buscando métodos de velocidad:")
    for name, obj in inspect.getmembers(MacroRotation):
        if 'speed' in name.lower() or 'velocity' in name.lower() or 'rotation' in name.lower():
            if callable(obj) and not name.startswith('_'):
                print(f"\n   📌 {name}:")
                try:
                    sig = inspect.signature(obj)
                    print(f"      Firma: {name}{sig}")
                except:
                    print(f"      (no se pudo obtener firma)")
                    
    # Buscar calculate_delta
    print("\n🔍 Analizando calculate_delta:")
    if hasattr(MacroRotation, 'calculate_delta'):
        sig = inspect.signature(MacroRotation.calculate_delta)
        print(f"   Firma: calculate_delta{sig}")
        
        # Ver las primeras líneas
        source = inspect.getsource(MacroRotation.calculate_delta)
        lines = source.split('\n')[:10]
        print("\n   Primeras líneas:")
        for line in lines:
            print(f"   {line}")
    
    # Buscar en el archivo la línea problemática
    print("\n🔍 Buscando líneas problemáticas en el archivo:")
    import os
    file_path = "trajectory_hub/core/motion_components.py"
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if 'set_rotation_speeds' in line:
            print(f"\n   Línea {i+1}: {line.strip()}")
            # Mostrar contexto
            for j in range(max(0, i-2), min(len(lines), i+3)):
                print(f"   {j+1}: {lines[j].rstrip()}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Análisis completado")