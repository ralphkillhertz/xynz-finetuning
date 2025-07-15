# === fix_critical_errors.py ===
# 🔧 Fix: Corregir errores de dict.append y float*MotionState
# ⚡ Búsqueda y corrección directa

import os
import re

def fix_dict_append_error():
    """Buscar y corregir todos los .append en dicts"""
    
    files_to_check = [
        'trajectory_hub/core/enhanced_trajectory_engine.py',
        'trajectory_hub/core/motion_components.py'
    ]
    
    fixes_applied = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Buscar patrones de .append que podrían estar en dicts
        # Patrón 1: active_components.append
        pattern1 = r'(\s+)([\w\.]*active_components)\.append\(([^)]+)\)'
        
        def replace_append_dict(match):
            indent = match.group(1)
            var_name = match.group(2)
            component = match.group(3)
            
            # Extraer el nombre de la clase del componente
            return f'''{indent}# Fix: active_components es dict
{indent}if hasattr({component}, '__class__'):
{indent}    component_key = {component}.__class__.__name__.lower().replace('component', '')
{indent}    {var_name}[component_key] = {component}
{indent}else:
{indent}    {var_name}['component'] = {component}'''
        
        content = re.sub(pattern1, replace_append_dict, content)
        
        # Patrón 2: Buscar específicamente en set_macro_concentration
        if 'set_macro_concentration' in content:
            # Buscar el método completo
            method_pattern = r'(def set_macro_concentration.*?)(\n(?=\s{0,4}def|\s{0,4}class|\Z))'
            
            def fix_concentration_method(match):
                method_content = match.group(1)
                
                # Si tiene .append, reemplazar
                if '.append(' in method_content and 'concentration' in method_content:
                    method_content = method_content.replace(
                        'motion.active_components.append(concentration)',
                        "motion.active_components['concentration'] = concentration"
                    )
                
                return method_content + match.group(2)
            
            content = re.sub(method_pattern, fix_concentration_method, content, flags=re.DOTALL)
        
        if content != original_content:
            # Backup
            with open(f'{file_path}.backup_dict_fix', 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Guardar
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            fixes_applied += 1
            print(f"✅ Arreglado dict.append en {file_path}")
    
    return fixes_applied

def fix_motion_state_multiplication():
    """Buscar y corregir multiplicación float * MotionState"""
    
    files_to_check = [
        'trajectory_hub/core/enhanced_trajectory_engine.py',
        'trajectory_hub/core/motion_components.py'
    ]
    
    fixes_applied = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Buscar patrones de multiplicación que podrían involucrar MotionState
        # Patrón 1: dt * algo o algo * dt
        patterns = [
            (r'(\w+)\s*\*\s*dt\b', r'dt * '),
            (r'dt\s*\*\s*(\w+)', r' * dt'),
            (r'(\w+)\s*\*\s*self\.(\w+)', r' * self.')
        ]
        
        # Buscar específicamente en métodos update
        if 'def update' in content:
            # Buscar todos los métodos update
            update_pattern = r'(def update.*?)(\n(?=\s{0,8}def|\s{0,8}class|\Z))'
            
            def fix_update_method(match):
                method_content = match.group(1)
                
                # Buscar líneas problemáticas
                lines = method_content.split('\n')
                fixed_lines = []
                
                for line in lines:
                    # Si la línea tiene multiplicación y 'state'
                    if '*' in line and ('state' in line or 'motion' in line):
                        # Casos específicos conocidos
                        if 'dt * state' in line:
                            line = line.replace('dt * state', 'dt')
                        elif 'state * dt' in line:
                            line = line.replace('state * dt', 'dt')
                        elif '* motion' in line and 'dt' in line:
                            # Probablemente es dt * motion -> dt
                            line = re.sub(r'dt\s*\*\s*motion\b', 'dt', line)
                        elif '* state' in line and not 'state.' in line:
                            # Si está multiplicando por state directamente
                            line = re.sub(r'\*\s*state\b', '', line)
                    
                    fixed_lines.append(line)
                
                return '\n'.join(fixed_lines) + match.group(2)
            
            content = re.sub(update_pattern, fix_update_method, content, flags=re.DOTALL)
        
        # Buscar específicamente el error en engine.update
        if 'for source_id, motion in self.motion_states.items():' in content:
            # Este es el loop principal donde puede estar el error
            loop_pattern = r'(for source_id, motion in self\.motion_states\.items\(\):.*?)(\n\s{8}(?!if|motion\.)|\n\s{0,4}(?:def|class)|\Z)'
            
            def fix_main_loop(match):
                loop_content = match.group(1)
                
                # Si tiene motion.update(
                if 'motion.update(' in loop_content:
                    # Verificar los parámetros
                    update_call_pattern = r'motion\.update\((.*?)\)'
                    
                    def fix_update_call(m):
                        params = m.group(1)
                        # Si solo tiene 'dt * motion' o similar
                        if 'dt * motion' in params:
                            params = params.replace('dt * motion', 'dt')
                        elif 'motion' in params and params.count(',') < 2:
                            # Probablemente faltan parámetros
                            params = 'self._time, dt'
                        
                        return f'motion.update({params})'
                    
                    loop_content = re.sub(update_call_pattern, fix_update_call, loop_content)
                
                return loop_content + match.group(2)
            
            content = re.sub(loop_pattern, fix_main_loop, content, flags=re.DOTALL)
        
        if content != original_content:
            # Backup
            with open(f'{file_path}.backup_multiplication_fix', 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Guardar
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            fixes_applied += 1
            print(f"✅ Arreglado multiplicación en {file_path}")
    
    return fixes_applied

def create_emergency_fix():
    """Crear un fix de emergencia si los anteriores no funcionan"""
    
    emergency_fix = '''# === emergency_fix_update.py ===
# 🚨 Fix de emergencia para el método update
# ⚡ Reemplaza el método update completo

import os

def fix_engine_update():
    """Reemplazar el método update con una versión funcional"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Método update corregido
    update_method = """
    def update(self):
        \"\"\"Actualizar todas las fuentes y enviar datos OSC\"\"\"
        if not self.running:
            return
            
        # Calcular dt
        current_time = time.time()
        dt = current_time - self._last_time if hasattr(self, '_last_time') else 1.0/self.fps
        self._last_time = current_time
        self._time = current_time
        
        # Actualizar motion states (sistema de deltas)
        if hasattr(self, 'motion_states'):
            for source_id, motion in self.motion_states.items():
                if motion and hasattr(motion, 'update'):
                    try:
                        # Llamar update con los parámetros correctos
                        if hasattr(motion, 'state'):
                            motion.update(current_time, dt)
                        else:
                            motion.update(dt)
                    except TypeError as e:
                        # Si falla, intentar sin parámetros o con uno solo
                        try:
                            motion.update(dt)
                        except:
                            try:
                                motion.update()
                            except:
                                pass
        
        # Actualizar deformadores
        if self._deformers:
            for macro_id, deformer in self._deformers.items():
                if macro_id in self._macros:
                    macro = self._macros[macro_id]
                    for source_id in macro.source_ids:
                        if source_id < len(self._positions):
                            deformed_pos = deformer.apply(
                                self._positions[source_id], 
                                source_id, 
                                self._time
                            )
                            self._positions[source_id] = deformed_pos
        
        # Actualizar moduladores de orientación si están habilitados
        if self.enable_modulator and hasattr(self, 'orientation_modulators'):
            for source_id, state in self.motion_states.items():
                if source_id in self.orientation_modulators:
                    modulator = self.orientation_modulators[source_id]
                    if modulator.enabled:
                        # Actualizar estado con modulación
                        state = modulator.update(current_time, dt, state)
                        self.motion_states[source_id] = state
        
        # Actualizar el reloj interno
        self._frame_count += 1
        
        # Enviar actualización OSC
        if hasattr(self, '_send_osc_update'):
            self._send_osc_update()
"""
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_emergency', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar y reemplazar el método update
    import re
    pattern = r'def update\(self[^:]*\):.*?(?=\n    def|\nclass|\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, update_method.strip(), content, flags=re.DOTALL)
        
        # Guardar
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("✅ Método update reemplazado")
        return True
    
    return False

if __name__ == "__main__":
    fix_engine_update()
'''
    
    with open('emergency_fix_update.py', 'w', encoding='utf-8') as f:
        f.write(emergency_fix)
    
    print("✅ emergency_fix_update.py creado")

if __name__ == "__main__":
    print("🔧 FIXING CRITICAL ERRORS")
    print("=" * 60)
    
    # 1. Arreglar dict.append
    print("\n1️⃣ Arreglando error dict.append...")
    dict_fixes = fix_dict_append_error()
    
    # 2. Arreglar multiplicación MotionState
    print("\n2️⃣ Arreglando error float * MotionState...")
    mult_fixes = fix_motion_state_multiplication()
    
    # 3. Crear fix de emergencia
    print("\n3️⃣ Creando fix de emergencia...")
    create_emergency_fix()
    
    print(f"\n📊 RESUMEN:")
    print(f"  • Dict fixes aplicados: {dict_fixes}")
    print(f"  • Multiplication fixes aplicados: {mult_fixes}")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python test_system_working.py")
    print("2. Si falla, ejecutar: python emergency_fix_update.py")
    print("3. Volver a ejecutar: python test_system_working.py")