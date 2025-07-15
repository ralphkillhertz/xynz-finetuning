#!/usr/bin/env python3
"""
🔍 BUSCAR - Encontrar el método update o equivalente en el engine
⚡ Ver cómo se actualiza realmente el sistema
"""

import os
import re

def find_update_method():
    """Buscar cómo se actualiza el engine"""
    
    print("🔍 BUSCANDO MÉTODO DE ACTUALIZACIÓN EN EL ENGINE\n")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # 1. Buscar cualquier método que parezca update
    print("1️⃣ BUSCANDO MÉTODOS RELACIONADOS CON UPDATE...")
    
    # Buscar todos los métodos
    methods = re.findall(r'def (\w+)\(self[^)]*\):', content)
    
    update_methods = []
    for method in methods:
        if any(word in method.lower() for word in ['update', 'tick', 'step', 'process', 'run']):
            update_methods.append(method)
    
    if update_methods:
        print(f"   Métodos encontrados: {update_methods}")
    else:
        print("   ❌ No se encontraron métodos tipo update")
    
    # 2. Buscar dónde se usa _source_motions
    print("\n2️⃣ BUSCANDO USO DE _source_motions...")
    
    source_motion_uses = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if '_source_motions' in line:
            # Contexto: método donde se usa
            for j in range(i, max(0, i-20), -1):
                if 'def ' in lines[j]:
                    method_name = re.search(r'def (\w+)', lines[j])
                    if method_name:
                        source_motion_uses.append((method_name.group(1), i+1, line.strip()))
                        break
    
    if source_motion_uses:
        print("   _source_motions se usa en:")
        for method, line_no, line_content in source_motion_uses[:10]:
            print(f"   • {method}() línea {line_no}: {line_content[:60]}")
    
    # 3. Buscar cómo se envían posiciones OSC
    print("\n3️⃣ BUSCANDO ENVÍO DE POSICIONES OSC...")
    
    osc_sends = []
    for i, line in enumerate(lines):
        if 'send_position' in line or 'osc' in line.lower():
            # Encontrar el método
            for j in range(i, max(0, i-20), -1):
                if 'def ' in lines[j]:
                    method_name = re.search(r'def (\w+)', lines[j])
                    if method_name:
                        osc_sends.append((method_name.group(1), i+1))
                        break
    
    if osc_sends:
        print("   Envío OSC en:")
        for method, line_no in osc_sends[:5]:
            print(f"   • {method}() línea {line_no}")
    
    # 4. Buscar el patrón principal de actualización
    print("\n4️⃣ ANALIZANDO PATRÓN DE ACTUALIZACIÓN...")
    
    # Buscar bucles que iteren sobre fuentes
    for_patterns = re.findall(r'for\s+\w+(?:,\s*\w+)?\s+in\s+self\.([^:]+):', content)
    
    print("   Bucles encontrados sobre:")
    for pattern in set(for_patterns):
        if 'source' in pattern.lower() or 'motion' in pattern.lower():
            print(f"   • self.{pattern}")
    
    # 5. Crear script para explorar el engine en runtime
    print("\n5️⃣ CREANDO SCRIPT DE EXPLORACIÓN...")
    
    explore_script = '''#!/usr/bin/env python3
"""
🔍 Explorar métodos del engine en runtime
"""

import os
import sys

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine()
    
    print("🔍 MÉTODOS DEL ENGINE\\n")
    
    # Todos los métodos
    methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
    
    # Categorizar
    print("📊 MÉTODOS DE ACTUALIZACIÓN:")
    for method in methods:
        if any(word in method.lower() for word in ['update', 'tick', 'step', 'process']):
            print(f"   • {method}()")
    
    print("\\n📊 MÉTODOS DE FUENTES:")
    for method in methods:
        if 'source' in method.lower():
            print(f"   • {method}()")
    
    print("\\n📊 MÉTODOS DE POSICIÓN:")
    for method in methods:
        if 'position' in method.lower():
            print(f"   • {method}()")
    
    # Ver si tiene update
    if hasattr(engine, 'update'):
        import inspect
        sig = inspect.signature(engine.update)
        print(f"\\n✅ engine.update{sig}")
    else:
        print("\\n❌ engine NO tiene método update()")
        
        # Buscar alternativas
        print("\\n🔍 Buscando método principal de actualización...")
        
        # El controller debe llamar algo
        # Veamos qué métodos podrían ser
        candidates = []
        for method in methods:
            try:
                # Ver si acepta dt o no params
                sig = inspect.signature(getattr(engine, method))
                params = list(sig.parameters.keys())
                if len(params) <= 2:  # self y tal vez dt
                    if any(word in method.lower() for word in ['update', 'tick', 'step']):
                        candidates.append((method, sig))
            except:
                pass
        
        if candidates:
            print("\\n   Candidatos:")
            for method, sig in candidates:
                print(f"   • {method}{sig}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("explore_engine_methods.py", 'w') as f:
        f.write(explore_script)
    
    print("   ✅ Script creado: explore_engine_methods.py")
    
    # 6. Buscar en el controller cómo llama al engine
    print("\n6️⃣ BUSCANDO EN EL CONTROLLER...")
    
    controller_file = "trajectory_hub/interface/interactive_controller.py"
    if os.path.exists(controller_file):
        with open(controller_file, 'r') as f:
            controller_content = f.read()
        
        # Buscar llamadas a engine.algo
        engine_calls = re.findall(r'self\.engine\.(\w+)\(', controller_content)
        
        update_like_calls = []
        for call in set(engine_calls):
            if any(word in call.lower() for word in ['update', 'tick', 'step', 'process']):
                update_like_calls.append(call)
        
        if update_like_calls:
            print(f"   El controller llama a: engine.{update_like_calls}")

if __name__ == "__main__":
    find_update_method()
    
    print("\n" + "="*60)
    print("🚀 PRÓXIMOS PASOS:")
    print("="*60)
    
    print("\n1. Ejecuta la exploración:")
    print("   python explore_engine_methods.py")
    
    print("\n2. Esto nos dirá qué método usar")
    print("\n3. Entonces podremos arreglarlo correctamente")