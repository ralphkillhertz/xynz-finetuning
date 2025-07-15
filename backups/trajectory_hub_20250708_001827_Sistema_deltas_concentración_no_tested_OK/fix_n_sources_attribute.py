# === test_diagnostic_attributes.py ===
# Test para diagnosticar atributos del engine

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🔍 DIAGNÓSTICO DE ATRIBUTOS")
print("="*50)

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Verificar atributos relacionados con sources
    attrs_to_check = ['n_sources', 'max_sources', '_max_sources', 'n_max_sources', '_n_sources']
    
    print("\n📋 Atributos de sources:")
    for attr in attrs_to_check:
        if hasattr(engine, attr):
            value = getattr(engine, attr)
            print(f"  ✅ {attr}: {value}")
        else:
            print(f"  ❌ {attr}: NO EXISTE")
    
    # Verificar otros atributos importantes
    print("\n📋 Otros atributos importantes:")
    other_attrs = ['_active_sources', 'motion_states', '_positions']
    for attr in other_attrs:
        if hasattr(engine, attr):
            print(f"  ✅ {attr}: existe")
        else:
            print(f"  ❌ {attr}: NO EXISTE")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
# === fix_n_sources_attribute.py ===
# 🔧 Fix: Corrige el nombre del atributo n_sources
# ⚡ Impacto: BAJO - Simple cambio de nombre de atributo

import os
import re
from datetime import datetime

def fix_n_sources():
    """Arregla el atributo n_sources en create_source"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar cómo se llama realmente el atributo
    print("\n🔍 Buscando atributo correcto...")
    
    # Buscar en __init__
    init_pattern = r'def __init__\(self[^)]*\):(.*?)(?=\n\s{0,4}def|\nclass|\Z)'
    init_match = re.search(init_pattern, content, re.DOTALL)
    
    if init_match:
        init_content = init_match.group(1)
        
        # Buscar posibles nombres
        candidates = []
        if 'self.max_sources' in init_content:
            candidates.append('max_sources')
        if 'self._max_sources' in init_content:
            candidates.append('_max_sources')
        if 'self.n_max_sources' in init_content:
            candidates.append('n_max_sources')
        if 'self._n_sources' in init_content:
            candidates.append('_n_sources')
            
        # Buscar pattern n_sources = 
        n_sources_pattern = r'n_sources\s*[:=]\s*(\w+)'
        n_sources_match = re.search(n_sources_pattern, init_content)
        if n_sources_match:
            # n_sources es un parámetro, buscar dónde se guarda
            param_name = n_sources_match.group(1)
            store_pattern = rf'self\.(\w+)\s*=\s*{param_name}'
            store_match = re.search(store_pattern, init_content)
            if store_match:
                candidates.append(store_match.group(1))
        
        if candidates:
            attr_name = candidates[0]
            print(f"✅ Encontrado atributo: self.{attr_name}")
        else:
            # Default común
            attr_name = 'max_sources'
            print(f"⚠️ No se encontró, usando default: self.{attr_name}")
    else:
        attr_name = 'max_sources'
        print(f"⚠️ No se encontró __init__, usando default: self.{attr_name}")
    
    # Reemplazar en create_source
    if attr_name != 'n_sources':
        content = content.replace('self.n_sources', f'self.{attr_name}')
        print(f"✅ Reemplazado self.n_sources por self.{attr_name}")
    
    # También buscar y arreglar self._active_sources si no existe
    if 'self._active_sources.add(' in content and 'self._active_sources = ' not in content:
        # Necesitamos inicializar _active_sources en __init__
        print("\n🔧 Añadiendo inicialización de _active_sources...")
        
        # Buscar el final del __init__
        if init_match:
            # Buscar última línea con self.algo = 
            lines = init_content.split('\n')
            last_init_line = -1
            for i, line in enumerate(lines):
                if 'self.' in line and '=' in line:
                    last_init_line = i
            
            if last_init_line >= 0:
                # Insertar después de la última inicialización
                indent = ' ' * 8  # Asumiendo indentación estándar
                new_line = f"\n{indent}# Conjunto de fuentes activas\n{indent}self._active_sources = set()"
                
                # Reconstruir init_content
                lines.insert(last_init_line + 1, new_line)
                new_init = '\n'.join(lines)
                
                # Reemplazar en content
                content = content[:init_match.start(1)] + new_init + content[init_match.end(1):]
                print("✅ _active_sources inicializado")
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar sintaxis
    try:
        compile(content, engine_path, 'exec')
        print("\n✅ Sintaxis verificada correctamente")
        return True
    except SyntaxError as e:
        print(f"\n❌ Error de sintaxis: {e}")
        # Restaurar backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

def create_diagnostic_test():
    """Crea test de diagnóstico para verificar atributos"""
    test_code = '''# === test_diagnostic_attributes.py ===
# Test para diagnosticar atributos del engine

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🔍 DIAGNÓSTICO DE ATRIBUTOS")
print("="*50)

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    print("✅ Engine creado")
    
    # Verificar atributos relacionados con sources
    attrs_to_check = ['n_sources', 'max_sources', '_max_sources', 'n_max_sources', '_n_sources']
    
    print("\\n📋 Atributos de sources:")
    for attr in attrs_to_check:
        if hasattr(engine, attr):
            value = getattr(engine, attr)
            print(f"  ✅ {attr}: {value}")
        else:
            print(f"  ❌ {attr}: NO EXISTE")
    
    # Verificar otros atributos importantes
    print("\\n📋 Otros atributos importantes:")
    other_attrs = ['_active_sources', 'motion_states', '_positions']
    for attr in other_attrs:
        if hasattr(engine, attr):
            print(f"  ✅ {attr}: existe")
        else:
            print(f"  ❌ {attr}: NO EXISTE")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open('test_diagnostic_attributes.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test diagnóstico creado: test_diagnostic_attributes.py")

if __name__ == "__main__":
    print("🔧 FIX DE ATRIBUTO N_SOURCES")
    print("="*60)
    
    # Primero crear test diagnóstico
    create_diagnostic_test()
    print("\n💡 Ejecuta primero el diagnóstico:")
    print("$ python test_diagnostic_attributes.py")
    print("\n¿Continuar con el fix? (s/n): ", end='')
    
    response = input().strip().lower()
    
    if response == 's':
        # Aplicar fix
        success = fix_n_sources()
        
        if success:
            print("\n✅ Fix aplicado exitosamente")
            print("\n📋 Prueba ahora:")
            print("$ python test_delta_concentration_final.py")
        else:
            print("\n❌ Error al aplicar fix")
    else:
        print("\n❌ Fix cancelado")
        print("Ejecuta el diagnóstico primero para ver qué atributos existen")