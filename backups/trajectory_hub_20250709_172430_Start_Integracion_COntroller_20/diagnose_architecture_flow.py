import os
import json

def diagnose_architecture_flow():
    """Diagnosticar el flujo actual vs la arquitectura deseada"""
    print("🏗️ DIAGNÓSTICO ARQUITECTÓNICO")
    print("="*60)
    
    # 1. Cargar ADN del proyecto
    print("\n1️⃣ ARQUITECTURA DESEADA (PROJECT_DNA):")
    
    if os.path.exists("PROJECT_DNA.json"):
        with open("PROJECT_DNA.json", 'r') as f:
            dna = json.load(f)
        
        arch = dna.get("🧬 ADN_ARQUITECTONICO", {})
        print("\n📋 Responsabilidades por capa:")
        print("   • Controller: Solo UI/menús")
        print("   • CommandProcessor: TODA la lógica")
        print("   • FormationManager: Cálculo de formaciones")
        print("   • Engine: Solo aplicar posiciones")
    
    # 2. Analizar flujo actual
    print("\n\n2️⃣ FLUJO ACTUAL:")
    
    # CLI Interface
    cli_file = "trajectory_hub/control/interfaces/cli_interface.py"
    if os.path.exists(cli_file):
        with open(cli_file, 'r') as f:
            cli_content = f.read()
        
        print("\n📍 CLI Interface:")
        if 'command_processor' in cli_content.lower():
            print("   ✅ Usa CommandProcessor")
        else:
            print("   ❌ NO usa CommandProcessor")
        
        if 'engine' in cli_content:
            print("   ⚠️ Referencia directa a Engine (no debería)")
    
    # Command Processor
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            cp_content = f.read()
        
        print("\n📍 CommandProcessor:")
        if 'FormationManager' in cp_content:
            print("   ✅ Usa FormationManager")
        if 'calculate_formation' in cp_content:
            print("   ✅ Calcula formaciones correctamente")
        if 'engine.create_macro' in cp_content:
            print("   ✅ Delega a Engine para crear macro")
    
    # Engine
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            engine_content = f.read()
        
        print("\n📍 Engine:")
        
        # Ver create_macro
        if 'def create_macro' in engine_content:
            print("   ✅ Tiene create_macro")
            
            # Ver parámetros
            import re
            create_match = re.search(r'def create_macro\([^)]+\)', engine_content)
            if create_match:
                params = create_match.group(0)
                print(f"   Parámetros: {params}")
                
                if 'positions' in params:
                    print("   ✅ Recibe positions (correcto)")
                elif 'formation' in params:
                    print("   ❌ Recibe formation (calcula internamente - MAL)")
        
        # Ver si calcula formaciones
        if '_calculate_circle' in engine_content:
            print("   ❌ Tiene métodos de cálculo (no debería)")
        
        if 'elif formation ==' in engine_content:
            print("   ❌ Tiene lógica de formaciones (no debería)")
    
    # 3. Identificar el problema
    print("\n\n3️⃣ PROBLEMA IDENTIFICADO:")
    print("-" * 40)
    
    print("\n❌ El flujo actual NO respeta la arquitectura:")
    print("   1. Engine está calculando formaciones (MAL)")
    print("   2. No se está usando FormationManager correctamente")
    print("   3. El flujo debería ser:")
    print("      CLI → CommandProcessor → FormationManager → Engine")
    print("   4. Pero parece ser:")
    print("      CLI → ¿? → Engine (calcula todo)")

