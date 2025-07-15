# === fix_delta_system_complete.py ===
# 🔧 Fix COMPLETO del sistema de deltas
# ⚡ Arregla TODOS los problemas encontrados

import os
from datetime import datetime

def fix_complete_delta_system():
    """Arregla TODO el sistema de deltas"""
    
    print("🔧 APLICANDO FIX COMPLETO")
    print("="*60)
    
    # 1. Arreglar SourceMotion para que tenga update_with_deltas
    print("\n1️⃣ Arreglando SourceMotion...")
    fix_source_motion()
    
    # 2. Arreglar engine.update para procesar deltas correctamente
    print("\n2️⃣ Arreglando engine.update...")
    fix_engine_update()
    
    # 3. Arreglar ConcentrationComponent para usar centro correcto
    print("\n3️⃣ Arreglando ConcentrationComponent...")
    fix_concentration_center()
    
    print("\n✅ SISTEMA COMPLETO ARREGLADO")

def fix_source_motion():
    """Añade update_with_deltas a SourceMotion"""
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar si ya existe update_with_deltas
    if 'def update_with_deltas' not in content:
        print("   ⚠️ update_with_deltas no existe, creándolo...")
        
        # Buscar clase SourceMotion y añadir el método
        import re
        pattern = r'(class SourceMotion.*?:.*?)((?=\nclass)|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            class_content = match.group(0)
            
            # Añadir método al final de la clase
            method_code = '''
    def update_with_deltas(self, current_time: float, dt: float) -> list:
        """Actualiza componentes y retorna lista de deltas"""
        deltas = []
        
        # active_components es una LISTA
        if hasattr(self, 'active_components') and isinstance(self.active_components, list):
            for component in self.active_components:
                if hasattr(component, 'enabled') and component.enabled:
                    if hasattr(component, 'calculate_delta'):
                        # Llamar calculate_delta
                        delta = component.calculate_delta(self.motion_state, current_time, dt)
                        if delta is not None and hasattr(delta, 'position'):
                            if not all(v == 0 for v in delta.position):
                                deltas.append(delta)
        
        return deltas
'''
            
            # Insertar antes del final de la clase o de la siguiente clase
            if 'class ' in class_content[len('class SourceMotion'):]:
                # Hay otra clase después
                insert_pos = class_content.rfind('\nclass ')
                new_content = content[:match.start()] + class_content[:insert_pos] + method_code + class_content[insert_pos:] + content[match.end():]
            else:
                # Es la última clase
                new_content = content[:match.end()] + method_code + content[match.end():]
            
            with open(motion_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("   ✅ update_with_deltas añadido")

def fix_engine_update():
    """Arregla el procesamiento de deltas en engine.update"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya tiene procesamiento de deltas correcto
    if 'PROCESAMIENTO DE DELTAS' in content and 'active_components' not in content.split('PROCESAMIENTO DE DELTAS')[1].split('FIN PROCESAMIENTO')[0]:
        print("   ✅ Procesamiento de deltas ya existe")
        return
    
    # Si tiene el código antiguo (con dict), reemplazarlo
    if 'PROCESAMIENTO DE DELTAS' in content:
        print("   ⚠️ Actualizando código de deltas...")
        import re
        pattern = r'# 🔧 PROCESAMIENTO DE DELTAS.*?# FIN PROCESAMIENTO DE DELTAS\n'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Insertar código correcto
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '_apply_algorithmic_rotations' in line:
            # Insertar después
            indent = '        '
            delta_code = f'''
{indent}# 🔧 PROCESAMIENTO DE DELTAS - Sistema de composición
{indent}if hasattr(self, 'motion_states'):
{indent}    dt = self.dt
{indent}    current_time = self._time
{indent}    
{indent}    for source_id, motion in self.motion_states.items():
{indent}        if hasattr(motion, 'update_with_deltas'):
{indent}            # Obtener deltas
{indent}            deltas = motion.update_with_deltas(current_time, dt)
{indent}            
{indent}            # Aplicar cada delta
{indent}            for delta in deltas:
{indent}                if hasattr(delta, 'position') and delta.position is not None:
{indent}                    self._positions[source_id] += delta.position
{indent}# FIN PROCESAMIENTO DE DELTAS
'''
            lines.insert(i + 2, delta_code)
            break
    
    content = '\n'.join(lines)
    
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ Procesamiento de deltas actualizado")

def fix_concentration_center():
    """Arregla el centro de ConcentrationComponent"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar set_macro_concentration
    import re
    pattern = r'(def set_macro_concentration.*?return True)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        method_content = match.group(0)
        
        # Reemplazar centro=[0. 0. 0.] por cálculo del centro real
        if 'centro=[0. 0. 0.]' in method_content:
            print("   ⚠️ Arreglando centro de concentración...")
            
            # Añadir cálculo del centro antes del loop
            new_method = method_content.replace(
                'for sid in source_ids:',
                '''# Calcular centro real del macro
        positions = [self._positions[sid] for sid in source_ids]
        centro = np.mean(positions, axis=0)
        
        for sid in source_ids:'''
            )
            
            # Reemplazar [0. 0. 0.] por centro
            new_method = new_method.replace('centro=[0. 0. 0.]', 'centro=centro')
            
            content = content.replace(method_content, new_method)
            
            with open(engine_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   ✅ Centro de concentración arreglado")

if __name__ == "__main__":
    fix_complete_delta_system()
    
    print("\n📋 Ahora ejecuta:")
    print("$ python test_final_deltas.py")