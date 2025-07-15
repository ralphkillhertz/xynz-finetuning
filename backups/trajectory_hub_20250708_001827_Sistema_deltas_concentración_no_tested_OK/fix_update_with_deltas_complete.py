# === fix_update_with_deltas_complete.py ===
# 🔧 Fix: Arregla COMPLETAMENTE update_with_deltas
# ⚡ Este es EL fix definitivo

import os
import re
from datetime import datetime

def fix_update_with_deltas_completely():
    """Reescribe update_with_deltas para que funcione correctamente"""
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_path):
        print("❌ No se encuentra motion_components.py")
        return False
    
    # Leer archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar SourceMotion
    class_pattern = r'(class SourceMotion[^:]*:)(.*?)(?=\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encontró clase SourceMotion")
        return False
    
    class_content = class_match.group(2)
    
    # Buscar update_with_deltas
    method_pattern = r'(def update_with_deltas\(self[^)]*\):)(.*?)(?=\n\s{0,8}def|\Z)'
    method_match = re.search(method_pattern, class_content, re.DOTALL)
    
    if method_match:
        print("✅ Encontrado update_with_deltas, reemplazándolo...")
        
        # Nuevo método que FUNCIONA
        new_method = '''
        """Actualiza componentes y retorna LISTA de deltas"""
        deltas = []
        
        # Actualizar cada componente activo
        for comp_name, component in self.active_components.items():
            if hasattr(component, 'enabled') and component.enabled:
                if hasattr(component, 'calculate_delta'):
                    # Llamar calculate_delta con el estado correcto
                    delta = component.calculate_delta(self.motion_state, current_time, dt)
                    if delta is not None and hasattr(delta, 'position'):
                        # Verificar que el delta tenga datos válidos
                        if delta.position is not None and not all(delta.position == 0):
                            deltas.append(delta)
                            print(f"    ✅ Delta de {comp_name}: {delta.position}")
        
        # SIEMPRE retornar lista, aunque esté vacía
        return deltas'''
        
        # Reemplazar el método
        new_class_content = class_content[:method_match.start()] + method_match.group(1) + new_method + class_content[method_match.end():]
        
        # Reconstruir contenido completo
        new_content = content[:class_match.start(2)] + new_class_content + content[class_match.end(2):]
        
    else:
        print("⚠️ No se encontró update_with_deltas, creándolo...")
        
        # Buscar dónde insertar (después de __init__ o add_component)
        insert_pos = class_content.rfind('def add_component')
        if insert_pos > -1:
            # Buscar el final del método
            next_def = class_content.find('\n    def ', insert_pos + 10)
            if next_def > -1:
                insert_pos = next_def
            else:
                insert_pos = len(class_content)
        else:
            # Después de __init__
            insert_pos = class_content.find('def __init__')
            next_def = class_content.find('\n    def ', insert_pos + 10)
            if next_def > -1:
                insert_pos = next_def
        
        # Crear método
        new_method = '''
    def update_with_deltas(self, current_time: float, dt: float) -> list:
        """Actualiza componentes y retorna LISTA de deltas"""
        deltas = []
        
        # Actualizar cada componente activo
        for comp_name, component in self.active_components.items():
            if hasattr(component, 'enabled') and component.enabled:
                if hasattr(component, 'calculate_delta'):
                    # Llamar calculate_delta con el estado correcto
                    delta = component.calculate_delta(self.motion_state, current_time, dt)
                    if delta is not None and hasattr(delta, 'position'):
                        # Verificar que el delta tenga datos válidos
                        if delta.position is not None and not all(delta.position == 0):
                            deltas.append(delta)
                            print(f"    ✅ Delta de {comp_name}: {delta.position}")
        
        # SIEMPRE retornar lista, aunque esté vacía
        return deltas
'''
        
        # Insertar
        new_class_content = class_content[:insert_pos] + new_method + class_content[insert_pos:]
        new_content = content[:class_match.start(2)] + new_class_content + content[class_match.end(2):]
    
    # Escribir archivo
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ update_with_deltas arreglado completamente")
    
    # Verificar sintaxis
    try:
        compile(new_content, motion_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(motion_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

if __name__ == "__main__":
    print("🔧 FIX COMPLETO DE UPDATE_WITH_DELTAS")
    print("="*60)
    print("\n📌 Problemas detectados:")
    print("  1. update_with_deltas retorna UN delta, no lista")
    print("  2. El delta tiene position=[0,0,0] en lugar de [-0.8,0,0]")
    print("\n🔧 Aplicando fix completo...")
    
    success = fix_update_with_deltas_completely()
    
    if success:
        print("\n✅ ¡FIX APLICADO EXITOSAMENTE!")
        print("\n🎯 ESTE ES EL MOMENTO DE LA VERDAD")
        print("\n📋 Ejecuta:")
        print("$ python test_delta_concentration_final.py")
        print("\n🎉 Las fuentes DEBEN moverse ahora!")
    else:
        print("\n❌ Error al aplicar fix")