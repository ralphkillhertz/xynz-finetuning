#!/usr/bin/env python3
"""
fix_concentration_method.py - Verifica y corrige el método concentration_control_menu
"""

import os
import re
from datetime import datetime

def check_concentration_method():
    """Verificar dónde está el método concentration_control_menu"""
    print("🔍 VERIFICANDO MÉTODO concentration_control_menu...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método
    pattern = r'(\s*)async def concentration_control_menu\(self\):'
    match = re.search(pattern, content)
    
    if match:
        indent = len(match.group(1))
        print(f"✅ Método encontrado con indentación de {indent} espacios")
        
        # Verificar si está dentro de la clase
        # Buscar la clase InteractiveController
        class_pattern = r'class InteractiveController[^:]*:'
        class_match = re.search(class_pattern, content)
        
        if class_match:
            class_pos = class_match.start()
            method_pos = match.start()
            
            print(f"Posición de la clase: {class_pos}")
            print(f"Posición del método: {method_pos}")
            
            if method_pos > class_pos:
                # Verificar la indentación correcta (debe ser 4 espacios para métodos de clase)
                if indent == 4:
                    print("✅ El método está correctamente indentado dentro de la clase")
                    return True, "correct"
                else:
                    print(f"❌ Indentación incorrecta: {indent} espacios (debe ser 4)")
                    return True, "wrong_indent"
            else:
                print("❌ El método está ANTES de la clase")
                return True, "before_class"
        else:
            print("❌ No se encontró la clase InteractiveController")
            return False, "no_class"
    else:
        print("❌ No se encontró el método concentration_control_menu")
        return False, "not_found"

def add_concentration_method_correctly():
    """Agregar el método en el lugar correcto"""
    print("\n🔧 AGREGANDO MÉTODO CORRECTAMENTE...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    # Backup
    backup_name = f"{filepath}.backup_concentration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Primero, eliminar cualquier versión mal ubicada del método
    print("1. Eliminando versiones mal ubicadas...")
    
    in_concentration_method = False
    method_start = -1
    lines_to_remove = []
    
    for i, line in enumerate(lines):
        if 'async def concentration_control_menu(self):' in line:
            # Verificar indentación
            indent = len(line) - len(line.lstrip())
            if indent != 4:  # Indentación incorrecta
                in_concentration_method = True
                method_start = i
                lines_to_remove.append(i)
                print(f"   Encontrado método mal indentado en línea {i+1}")
        elif in_concentration_method:
            # Continuar hasta encontrar el siguiente método o fin de indentación
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and (current_indent <= indent or 'def ' in line):
                in_concentration_method = False
            else:
                lines_to_remove.append(i)
    
    # Eliminar líneas
    if lines_to_remove:
        for i in reversed(lines_to_remove):
            del lines[i]
        print(f"   ✅ Eliminadas {len(lines_to_remove)} líneas")
    
    # Ahora buscar dónde insertar el método correctamente
    print("\n2. Buscando lugar correcto para insertar...")
    
    # Buscar un buen lugar: después de otro método async de menú
    insert_pos = -1
    
    # Buscar métodos de menú existentes
    menu_methods = [
        'async def deformation_menu',
        'async def distance_control_menu',
        'async def modulator_control_menu'
    ]
    
    for method in menu_methods:
        for i, line in enumerate(lines):
            if method in line:
                # Buscar el final de este método
                j = i + 1
                indent_level = 8  # Indentación dentro del método
                while j < len(lines):
                    if lines[j].strip() and not lines[j].startswith(' ' * indent_level):
                        insert_pos = j
                        break
                    j += 1
                
                if insert_pos != -1:
                    print(f"   ✅ Insertaré después del método {method} (línea {insert_pos})")
                    break
        
        if insert_pos != -1:
            break
    
    # Si no encontramos un buen lugar, buscar antes del final de la clase
    if insert_pos == -1:
        for i in range(len(lines)-1, 0, -1):
            if 'if __name__' in lines[i]:
                insert_pos = i - 1
                print(f"   ✅ Insertaré antes del main (línea {insert_pos})")
                break
    
    # Método concentration_control_menu completo
    method_code = '''
    async def concentration_control_menu(self):
        """Control de concentración de fuentes (Opción 31)"""
        print("\\n" + "="*50)
        print("🎯 CONTROL DE CONCENTRACIÓN DE FUENTES")
        print("="*50)
        
        # Seleccionar macro
        macro_list = [(name, id) for name, id in self.macros.items()]
        if not macro_list:
            print("\\n❌ No hay macros disponibles")
            print("\\nCrea un macro primero (opción 1)")
            await asyncio.sleep(2)
            return
            
        print("\\nMacros disponibles:")
        for i, (name, _) in enumerate(macro_list, 1):
            print(f"{i}. {name}")
            
        try:
            idx = await self._get_int("Seleccionar macro: ", 1, len(macro_list))
            macro_name, macro_id = macro_list[idx - 1]
        except:
            print("\\n❌ Selección cancelada")
            return
        
        while True:
            # Obtener estado
            state = self.engine.get_macro_concentration_state(macro_id)
            if "error" in state:
                print(f"\\n❌ {state['error']}")
                break
                
            factor = state.get("factor", 1.0)
            
            print(f"\\n📍 Macro: {macro_name}")
            print(f"📊 Factor: {factor:.2f} {'[Concentrado]' if factor < 0.5 else '[Disperso]'}")
            print(f"🎬 Animando: {'Sí' if state.get('animating') else 'No'}")
            print(f"📌 Modo: {state.get('mode', 'fixed_point')}")
            
            print("\\nOpciones:")
            print("1. Establecer factor (0-1)")
            print("2. Animar concentración")
            print("3. Toggle (concentrar/dispersar)")
            print("4. Configurar modo")
            print("5. Presets rápidos")
            print("0. Volver")
            
            option = await self._get_input("\\nOpción: ")
            
            if option == "0":
                break
                
            elif option == "1":
                try:
                    factor = await self._get_float("Factor (0=concentrado, 1=disperso): ", 0.0, 1.0)
                    self.engine.set_macro_concentration(macro_id, factor)
                    print(f"✅ Factor establecido: {factor:.2f}")
                except:
                    print("❌ Valor inválido")
                
            elif option == "2":
                try:
                    target = await self._get_float("Factor objetivo: ", 0.0, 1.0)
                    duration = await self._get_float("Duración (segundos): ", 0.1, 10.0)
                    
                    curves = ["linear", "ease_in", "ease_out", "ease_in_out", "exponential", "bounce"]
                    print("\\nCurvas disponibles:")
                    for i, c in enumerate(curves, 1):
                        print(f"{i}. {c}")
                    curve_idx = await self._get_int("Seleccionar curva: ", 1, len(curves))
                    
                    self.engine.animate_macro_concentration(
                        macro_id, target, duration, curves[curve_idx-1]
                    )
                    print(f"✅ Animación iniciada")
                except:
                    print("❌ Valores inválidos")
                
            elif option == "3":
                self.engine.toggle_macro_concentration(macro_id)
                print("✅ Toggle ejecutado")
                
            elif option == "4":
                print("\\nModos disponibles:")
                print("1. Punto fijo")
                print("2. Seguir macro")
                
                try:
                    mode_idx = await self._get_int("Seleccionar modo: ", 1, 2)
                    mode = ["fixed_point", "follow_macro"][mode_idx-1]
                    
                    self.engine.set_macro_concentration(macro_id, factor, 0, mode)
                    print(f"✅ Modo establecido: {mode}")
                except:
                    print("❌ Selección inválida")
                
            elif option == "5":
                print("\\nPresets:")
                print("1. Explosión (dispersar en 0.5s)")
                print("2. Implosión (concentrar en 0.5s)")
                print("3. Pulso (toggle rápido)")
                print("4. Convergencia dramática (3s)")
                
                try:
                    preset = await self._get_int("Seleccionar preset: ", 1, 4)
                    
                    if preset == 1:
                        self.engine.animate_macro_concentration(macro_id, 1.0, 0.5, "ease_out")
                    elif preset == 2:
                        self.engine.animate_macro_concentration(macro_id, 0.0, 0.5, "ease_in")
                    elif preset == 3:
                        self.engine.toggle_macro_concentration(macro_id)
                    elif preset == 4:
                        self.engine.animate_macro_concentration(macro_id, 0.0, 3.0, "exponential")
                        
                    print("✅ Preset aplicado")
                except:
                    print("❌ Selección inválida")
'''
    
    # Insertar el método
    if insert_pos != -1:
        lines.insert(insert_pos, method_code)
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"\n✅ Método agregado correctamente en línea {insert_pos}")
        return True
    else:
        print("\n❌ No se encontró un lugar adecuado para insertar")
        return False

def verify_final():
    """Verificación final"""
    print("\n\n🔍 VERIFICACIÓN FINAL...\n")
    
    # Verificar que el método existe y está accesible
    try:
        from trajectory_hub.interface.interactive_controller import InteractiveController
        
        # Verificar que el método existe
        if hasattr(InteractiveController, 'concentration_control_menu'):
            print("✅ El método concentration_control_menu está disponible")
            return True
        else:
            print("❌ El método NO está disponible en la clase")
            
            # Listar métodos disponibles
            methods = [m for m in dir(InteractiveController) if not m.startswith('_')]
            print(f"\nMétodos disponibles: {len(methods)}")
            
            # Buscar métodos de menú
            menu_methods = [m for m in methods if 'menu' in m]
            print(f"\nMétodos de menú encontrados:")
            for m in menu_methods:
                print(f"  - {m}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar: {e}")
        return False

def main():
    print("="*70)
    print("🔧 CORRECCIÓN DEL MÉTODO concentration_control_menu")
    print("="*70)
    
    # Verificar estado actual
    found, status = check_concentration_method()
    
    if not found or status != "correct":
        # Agregar el método correctamente
        if add_concentration_method_correctly():
            # Verificar
            if verify_final():
                print("\n" + "="*70)
                print("✅ MÉTODO CORREGIDO Y FUNCIONANDO")
                print("\nAhora la opción 31 funcionará correctamente:")
                print("  python -m trajectory_hub.interface.interactive_controller")
                print("  Seleccionar opción 31")
            else:
                print("\n⚠️  El método se agregó pero puede necesitar reiniciar Python")
        else:
            print("\n❌ No se pudo corregir el método")
    else:
        print("\n✅ El método ya está correctamente ubicado")
        verify_final()

if __name__ == "__main__":
    main()