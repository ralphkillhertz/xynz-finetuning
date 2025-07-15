#!/usr/bin/env python3
"""
🔧 Implementa list_macros() en la posición exacta
⚡ Inserta después de línea 428, antes de _apply_formation
🎯 Impacto: BAJO - Solo lectura
"""

import os
import datetime

def implement_list_macros():
    """Implementa list_macros en la posición correcta"""
    
    print("🔧 IMPLEMENTANDO list_macros()")
    print("=" * 60)
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{engine_path}.backup_before_list_macros_{timestamp}"
    os.system(f"cp '{engine_path}' '{backup_path}'")
    print(f"✅ Backup: {backup_path}")
    
    # Leer archivo
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Verificar que no existe
    content = ''.join(lines)
    if 'def list_macros' in content:
        print("⚠️ list_macros ya existe")
        return False
    
    # Código a insertar (con indentación correcta de 4 espacios)
    list_macros_code = '''    def list_macros(self):
        """Lista todos los macros activos con información detallada
        
        Returns:
            list: Lista de diccionarios con info de cada macro
        """
        macro_list = []
        
        for macro_key, macro in self._macros.items():
            # Extraer nombre limpio del macro
            # Formato esperado: macro_N_nombre
            parts = macro_key.split('_', 2)
            macro_name = parts[2] if len(parts) > 2 else macro_key
            
            # Determinar formación basándose en el nombre
            formation = "unknown"
            formations = ["circle", "line", "grid", "spiral", "random", "sphere"]
            for form in formations:
                if form in macro_name.lower():
                    formation = form
                    break
            
            # Recopilar información del macro
            macro_info = {
                'key': macro_key,  # ID completo
                'name': macro_name,  # Nombre limpio
                'num_sources': len(macro.source_ids) if hasattr(macro, 'source_ids') else 0,
                'source_ids': list(macro.source_ids) if hasattr(macro, 'source_ids') else [],
                'behavior': macro.behavior_name if hasattr(macro, 'behavior_name') else 'unknown',
                'formation': formation
            }
            macro_list.append(macro_info)
        
        return macro_list

'''
    
    # Insertar después de la línea 428 (índice 427)
    # Añadir línea en blanco antes si no la hay
    if lines[428].strip() != '':
        lines.insert(428, '\n')
        lines.insert(429, list_macros_code)
    else:
        lines.insert(429, list_macros_code)
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ list_macros() insertado después de create_macro()")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis...")
    result = os.system(f"python -m py_compile '{engine_path}' 2>&1")
    
    if result == 0:
        print("✅ Sintaxis correcta")
        
        # Test
        print("\n🧪 Probando list_macros()...")
        try:
            from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
            engine = EnhancedTrajectoryEngine()
            
            # Test sin macros
            empty_list = engine.list_macros()
            print(f"   Sin macros: {len(empty_list)} ✅")
            
            # Test con macros
            engine.start()
            engine.create_macro("test_list", 3, formation="circle")
            
            macros = engine.list_macros()
            print(f"   Con macros: {len(macros)} macros")
            
            if macros:
                macro = macros[0]
                print(f"   Ejemplo: {macro['name']} ({macro['num_sources']} sources)")
                print(f"   Key: {macro['key']}")
            
            engine.stop()
            
            print("\n✅ IMPLEMENTACIÓN EXITOSA")
            return True
            
        except Exception as e:
            print(f"❌ Error en test: {e}")
            print("🔄 Restaurando backup...")
            os.system(f"cp '{backup_path}' '{engine_path}'")
            return False
    else:
        print("❌ Error de sintaxis")
        print("🔄 Restaurando backup...")
        os.system(f"cp '{backup_path}' '{engine_path}'")
        return False

if __name__ == "__main__":
    if implement_list_macros():
        print("\n🎯 list_macros() implementado correctamente")
        print("📋 Siguiente paso: Analizar dónde insertar select_macro()")
    else:
        print("\n⚠️ Revisar errores")