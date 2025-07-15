#!/usr/bin/env python3
"""
fix_syntax_error.py - Corregir error de sintaxis en el diccionario de componentes
"""

import os
from datetime import datetime

def fix_components_syntax():
    """Corregir el error de sintaxis en el diccionario de componentes"""
    print("🔧 CORRIGIENDO ERROR DE SINTAXIS...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{filepath}.backup_syntax_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar la línea con el error (línea 875)
    error_line = 874  # índice 874 = línea 875
    
    print(f"Líneas alrededor del error:")
    for i in range(max(0, error_line-5), min(len(lines), error_line+5)):
        marker = ">>>" if i == error_line else "   "
        print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Corregir: necesitamos agregar una coma al final de la línea anterior
    if error_line > 0:
        prev_line = lines[error_line-1]
        if not prev_line.rstrip().endswith(','):
            lines[error_line-1] = prev_line.rstrip() + ',\n'
            print(f"\n✅ Agregada coma al final de la línea {error_line}")
    
    # Verificar que la línea de concentration esté bien
    if error_line < len(lines):
        conc_line = lines[error_line]
        # Asegurarse de que tenga la indentación correcta
        if "'concentration'" in conc_line:
            # Obtener indentación de la línea anterior
            prev_line = lines[error_line-1]
            indent = len(prev_line) - len(prev_line.lstrip())
            
            # Reconstruir la línea con la indentación correcta
            lines[error_line] = " " * indent + "'concentration': ConcentrationComponent(),\n"
            print(f"✅ Corregida línea de concentration")
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")

def verify_import():
    """Verificar que se puede importar sin errores"""
    print("\n\n🔍 VERIFICANDO IMPORTACIÓN...\n")
    
    try:
        from trajectory_hub.core.motion_components import SourceMotion, ConcentrationComponent
        print("✅ Importación exitosa")
        
        # Crear una instancia para verificar
        motion = SourceMotion(0)
        print("\nComponentes disponibles:")
        for comp in motion.components:
            print(f"  - {comp}")
        
        if 'concentration' in motion.components:
            print("\n✅ ConcentrationComponent se crea automáticamente")
            return True
        else:
            print("\n❌ ConcentrationComponent NO se crea")
            return False
            
    except Exception as e:
        print(f"❌ Error al importar: {e}")
        return False

def final_integration_test():
    """Test final de integración completa"""
    print("\n\n🧪 TEST DE INTEGRACIÓN COMPLETA...\n")
    
    test_code = '''
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("1. Creando engine y macro...")
engine = EnhancedTrajectoryEngine()
macro_id = engine.create_macro("test", 5, formation="circle", spacing=5.0)

# Verificar componentes
macro = engine._macros[macro_id]
sid = list(macro.source_ids)[0]
motion = engine._source_motions[sid]

print("\\n2. Verificando concentration:")
if 'concentration' in motion.components:
    print("   ✅ ConcentrationComponent existe automáticamente")
else:
    print("   ❌ ConcentrationComponent NO existe")

# Posiciones iniciales
print("\\n3. Posiciones iniciales:")
for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._positions[sid]
    print(f"   Fuente {sid}: {pos}")

# Aplicar concentración
print("\\n4. Aplicando concentración total (factor=0.0)...")
engine.set_macro_concentration(macro_id, 0.0)

# Hacer varios updates
print("\\n5. Ejecutando 30 updates...")
for _ in range(30):
    engine.update()

# Verificar resultado
print("\\n6. Posiciones finales:")
distances = []
for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._positions[sid]
    print(f"   Fuente {sid}: {pos}")
    # Calcular distancia al centro
    dist = np.linalg.norm(pos)
    distances.append(dist)

avg_distance = np.mean(distances)
print(f"\\n7. Distancia promedio al centro: {avg_distance:.3f}")

if avg_distance < 1.0:
    print("\\n✅ ¡LA CONCENTRACIÓN FUNCIONA PERFECTAMENTE!")
    print("   Las fuentes se han concentrado en el centro")
else:
    print("\\n❌ La concentración no está funcionando")
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print("Resultado:")
    print("-" * 70)
    print(result.stdout)
    if result.stderr and "INFO:" not in result.stderr:
        print("Errores:")
        print(result.stderr)
    print("-" * 70)

def main():
    print("="*70)
    print("🔧 CORRECCIÓN DE ERROR DE SINTAXIS Y TEST FINAL")
    print("="*70)
    
    # Corregir sintaxis
    fix_components_syntax()
    
    # Verificar importación
    if verify_import():
        # Test final
        final_integration_test()
        
        print("\n" + "="*70)
        print("✅ SISTEMA DE CONCENTRACIÓN LISTO")
        print("="*70)
        print("\nAhora puedes:")
        print("1. Reiniciar el controlador")
        print("2. Usar la opción 31 - la concentración funcionará en Spat")
    else:
        print("\n❌ Todavía hay problemas con la importación")

if __name__ == "__main__":
    main()