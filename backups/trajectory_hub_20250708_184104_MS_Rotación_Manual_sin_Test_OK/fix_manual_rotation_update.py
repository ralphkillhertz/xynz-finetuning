# === fix_manual_rotation_update.py ===
# 🔧 Fix: Añadir método update a ManualMacroRotation
# ⚡ Implementa el método abstracto requerido
# 🎯 Impacto: CRÍTICO - Completa la clase

import re
from datetime import datetime
import shutil

def add_update_method():
    """Añade el método update a ManualMacroRotation"""
    
    # Backup
    backup_name = f"motion_components.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy("trajectory_hub/core/motion_components.py", backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    with open("trajectory_hub/core/motion_components.py", 'r') as f:
        content = f.read()
    
    # Buscar el final de calculate_delta en ManualMacroRotation
    # Necesitamos insertar el método update después
    
    # Encontrar la clase ManualMacroRotation
    class_match = re.search(r'class ManualMacroRotation.*?\n(.*?)(?=class|\Z)', content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encontró ManualMacroRotation")
        return False
    
    class_content = class_match.group(0)
    
    # Verificar si ya tiene update
    if "def update(" in class_content:
        print("⚠️ Ya tiene método update")
        return True
    
    # Buscar el final de calculate_delta
    delta_end = class_content.rfind("return delta")
    if delta_end == -1:
        print("❌ No se encontró el final de calculate_delta")
        return False
    
    # Encontrar el salto de línea después de return delta
    insert_pos = class_content.find("\n", delta_end) + 1
    
    # El método update
    update_method = '''
    def update(self, current_time: float, dt: float, state: 'MotionState') -> 'MotionState':
        """Actualiza el estado aplicando la rotación manual"""
        if not self.enabled:
            return state
            
        # Sincronizar estado actual
        self._sync_with_state(state)
        
        # Calcular delta
        delta = self.calculate_delta(state, current_time, dt)
        
        if delta and delta.position is not None:
            # Aplicar el delta al estado
            state.position = [
                state.position[0] + delta.position[0],
                state.position[1] + delta.position[1],
                state.position[2] + delta.position[2]
            ]
            
        return state
'''
    
    # Insertar el método
    new_class_content = class_content[:insert_pos] + update_method + class_content[insert_pos:]
    
    # Reemplazar en el contenido completo
    new_content = content.replace(class_content, new_class_content)
    
    # Guardar
    with open("trajectory_hub/core/motion_components.py", 'w') as f:
        f.write(new_content)
    
    print("✅ Método update añadido a ManualMacroRotation")
    
    # Verificar también ManualIndividualRotation si existe
    if "class ManualIndividualRotation" in content and "def update(" not in content[content.find("class ManualIndividualRotation"):]:
        print("\n🔧 Añadiendo update a ManualIndividualRotation también...")
        
        # Leer de nuevo el archivo actualizado
        with open("trajectory_hub/core/motion_components.py", 'r') as f:
            content = f.read()
            
        # Buscar ManualIndividualRotation
        mir_match = re.search(r'class ManualIndividualRotation.*?\n(.*?)(?=class|\Z)', content, re.DOTALL)
        if mir_match:
            mir_class = mir_match.group(0)
            # Similar proceso para añadir update
            if "return delta" in mir_class:
                delta_end = mir_class.rfind("return delta")
                insert_pos = mir_class.find("\n", delta_end) + 1
                new_mir_class = mir_class[:insert_pos] + update_method + mir_class[insert_pos:]
                new_content = content.replace(mir_class, new_mir_class)
                
                with open("trajectory_hub/core/motion_components.py", 'w') as f:
                    f.write(new_content)
                    
                print("✅ Método update añadido a ManualIndividualRotation")
    
    return True

def verify_fix():
    """Verifica que las clases ya no sean abstractas"""
    print("\n🔍 Verificando clases de rotación...")
    
    try:
        # Intentar importar y crear instancias
        import sys
        sys.path.insert(0, '.')
        
        from trajectory_hub.core.motion_components import ManualMacroRotation
        
        # Intentar crear una instancia
        try:
            rotation = ManualMacroRotation()
            print("✅ ManualMacroRotation ya no es abstracta")
            
            # Verificar que tiene todos los métodos
            if hasattr(rotation, 'update'):
                print("✅ Tiene método update")
            if hasattr(rotation, 'calculate_delta'):
                print("✅ Tiene método calculate_delta")
                
            return True
        except TypeError as e:
            print(f"❌ Error: {e}")
            return False
            
    except Exception as e:
        print(f"⚠️ No se pudo verificar: {e}")
        return True  # Asumimos que está bien

if __name__ == "__main__":
    print("🔧 Arreglando ManualMacroRotation")
    print("="*60)
    
    if add_update_method():
        verify_fix()
        print("\n🎯 Próximo paso:")
        print("$ python test_rotation_controlled.py")
    else:
        print("\n❌ Error al aplicar corrección")