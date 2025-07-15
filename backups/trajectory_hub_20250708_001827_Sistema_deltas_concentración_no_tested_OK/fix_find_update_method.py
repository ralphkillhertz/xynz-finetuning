# === fix_find_update_method.py ===
# 🔧 Fix: Encuentra el método de actualización real y activa deltas
# ⚡ Impacto: CRÍTICO - Encuentra y arregla el método correcto

import os
import re
from datetime import datetime

def find_update_methods():
    """Busca todos los métodos relacionados con actualización"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return []
    
    print("🔍 Buscando métodos de actualización...")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todos los métodos
    method_pattern = r'def (\w+)\(self[^)]*\):'
    methods = re.findall(method_pattern, content)
    
    # Filtrar métodos relacionados con update/step
    update_methods = []
    keywords = ['update', 'step', 'tick', 'advance', 'process', 'run']
    
    for method in methods:
        for keyword in keywords:
            if keyword in method.lower():
                update_methods.append(method)
                break
    
    print(f"\n📋 Métodos encontrados relacionados con actualización:")
    for method in update_methods:
        print(f"  - {method}")
    
    # También buscar qué método se llama desde el test
    if 'engine.update(' in content or 'self.update(' in content:
        print("\n✅ Se usa 'update' en el código")
    if 'engine.step(' in content or 'self.step(' in content:
        print("\n✅ Se usa 'step' en el código")
    
    return update_methods, content

def check_test_usage():
    """Verifica qué método usa el test"""
    
    test_path = "test_delta_concentration_final.py"
    
    if os.path.exists(test_path):
        with open(test_path, 'r', encoding='utf-8') as f:
            test_content = f.read()
        
        if 'engine.update(' in test_content:
            print("\n📌 El test usa engine.update()")
            return 'update'
        elif 'engine.step(' in test_content:
            print("\n📌 El test usa engine.step()")
            return 'step'
    
    return None

def add_or_fix_update_method():
    """Añade o arregla el método update"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅ Backup creado: {backup_path}")
    
    # Verificar si existe update
    if 'def update(' not in content:
        print("\n⚠️ No existe método update, creándolo...")
        
        # Buscar dónde insertar (después de __init__ o create_source)
        insert_pattern = r'(def create_source.*?\n.*?return.*?\n)'
        match = re.search(insert_pattern, content, re.DOTALL)
        
        if match:
            insert_pos = match.end()
        else:
            # Buscar después de __init__
            init_pattern = r'(def __init__.*?\n(?:.*?\n)*?)\n\s{0,4}def'
            init_match = re.search(init_pattern, content, re.DOTALL)
            if init_match:
                insert_pos = init_match.end(1)
            else:
                print("❌ No se puede determinar dónde insertar update")
                return False
        
        # Nuevo método update
        update_method = '''
    def update(self) -> None:
        """Actualiza el sistema con soporte para deltas"""
        if not self.running:
            return
        
        current_time = time.time()
        dt = 1.0 / self._update_rate
        
        # Sistema de deltas para composición de movimientos
        all_deltas = []
        
        # Actualizar cada SourceMotion y recolectar deltas
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                if deltas:
                    all_deltas.extend(deltas)
        
        # Aplicar todos los deltas a las posiciones
        for delta in all_deltas:
            if delta.source_id < len(self._positions):
                if delta.position is not None:
                    self._positions[delta.source_id] += delta.position
        
        # Enviar actualizaciones OSC si está habilitado
        if hasattr(self, '_send_osc_updates'):
            self._send_osc_updates()
        
        # Actualizar estadísticas
        if hasattr(self, '_frame_count'):
            self._frame_count += 1
        if hasattr(self, '_time'):
            self._time = current_time
'''
        
        # Insertar
        content = content[:insert_pos] + update_method + content[insert_pos:]
        print("✅ Método update creado")
        
    else:
        print("\n✅ Método update existe, actualizándolo...")
        
        # Reemplazar método existente
        pattern = r'(def update\(self[^)]*\):)(.*?)(?=\n\s{0,4}def|\n\s{0,4}async def|\nclass|\Z)'
        
        def replace_update(match):
            method_def = match.group(1)
            old_content = match.group(2)
            
            # Verificar si ya tiene deltas
            if 'update_with_deltas' in old_content:
                print("   ✅ Ya tiene soporte de deltas")
                return match.group(0)
            
            # Nueva implementación
            new_content = '''
        """Actualiza el sistema con soporte para deltas"""
        if not self.running:
            return
        
        current_time = time.time()
        dt = 1.0 / self._update_rate
        
        # Sistema de deltas para composición de movimientos
        all_deltas = []
        
        # Actualizar cada SourceMotion y recolectar deltas
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                if deltas:
                    all_deltas.extend(deltas)
        
        # Aplicar todos los deltas a las posiciones
        for delta in all_deltas:
            if delta.source_id < len(self._positions):
                if delta.position is not None:
                    self._positions[delta.source_id] += delta.position
        
        # Código original si hay algo importante
''' + old_content.strip()
            
            return method_def + new_content
        
        content = re.sub(pattern, replace_update, content, flags=re.DOTALL)
    
    # Verificar imports
    if 'import time' not in content:
        content = 'import time\n' + content
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar sintaxis
    try:
        compile(content, engine_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

if __name__ == "__main__":
    print("🔧 ACTIVAR SISTEMA DE DELTAS EN UPDATE")
    print("="*60)
    
    # Verificar qué método usa el test
    test_method = check_test_usage()
    
    # Buscar métodos existentes
    methods, content = find_update_methods()
    
    # Aplicar fix
    print("\n🔧 Aplicando fix...")
    success = add_or_fix_update_method()
    
    if success:
        print("\n✅ Sistema de deltas activado!")
        print("\n🎯 ESTE ES EL MOMENTO - Las fuentes deberían moverse ahora!")
        print("\n🚀 Ejecuta:")
        print("$ python test_delta_concentration_final.py")
        print("\n🤞 Si funciona, verás las distancias disminuir de 10.00 a ~2.00")
    else:
        print("\n❌ Error al activar deltas")