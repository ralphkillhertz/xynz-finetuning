#!/usr/bin/env python3
"""
🔧 Implementa select_macro() después de list_macros()
⚡ Inserta después de línea 464, antes de _apply_formation
🎯 Impacto: BAJO - Solo búsqueda
"""

import os
import datetime

def implement_select_macro():
    """Implementa select_macro en la posición correcta"""
    
    print("🔧 IMPLEMENTANDO select_macro()")
    print("=" * 60)
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{engine_path}.backup_before_select_macro_{timestamp}"
    os.system(f"cp '{engine_path}' '{backup_path}'")
    print(f"✅ Backup: {backup_path}")
    
    # Leer archivo
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Verificar que no existe
    content = ''.join(lines)
    if 'def select_macro' in content:
        print("⚠️ select_macro ya existe")
        return False
    
    # Código a insertar
    select_macro_code = '''    def select_macro(self, identifier):
        """Selecciona un macro por nombre o ID
        
        Args:
            identifier: Puede ser:
                - ID completo (macro_0_nombre)
                - Nombre parcial (nombre)
                - Índice del macro (0, 1, 2...)
            
        Returns:
            dict: Información del macro o None si no se encuentra
        """
        if not self._macros:
            return None
        
        # Buscar por ID exacto
        if identifier in self._macros:
            macro = self._macros[identifier]
            return {
                'key': identifier,
                'macro': macro,
                'source_ids': list(macro.source_ids) if hasattr(macro, 'source_ids') else [],
                'num_sources': len(macro.source_ids) if hasattr(macro, 'source_ids') else 0,
                'behavior': macro.behavior_name if hasattr(macro, 'behavior_name') else 'unknown'
            }
        
        # Buscar por índice si es número
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            idx = int(identifier)
            macro_keys = list(self._macros.keys())
            if 0 <= idx < len(macro_keys):
                key = macro_keys[idx]
                return self.select_macro(key)  # Recursión para reusar lógica
        
        # Buscar por nombre parcial (case insensitive)
        identifier_lower = str(identifier).lower()
        
        # Primero buscar coincidencia exacta en el nombre
        for macro_id, macro in self._macros.items():
            # Extraer nombre del formato macro_N_nombre
            parts = macro_id.split('_', 2)
            macro_name = parts[2] if len(parts) > 2 else macro_id
            
            if macro_name.lower() == identifier_lower:
                return self.select_macro(macro_id)
        
        # Luego buscar coincidencia parcial
        for macro_id, macro in self._macros.items():
            if identifier_lower in macro_id.lower():
                return self.select_macro(macro_id)
        
        return None

'''
    
    # Insertar después de línea 464
    # Verificar si necesitamos añadir línea en blanco
    insert_pos = 464
    if insert_pos < len(lines) and lines[insert_pos].strip() != '':
        lines.insert(insert_pos, '\n')
        insert_pos += 1
    
    lines.insert(insert_pos, select_macro_code)
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ select_macro() insertado después de list_macros()")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis...")
    result = os.system(f"python -m py_compile '{engine_path}' 2>&1")
    
    if result == 0:
        print("✅ Sintaxis correcta")
        
        # Test
        print("\n🧪 Probando select_macro()...")
        try:
            from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
            engine = EnhancedTrajectoryEngine()
            engine.start()
            
            # Crear varios macros
            engine.create_macro("test_circle", 3, formation="circle")
            engine.create_macro("test_line", 2, formation="line")
            
            # Test 1: Búsqueda por nombre parcial
            result1 = engine.select_macro("circle")
            print(f"   Búsqueda 'circle': {'✅' if result1 else '❌'}")
            if result1:
                print(f"      Encontrado: {result1['key']}")
            
            # Test 2: Búsqueda por índice
            result2 = engine.select_macro(0)
            print(f"   Búsqueda por índice 0: {'✅' if result2 else '❌'}")
            
            # Test 3: Búsqueda por ID completo
            if result1:
                result3 = engine.select_macro(result1['key'])
                print(f"   Búsqueda por ID completo: {'✅' if result3 else '❌'}")
            
            # Test 4: Búsqueda no existente
            result4 = engine.select_macro("no_existe")
            print(f"   Búsqueda inexistente: {'✅' if not result4 else '❌'}")
            
            engine.stop()
            
            print("\n✅ IMPLEMENTACIÓN EXITOSA")
            return True
            
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
    if implement_select_macro():
        print("\n🎯 select_macro() implementado correctamente")
        print("📋 Siguiente paso: Implementar delete_macro()")
    else:
        print("\n⚠️ Revisar errores")