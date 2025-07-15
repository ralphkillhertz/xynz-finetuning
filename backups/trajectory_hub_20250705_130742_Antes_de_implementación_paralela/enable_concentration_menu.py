#!/usr/bin/env python3
"""
enable_concentration_menu.py - Activa la opción 31 de concentración en el controlador
"""

import os
import re
from datetime import datetime

def find_option_31_handler():
    """Buscar dónde se maneja la opción 31"""
    print("🔍 BUSCANDO HANDLER DE OPCIÓN 31...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar referencias a opción 31
    # Primero buscar en el menú
    menu_match = re.search(r'31\.\s+[^"]*Concentración[^"]*', content)
    if menu_match:
        print(f"✅ Encontrado en menú: {menu_match.group(0)}")
    
    # Buscar el handler
    handler_patterns = [
        r'elif\s+choice\s*==\s*["\']31["\']',
        r'elif\s+option\s*==\s*["\']31["\']',
        r'elif\s+.*\s*==\s*31',
        r'if\s+.*\s*==\s*["\']31["\']'
    ]
    
    handler_found = False
    for pattern in handler_patterns:
        matches = list(re.finditer(pattern, content))
        if matches:
            for match in matches:
                print(f"\n✅ Encontrado handler en posición {match.start()}:")
                
                # Mostrar contexto
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                
                print("-" * 60)
                print(context)
                print("-" * 60)
                
                # Ver si está marcado como "en desarrollo"
                if "desarrollo" in context or "próximamente" in context:
                    print("\n⚠️  ESTÁ MARCADO COMO EN DESARROLLO")
                    handler_found = True
    
    return handler_found

def fix_option_31():
    """Corregir el handler de la opción 31"""
    print("\n\n🔧 ACTIVANDO OPCIÓN 31...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    # Backup
    backup_name = f"{filepath}.backup_option31_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar y reemplazar el handler
    in_option_31 = False
    changes_made = 0
    
    for i in range(len(lines)):
        line = lines[i]
        
        # Detectar el inicio del handler de opción 31
        if re.search(r'elif\s+choice\s*==\s*["\']31["\']', line) or \
           re.search(r'elif\s+option\s*==\s*["\']31["\']', line):
            in_option_31 = True
            print(f"Encontrado handler en línea {i+1}")
            continue
        
        # Si estamos en el handler de opción 31
        if in_option_31:
            # Buscar la línea que dice "en desarrollo" o similar
            if ("desarrollo" in line or "próximamente" in line or 
                "print" in line and ("desarrollo" in line or "Función" in line)):
                
                print(f"  Línea {i+1}: {line.strip()}")
                
                # Obtener la indentación
                indent = len(line) - len(line.lstrip())
                
                # Reemplazar con la llamada correcta
                new_line = " " * indent + "await self.concentration_control_menu()\n"
                lines[i] = new_line
                
                print(f"  Reemplazada por: {new_line.strip()}")
                changes_made += 1
                
                # Salir del bloque
                in_option_31 = False
            
            # Si llegamos a otro elif o else, salir
            elif re.match(r'\s*(elif|else)', line) and not line.strip().startswith("#"):
                in_option_31 = False
    
    if changes_made > 0:
        # Guardar archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"\n✅ {changes_made} cambios realizados")
        return True
    else:
        print("\n⚠️  No se encontró la línea a reemplazar")
        return False

def verify_concentration_menu_exists():
    """Verificar que el método concentration_control_menu existe"""
    print("\n\n🔍 VERIFICANDO QUE concentration_control_menu EXISTE...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "async def concentration_control_menu" in content:
        print("✅ El método concentration_control_menu existe")
        
        # Buscar y mostrar las primeras líneas
        match = re.search(r'async def concentration_control_menu\(self\):(.*?)(?=\n\s{0,4}async def|\n\s{0,4}def|\Z)', 
                         content, re.DOTALL)
        if match:
            lines = match.group(0).split('\n')[:10]
            print("\nPrimeras líneas del método:")
            print("-" * 60)
            for line in lines:
                print(line)
            print("-" * 60)
        
        return True
    else:
        print("❌ El método concentration_control_menu NO existe")
        print("   Necesitamos agregarlo")
        return False

def add_concentration_menu_if_missing():
    """Agregar el método si no existe"""
    concentration_menu_code = '''
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
    
    print("\n🔧 AGREGANDO concentration_control_menu...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar un buen lugar para insertar (antes del final de la clase)
    # Buscar el último método async
    last_async = content.rfind("async def")
    if last_async != -1:
        # Buscar el final de ese método
        next_method = content.find("\n    async def", last_async + 1)
        if next_method == -1:
            next_method = content.find("\n    def", last_async + 1)
        if next_method == -1:
            # Buscar el final de la clase
            next_method = content.find("\nif __name__", last_async)
        
        if next_method != -1:
            # Insertar antes del siguiente método
            content = content[:next_method] + "\n" + concentration_menu_code + content[next_method:]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Método agregado")
            return True
    
    return False

def main():
    print("="*70)
    print("🔧 ACTIVACIÓN DE LA OPCIÓN 31 - CONCENTRACIÓN")
    print("="*70)
    
    # Buscar el handler actual
    found = find_option_31_handler()
    
    if found:
        # Verificar que el método existe
        if not verify_concentration_menu_exists():
            # Agregar el método si no existe
            if not add_concentration_menu_if_missing():
                print("\n❌ No se pudo agregar el método")
                return
        
        # Activar la opción
        if fix_option_31():
            print("\n" + "="*70)
            print("✅ OPCIÓN 31 ACTIVADA")
            print("\nAhora puedes usar:")
            print("  python -m trajectory_hub.interface.interactive_controller")
            print("  Seleccionar opción 31 - Control de Concentración")
            print("\n🎯 Funcionalidades disponibles:")
            print("  - Establecer factor de concentración")
            print("  - Animaciones con diferentes curvas")
            print("  - Toggle rápido")
            print("  - Modos: punto fijo o seguir macro")
            print("  - Presets: explosión, implosión, pulso, convergencia")
        else:
            print("\n❌ No se pudo activar la opción")
    else:
        print("\n❌ No se encontró el handler de la opción 31")

if __name__ == "__main__":
    main()