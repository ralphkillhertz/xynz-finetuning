#!/usr/bin/env python3
# 🔧 Fix: Implementar gestión completa de macros
# ⚡ Añadir métodos list, select, delete
# 🎯 Impacto: ALTO

import os
import shutil
from datetime import datetime

def implement_macro_management():
    print("\n🔧 IMPLEMENTANDO GESTIÓN DE MACROS")
    print("=" * 60)
    
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    # Leer archivo
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar dónde insertar los nuevos métodos (después de create_macro)
    insert_line = None
    for i, line in enumerate(lines):
        if 'def create_macro' in line:
            # Buscar el final del método
            indent_count = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                if lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) <= indent_count:
                    insert_line = j
                    break
    
    if insert_line:
        # Código a insertar
        new_methods = '''
    def list_macros(self) -> dict:
        """Lista todos los macros activos con información detallada"""
        macro_info = {}
        for key, macro in self._macros.items():
            # Extraer nombre limpio
            parts = key.split('_', 2)
            clean_name = parts[2] if len(parts) > 2 else macro.name
            
            macro_info[key] = {
                'name': clean_name,
                'source_count': len(macro.source_ids),
                'source_ids': list(macro.source_ids),
                'behavior': macro.behavior_name,
                'concentration_active': macro.concentration_active
            }
        return macro_info
    
    def select_macro(self, macro_key: str) -> dict:
        """Selecciona un macro específico y retorna su información"""
        if macro_key not in self._macros:
            # Intentar buscar por nombre parcial
            for key in self._macros:
                if macro_key in key:
                    macro_key = key
                    break
            else:
                return {'error': f'Macro "{macro_key}" no encontrado'}
        
        macro = self._macros[macro_key]
        # Obtener posiciones actuales de las sources
        positions = {}
        for sid in macro.source_ids:
            if sid in self._sources:
                source = self._sources[sid]
                state = source.motion_engine.sample()
                positions[sid] = {
                    'name': source.name,
                    'position': state.position.tolist()
                }
        
        return {
            'key': macro_key,
            'name': macro.name,
            'source_count': len(macro.source_ids),
            'source_ids': list(macro.source_ids),
            'behavior': macro.behavior_name,
            'positions': positions,
            'concentration_active': macro.concentration_active
        }
    
    def delete_macro(self, macro_key: str) -> dict:
        """Elimina un macro y todas sus sources"""
        if macro_key not in self._macros:
            # Intentar buscar por nombre parcial
            for key in self._macros:
                if macro_key in key:
                    macro_key = key
                    break
            else:
                return {'error': f'Macro "{macro_key}" no encontrado'}
        
        macro = self._macros[macro_key]
        deleted_sources = []
        
        # Eliminar todas las sources del macro
        for source_id in list(macro.source_ids):
            if source_id in self._sources:
                # Remover de sources activas
                self._active_sources.discard(source_id)
                # Remover de diccionario de sources
                del self._sources[source_id]
                deleted_sources.append(source_id)
        
        # Eliminar el macro
        del self._macros[macro_key]
        
        # Actualizar macro_index si es necesario
        if hasattr(self, '_macro_index'):
            self._macro_index = max(0, self._macro_index - 1)
        
        return {
            'success': True,
            'deleted_macro': macro_key,
            'deleted_sources': deleted_sources,
            'remaining_macros': len(self._macros),
            'remaining_sources': len(self._active_sources)
        }'''
        
        # Insertar los nuevos métodos
        lines.insert(insert_line, new_methods)
        
        # Escribir archivo actualizado
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Métodos añadidos:")
        print("   - list_macros(): Lista todos los macros")
        print("   - select_macro(key): Selecciona y muestra info de un macro")
        print("   - delete_macro(key): Elimina un macro y sus sources")
        print("\n⚡ Los métodos ya están disponibles en el engine")
    else:
        print("❌ No se pudo encontrar dónde insertar los métodos")

if __name__ == "__main__":
    implement_macro_management()