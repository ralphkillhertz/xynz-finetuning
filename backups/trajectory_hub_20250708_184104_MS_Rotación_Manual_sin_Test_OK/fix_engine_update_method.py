# fix_engine_update_method.py
# Encuentra y corrige el método update que se está ejecutando

def fix_engine_update():
    print("🔍 Buscando todos los métodos update() en EnhancedTrajectoryEngine...")
    
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar todos los métodos update
    update_methods = []
    for i, line in enumerate(lines):
        if 'def update(self' in line:
            update_methods.append(i)
            print(f"📌 Encontrado update() en línea {i + 1}: {line.strip()}")
    
    print(f"\n⚠️ Hay {len(update_methods)} métodos update() en el engine")
    
    # El problema es que el primer update() (línea 1231) llama a motion.update()
    # que retorna MotionState, no deltas. Necesitamos que use update_with_deltas
    
    print("\n🔧 Corrigiendo el método update() principal...")
    
    # Buscar el método update principal (debería ser el primero)
    if update_methods:
        main_update_line = update_methods[0]
        print(f"   Modificando update() en línea {main_update_line + 1}")
        
        # Buscar donde llama a motion.update()
        new_lines = []
        fixed = False
        
        for i, line in enumerate(lines):
            if i >= main_update_line and not fixed:
                # Buscar motion.update(
                if 'motion.update(' in line and 'update_with_deltas' not in line:
                    # Reemplazar con update_with_deltas
                    indent = len(line) - len(line.lstrip())
                    spaces = ' ' * indent
                    
                    print(f"   Reemplazando línea {i + 1}: {line.strip()}")
                    
                    # Comentar la línea original
                    new_lines.append(f"{spaces}# {line.strip()}  # REEMPLAZADO")
                    
                    # Agregar el nuevo código
                    new_lines.append(f"{spaces}# Usar update_with_deltas para obtener deltas")
                    new_lines.append(f"{spaces}if hasattr(motion, 'update_with_deltas'):")
                    new_lines.append(f"{spaces}    deltas = motion.update_with_deltas(current_time, dt)")
                    new_lines.append(f"{spaces}    # Aplicar deltas")
                    new_lines.append(f"{spaces}    for delta in deltas:")
                    new_lines.append(f"{spaces}        if delta.source_id in self._positions:")
                    new_lines.append(f"{spaces}            self._positions[delta.source_id] += delta.position")
                    new_lines.append(f"{spaces}            if delta.source_id in self.motion_states:")
                    new_lines.append(f"{spaces}                state = self.motion_states[delta.source_id].state")
                    new_lines.append(f"{spaces}                state.position[:] = self._positions[delta.source_id]")
                    new_lines.append(f"{spaces}                state.orientation += delta.orientation")
                    new_lines.append(f"{spaces}                if hasattr(delta, 'aperture') and delta.aperture is not None:")
                    new_lines.append(f"{spaces}                    state.aperture = delta.aperture")
                    
                    fixed = True
                    continue
            
            new_lines.append(line)
        
        if fixed:
            # Guardar el archivo corregido
            with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'w') as f:
                f.write('\n'.join(new_lines))
            
            print("\n✅ Método update() corregido para usar update_with_deltas")
        else:
            print("\n❌ No se encontró la línea motion.update() para corregir")
            
            # Buscar manualmente
            print("\n🔍 Buscando motion.update manualmente...")
            for i in range(main_update_line, min(main_update_line + 50, len(lines))):
                if 'motion' in lines[i] and 'update' in lines[i]:
                    print(f"   Línea {i + 1}: {lines[i].strip()}")

if __name__ == "__main__":
    fix_engine_update()
    
    print("\n📝 Próximo paso:")
    print("python debug_rotation_final.py")
    print("\nLas rotaciones deberían funcionar ahora con el sistema de deltas!")