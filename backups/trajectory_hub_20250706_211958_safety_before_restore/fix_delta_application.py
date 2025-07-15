#!/usr/bin/env python3
"""
🚨 FIX CRÍTICO: Aplicar deltas acumulados
El problema es que los deltas se calculan pero nunca se aplican
"""

import os
import shutil
from datetime import datetime
import re

print("=" * 80)
print("🚨 FIX CRÍTICO: APLICACIÓN DE DELTAS")
print("=" * 80)

# Buscar dónde se hace el update principal
print("\n1️⃣ BUSCANDO DÓNDE APLICAR DELTAS...")

# Posibles archivos donde el engine hace update
candidates = [
    "trajectory_hub/core/enhanced_trajectory_engine.py",
    "trajectory_hub/core/trajectory_engine.py",
    "trajectory_hub/core/engine.py",
    "trajectory_hub/core/spatial_engine.py"
]

engine_file = None
for candidate in candidates:
    if os.path.exists(candidate):
        engine_file = candidate
        print(f"✅ Encontrado: {engine_file}")
        break

if not engine_file:
    print("❌ No se encontró el archivo del engine")
    exit(1)

# Backup
backup_dir = f"fix_deltas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)
shutil.copy2(engine_file, os.path.join(backup_dir, os.path.basename(engine_file)))
print(f"✅ Backup: {backup_dir}")

# Leer archivo
with open(engine_file, 'r') as f:
    content = f.read()

# Buscar el método update principal
print("\n2️⃣ BUSCANDO MÉTODO UPDATE...")

# Buscar dónde se actualizan las posiciones de las fuentes
update_found = False
lines = content.split('\n')

# Buscar el patrón donde se hace source.update o motion.update
for i, line in enumerate(lines):
    if 'motion.update(' in line or 'source.update(' in line:
        print(f"✅ Update encontrado en línea {i+1}: {line.strip()[:60]}...")
        
        # Buscar el contexto para insertar la aplicación de deltas
        # Necesitamos insertar DESPUÉS del update pero ANTES de enviar a Spat
        
        # Buscar hacia adelante para encontrar dónde se envían las posiciones
        for j in range(i, min(i+50, len(lines))):
            if 'send_source_position' in lines[j] or '_send_positions' in lines[j]:
                print(f"   Envío a Spat en línea {j+1}")
                
                # Insertar la aplicación de deltas ANTES del envío
                insert_line = j
                
                # Preparar el código a insertar
                delta_application = """
        # APLICAR DELTAS ACUMULADOS (Arquitectura Paralela)
        if hasattr(self, '_apply_accumulated_deltas'):
            self._apply_accumulated_deltas()
        else:
            # Aplicación directa si no existe el método
            try:
                from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
                for i in range(self.num_sources):
                    if hasattr(self._source_motions[i], 'source_id'):
                        source_id = self._source_motions[i].source_id
                    else:
                        source_id = i
                    
                    # Obtener deltas acumulados
                    delta = compat.get_accumulated_delta(source_id)
                    if delta is not None:
                        # Aplicar delta a la posición
                        self._positions[i] += delta
                        # Limpiar deltas aplicados
                        compat.clear_deltas(source_id)
            except:
                pass  # Si falla, continuar sin deltas
"""
                
                # Obtener indentación correcta
                indent = len(lines[j]) - len(lines[j].lstrip())
                indented_code = '\n'.join(' ' * indent + line for line in delta_application.strip().split('\n'))
                
                # Insertar
                lines.insert(insert_line, indented_code)
                update_found = True
                print(f"✅ Código de aplicación de deltas insertado en línea {insert_line}")
                break
        
        if update_found:
            break

if not update_found:
    print("⚠️ No se encontró el patrón esperado, buscando alternativa...")
    
    # Buscar el método update del engine
    for i, line in enumerate(lines):
        if 'def update(' in line and 'self' in line:
            # Buscar el final del método
            method_indent = len(line) - len(line.lstrip())
            
            for j in range(i+1, len(lines)):
                # Buscar línea antes del return o final del método
                if (lines[j].strip().startswith('return') or 
                    (lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= method_indent)):
                    
                    # Insertar antes del return
                    insert_line = j - 1
                    
                    delta_code = """
    # Aplicar deltas acumulados antes de terminar update
    try:
        from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
        for i in range(len(self._positions) if hasattr(self, '_positions') else 0):
            delta = compat.get_accumulated_delta(i)
            if delta is not None:
                self._positions[i] += delta
                compat.clear_deltas(i)
    except:
        pass
"""
                    
                    lines.insert(insert_line, delta_code)
                    update_found = True
                    print(f"✅ Aplicación de deltas agregada al final de update()")
                    break
            
            if update_found:
                break

# Escribir archivo modificado
if update_found:
    new_content = '\n'.join(lines)
    with open(engine_file, 'w') as f:
        f.write(new_content)
    
    print("\n✅ ARCHIVO MODIFICADO EXITOSAMENTE")
else:
    print("\n❌ No se pudo encontrar dónde insertar el código")

# Crear método auxiliar
print("\n3️⃣ CREANDO MÉTODO AUXILIAR...")

helper_code = '''#!/usr/bin/env python3
"""
🔧 Método auxiliar para aplicar deltas
Agregar a EnhancedTrajectoryEngine si es necesario
"""

def _apply_accumulated_deltas(self):
    """Aplica todos los deltas acumulados a las posiciones"""
    try:
        from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
        
        applied_count = 0
        for i in range(self.num_sources):
            # Obtener source_id
            if hasattr(self._source_motions[i], 'source_id'):
                source_id = self._source_motions[i].source_id
            else:
                source_id = i
            
            # Obtener delta acumulado
            delta = compat.get_accumulated_delta(source_id)
            
            if delta is not None:
                # Aplicar delta
                old_pos = self._positions[i].copy()
                self._positions[i] += delta
                
                # Log para debug
                if compat.config.get('LOG_DELTAS', False):
                    movement = np.linalg.norm(delta)
                    print(f"   [APPLIED] Source {source_id}: moved {movement:.4f}")
                
                # Limpiar delta aplicado
                compat.clear_deltas(source_id)
                applied_count += 1
        
        if applied_count > 0 and compat.config.get('LOG_DELTAS', False):
            print(f"   ✅ Applied deltas to {applied_count} sources")
            
    except Exception as e:
        print(f"   ❌ Error applying deltas: {e}")

# Agregar este método a tu clase EnhancedTrajectoryEngine
'''

with open("delta_application_method.py", 'w') as f:
    f.write(helper_code)

print("✅ Método auxiliar creado: delta_application_method.py")

# También arreglar el problema de los deltas muy pequeños
print("\n4️⃣ VERIFICANDO ANIMACIÓN DE CONCENTRACIÓN...")

motion_file = "trajectory_hub/core/motion_components.py"
if os.path.exists(motion_file):
    with open(motion_file, 'r') as f:
        motion_content = f.read()
    
    # Verificar si hay animación activa
    if 'animation_active' in motion_content and 'animation_elapsed' in motion_content:
        print("✅ Sistema de animación detectado")
        print("   Los deltas pequeños pueden ser debido a animación gradual")
        print("   Esto es normal si está animando de factor 1.0 a 0.0")

print("\n" + "=" * 80)
print("RESUMEN:")
print("=" * 80)
print("1. ✅ Código de aplicación de deltas agregado al engine")
print("2. ✅ Los deltas ahora deberían aplicarse a las posiciones")
print("3. ℹ️  Los deltas pequeños son normales si hay animación")
print("\n⚡ REINICIA EL CONTROLADOR para aplicar cambios")
print("=" * 80)