# === diagnose_manual_individual_deep.py ===
# 🔍 Diagnóstico específico: ManualIndividualRotation
# ⚡ Rastrear por qué motion.state se convierte en float

def analyze_manual_individual_rotation():
    """Analizar ManualIndividualRotation en motion_components.py"""
    print("🔍 DIAGNÓSTICO: ManualIndividualRotation")
    print("=" * 70)
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    # Buscar ManualIndividualRotation
    start = content.find("class ManualIndividualRotation")
    if start > 0:
        end = content.find("\nclass ", start + 1)
        if end == -1:
            end = len(content)
        
        class_code = content[start:end]
        
        # Buscar método update
        update_start = class_code.find("def update(")
        if update_start > 0:
            update_end = class_code.find("\n    def ", update_start + 1)
            if update_end == -1:
                update_end = len(class_code)
            
            update_method = class_code[update_start:update_end]
            
            print("📄 Método update() de ManualIndividualRotation:")
            print("-" * 70)
            print(update_method[:500])
            
            # Buscar return statements
            print("\n🔍 Buscando returns en update():")
            for line in update_method.split('\n'):
                if 'return' in line:
                    print(f"   >>> {line.strip()}")

def check_source_motion_update():
    """Verificar SourceMotion.update()"""
    print("\n\n📋 Verificando SourceMotion.update():")
    print("-" * 70)
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    # Buscar SourceMotion.update
    sm_start = content.find("class SourceMotion")
    if sm_start > 0:
        sm_end = content.find("\nclass ", sm_start + 1)
        if sm_end == -1:
            sm_end = len(content)
        
        sm_code = content[sm_start:sm_end]
        
        # Buscar update method
        update_idx = sm_code.find("def update(")
        if update_idx > 0:
            update_code = sm_code[update_idx:update_idx+800]
            print(update_code)
            
            # Buscar todos los returns
            print("\n🔍 Returns en SourceMotion.update():")
            for line in update_code.split('\n'):
                if 'return' in line:
                    print(f"   >>> {line.strip()}")

def trace_set_manual_individual():
    """Rastrear set_manual_individual_rotation"""
    print("\n\n🔍 Rastreando set_manual_individual_rotation:")
    print("-" * 70)
    
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar set_manual_individual_rotation
    for i, line in enumerate(lines):
        if 'def set_manual_individual_rotation' in line:
            print(f"\n📍 Encontrado en línea {i+1}")
            # Mostrar las siguientes 30 líneas
            for j in range(i, min(i+30, len(lines))):
                print(f"{j+1:4d}: {lines[j].rstrip()}")
            break

if __name__ == "__main__":
    analyze_manual_individual_rotation()
    check_source_motion_update()
    trace_set_manual_individual()