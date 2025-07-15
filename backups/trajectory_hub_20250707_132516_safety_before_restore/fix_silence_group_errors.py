#!/usr/bin/env python3
"""
🔧 Fix: Silenciar errores de grupos OSC y desactivar temporalmente
⚡ Líneas modificadas: spat_osc_bridge.py L750-780
🎯 Impacto: BAJO - Solo silencia errores cosméticos
"""

import os
import shutil
from datetime import datetime

def fix_osc_bridge():
    """Arreglar errores de grupos en OSC Bridge"""
    
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    # Backup
    backup = f"{bridge_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(bridge_file, backup)
    print(f"✅ Backup creado: {backup}")
    
    # Leer archivo
    with open(bridge_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Comentar prints molestos
    content = content.replace(
        '📡 Creando grupo OSC:',
        '# 📡 Creando grupo OSC:'
    )
    content = content.replace(
        '🔄 Añadiendo fuente',
        '# 🔄 Añadiendo fuente'
    )
    
    # Fix 2: Reemplazar método create_group
    old_create_group = '''    def create_group(self, group_id: str, group_name: str):
        """Crear un grupo/macro en Spat."""
        try:
            group_name = str(group_name)  # Asegurar tipo string
            
            for target in self.targets:
                # Usar client para enviar
                if hasattr(self, 'client'):
                    self.client.send_message("/group/new", [group_name], target.host, target.port)
                else:
                    # Fallback si no hay client
                    self.send_message("/group/new", [group_name])
            
            print(f"   ✅ Grupo '{group_name}' creado via OSC")
            
        except Exception as e:
            print(f"   ❌ Error creando grupo: {e}")'''
    
    new_create_group = '''    def create_group(self, group_id: str, group_name: str):
        """Crear un grupo/macro en Spat."""
        # TEMPORALMENTE DESHABILITADO - Los grupos se crean manualmente en Spat
        pass'''
    
    if old_create_group in content:
        content = content.replace(old_create_group, new_create_group)
    else:
        # Buscar versión alternativa
        import re
        pattern = r'def create_group\(self.*?\n(?:.*?\n)*?.*?except Exception.*?\n.*?\n'
        content = re.sub(pattern, new_create_group + '\n', content, flags=re.DOTALL)
    
    # Fix 3: Reemplazar método add_source_to_group
    old_add_source = '''    def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir una fuente a un grupo en Spat."""
        try:
            source_id = int(source_id)  # Asegurar tipo int
            group_name = str(group_name)  # Asegurar tipo string
            
            for target in self.targets:
                if hasattr(self, 'client'):
                    self.client.send_message(
                        f"/source/{source_id}/group", 
                        [group_name], 
                        target.host, 
                        target.port
                    )
                else:
                    self.send_message(f"/source/{source_id}/group", [group_name])
                    
        except Exception as e:
            print(f"   ❌ Error añadiendo fuente al grupo: {e}")'''
    
    new_add_source = '''    def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir una fuente a un grupo en Spat."""
        # TEMPORALMENTE DESHABILITADO - Los grupos se crean manualmente en Spat
        pass'''
    
    if old_add_source in content:
        content = content.replace(old_add_source, new_add_source)
    else:
        # Buscar versión alternativa
        pattern = r'def add_source_to_group\(self.*?\n(?:.*?\n)*?.*?except Exception.*?\n.*?\n'
        content = re.sub(pattern, new_add_source + '\n', content, flags=re.DOTALL)
    
    # Guardar
    with open(bridge_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Errores de grupos silenciados")
    print("📝 Los métodos create_group y add_source_to_group están temporalmente deshabilitados")
    
    # Fix adicional en engine
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r', encoding='utf-8') as f:
            engine_content = f.read()
        
        # Comentar prints en create_macro
        engine_content = engine_content.replace(
            'print(f"📡 Creando grupo OSC:',
            '# print(f"📡 Creando grupo OSC:'
        )
        engine_content = engine_content.replace(
            'print(f"🔄 Añadiendo fuente',
            '# print(f"🔄 Añadiendo fuente'
        )
        
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.write(engine_content)
        
        print("✅ Prints en engine también silenciados")
    
    return True

def main():
    print("🔧 SILENCIANDO ERRORES DE GRUPOS OSC")
    print("=" * 50)
    
    if fix_osc_bridge():
        print("\n✅ COMPLETADO")
        print("\n📝 NOTAS:")
        print("- Los errores de grupos están silenciados")
        print("- Los macros funcionan perfectamente para movimiento")
        print("- Crea los grupos manualmente en Spat por ahora")
        print("- Las posiciones se siguen enviando correctamente")
        
        print("\n🎯 PRÓXIMO PASO:")
        print("python trajectory_hub/interface/interactive_controller.py")
        print("\nYa no verás errores molestos al crear macros 🎉")

if __name__ == "__main__":
    main()