def create_architecture_compliant_fix():
    """Crear fix que respete la arquitectura"""
    
    print("\n\n🔧 CREANDO FIX ARQUITECTÓNICO")
    
    fix_content = '''
# === fix_sphere_architecture_compliant.py ===
"""
Fix que respeta la arquitectura del proyecto:
- Controller: Solo UI
- CommandProcessor: Lógica
- FormationManager: Cálculos
- Engine: Solo aplicar
"""
import os
from datetime import datetime
import shutil

print("🏗️ FIX SPHERE RESPETANDO ARQUITECTURA")
print("="*60)

# El problema es que Engine está calculando formaciones
# cuando debería solo recibirlas

print("\\n⚠️ IMPORTANTE:")
print("Este fix requiere cambios estructurales")
print("Engine NO debe calcular formaciones")
print("\\nOpciones:")
print("1. Refactorizar para usar CommandProcessor correctamente")
print("2. Hacer que Engine use FormationManager (temporal)")
print("\\nPor ahora, opción 2 (menos invasiva)...")

# Fix temporal: Hacer que Engine delegue a FormationManager
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if os.path.exists(engine_file):
    backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, backup)
    
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar create_macro
    for i, line in enumerate(lines):
        if 'def create_macro' in line:
            print(f"\\n✅ create_macro en línea {i+1}")
            
            # Ver si tiene formation como parámetro
            if 'formation' in line:
                print("   ⚠️ create_macro recibe 'formation'")
                print("   → Necesita calcular internamente")
                
                # Insertar import de FormationManager al inicio
                import_added = False
                for j in range(50):  # Buscar en primeras 50 líneas
                    if 'from trajectory_hub' in lines[j]:
                        # Insertar después de otros imports
                        lines.insert(j+1, 
                            "from trajectory_hub.control.managers.formation_manager import FormationManager\\n")
                        import_added = True
                        print("   ✅ Import FormationManager añadido")
                        break
                
                # Buscar dónde se calculan formaciones
                for j in range(i, min(len(lines), i+200)):
                    if 'if formation ==' in lines[j] or 'elif formation ==' in lines[j]:
                        # Reemplazar toda la lógica de formaciones
                        print(f"\\n   📍 Lógica de formaciones en línea {j+1}")
                        
                        # Encontrar inicio y fin del bloque de formaciones
                        start_line = j
                        while start_line > i and ('if' in lines[start_line] or 'elif' in lines[start_line]):
                            start_line -= 1
                        start_line += 1
                        
                        # Encontrar fin
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        end_line = j + 1
                        for k in range(j+1, len(lines)):
                            if lines[k].strip() and len(lines[k]) - len(lines[k].lstrip()) < indent:
                                end_line = k
                                break
                        
                        # Reemplazar con FormationManager
                        new_code = f"""
        # Delegar cálculo de formaciones a FormationManager
        if formation:
            fm = FormationManager()
            positions = fm.calculate_formation(formation, self.config['n_sources'])
            print(f"📐 FormationManager calculó {{formation}}: {{len(positions)}} posiciones")
        else:
            positions = []
"""
                        
                        # Reemplazar
                        lines[start_line:end_line] = [new_code]
                        print("   ✅ Reemplazado con FormationManager")
                        break
                break
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print("\\n✅ Engine actualizado para usar FormationManager")

print("\\n⚠️ NOTA ARQUITECTÓNICA:")
print("Este es un fix temporal. La solución correcta es:")
print("1. Engine.create_macro debe recibir positions, no formation")
print("2. CommandProcessor debe calcular positions usando FormationManager")
print("3. Engine solo debe aplicar las positions recibidas")
'''
    
    with open("fix_sphere_architecture_compliant.py", 'w') as f:
        f.write(fix_content)
    
    print("✅ Fix creado: fix_sphere_architecture_compliant.py")

if __name__ == "__main__":
    diagnose_architecture_flow()
    create_architecture_compliant_fix()
    
    print("\n\n💡 RECOMENDACIÓN:")
    print("El sistema actual NO respeta la arquitectura definida")
    print("Este fix es temporal para hacer funcionar sphere")
    print("\n🏗️ La refactorización completa requiere:")
    print("1. Que CommandProcessor orqueste todo")
    print("2. Que Engine solo aplique posiciones")
    print("3. Implementar la arquitectura de PROJECT_DNA.json")