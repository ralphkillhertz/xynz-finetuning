import os
import re

def trace_sphere_flow():
    """Trazar el flujo completo cuando se selecciona sphere"""
    print("🔍 TRAZANDO FLUJO COMPLETO DE SPHERE")
    print("="*60)
    
    # 1. CLI Interface - ¿Qué envía?
    print("\n1️⃣ CLI INTERFACE")
    cli_file = "trajectory_hub/control/interfaces/cli_interface.py"
    
    if os.path.exists(cli_file):
        with open(cli_file, 'r') as f:
            content = f.read()
        
        # Buscar get_choice_from_list con formations
        if 'get_choice_from_list' in content and 'formations' in content:
            print("✅ CLI muestra lista de formaciones")
            
            # Ver qué hace con la selección
            pattern = r'formation.*=.*get_choice_from_list.*\n.*'
            match = re.search(pattern, content)
            if match:
                print(f"   Código: {match.group(0).strip()}")
    
    # 2. Command Processor - ¿Qué recibe y envía?
    print("\n2️⃣ COMMAND PROCESSOR")
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar handle_create_macro
        for i, line in enumerate(lines):
            if 'def handle_create_macro' in line:
                print(f"✅ handle_create_macro en línea {i+1}")
                
                # Buscar cómo obtiene formation
                for j in range(i, min(len(lines), i+50)):
                    if 'formation' in lines[j] and ('=' in lines[j] or 'get' in lines[j]):
                        print(f"   L{j+1}: {lines[j].strip()}")
                    
                    # Ver si usa FormationManager
                    if 'formation_manager' in lines[j].lower():
                        print(f"   L{j+1}: USA FormationManager")
                        
                        # Ver qué parámetros pasa
                        if 'get_formation' in lines[j]:
                            # Extraer la llamada completa
                            call_start = j
                            call_lines = []
                            paren_count = 0
                            
                            for k in range(j, min(len(lines), j+10)):
                                call_lines.append(lines[k])
                                paren_count += lines[k].count('(') - lines[k].count(')')
                                if paren_count == 0 and '(' in lines[j]:
                                    break
                            
                            call_text = '\n'.join(call_lines)
                            print(f"\n   LLAMADA COMPLETA:")
                            print(f"   {call_text}")
                            
                            # Verificar parámetros
                            if 'formation_type' in call_text or 'formation' in call_text:
                                print("   ✅ Pasa tipo de formación")
                            else:
                                print("   ❌ NO pasa tipo de formación!")
                break
    
    # 3. Formation Manager - ¿Qué calcula?
    print("\n3️⃣ FORMATION MANAGER")
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if os.path.exists(fm_file):
        with open(fm_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar get_formation
        for i, line in enumerate(lines):
            if 'def get_formation' in line:
                print(f"✅ get_formation en línea {i+1}")
                
                # Ver parámetros
                print(f"   Definición: {line.strip()}")
                
                # Ver si maneja sphere
                method_end = i + 100  # Aproximado
                for j in range(i, min(len(lines), method_end)):
                    if 'if formation' in lines[j] and 'sphere' in lines[j]:
                        print(f"   L{j+1}: {lines[j].strip()} ✅")
                        break
                else:
                    # No encontró sphere directamente, buscar si hay un switch/dict
                    for j in range(i, min(len(lines), method_end)):
                        if 'sphere' in lines[j]:
                            print(f"   L{j+1}: {lines[j].strip()}")
                            break
                break
    
    # 4. Engine - ¿Qué hace con las posiciones?
    print("\n4️⃣ ENGINE")
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Buscar create_macro
        create_match = re.search(r'def create_macro.*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
        
        if create_match:
            method = create_match.group(0)
            
            # Ver si recibe positions o las calcula
            if 'positions' in method:
                print("✅ create_macro maneja positions")
                
                # Ver cómo usa positions
                if 'for i, position in enumerate(positions)' in method:
                    print("   ✅ Itera sobre positions")
                    
                    # Ver si usa las 3 coordenadas
                    add_target_pattern = r'add_target\([^)]+\)'
                    add_targets = re.findall(add_target_pattern, method)
                    
                    if add_targets:
                        print(f"\n   LLAMADAS add_target:")
                        for call in add_targets[:3]:
                            print(f"   {call}")
                            
                            # Verificar si usa 3 coordenadas
                            if 'position[2]' in call or ', position)' in call:
                                print("   ✅ Usa coordenada Z")
                            else:
                                print("   ❌ NO usa coordenada Z!")

def check_add_target_signature():
    """Verificar la firma de add_target"""
    print("\n\n5️⃣ VERIFICANDO FIRMA DE add_target")
    print("-" * 40)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar definición de add_target
        for i, line in enumerate(lines):
            if 'def add_target' in line:
                print(f"✅ add_target definido en línea {i+1}")
                print(f"   {line.strip()}")
                
                # Ver parámetros
                if ', z' in line or 'position' in line:
                    print("   ✅ Acepta coordenada Z")
                else:
                    print("   ❌ NO acepta coordenada Z!")
                    print("   → Este es el problema!")
                break

if __name__ == "__main__":
    trace_sphere_flow()
    check_add_target_signature()
    
    print("\n\n📊 RESUMEN DEL PROBLEMA:")
    print("Si sphere se ve como círculo 2D, es porque:")
    print("1. FormationManager calcula bien (x,y,z)")
    print("2. Pero algo en la cadena solo usa (x,y)")
    print("3. Probablemente engine.add_target() solo acepta x,y")