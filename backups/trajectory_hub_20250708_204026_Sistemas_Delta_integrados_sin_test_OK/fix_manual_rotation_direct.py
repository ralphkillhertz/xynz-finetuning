# === fix_manual_rotation_direct.py ===
# 🔧 Fix directo y específico
# ⚡ Cambiar líneas problemáticas directamente

def fix_manual_rotation_direct():
    """Fix directo de los problemas específicos"""
    
    print("🔧 FIX DIRECTO: ManualIndividualRotation")
    print("=" * 60)
    
    import os
    
    # 1. Arreglar en enhanced_trajectory_engine.py
    engine_file = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("\n1️⃣ Arreglando enhanced_trajectory_engine.py...")
    
    with open(engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cambiar center=center por center=None en la línea problemática
    old_line = "rotation = ManualIndividualRotation(center=center)"
    new_line = "rotation = ManualIndividualRotation()"  # Sin center, usará [0,0,0] por defecto
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("   ✅ Cambiado: ManualIndividualRotation() sin center")
    
    # Buscar y comentar la línea que calcula current_yaw con arctan2
    import re
    pattern = r'rotation\.current_yaw = np\.arctan2\([^)]+\)'
    matches = re.findall(pattern, content)
    if matches:
        for match in matches:
            content = content.replace(match, 'rotation.current_yaw = 0.0  # Empezar desde 0')
            print(f"   ✅ Cambiado: current_yaw = 0.0")
    
    # Guardar
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 2. Verificar en motion_components.py
    components_file = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("\n2️⃣ Verificando motion_components.py...")
    
    with open(components_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar ManualIndividualRotation y el método calculate_delta
    in_class = False
    in_calculate_delta = False
    changes = []
    
    for i, line in enumerate(lines):
        if 'class ManualIndividualRotation' in line:
            in_class = True
            
        if in_class and 'def calculate_delta' in line:
            in_calculate_delta = True
            print(f"   Encontrado calculate_delta en línea {i+1}")
            
        if in_calculate_delta and 'relative_pos = state.position - self.center' in line:
            print(f"   Línea {i+1}: {line.strip()}")
            # Esta línea está bien
            
        if in_calculate_delta and 'if np.linalg.norm(relative_pos[:2]) < 0.001:' in line:
            # Verificar las siguientes líneas
            if i+1 < len(lines) and 'return None' in lines[i+1]:
                print(f"   ❌ Encontrado: return None cuando posición cerca del centro")
                # Cambiar return None por return delta vacío
                lines[i+1] = lines[i+1].replace('return None', 
                    'return MotionDelta(source_id=state.source_id, position=np.zeros(3))')
                changes.append(f"Línea {i+2}: Cambiado return None por delta vacío")
    
    if changes:
        with open(components_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("\n   Cambios aplicados:")
        for change in changes:
            print(f"   - {change}")
    
    # 3. Añadir sincronización en engine.update()
    print("\n3️⃣ Añadiendo sincronización state.position...")
    
    with open(engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update
    if 'def update(self):' in content:
        # Buscar donde procesa motion states
        pattern = r'for source_id, motion in self\.motion_states\.items\(\):'
        match = re.search(pattern, content)
        
        if match:
            # Insertar sincronización justo después del for
            insertion_point = match.end()
            # Encontrar el final de la línea
            newline_pos = content.find('\n', insertion_point)
            if newline_pos != -1:
                # Detectar indentación
                next_line_start = newline_pos + 1
                indent = ''
                while next_line_start < len(content) and content[next_line_start] in ' \t':
                    indent += content[next_line_start]
                    next_line_start += 1
                
                # Insertar sincronización
                sync_code = f"\n{indent}# Sincronizar state con position\n"
                sync_code += f"{indent}if source_id in self._active_sources:\n"
                sync_code += f"{indent}    motion.state.position = self._positions[source_id].copy()\n"
                
                content = content[:newline_pos+1] + sync_code + content[newline_pos+1:]
                print("   ✅ Añadida sincronización state.position")
    
    # Guardar
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Fixes aplicados")
    
    # 4. Test inmediato
    print("\n4️⃣ Test inmediato:")
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        from trajectory_hub.core.motion_components import ManualIndividualRotation
        
        # Test del componente solo
        comp = ManualIndividualRotation()
        print(f"   Center por defecto: {comp.center}")
        print(f"   Current yaw inicial: {comp.current_yaw}")
        
        # Test con engine
        engine = EnhancedTrajectoryEngine(max_sources=1, enable_modulator=False)
        sid = 0
        engine.create_source(sid)
        engine._positions[sid] = [3.0, 0.0, 0.0]
        
        result = engine.set_manual_individual_rotation(sid, yaw=1.57)
        print(f"   Configuración: {result}")
        
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"   Center del componente: {comp.center}")
                print(f"   Current yaw: {comp.current_yaw}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📋 Ejecuta ahora: python test_manual_is_fixed.py")

if __name__ == "__main__":
    fix_manual_rotation_direct()