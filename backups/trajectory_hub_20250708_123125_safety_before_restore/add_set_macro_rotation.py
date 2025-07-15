# === add_set_macro_rotation.py ===
# 🔧 Fix: Añadir set_macro_rotation al engine definitivamente
# ⚡ Impacto: CRÍTICO - Habilita rotaciones

import os

def add_rotation_method():
    """Añade el método set_macro_rotation al engine"""
    
    print("🔧 AÑADIENDO set_macro_rotation DEFINITIVAMENTE\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar si realmente existe
    print("🔍 Buscando set_macro_rotation...")
    found = False
    for i, line in enumerate(lines):
        if 'def set_macro_rotation' in line:
            print(f"✅ Encontrado en línea {i+1}")
            found = True
            break
    
    if not found:
        print("❌ NO encontrado, añadiendo...")
        
        # Buscar dónde insertar (después de apply_formation)
        insert_line = None
        for i, line in enumerate(lines):
            if 'def apply_formation' in line:
                # Buscar el final de este método
                indent_count = 0
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' '):
                        break
                    if lines[j].strip().startswith('def '):
                        insert_line = j
                        break
                if not insert_line:
                    # Buscar el siguiente método
                    for j in range(i+1, len(lines)):
                        if lines[j].strip().startswith('def ') and not lines[j].strip().startswith('def _'):
                            insert_line = j
                            break
        
        if not insert_line:
            # Insertar al final de la clase
            for i in range(len(lines)-1, 0, -1):
                if lines[i].strip().startswith('def ') and lines[i].startswith('    '):
                    insert_line = i + 10  # Después del último método
                    break
        
        if insert_line and insert_line < len(lines):
            print(f"📍 Insertando en línea {insert_line}")
            
            # Método completo
            rotation_method = '''
    def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):
        """Configura rotación algorítmica para un macro alrededor de su centro"""
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return
            
        macro = self._macros[macro_name]
        
        # Calcular centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid < len(self._positions):
                positions.append(self._positions[sid])
        
        if not positions:
            print("❌ No hay posiciones válidas")
            return
            
        center = np.mean(positions, axis=0)
        
        # Importar MacroRotation
        from .motion_components import MacroRotation
        
        # Configurar rotación para cada fuente
        configured = 0
        for sid in macro.source_ids:
            if sid in self.motion_states:
                state = self.motion_states[sid]
                
                # Crear componente de rotación si no existe
                if not hasattr(state, 'active_components'):
                    state.active_components = {}
                    
                if 'macro_rotation' not in state.active_components:
                    rotation = MacroRotation()
                    state.active_components['macro_rotation'] = rotation
                else:
                    rotation = state.active_components['macro_rotation']
                
                # Configurar rotación
                rotation.update_center(center)
                rotation.set_rotation(speed_x, speed_y, speed_z)
                configured += 1
                
        print(f"✅ Rotación configurada para '{macro_name}'")
        print(f"   Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
        print(f"   Velocidades: X={speed_x}, Y={speed_y}, Z={speed_z} rad/s")
        print(f"   Fuentes: {configured}/{len(macro.source_ids)}")

'''
            # Insertar
            lines.insert(insert_line, rotation_method)
            print("✅ Método añadido")
        else:
            print("❌ No se encontró dónde insertar")
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo actualizado")
    
    # Verificar
    print("\n🔍 Verificando...")
    with open(engine_path, 'r') as f:
        content = f.read()
        if 'def set_macro_rotation' in content:
            print("✅ set_macro_rotation ahora existe")
        else:
            print("❌ set_macro_rotation todavía no existe")

if __name__ == "__main__":
    add_rotation_method()
    print("\n🚀 Ejecutando test...")
    os.system("python test_rotation_ms_final.py")