#!/usr/bin/env python3
"""
🔧 Implementación completa de integración de macros
⚡ Actualiza métodos existentes y añade delete
🎯 Impacto: ALTO - Funcionalidad completa en UI
"""

import os
import datetime

def implement_macro_integration():
    """Implementa la integración completa"""
    
    print("🔧 IMPLEMENTANDO INTEGRACIÓN COMPLETA DE MACROS")
    print("=" * 60)
    
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    # Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{controller_path}.backup_macro_integration_{timestamp}"
    os.system(f"cp '{controller_path}' '{backup_path}'")
    print(f"✅ Backup: {backup_path}")
    
    # Leer archivo
    with open(controller_path, 'r') as f:
        lines = f.readlines()
    
    changes_made = []
    
    # 1. AÑADIR OPCIÓN 7 AL MENÚ
    print("\n1️⃣ Añadiendo opción 7 al menú system...")
    
    # Buscar línea con opción 6
    for i, line in enumerate(lines):
        if '("6", "📂 Cargar Configuración")' in line:
            # Insertar nueva opción después
            new_option = '            ("7", "🗑️ Eliminar Macro"),\n'
            lines.insert(i + 1, new_option)
            changes_made.append(f"Añadida opción 7 en línea {i + 2}")
            break
    
    # 2. AÑADIR CASO EN PROCESS_SYSTEM_CHOICE
    print("\n2️⃣ Añadiendo procesamiento de opción 7...")
    
    # Buscar elif choice == "6"
    for i, line in enumerate(lines):
        if 'elif choice == "6"' in line and '_load_configuration' in lines[i+1]:
            # Buscar el siguiente elif o final
            j = i + 2
            while j < len(lines):
                if lines[j].strip().startswith('elif') or lines[j].strip().startswith('else'):
                    # Insertar antes
                    new_case = '''        elif choice == "7":
            self._delete_macro()
'''
                    lines.insert(j, new_case)
                    changes_made.append(f"Añadido caso para opción 7 en línea {j + 1}")
                    break
                j += 1
            break
    
    # 3. ACTUALIZAR _list_active_macros
    print("\n3️⃣ Actualizando _list_active_macros()...")
    
    # Buscar el método
    list_macros_start = -1
    for i, line in enumerate(lines):
        if 'def _list_active_macros(self):' in line:
            list_macros_start = i
            break
    
    if list_macros_start > 0:
        # Reemplazar el método completo
        old_method_end = list_macros_start + 1
        while old_method_end < len(lines):
            if lines[old_method_end].strip() and not lines[old_method_end].startswith('    '):
                break
            old_method_end += 1
        
        # Nuevo método
        new_method = '''    def _list_active_macros(self):
        """Lista macros activos usando engine.list_macros()"""
        self.ui.show_header("MACROS ACTIVOS")
        
        macros = self.engine.list_macros()
        
        if not macros:
            self.ui.show_info("No hay macros activos")
        else:
            print(f"\\n  Total: {len(macros)} macros\\n")
            for i, macro in enumerate(macros):
                status = "✅" if macro['key'] == self.selected_macro else "  "
                print(f"  {status} [{i+1}] {macro['name']}")
                print(f"       Sources: {macro['num_sources']} | Formation: {macro['formation']}")
                
        self.ui.pause()
    
'''
        # Reemplazar
        del lines[list_macros_start:old_method_end]
        lines.insert(list_macros_start, new_method)
        changes_made.append(f"Actualizado _list_active_macros en línea {list_macros_start + 1}")
    
    # 4. IMPLEMENTAR _show_macro_info
    print("\n4️⃣ Implementando _show_macro_info()...")
    
    # Buscar el método
    show_info_start = -1
    for i, line in enumerate(lines):
        if 'def _show_macro_info(self):' in line:
            show_info_start = i
            break
    
    if show_info_start > 0:
        # Reemplazar el método
        old_method_end = show_info_start + 1
        while old_method_end < len(lines):
            if lines[old_method_end].strip() and not lines[old_method_end].startswith('    '):
                break
            old_method_end += 1
        
        new_method = '''    def _show_macro_info(self):
        """Muestra información detallada de un macro"""
        if not self._ensure_macro_selected():
            return
            
        # Buscar el macro
        macro_info = self.engine.select_macro(self.selected_macro)
        
        if not macro_info:
            self.ui.show_error(f"Macro '{self.selected_macro}' no encontrado")
            self.selected_macro = None
            self.ui.pause()
            return
        
        # Mostrar información
        self.ui.show_header(f"INFORMACIÓN DE MACRO: {macro_info['key']}")
        
        print(f"\\n  Nombre: {macro_info['key'].split('_', 2)[2]}")
        print(f"  Comportamiento: {macro_info['behavior']}")
        print(f"  Total Sources: {macro_info['num_sources']}")
        print(f"\\n  IDs de Sources:")
        
        # Mostrar IDs en filas de 10
        for i, sid in enumerate(macro_info['source_ids']):
            if i % 10 == 0:
                print("    ", end="")
            print(f"{sid:3d}", end="  ")
            if (i + 1) % 10 == 0:
                print()
        
        if len(macro_info['source_ids']) % 10 != 0:
            print()
            
        self.ui.pause()
    
'''
        del lines[show_info_start:old_method_end]
        lines.insert(show_info_start, new_method)
        changes_made.append(f"Implementado _show_macro_info en línea {show_info_start + 1}")
    
    # 5. AÑADIR _delete_macro
    print("\n5️⃣ Añadiendo _delete_macro()...")
    
    # Buscar dónde insertarlo (después de _show_macro_info)
    insert_pos = -1
    for i, line in enumerate(lines):
        if 'def _show_macro_info(self):' in line:
            # Buscar el final del método
            j = i + 1
            while j < len(lines):
                if lines[j].strip() and not lines[j].startswith('    '):
                    insert_pos = j
                    break
                j += 1
            break
    
    if insert_pos > 0:
        new_method = '''    def _delete_macro(self):
        """Elimina un macro seleccionado"""
        self.ui.show_header("ELIMINAR MACRO")
        
        # Mostrar macros disponibles
        macros = self.engine.list_macros()
        
        if not macros:
            self.ui.show_info("No hay macros para eliminar")
            self.ui.pause()
            return
        
        print("\\n  Macros disponibles:\\n")
        for i, macro in enumerate(macros):
            print(f"  [{i+1}] {macro['name']} ({macro['num_sources']} sources)")
        
        print("\\n  [0] Cancelar")
        
        # Solicitar selección
        try:
            choice = input("\\n  Seleccionar macro a eliminar (número): ").strip()
            
            if choice == "0":
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(macros):
                macro_to_delete = macros[idx]
                
                # Confirmar
                confirm = input(f"\\n  ⚠️  ¿Eliminar '{macro_to_delete['name']}' con {macro_to_delete['num_sources']} sources? (s/n): ").strip().lower()
                
                if confirm == 's':
                    if self.engine.delete_macro(macro_to_delete['key']):
                        self.ui.show_success(f"Macro '{macro_to_delete['name']}' eliminado")
                        # Si era el seleccionado, limpiar selección
                        if self.selected_macro == macro_to_delete['key']:
                            self.selected_macro = None
                    else:
                        self.ui.show_error("Error al eliminar macro")
                else:
                    self.ui.show_info("Eliminación cancelada")
            else:
                self.ui.show_error("Número inválido")
                
        except ValueError:
            self.ui.show_error("Entrada inválida")
        except Exception as e:
            self.ui.show_error(f"Error: {e}")
        
        self.ui.pause()
    
'''
        lines.insert(insert_pos, new_method)
        changes_made.append(f"Añadido _delete_macro en línea {insert_pos + 1}")
    
    # Guardar archivo
    with open(controller_path, 'w') as f:
        f.writelines(lines)
    
    print("\n✅ CAMBIOS REALIZADOS:")
    for change in changes_made:
        print(f"   - {change}")
    
    print(f"\n📁 Backup guardado: {backup_path}")
    print("\n🎯 Sistema de gestión de macros completamente integrado")
    
    return True

if __name__ == "__main__":
    if implement_macro_integration():
        print("\n🚀 Ejecución exitosa")
        print("📋 Prueba el sistema:")
        print("   python -m trajectory_hub.interface.interactive_controller")
        print("   → Ve al menú System (opción 5)")
        print("   → Prueba opciones 2, 3 y 7")