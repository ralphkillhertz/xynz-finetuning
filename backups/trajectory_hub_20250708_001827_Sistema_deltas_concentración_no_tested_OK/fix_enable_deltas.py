# === fix_enable_deltas.py ===
# 🔧 Fix: Activa el sistema de deltas en el update del engine
# ⚡ Impacto: CRÍTICO - Sin esto, los componentes no mueven las fuentes

import os
import re
from datetime import datetime

def diagnose_update_method():
    """Diagnostica el método update del engine"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    print("🔍 Analizando método update()...")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar método update
    pattern = r'def update\(self[^)]*\):(.*?)(?=\n\s{0,4}def|\n\s{0,4}async def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        update_content = match.group(1)
        
        # Verificar qué hay en update
        checks = {
            'update_with_deltas': 'update_with_deltas' in update_content,
            'motion.update': 'motion.update' in update_content,
            'calculate_delta': 'calculate_delta' in update_content,
            'motion_states loop': 'for.*motion_states' in update_content or 'motion_states.items()' in update_content
        }
        
        print("\n📋 Contenido del método update:")
        for check, present in checks.items():
            status = "✅" if present else "❌"
            print(f"  {status} {check}")
        
        return update_content, checks
    else:
        print("❌ No se encontró método update")
        return None, {}

def fix_update_method():
    """Arregla el método update para usar deltas"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅ Backup creado: {backup_path}")
    
    # Buscar el método update completo
    pattern = r'(def update\(self[^)]*\):)(.*?)(?=\n\s{0,4}def|\n\s{0,4}async def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró método update")
        return False
    
    # Nuevo método update con sistema de deltas
    new_update = '''def update(self) -> None:
        """Actualiza el sistema con soporte para deltas"""
        if not self.running:
            return
        
        current_time = time.time()
        dt = 1.0 / self._update_rate
        
        # Actualizar cada SourceMotion y recolectar deltas
        all_deltas = []
        
        for source_id, motion in self.motion_states.items():
            if isinstance(motion, SourceMotion):
                # Actualizar el SourceMotion (que actualiza sus componentes)
                deltas = motion.update_with_deltas(current_time, dt)
                all_deltas.extend(deltas)
        
        # Aplicar todos los deltas a las posiciones
        for delta in all_deltas:
            if delta.source_id < len(self._positions):
                # Aplicar delta de posición
                if delta.position is not None:
                    self._positions[delta.source_id] += delta.position
                
                # Aplicar delta de orientación si existe
                if hasattr(self, '_orientations') and delta.orientation is not None:
                    self._orientations[delta.source_id] += delta.orientation
        
        # Enviar actualizaciones OSC
        self._send_osc_updates()
        
        # Actualizar estadísticas
        self._frame_count += 1
        self._time = current_time'''
    
    # Reemplazar el método completo
    indent = '    '  # Asumiendo indentación de clase
    new_update_indented = '\n'.join(indent + line if line else line 
                                   for line in new_update.split('\n'))
    
    # Encontrar los límites del método
    method_start = match.start()
    method_end = match.end()
    
    # Reemplazar
    new_content = content[:method_start] + new_update_indented + content[method_end:]
    
    # Verificar que tenemos los imports necesarios
    if 'import time' not in new_content:
        # Añadir import al principio
        import_pos = new_content.find('import')
        if import_pos > -1:
            new_content = new_content[:import_pos] + 'import time\n' + new_content[import_pos:]
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Método update reemplazado con soporte de deltas")
    
    # Verificar sintaxis
    try:
        compile(new_content, engine_path, 'exec')
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
    print("🔧 FIX PARA ACTIVAR SISTEMA DE DELTAS")
    print("="*60)
    
    # Primero diagnosticar
    update_content, checks = diagnose_update_method()
    
    if not checks.get('update_with_deltas', False):
        print("\n⚠️ El sistema de deltas NO está activo en update()")
        print("🔧 Aplicando fix...")
        
        success = fix_update_method()
        
        if success:
            print("\n✅ Sistema de deltas activado!")
            print("\n🎯 MOMENTO DE LA VERDAD - Prueba ahora:")
            print("$ python test_delta_concentration_final.py")
            print("\n🤞 Las fuentes deberían moverse hacia el centro!")
        else:
            print("\n❌ Error al aplicar fix")
    else:
        print("\n✅ El sistema de deltas ya está activo")
        print("🤔 El problema debe estar en otro lugar")