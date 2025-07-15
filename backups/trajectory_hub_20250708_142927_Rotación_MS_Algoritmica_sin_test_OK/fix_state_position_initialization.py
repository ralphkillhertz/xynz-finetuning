# === fix_state_position_initialization.py ===
# 🔧 Fix: Asegurar que state.position se inicialice correctamente
# ⚡ El problema es que state.position empieza en [0,0,0]

import os

def fix_state_initialization():
    """Asegurar que state.position se inicialice con la posición real"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando create_source...")
    
    # Buscar el método create_source
    import re
    pattern = r'(def create_source\s*\([^)]*\):.*?)(# Crear estado inicial\s*state = MotionState\(\).*?)(state\.position = .*?\n)'
    
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("✅ create_source encontrado")
        
        # Ver qué se asigna a state.position
        position_line = match.group(3)
        print(f"\n📋 Asignación actual: {position_line.strip()}")
        
        if 'self._positions[source_id].copy()' in position_line:
            print("✅ Ya está usando _positions[source_id]")
        else:
            print("❌ NO está usando la posición correcta")
    
    # Buscar específicamente la creación del estado
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'state = MotionState()' in line:
            print(f"\n📍 MotionState creado en línea {i+1}")
            # Ver las siguientes líneas
            print("\n📋 Inicialización de state:")
            for j in range(i, min(i+10, len(lines))):
                print(f"{j+1:4d}: {lines[j]}")
                if 'state.position' in lines[j]:
                    if 'zeros' in lines[j] or '0' in lines[j]:
                        print("      ^^^ PROBLEMA: Inicializado con zeros!")
                        
                        # Corregir
                        lines[j] = '        state.position = self._positions[source_id].copy()\n'
                        print("      ✅ CORREGIDO: Usando _positions[source_id]")
                        
                        # Guardar
                        import shutil
                        from datetime import datetime
                        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(file_path, backup_name)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(lines))
                        
                        return True
    
    # Si no se encontró el problema, buscar de otra forma
    print("\n🔍 Buscando inicialización alternativa...")
    
    # Buscar en SourceMotion.__init__
    file_path2 = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    with open(file_path2, 'r', encoding='utf-8') as f:
        content2 = f.read()
    
    # Buscar MotionState.__init__
    pattern2 = r'class MotionState.*?def __init__\(self\):(.*?)(?=\n    def|\nclass)'
    match2 = re.search(pattern2, content2, re.DOTALL)
    
    if match2:
        init_content = match2.group(1)
        print("\n📋 MotionState.__init__:")
        for line in init_content.split('\n')[:15]:
            print(f"  {line}")
            if 'self.position' in line and ('zeros' in line or '0.0' in line):
                print("  ^^^ PROBLEMA: position inicializada con zeros")
    
    return False

if __name__ == "__main__":
    print("🔧 Arreglando inicialización de state.position...")
    
    if fix_state_initialization():
        print("\n✅ Fix aplicado")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
    else:
        print("\n💡 El problema real es que MotionState.position")
        print("   se inicializa en [0,0,0] y nunca se actualiza correctamente")
        print("\n🔧 Solución: Asegurar que la sincronización funcione")