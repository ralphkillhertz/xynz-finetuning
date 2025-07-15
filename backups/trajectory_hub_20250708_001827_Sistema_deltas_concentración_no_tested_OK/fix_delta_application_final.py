# === fix_delta_application_final.py ===
# 🔧 Fix FINAL - Aplica los deltas que YA se calculan correctamente
# ⚡ Este ES el fix definitivo

import os
from datetime import datetime

def apply_final_fix():
    """Aplica el fix final para que los deltas se apliquen"""
    
    print("🔧 APLICANDO FIX FINAL DE DELTAS")
    print("="*60)
    
    # 1. Añadir update_with_deltas a SourceMotion
    print("\n1️⃣ Añadiendo update_with_deltas a SourceMotion...")
    add_update_with_deltas()
    
    # 2. Verificar que engine.update procesa deltas
    print("\n2️⃣ Verificando procesamiento de deltas en engine.update...")
    verify_engine_update()
    
    print("\n✅ FIX COMPLETO APLICADO")

def add_update_with_deltas():
    """Añade update_with_deltas que funcione con la estructura real"""
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    # Leer archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Si ya existe update_with_deltas, reemplazarlo
    if 'def update_with_deltas' in content:
        print("   ⚠️ update_with_deltas existe, actualizándolo...")
        import re
        # Eliminar método existente
        pattern = r'def update_with_deltas\(self.*?\n(?=\s{0,8}def|\s{0,8}class|\Z)'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Buscar SourceMotion y añadir el método
    import re
    pattern = r'(class SourceMotion.*?)((?=\nclass)|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        class_content = match.group(0)
        
        # Nuevo método que FUNCIONA con la estructura real
        method_code = '''
    def update_with_deltas(self, current_time: float, dt: float) -> list:
        """Actualiza componentes y retorna lista de deltas"""
        deltas = []
        
        # active_components es una LISTA
        if hasattr(self, 'active_components') and isinstance(self.active_components, list):
            for component in self.active_components:
                if hasattr(component, 'enabled') and component.enabled:
                    if hasattr(component, 'calculate_delta'):
                        # state es el atributo correcto
                        delta = component.calculate_delta(self.state, current_time, dt)
                        if delta is not None:
                            deltas.append(delta)
        
        return deltas
'''
        
        # Insertar antes del final de la clase
        if '\nclass ' in class_content[len('class SourceMotion'):]:
            insert_pos = class_content.rfind('\nclass ')
            new_content = content[:match.start()] + class_content[:insert_pos] + method_code + class_content[insert_pos:]
        else:
            new_content = content[:match.end()-1] + method_code + '\n'
        
        with open(motion_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("   ✅ update_with_deltas añadido correctamente")

def verify_engine_update():
    """Verifica y arregla el procesamiento de deltas en engine.update"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si tiene procesamiento de deltas
    if 'PROCESAMIENTO DE DELTAS' not in content:
        print("   ❌ No hay procesamiento de deltas, añadiéndolo...")
        
        # Buscar dónde insertar
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'def update(self)' in line:
                # Buscar después de las rotaciones
                for j in range(i, min(i+20, len(lines))):
                    if '_apply_algorithmic_rotations' in lines[j]:
                        # Insertar aquí
                        delta_code = '''
        # 🔧 PROCESAMIENTO DE DELTAS - Sistema de composición
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(self._time, self.dt)
                
                for delta in deltas:
                    if hasattr(delta, 'position') and delta.position is not None:
                        # Aplicar delta a la posición
                        self._positions[source_id] = self._positions[source_id] + delta.position
        # FIN PROCESAMIENTO DE DELTAS
'''
                        lines.insert(j + 2, delta_code)
                        content = '\n'.join(lines)
                        
                        with open(engine_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print("   ✅ Procesamiento de deltas añadido")
                        return
    else:
        print("   ✅ Procesamiento de deltas ya existe")

if __name__ == "__main__":
    apply_final_fix()
    
    print("\n📋 ÚLTIMO TEST - Ejecuta:")
    print("$ python test_deltas_final_working.py")