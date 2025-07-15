# === fix_create_source_manual.py ===
# 🔧 Fix: Diagnóstico detallado y reemplazo manual de create_source
# ⚡ Impacto: CRÍTICO - Solución definitiva

import os
import re
from datetime import datetime

def diagnose_create_source():
    """Diagnóstica el problema con create_source"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    print("🔍 Analizando archivo...")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar create_source
    start_line = -1
    for i, line in enumerate(lines):
        if 'def create_source(' in line:
            start_line = i
            print(f"✅ Encontrado create_source en línea {i+1}")
            break
    
    if start_line == -1:
        print("❌ No se encuentra create_source")
        return False
    
    # Detectar indentación
    indent_match = re.match(r'^(\s*)def', lines[start_line])
    base_indent = len(indent_match.group(1)) if indent_match else 0
    print(f"📏 Indentación base: {base_indent} espacios")
    
    # Buscar el final del método
    end_line = start_line + 1
    method_indent = base_indent + 4  # Asumiendo 4 espacios
    
    while end_line < len(lines):
        line = lines[end_line]
        # Si encontramos algo al mismo nivel que def, terminamos
        if line.strip() and not line.startswith(' ' * method_indent) and not line.strip().startswith('#'):
            # Verificar si es otro método o clase
            if re.match(r'^' + ' ' * base_indent + r'(def|class|async def)', line):
                break
        end_line += 1
    
    print(f"📍 Método termina en línea {end_line}")
    print(f"📊 Total líneas del método: {end_line - start_line}")
    
    # Mostrar contenido actual
    print("\n📄 Contenido actual de create_source:")
    print("=" * 60)
    for i in range(start_line, min(start_line + 10, end_line)):
        print(f"{i+1:4d}: {lines[i]}", end='')
    if end_line - start_line > 10:
        print(f"... ({end_line - start_line - 10} líneas más)")
    print("=" * 60)
    
    return True, engine_path, lines, start_line, end_line, base_indent

def create_fixed_version():
    """Crea versión arreglada del archivo"""
    
    result = diagnose_create_source()
    if not result or result is False:
        return False
    
    _, engine_path, lines, start_line, end_line, base_indent = result
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(engine_path, 'r', encoding='utf-8') as f:
        backup_content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(backup_content)
    print(f"\n✅ Backup creado: {backup_path}")
    
    # Crear nuevo método con indentación correcta
    indent = ' ' * base_indent
    method_indent = ' ' * (base_indent + 4)
    
    new_method_lines = [
        f"{indent}def create_source(self, source_id: int, name: str = None):\n",
        f'{method_indent}"""Crea una nueva fuente de sonido"""\n',
        f"{method_indent}if source_id >= self.n_sources:\n",
        f"{method_indent}    raise ValueError(f\"ID {{source_id}} excede el máximo de fuentes ({{self.n_sources}})\")\n",
        f"{method_indent}\n",
        f"{method_indent}if source_id in self.motion_states:\n",
        f"{method_indent}    print(f\"⚠️ Fuente {{source_id}} ya existe\")\n",
        f"{method_indent}    return self.motion_states[source_id]\n",
        f"{method_indent}\n",
        f"{method_indent}# Crear estado inicial\n",
        f"{method_indent}state = MotionState()\n",
        f"{method_indent}state.source_id = source_id\n",
        f"{method_indent}state.position = self._positions[source_id].copy()\n",
        f"{method_indent}state.velocity = np.zeros(3)\n",
        f"{method_indent}state.name = name or f\"source_{{source_id}}\"\n",
        f"{method_indent}\n",
        f"{method_indent}# Crear SourceMotion básico\n",
        f"{method_indent}motion = SourceMotion(source_id, state)\n",
        f"{method_indent}\n",
        f"{method_indent}# Registrar\n",
        f"{method_indent}self.motion_states[source_id] = motion\n",
        f"{method_indent}self._active_sources.add(source_id)\n",
        f"{method_indent}\n",
        f"{method_indent}# Notificar al bridge OSC si existe\n",
        f"{method_indent}if hasattr(self, 'osc_bridge') and self.osc_bridge:\n",
        f"{method_indent}    try:\n",
        f"{method_indent}        self.osc_bridge.source_created(source_id, state.name)\n",
        f"{method_indent}    except:\n",
        f"{method_indent}        pass\n",
        f"{method_indent}\n",
        f"{method_indent}print(f\"✅ Fuente {{source_id}} creada: {{state.name}}\")\n",
        f"{method_indent}return motion\n",
        f"{method_indent}\n"
    ]
    
    # Reemplazar método
    new_lines = lines[:start_line] + new_method_lines + lines[end_line:]
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Método reemplazado")
    
    # Verificar sintaxis
    try:
        with open(engine_path, 'r', encoding='utf-8') as f:
            compile(f.read(), engine_path, 'exec')
        print("✅ Sintaxis verificada correctamente")
        return True
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text if e.text else 'N/A'}")
        # Restaurar backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO Y FIX MANUAL DE CREATE_SOURCE")
    print("="*60)
    
    # Primero diagnóstico
    print("\n🔍 FASE 1: Diagnóstico")
    diagnose_create_source()
    
    # Preguntar si continuar
    print("\n❓ ¿Deseas aplicar el fix? (s/n): ", end='')
    response = input().strip().lower()
    
    if response == 's':
        print("\n🔧 FASE 2: Aplicando fix")
        success = create_fixed_version()
        
        if success:
            print("\n✅ Fix aplicado exitosamente")
            print("\n📋 Prueba ahora:")
            print("$ python test_delta_concentration_final.py")
        else:
            print("\n❌ Error al aplicar fix")
    else:
        print("\n❌ Fix cancelado")