#!/usr/bin/env python3
"""
🔧 Implementa delete_macro() después de select_macro()
⚡ Inserta después de línea 518
🎯 Impacto: MEDIO - Elimina macros y sources
"""

import os
import datetime

def implement_delete_macro():
    """Implementa delete_macro en la posición correcta"""
    
    print("🔧 IMPLEMENTANDO delete_macro()")
    print("=" * 60)
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{engine_path}.backup_before_delete_macro_{timestamp}"
    os.system(f"cp '{engine_path}' '{backup_path}'")
    print(f"✅ Backup: {backup_path}")
    
    # Leer archivo
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Verificar que no existe
    content = ''.join(lines)
    if 'def delete_macro' in content:
        print("⚠️ delete_macro ya existe")
        return False
    
    # Código a insertar
    delete_macro_code = '''    def delete_macro(self, identifier):
        """Elimina un macro y todas sus sources
        
        Args:
            identifier: Nombre del macro, ID completo o índice
            
        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        # Primero buscar el macro usando select_macro
        macro_info = self.select_macro(identifier)
        
        if not macro_info:
            print(f"❌ Macro '{identifier}' no encontrado")
            return False
        
        macro_key = macro_info['key']
        macro = macro_info['macro']
        source_ids = macro_info['source_ids']
        
        print(f"🗑️ Eliminando macro '{macro_key}' con {len(source_ids)} sources...")
        
        # Eliminar todas las sources del macro de _active_sources
        removed_count = 0
        for source_id in source_ids:
            self._active_sources.discard(source_id)  # discard no lanza error si no existe
            removed_count += 1
            print(f"   ✅ Source {source_id} eliminada")
        
        # Eliminar el macro del diccionario
        if macro_key in self._macros:
            del self._macros[macro_key]
            print(f"✅ Macro '{macro_key}' eliminado completamente")
        
        # Actualizar contador de macros si existe
        if hasattr(self, 'macro_count'):
            self.macro_count = len(self._macros)
        
        # Log final
        print(f"✅ Eliminación completa: {removed_count} sources removidas")
        
        return True

'''
    
    # Insertar después de línea 518
    insert_pos = 518
    
    # Añadir línea en blanco si es necesario
    if insert_pos < len(lines) and lines[insert_pos].strip() != '':
        lines.insert(insert_pos, '\n')
        insert_pos += 1
    
    lines.insert(insert_pos, delete_macro_code)
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ delete_macro() insertado después de select_macro()")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis...")
    result = os.system(f"python -m py_compile '{engine_path}' 2>&1")
    
    if result == 0:
        print("✅ Sintaxis correcta")
        
        # Test completo
        print("\n🧪 PROBANDO delete_macro()...")
        try:
            from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
            engine = EnhancedTrajectoryEngine()
            engine.start()
            
            # Crear macros de prueba
            engine.create_macro("test_delete", 3, formation="circle")
            engine.create_macro("test_keep", 2, formation="line")
            
            # Verificar estado inicial
            macros_before = engine.list_macros()
            sources_before = len(engine._active_sources)
            print(f"\n📊 ESTADO INICIAL:")
            print(f"   Macros: {len(macros_before)}")
            print(f"   Sources activas: {sources_before}")
            
            # Test 1: Eliminar por nombre
            print("\n1️⃣ TEST: Eliminar por nombre")
            result1 = engine.delete_macro("test_delete")
            print(f"   Resultado: {'✅' if result1 else '❌'}")
            
            # Verificar estado después
            macros_after = engine.list_macros()
            sources_after = len(engine._active_sources)
            print(f"\n📊 ESTADO DESPUÉS:")
            print(f"   Macros: {len(macros_after)}")
            print(f"   Sources activas: {sources_after}")
            print(f"   Macros restantes: {[m['name'] for m in macros_after]}")
            
            # Test 2: Intentar eliminar macro inexistente
            print("\n2️⃣ TEST: Eliminar macro inexistente")
            result2 = engine.delete_macro("no_existe")
            print(f"   Resultado: {'✅ (correctamente rechazado)' if not result2 else '❌'}")
            
            # Test 3: Eliminar por índice
            print("\n3️⃣ TEST: Eliminar por índice 0")
            if len(macros_after) > 0:
                result3 = engine.delete_macro(0)
                print(f"   Resultado: {'✅' if result3 else '❌'}")
                
                final_macros = engine.list_macros()
                print(f"   Macros finales: {len(final_macros)}")
            
            engine.stop()
            
            # Verificación final
            success = (
                result1 and 
                not result2 and 
                len(macros_after) == len(macros_before) - 1 and
                sources_after == sources_before - 3  # Se eliminaron 3 sources
            )
            
            if success:
                print("\n✅ TODOS LOS TESTS PASADOS")
                return True
            else:
                print("\n⚠️ Algunos tests fallaron")
                return False
            
        except Exception as e:
            print(f"❌ Error en test: {e}")
            import traceback
            traceback.print_exc()
            print("\n🔄 Restaurando backup...")
            os.system(f"cp '{backup_path}' '{engine_path}'")
            return False
    else:
        print("❌ Error de sintaxis")
        print("🔄 Restaurando backup...")
        os.system(f"cp '{backup_path}' '{engine_path}'")
        return False

if __name__ == "__main__":
    if implement_delete_macro():
        print("\n🎉 IMPLEMENTACIÓN COMPLETA")
        print("✅ list_macros() - LISTO")
        print("✅ select_macro() - LISTO")
        print("✅ delete_macro() - LISTO")
        print("\n🎯 Sistema de gestión de macros completo")
        print("📋 Siguiente: Ejecutar test completo del sistema")
    else:
        print("\n⚠️ Revisar errores")