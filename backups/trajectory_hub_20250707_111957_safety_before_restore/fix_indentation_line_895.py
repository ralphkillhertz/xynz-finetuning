#!/usr/bin/env python3
"""
🔧 FIX RÁPIDO - Corregir indentación línea 895
⚡ Arreglar el error de sintaxis
"""

import os

def fix_indentation_error():
    """Corregir el error de indentación en línea 895"""
    
    print("🔧 CORRIGIENDO ERROR DE INDENTACIÓN\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    # Leer el archivo
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    print(f"📄 Total de líneas: {len(lines)}")
    
    # Verificar alrededor de la línea 895
    if len(lines) >= 895:
        print("\n🔍 Contexto alrededor de línea 895:")
        
        for i in range(max(0, 892), min(len(lines), 898)):
            prefix = ">>>" if i == 894 else "   "
            print(f"{prefix} L{i+1}: {repr(lines[i][:60])}")
    
    # El problema es que falta la declaración del método
    # Buscar hacia atrás para encontrar dónde debería estar
    for i in range(894, max(0, 880), -1):
        if 'def ' in lines[i] or 'class ' in lines[i]:
            print(f"\n📍 Encontrado en línea {i+1}: {lines[i].strip()}")
            
            # Si es una definición de método sin cuerpo
            if lines[i].strip().endswith(':') and i < 894:
                # La siguiente línea debería tener el docstring
                if i+1 < len(lines) and '"""' in lines[i+1]:
                    # Verificar la indentación
                    method_indent = len(lines[i]) - len(lines[i].lstrip())
                    docstring_indent = len(lines[i+1]) - len(lines[i+1].lstrip())
                    
                    if docstring_indent <= method_indent:
                        print(f"   ❌ Indentación incorrecta del docstring")
                        # Corregir agregando 4 espacios más
                        lines[i+1] = ' ' * (method_indent + 4) + lines[i+1].lstrip()
                        
                        # Corregir las siguientes líneas también
                        j = i + 2
                        while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('def'):
                            if len(lines[j].strip()) > 0:
                                # Asegurar indentación correcta
                                lines[j] = ' ' * (method_indent + 4) + lines[j].lstrip()
                            j += 1
                        
                        break
    
    # Guardar el archivo corregido
    print("\n💾 Guardando correcciones...")
    
    with open(motion_file, 'w') as f:
        f.writelines(lines)
    
    # Verificar sintaxis
    try:
        with open(motion_file, 'r') as f:
            compile(f.read(), motion_file, 'exec')
        print("✅ Sintaxis corregida")
        return True
    except SyntaxError as e:
        print(f"❌ Aún hay error en línea {e.lineno}: {e.msg}")
        
        # Intento alternativo: restaurar y aplicar cambios más cuidadosamente
        print("\n🔄 Intentando fix alternativo...")
        return fix_alternative()

def fix_alternative():
    """Restaurar desde backup y aplicar cambios cuidadosamente"""
    
    print("\n🔧 APLICANDO FIX ALTERNATIVO\n")
    
    # Buscar el backup más reciente
    import glob
    backups = sorted(glob.glob("backup_final_*/motion_components.py"))
    
    if not backups:
        print("❌ No hay backups disponibles")
        return False
    
    backup_file = backups[-1]
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print(f"📁 Restaurando desde: {backup_file}")
    
    import shutil
    shutil.copy2(backup_file, motion_file)
    
    # Ahora aplicar los cambios más cuidadosamente
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar el método update en SourceMotion
    import re
    
    # Encontrar la clase SourceMotion
    class_pattern = r'(class SourceMotion[^:]*:)(.*?)(?=\nclass|\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if class_match:
        class_header = class_match.group(1)
        class_body = class_match.group(2)
        
        # Buscar el método update
        update_pattern = r'(\n    def update\(self, dt: float\):)\s*\n'
        update_match = re.search(update_pattern, class_body)
        
        if update_match:
            # Reemplazar con el método correcto con indentación apropiada
            new_update = '''
    def update(self, dt: float):
        """Actualizar posición aplicando offsets a state.position"""
        if dt < 0.0001:
            return
        
        # Resetear offsets
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)
        
        # Posición base del state
        base_pos = self.state.position.copy()
        
        # Calcular offset de concentración
        if 'concentration' in self.components:
            conc = self.components['concentration']
            if hasattr(conc, 'enabled') and conc.enabled and hasattr(conc, 'factor'):
                if conc.factor < 0.99:
                    target = getattr(conc, 'target_point', self.macro_reference)
                    concentrated = base_pos * conc.factor + target * (1 - conc.factor)
                    self.concentration_offset = concentrated - base_pos
        
        # Actualizar la posición sumando offsets
        self.state.position = (base_pos + 
                              self.concentration_offset + 
                              self.macro_rotation_offset +
                              self.trajectory_offset +
                              self.algorithmic_rotation_offset)
'''
            
            # Encontrar dónde termina el método update actual
            next_method = re.search(r'\n    def \w+\(', class_body[update_match.end():])
            if next_method:
                end_pos = update_match.end() + next_method.start()
            else:
                end_pos = len(class_body)
            
            # Reemplazar
            new_class_body = (class_body[:update_match.start()] + 
                            new_update + 
                            class_body[end_pos:])
            
            # Reconstruir el contenido
            new_content = content.replace(class_header + class_body, 
                                        class_header + new_class_body)
            
            # Guardar
            with open(motion_file, 'w') as f:
                f.write(new_content)
            
            print("✅ Método update corregido")
            return True
    
    return False

if __name__ == "__main__":
    success = fix_indentation_error()
    
    if success:
        print("\n🎉 ERROR CORREGIDO")
        print("\n🚀 Ahora ejecuta:")
        print("   python test_final_concentration.py")
    else:
        print("\n❌ No se pudo corregir automáticamente")
        print("\nOpciones:")
        print("1. Revisar manualmente la línea 895")
        print("2. Restaurar desde backup_final_*/motion_components.py")