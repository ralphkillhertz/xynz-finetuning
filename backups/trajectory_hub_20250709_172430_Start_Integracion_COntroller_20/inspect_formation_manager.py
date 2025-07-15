import os
import re

def inspect_formation_manager():
    """Inspeccionar FormationManager para entender su API"""
    print("🔍 INSPECCIONANDO FormationManager")
    print("="*60)
    
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if not os.path.exists(fm_file):
        print(f"❌ No existe: {fm_file}")
        return
    
    with open(fm_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Buscar todos los métodos
    print("\n📋 MÉTODOS DE FormationManager:")
    methods = []
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            method_name = line.strip().split('(')[0].replace('def ', '')
            methods.append((i+1, method_name, line.strip()))
            print(f"   L{i+1}: {method_name}()")
    
    # 2. Buscar cómo se manejan las formaciones
    print("\n\n🎯 MANEJO DE FORMACIONES:")
    
    # Buscar if/elif con formation
    formation_handlers = []
    for i, line in enumerate(lines):
        if ('if formation' in line or 'elif formation' in line) and '==' in line:
            formation_handlers.append((i+1, line.strip()))
            print(f"   L{i+1}: {line.strip()}")
    
    # 3. Ver la estructura de sphere específicamente
    print("\n\n🌐 CÓDIGO DE SPHERE:")
    sphere_start = None
    for i, line in enumerate(lines):
        if 'formation == "sphere"' in line:
            sphere_start = i
            break
    
    if sphere_start:
        # Mostrar 20 líneas del código sphere
        for i in range(sphere_start, min(len(lines), sphere_start + 20)):
            print(f"   {i+1}: {lines[i]}")
    
    # 4. Ver cómo se llama desde fuera
    print("\n\n🔗 CÓMO SE USA FormationManager:")
    
    # Buscar en CommandProcessor
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            cp_content = f.read()
        
        # Buscar FormationManager
        fm_usage = re.findall(r'formation_manager\.\w+\([^)]*\)', cp_content)
        
        if fm_usage:
            print("\n   En CommandProcessor:")
            for usage in fm_usage[:5]:
                print(f"   - {usage}")
        
        # Buscar importación
        import_match = re.search(r'from.*FormationManager.*import.*', cp_content)
        if import_match:
            print(f"\n   Import: {import_match.group(0)}")

def create_correct_test():
    """Crear test con la API correcta"""
    print("\n\n📝 CREANDO TEST CORRECTO...")
    
    # Primero ver si FormationManager existe y cómo funciona
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if os.path.exists(fm_file):
        with open(fm_file, 'r') as f:
            content = f.read()
        
        # Buscar el método principal
        main_method = None
        if 'def calculate_formation' in content:
            main_method = 'calculate_formation'
        elif 'def get_positions' in content:
            main_method = 'get_positions'
        elif 'def create_formation' in content:
            main_method = 'create_formation'
        else:
            # Buscar cualquier método que devuelva positions
            method_match = re.search(r'def (\w+).*\n.*positions.*\n.*return', content)
            if method_match:
                main_method = method_match.group(1)
        
        if main_method:
            print(f"✅ Método principal parece ser: {main_method}()")
            
            test_content = f'''
# === test_sphere_correct.py ===
import sys
sys.path.append('.')

# Test directo del cálculo de sphere
print("🧪 TEST DE SPHERE 3D")
print("="*40)

# Opción 1: Probar FormationManager si existe
try:
    from trajectory_hub.control.managers.formation_manager import FormationManager
    fm = FormationManager()
    
    # Intentar diferentes métodos
    methods_to_try = ['{main_method}', 'get_formation', 'calculate_formation', 'create_formation']
    
    for method_name in methods_to_try:
        if hasattr(fm, method_name):
            print(f"\\n✅ Probando {{method_name}}()...")
            method = getattr(fm, method_name)
            try:
                # Intentar llamar con diferentes firmas
                try:
                    positions = method("sphere", 8)
                except:
                    positions = method("sphere", 8, scale=2.0)
                
                if positions:
                    print(f"\\n🌐 POSICIONES SPHERE ({{len(positions)}} fuentes):")
                    for i, pos in enumerate(list(positions)[:5]):
                        if isinstance(pos, tuple) and len(pos) >= 3:
                            print(f"   Fuente {{i}}: x={{pos[0]:.2f}}, y={{pos[1]:.2f}}, z={{pos[2]:.2f}}")
                        else:
                            print(f"   Fuente {{i}}: {{pos}}")
                    break
            except Exception as e:
                print(f"   Error con {{method_name}}: {{e}}")
                
except ImportError:
    print("❌ No se pudo importar FormationManager")

# Opción 2: Probar directamente el código sphere
print("\\n\\n📊 CÁLCULO DIRECTO DE SPHERE:")
import math

positions = []
source_count = 8
radius = 2.0
scale = 1.0
center = (0, 0, 0)

# Código sphere con espiral de Fibonacci
golden_ratio = (1 + math.sqrt(5)) / 2

for i in range(source_count):
    # Y va de 1 a -1
    y = 1 - (2 * i / (source_count - 1)) if source_count > 1 else 0
    
    # Radio en plano XZ
    radius_xz = math.sqrt(1 - y * y)
    
    # Ángulo usando proporción áurea
    theta = 2 * math.pi * i / golden_ratio
    
    # Coordenadas 3D
    x = radius_xz * math.cos(theta) * radius * scale
    y_scaled = y * radius * scale
    z = radius_xz * math.sin(theta) * radius * scale
    
    positions.append((center[0] + x, center[1] + y_scaled, center[2] + z))
    
    print(f"Fuente {{i}}: x={{x:.2f}}, y={{y_scaled:.2f}}, z={{z:.2f}}")

# Verificar que es 3D
y_values = [pos[1] for pos in positions]
z_values = [pos[2] for pos in positions]

print(f"\\n✅ Rango Y: {{min(y_values):.2f}} a {{max(y_values):.2f}}")
print(f"✅ Rango Z: {{min(z_values):.2f}} a {{max(z_values):.2f}}")

if max(y_values) - min(y_values) > 0.1:
    print("\\n✅ ES 3D! Tiene variación en altura (Y)")
else:
    print("\\n❌ ES 2D! Sin variación en Y")
'''
            
            with open("test_sphere_correct.py", 'w') as f:
                f.write(test_content)
            
            print("✅ Test creado: test_sphere_correct.py")

if __name__ == "__main__":
    inspect_formation_manager()
    create_correct_test()
    
    print("\n\n🚀 EJECUTA:")
    print("python test_sphere_correct.py")