#!/usr/bin/env python3
"""
trace_concentration_execution.py - Rastrea la ejecución del componente
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

# Monkey patch para debug
original_update = ConcentrationComponent.update
update_calls = []

def debug_update(self, state, time, dt):
    """Wrapper para rastrear llamadas"""
    update_calls.append({
        'enabled': self.enabled,
        'factor': self.factor,
        'pos_before': state.position.copy(),
        'target': self.target_point.copy()
    })
    
    # Llamar al original
    result = original_update(self, state, time, dt)
    
    update_calls[-1]['pos_after'] = result.position.copy()
    update_calls[-1]['changed'] = not np.allclose(state.position, result.position)
    
    return result

# Aplicar monkey patch
ConcentrationComponent.update = debug_update

def trace_execution():
    """Rastrear la ejecución paso a paso"""
    print("🔍 RASTREANDO EJECUCIÓN DEL COMPONENTE DE CONCENTRACIÓN\n")
    
    # Limpiar llamadas previas
    update_calls.clear()
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("trace", 3, formation="circle", spacing=3.0)
    
    # Aplicar concentración
    print("1. Aplicando concentración...")
    engine.set_macro_concentration(macro_id, 0.0)
    
    # Hacer algunos updates
    print("\n2. Ejecutando 5 updates...")
    for i in range(5):
        engine.update()
        print(f"   Update {i+1} completado")
    
    # Analizar llamadas
    print(f"\n3. Análisis de llamadas a ConcentrationComponent.update:")
    print(f"   Total de llamadas: {len(update_calls)}")
    
    if update_calls:
        print("\n   Detalle de llamadas:")
        for i, call in enumerate(update_calls[:10]):  # Primeras 10
            print(f"\n   Llamada {i+1}:")
            print(f"     - Enabled: {call['enabled']}")
            print(f"     - Factor: {call['factor']}")
            print(f"     - Pos antes: {call['pos_before']}")
            print(f"     - Pos después: {call['pos_after']}")
            print(f"     - Target: {call['target']}")
            print(f"     - ¿Cambió?: {call['changed']}")
    else:
        print("\n   ❌ NO SE REGISTRARON LLAMADAS AL COMPONENTE")
        print("      El componente NO se está ejecutando")

def check_source_motion_update_flow():
    """Verificar el flujo en SourceMotion.update"""
    print("\n\n🔍 VERIFICANDO FLUJO EN SourceMotion.update()...\n")
    
    import os
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar SourceMotion.update
    in_update = False
    update_lines = []
    
    for i, line in enumerate(lines):
        if "class SourceMotion" in line:
            class_line = i
        elif "def update(self" in line and i > class_line:
            in_update = True
        elif in_update and line.strip() and not line.startswith("        "):
            break
        elif in_update:
            update_lines.append((i+1, line.rstrip()))
    
    print("Últimas 30 líneas de SourceMotion.update():")
    print("-" * 70)
    
    concentration_found = False
    for line_num, line in update_lines[-30:]:
        if "concentration" in line.lower():
            print(f">>> {line_num}: {line}")
            concentration_found = True
        else:
            print(f"    {line_num}: {line}")
    
    print("-" * 70)
    
    if not concentration_found:
        print("\n❌ NO se encontró procesamiento de concentration")
        print("   El componente NO se está ejecutando en SourceMotion.update()")

def add_concentration_to_source_motion():
    """Asegurar que concentration se procesa en SourceMotion.update"""
    print("\n\n🔧 ASEGURANDO PROCESAMIENTO DE CONCENTRATION...\n")
    
    import os
    from datetime import datetime
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{filepath}.backup_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar el return en SourceMotion.update
    in_source_motion = False
    in_update = False
    return_line = -1
    
    for i, line in enumerate(lines):
        if "class SourceMotion" in line:
            in_source_motion = True
        elif in_source_motion and "def update(self" in line:
            in_update = True
        elif in_update and "return" in line and "self.state" in line:
            return_line = i
            print(f"✅ Encontrado return en línea {i+1}")
            break
    
    if return_line != -1:
        # Verificar si concentration ya se procesa
        concentration_exists = False
        for i in range(max(0, return_line-20), return_line):
            if "concentration" in lines[i]:
                concentration_exists = True
                break
        
        if not concentration_exists:
            # Agregar procesamiento antes del return
            indent = len(lines[return_line]) - len(lines[return_line].lstrip())
            
            concentration_code = [
                "\n",
                " " * indent + "# Procesar concentration al final\n",
                " " * indent + "for comp_name, component in self.components.items():\n",
                " " * (indent + 4) + "if component.enabled:\n",
                " " * (indent + 8) + "self.state = component.update(self.state, time, dt)\n",
                "\n"
            ]
            
            # Insertar antes del return
            for j, code_line in enumerate(concentration_code):
                lines.insert(return_line + j, code_line)
            
            # Guardar
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("✅ Agregado procesamiento de componentes antes del return")
            return True
        else:
            print("✅ Ya existe procesamiento de concentration")
    
    return False

def main():
    print("="*70)
    print("🔍 RASTREO DE EJECUCIÓN DE CONCENTRATION")
    print("="*70)
    
    # Rastrear ejecución
    trace_execution()
    
    # Verificar flujo
    check_source_motion_update_flow()
    
    # Si no se ejecuta, agregar
    if len(update_calls) == 0:
        print("\n⚠️  El componente NO se está ejecutando")
        
        if add_concentration_to_source_motion():
            print("\n🔄 Probando de nuevo después de la corrección...")
            
            # Limpiar y probar de nuevo
            update_calls.clear()
            trace_execution()
            
            if len(update_calls) > 0:
                print("\n✅ ¡AHORA SÍ SE ESTÁ EJECUTANDO!")
            else:
                print("\n❌ Todavía no se ejecuta, puede necesitar reiniciar Python")
    
    # Restaurar update original
    ConcentrationComponent.update = original_update
    
    print("\n" + "="*70)
    print("CONCLUSIÓN")
    print("="*70)

if __name__ == "__main__":
    main()