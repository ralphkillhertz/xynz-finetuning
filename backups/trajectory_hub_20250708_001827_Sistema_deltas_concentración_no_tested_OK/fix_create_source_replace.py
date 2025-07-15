# === fix_create_source_replace.py ===
# 🔧 Fix: Reemplaza create_source con versión funcional mínima
# ⚡ Impacto: CRÍTICO - Implementa versión sin components

import os
import re
from datetime import datetime

def replace_create_source():
    """Reemplaza create_source con versión funcional"""
    
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
    
    # Nueva implementación de create_source
    new_create_source = '''    def create_source(self, source_id: int, name: str = None) -> 'SourceMotion':
        """Crea una nueva fuente de sonido"""
        if source_id >= self.n_sources:
            raise ValueError(f"ID {source_id} excede el máximo de fuentes ({self.n_sources})")
        
        if source_id in self.motion_states:
            print(f"⚠️ Fuente {source_id} ya existe")
            return self.motion_states[source_id]
        
        # Crear estado inicial
        state = MotionState()
        state.source_id = source_id
        state.position = self._positions[source_id].copy()
        state.velocity = np.zeros(3)
        state.name = name or f"source_{source_id}"
        
        # Crear SourceMotion básico
        motion = SourceMotion(source_id, state)
        
        # Inicializar componentes básicos si motion tiene el atributo
        if hasattr(motion, 'components'):
            # Por ahora no añadimos componentes para evitar errores
            pass
        
        # Registrar
        self.motion_states[source_id] = motion
        self._active_sources.add(source_id)
        
        # Notificar al bridge OSC
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            self.osc_bridge.source_created(source_id, state.name)
        
        print(f"✅ Fuente {source_id} creada: {state.name}")
        return motion'''
    
    # Buscar y reemplazar el método completo
    # Patrón mejorado para capturar todo el método
    pattern = r'(\s*)def create_source\(self[^:]*\):[^\n]*\n((?:\1(?:\s|\t)+.*\n)*)'
    
    match = re.search(pattern, content)
    
    if not match:
        print("❌ No se encuentra el patrón de create_source")
        # Intento alternativo
        start = content.find('def create_source(')
        if start == -1:
            print("❌ No se encuentra create_source en absoluto")
            return False
        
        # Encontrar el siguiente def al mismo nivel
        indent_match = re.match(r'(\s*)def', content[start:])
        if indent_match:
            base_indent = len(indent_match.group(1))
            
            # Buscar siguiente método
            next_method = re.search(f'\n{" " * base_indent}def ', content[start + 10:])
            if next_method:
                end = start + 10 + next_method.start()
            else:
                # Buscar class o final
                next_class = content.find('\nclass ', start)
                if next_class != -1:
                    end = next_class
                else:
                    end = len(content)
            
            # Reemplazar
            content = content[:start] + new_create_source + content[end:]
            print("✅ create_source reemplazado (método alternativo)")
    else:
        # Reemplazar usando el match
        content = content[:match.start()] + new_create_source + content[match.end():]
        print("✅ create_source reemplazado")
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar sintaxis
    try:
        compile(content, engine_path, 'exec')
        print("✅ Sintaxis verificada correctamente")
        return True
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
        # Restaurar backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

def verify_imports():
    """Verifica que todos los imports necesarios estén presentes"""
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_imports = [
        ('MotionState', 'from trajectory_hub.core.motion_components import MotionState'),
        ('SourceMotion', 'from trajectory_hub.core.motion_components import SourceMotion'),
        ('np', 'import numpy as np')
    ]
    
    missing = []
    for name, import_line in required_imports:
        if name not in content:
            missing.append(import_line)
    
    if missing:
        print("\n⚠️ Imports faltantes detectados:")
        for imp in missing:
            print(f"  - {imp}")
    
    return len(missing) == 0

if __name__ == "__main__":
    print("🔧 REEMPLAZO COMPLETO DE CREATE_SOURCE")
    print("="*60)
    
    # Verificar imports primero
    imports_ok = verify_imports()
    
    if not imports_ok:
        print("\n⚠️ Hay imports faltantes, pero continuando...")
    
    success = replace_create_source()
    
    if success:
        print("\n✅ create_source reemplazado exitosamente")
        print("\n📋 Prueba ahora:")
        print("$ python test_delta_concentration_final.py")
        print("\nSi aún falla, ejecuta:")
        print("$ python test_delta_minimal.py")
    else:
        print("\n❌ Error al reemplazar create_source")
        print("\n🔧 Alternativa: edita manualmente enhanced_trajectory_engine.py")
        print("Busca 'def create_source' y reemplaza todo el método con:")
        print("-" * 60)
        print(new_create_source)
        print("-" * 60)