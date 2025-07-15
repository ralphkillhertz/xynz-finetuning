import os
import re
from datetime import datetime
import shutil

def fix_sphere_flow():
    """Verificar y arreglar el flujo completo de sphere"""
    print("🔧 ARREGLANDO FLUJO DE SPHERE 3D")
    print("="*60)
    
    # 1. Verificar FormationManager
    check_formation_manager()
    
    # 2. Verificar CommandProcessor
    check_command_processor()
    
    # 3. Verificar que las posiciones Z se usen
    check_z_coordinates()

def check_formation_manager():
    """Verificar el código sphere en FormationManager"""
    print("\n1️⃣ VERIFICANDO FormationManager...")
    
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    with open(fm_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar el código de sphere
    sphere_start = None
    for i, line in enumerate(lines):
        if 'formation == "sphere"' in line:
            sphere_start = i
            break
    
    if sphere_start:
        print(f"✅ Código sphere encontrado en línea {sphere_start+1}")
        
        # Verificar que calcule Z correctamente
        sphere_code = '\n'.join(lines[sphere_start:sphere_start+30])
        
        if 'radius * scale' in sphere_code:
            print("✅ Usa scale en las 3 coordenadas")
        else:
            print("⚠️ Posible problema con scale")
        
        # Verificar que devuelva tuplas de 3 elementos
        if 'positions.append((' in sphere_code:
            # Contar comas en la línea append
            append_line = None
            for j in range(sphere_start, min(len(lines), sphere_start+30)):
                if 'positions.append' in lines[j]:
                    append_line = lines[j:j+5]  # Puede ser multilínea
                    break
            
            if append_line:
                append_text = ''.join(append_line) if isinstance(append_line, list) else append_line
                comma_count = append_text.count(',')
                
                if comma_count >= 2:
                    print("✅ Devuelve tuplas (x, y, z)")
                else:
                    print("❌ PROBLEMA: No devuelve 3 coordenadas")
                    fix_formation_manager_3d(fm_file, sphere_start)

def fix_formation_manager_3d(fm_file, sphere_start):
    """Arreglar FormationManager para que devuelva 3D real"""
    print("\n🔧 Arreglando FormationManager para 3D...")
    
    # Backup
    backup = f"{fm_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(fm_file, backup)
    
    with open(fm_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar el bloque sphere completo
    indent = len(lines[sphere_start]) - len(lines[sphere_start].lstrip())
    
    # Reemplazar con implementación 3D correcta
    new_sphere_code = f'''
{' ' * indent}if formation == "sphere":
{' ' * (indent+4)}# Distribución uniforme en esfera 3D usando espiral de Fibonacci
{' ' * (indent+4)}import math
{' ' * (indent+4)}golden_ratio = (1 + math.sqrt(5)) / 2
{' ' * (indent+4)}
{' ' * (indent+4)}for i in range(source_count):
{' ' * (indent+8)}# Y va de 1 a -1 (polo norte a polo sur)
{' ' * (indent+8)}y = 1 - (2 * i / (source_count - 1)) if source_count > 1 else 0
{' ' * (indent+8)}
{' ' * (indent+8)}# Radio en el plano XZ para esta altura
{' ' * (indent+8)}radius_xz = math.sqrt(1 - y * y)
{' ' * (indent+8)}
{' ' * (indent+8)}# Ángulo usando proporción áurea para distribución uniforme
{' ' * (indent+8)}theta = 2 * math.pi * i / golden_ratio
{' ' * (indent+8)}
{' ' * (indent+8)}# Coordenadas 3D finales
{' ' * (indent+8)}x = radius_xz * math.cos(theta) * radius * scale
{' ' * (indent+8)}y_scaled = y * radius * scale  # Altura 3D!
{' ' * (indent+8)}z = radius_xz * math.sin(theta) * radius * scale
{' ' * (indent+8)}
{' ' * (indent+8)}positions.append((center[0] + x, center[1] + y_scaled, center[2] + z))
{' ' * (indent+8)}
{' ' * (indent+8)}# Debug primeras posiciones
{' ' * (indent+8)}if i < 3:
{' ' * (indent+12)}print(f"Sphere pos {{i}}: x={{x:.2f}}, y={{y_scaled:.2f}}, z={{z:.2f}}")
'''
    
    # Encontrar el final del bloque sphere actual
    end_line = sphere_start + 1
    for i in range(sphere_start + 1, len(lines)):
        if lines[i].strip() and not lines[i].startswith(' ' * (indent + 4)):
            end_line = i
            break
    
    # Reemplazar
    lines[sphere_start:end_line] = [new_sphere_code]
    
    with open(fm_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ FormationManager actualizado con sphere 3D real")

def check_command_processor():
    """Verificar que CommandProcessor use FormationManager"""
    print("\n2️⃣ VERIFICANDO CommandProcessor...")
    
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    with open(cp_file, 'r') as f:
        content = f.read()
    
    # Buscar handle_create_macro
    if 'formation_manager' in content.lower():
        print("✅ CommandProcessor usa FormationManager")
        
        # Verificar que pase la formación correctamente
        if 'get_formation' in content:
            print("✅ Llama a get_formation")
        else:
            print("⚠️ Verificar que pase formation='sphere' correctamente")
    else:
        print("❌ CommandProcessor NO usa FormationManager")

def check_z_coordinates():
    """Verificar que se usen las coordenadas Z"""
    print("\n3️⃣ VERIFICANDO USO DE COORDENADA Z...")
    
    # Buscar en engine
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Buscar si se usan posiciones 3D
        if 'position[2]' in content or 'z=' in content or ', z)' in content:
            print("✅ Engine maneja coordenada Z")
        else:
            print("⚠️ Engine podría no estar usando Z")
            
            # Buscar create_macro
            if 'def create_macro' in content:
                print("\n🔍 Verificando create_macro en engine...")
                
                # Ver si solo usa x,y o x,y,z
                create_match = re.search(r'def create_macro.*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
                if create_match:
                    method = create_match.group(0)
                    
                    if 'add_target' in method:
                        # Buscar cómo llama a add_target
                        add_target_calls = re.findall(r'add_target\([^)]+\)', method)
                        for call in add_target_calls[:2]:
                            print(f"   add_target: {call}")
                        
                        if 'position[0], position[1]' in method and 'position[2]' not in method:
                            print("   ❌ PROBLEMA: Solo usa X,Y, ignora Z!")
                            print("   → Esto causa que sphere se vea como círculo")

def generate_test_script():
    """Generar script de prueba"""
    test_script = '''
# === test_sphere_3d.py ===
from trajectory_hub.control.managers.formation_manager import FormationManager

# Test directo
fm = FormationManager()
positions = fm.get_formation("sphere", 8, scale=2.0)

print("\\n🌐 POSICIONES SPHERE (8 fuentes):")
for i, pos in enumerate(positions):
    print(f"Fuente {i}: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")

# Verificar que es 3D
y_values = [pos[1] for pos in positions]
z_values = [pos[2] for pos in positions]

if len(set(y_values)) > 1:
    print("\\n✅ Variación en Y (altura) - ES 3D!")
else:
    print("\\n❌ Sin variación en Y - ES 2D!")

if len(set(z_values)) > 2:
    print("✅ Variación en Z (profundidad)")
else:
    print("❌ Sin variación en Z")
'''
    
    with open("test_sphere_3d.py", 'w') as f:
        f.write(test_script)
    
    print("\n📝 Script de prueba creado: test_sphere_3d.py")

if __name__ == "__main__":
    fix_sphere_flow()
    generate_test_script()
    
    print("\n\n🧪 PRÓXIMOS PASOS:")
    print("1. python test_sphere_3d.py  # Verificar que sphere es 3D")
    print("2. Ejecutar el programa y crear macro con sphere")
    print("3. Si sigue siendo 2D, el problema está en engine")