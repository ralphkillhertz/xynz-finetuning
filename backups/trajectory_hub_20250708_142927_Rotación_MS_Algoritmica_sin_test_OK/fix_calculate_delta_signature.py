# === fix_calculate_delta_signature.py ===
# 🔧 Fix: Corregir la firma de calculate_delta en IndividualTrajectory
# ⚡ Error: calculate_delta() takes 3 positional arguments but 4 were given
# 🎯 Impacto: ALTO - Sin esto no funciona el sistema de deltas

import os
import re

def analyze_calculate_delta_signatures():
    """Analiza las firmas de calculate_delta en todos los componentes"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔍 Analizando firmas de calculate_delta...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las definiciones de calculate_delta
    pattern = r'def calculate_delta\([^)]+\):'
    matches = re.findall(pattern, content)
    
    print("\n📋 Firmas encontradas:")
    for i, match in enumerate(matches, 1):
        print(f"   {i}. {match}")
    
    # Buscar cómo se llama en update_with_deltas
    call_pattern = r'component\.calculate_delta\([^)]+\)'
    call_matches = re.findall(call_pattern, content)
    
    print("\n📞 Llamadas encontradas:")
    for match in call_matches[:3]:  # Primeras 3
        print(f"   - {match}")
    
    return len(matches)

def fix_individual_trajectory_calculate_delta():
    """Corrige la firma de calculate_delta en IndividualTrajectory"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("\n🔧 Corrigiendo calculate_delta en IndividualTrajectory...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la clase IndividualTrajectory
    class_start = content.find("class IndividualTrajectory")
    if class_start == -1:
        print("❌ No se encontró IndividualTrajectory")
        return False
    
    # Buscar el final de la clase
    next_class = content.find("\nclass ", class_start + 1)
    if next_class == -1:
        next_class = len(content)
    
    class_content = content[class_start:next_class]
    
    # Ver si ya tiene calculate_delta
    if "def calculate_delta" in class_content:
        print("✅ Ya tiene calculate_delta, verificando firma...")
        
        # Buscar y corregir la firma
        old_pattern = r'def calculate_delta\(self, current_time, dt\):'
        new_signature = 'def calculate_delta(self, state, current_time, dt):'
        
        if re.search(old_pattern, class_content):
            class_content = re.sub(old_pattern, new_signature, class_content)
            print("✅ Firma corregida")
        else:
            print("⚠️ Firma diferente, verificando...")
    else:
        print("❌ No tiene calculate_delta, añadiendo...")
        
        # Añadir el método al final de la clase
        method_code = '''
    def calculate_delta(self, state, current_time, dt):
        """Calcula el delta de movimiento para esta trayectoria individual"""
        if not self.enabled:
            return None
        
        # Actualizar posición en la trayectoria
        self.update_position(dt)
        
        # Calcular nueva posición 3D
        new_position = self._calculate_position_on_trajectory()
        
        # Crear delta
        delta = MotionDelta()
        delta.position = new_position - state.position
        
        return delta'''
        
        # Insertar antes del final de la clase
        insert_pos = class_start + len(class_content) - 1
        class_content = class_content[:-1] + method_code + "\n"
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(motion_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Reemplazar en el contenido completo
    new_content = content[:class_start] + class_content + content[next_class:]
    
    # Escribir el archivo
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ IndividualTrajectory corregido")
    return True

def fix_update_with_deltas_compatibility():
    """Asegura que update_with_deltas funcione con ambas firmas"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("\n🔧 Haciendo update_with_deltas compatible...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar update_with_deltas en SourceMotion
    pattern = r'def update_with_deltas\(self[^)]*\):[^}]+?return'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró update_with_deltas")
        return False
    
    # Nuevo código compatible
    new_method = '''def update_with_deltas(self, current_time, dt):
        """Actualiza y retorna deltas de todos los componentes activos"""
        all_deltas = []
        
        for component_name, component in self.active_components.items():
            if component is not None and getattr(component, 'enabled', False):
                if hasattr(component, 'calculate_delta'):
                    try:
                        # Intentar con firma nueva (4 args)
                        delta = component.calculate_delta(self.state, current_time, dt)
                    except TypeError:
                        try:
                            # Intentar con firma vieja (3 args)
                            delta = component.calculate_delta(current_time, dt)
                        except:
                            # Si falla, skip
                            continue
                    
                    if delta:
                        all_deltas.append(delta)
        
        return all_deltas'''
    
    # Encontrar el método para reemplazarlo
    method_start = content.find("def update_with_deltas(self")
    if method_start == -1:
        print("❌ No se encontró el método")
        return False
    
    # Encontrar el final del método
    # Buscar el siguiente def al mismo nivel de indentación
    next_method = re.search(r'\n    def \w+', content[method_start + 50:])
    if next_method:
        method_end = method_start + 50 + next_method.start()
    else:
        # Si no hay siguiente método, buscar el final de la clase
        method_end = content.find("\n\nclass", method_start)
        if method_end == -1:
            method_end = len(content)
    
    # Reemplazar
    new_content = content[:method_start] + new_method + content[method_end:]
    
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ update_with_deltas ahora es compatible con ambas firmas")
    return True

if __name__ == "__main__":
    print("🔧 FIX CALCULATE_DELTA SIGNATURES")
    print("=" * 50)
    
    # Analizar el problema
    analyze_calculate_delta_signatures()
    
    # Aplicar fixes
    print("\n📝 Aplicando correcciones...")
    
    if fix_individual_trajectory_calculate_delta():
        print("✅ Paso 1 completado")
    
    if fix_update_with_deltas_compatibility():
        print("✅ Paso 2 completado")
    
    print("\n✅ Fixes aplicados")
    print("\n📝 Ejecuta nuevamente:")
    print("python test_individual_minimal.py")