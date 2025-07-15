# === fix_parameter_order.py ===
# 🔧 Fix: Corregir orden de parámetros en update
# ⚡ El problema es que SourceMotion pasa los parámetros en orden incorrecto

import os

def fix_parameter_order():
    """Corregir el orden de los parámetros en component.update()"""
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_param_order', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # Buscar y corregir la línea 134 (o cerca)
    fixed = False
    for i, line in enumerate(lines):
        # Buscar la línea problemática
        if 'new_state = component.update(current_time, dt, self.state)' in line:
            # Corregir el orden
            lines[i] = line.replace(
                'component.update(current_time, dt, self.state)',
                'component.update(self.state, current_time, dt)'
            )
            print(f"✅ Corregida línea {i+1}: orden de parámetros arreglado")
            fixed = True
            break
    
    # Si no encontró la línea exacta, buscar patrón similar
    if not fixed:
        for i, line in enumerate(lines):
            if 'component.update(' in line and 'current_time' in line and 'self.state' in line:
                if 'current_time, dt, self.state' in line:
                    lines[i] = line.replace(
                        'current_time, dt, self.state',
                        'self.state, current_time, dt'
                    )
                    print(f"✅ Corregida línea {i+1}: orden de parámetros arreglado")
                    fixed = True
                    break
    
    if fixed:
        # Guardar archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("\n✅ Archivo corregido exitosamente")
        return True
    else:
        print("\n❌ No se encontró la línea a corregir")
        return False

def verify_all_update_signatures():
    """Verificar que todas las firmas de update sean consistentes"""
    
    verification = '''# === verify_signatures.py ===
# 🔍 Verificar firmas de update
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Test simple
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
macro = engine.create_macro("test", 2, formation='line')

# Aplicar varios componentes
engine.set_macro_concentration(macro, 0.5)
engine.set_individual_trajectory(macro, 0, 'circle', {'radius': 2.0})

try:
    # Múltiples updates para verificar
    for i in range(5):
        engine.update()
    
    print("✅ Sistema funcionando correctamente")
    print(f"   Posición fuente 0: {engine._positions[0]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open('verify_signatures.py', 'w', encoding='utf-8') as f:
        f.write(verification)
    
    print("✅ verify_signatures.py creado")

if __name__ == "__main__":
    print("🔧 FIXING PARAMETER ORDER BUG")
    print("=" * 60)
    print("\n📍 Problema identificado:")
    print("   SourceMotion.update() pasa: (current_time, dt, state)")
    print("   Componentes esperan: (state, current_time, dt)")
    print("\n")
    
    if fix_parameter_order():
        verify_all_update_signatures()
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ejecutar: python verify_signatures.py")
        print("2. Si funciona, ejecutar: python test_system_working.py")
        print("3. ¡TODO OK → MCP Server! 🚀")