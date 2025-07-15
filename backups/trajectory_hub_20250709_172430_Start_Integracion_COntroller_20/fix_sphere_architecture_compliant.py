
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

print("\n⚠️ IMPORTANTE:")
print("Este fix requiere cambios estructurales")
print("Engine NO debe calcular formaciones")
print("\nOpciones:")
print("1. Refactorizar para usar CommandProcessor correctamente")
print("2. Hacer que Engine use FormationManager (temporal)")
print("\nPor ahora, opción 2 (menos invasiva)...")

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
            print(f"\n✅ create_macro en línea {i+1}")
            
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
                            "from trajectory_hub.control.managers.formation_manager import FormationManager\n")
                        import_added = True
                        print("   ✅ Import FormationManager añadido")
                        break
                
                # Buscar dónde se calculan formaciones
                for j in range(i, min(len(lines), i+200)):
                    if 'if formation ==' in lines[j] or 'elif formation ==' in lines[j]:
                        # Reemplazar toda la lógica de formaciones
                        print(f"\n   📍 Lógica de formaciones en línea {j+1}")
                        
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
    
    print("\n✅ Engine actualizado para usar FormationManager")

print("\n⚠️ NOTA ARQUITECTÓNICA:")
print("Este es un fix temporal. La solución correcta es:")
print("1. Engine.create_macro debe recibir positions, no formation")
print("2. CommandProcessor debe calcular positions usando FormationManager")
print("3. Engine solo debe aplicar las positions recibidas")
