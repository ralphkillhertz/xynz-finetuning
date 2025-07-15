# === fix_macros_underscore.py ===
# 🔧 Fix: Corregir el nombre del atributo macros (con underscore)
# ⚡ Solución directa self.macros → self._macros

import os

def fix_macros_underscore():
    """Cambiar self.macros por self._macros"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_underscore', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Reemplazar self.macros por self._macros
    changes = 0
    
    # En returns
    if 'return self.macros[' in content:
        content = content.replace('return self.macros[', 'return self._macros[')
        changes += content.count('return self._macros[')
        print(f"✅ Corregidos {changes} returns")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Atributo corregido: self.macros → self._macros")

def run_tests():
    """Ejecutar tests para verificar"""
    
    print("\n🧪 Ejecutando verificación...")
    
    test_code = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Test rápido
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
print("\\n1️⃣ Creando macro...")
result = engine.create_macro("test", 2)

print(f"   Tipo retornado: {type(result)}")
if hasattr(result, 'source_ids'):
    print(f"   ✅ ÉXITO: Macro tiene source_ids: {result.source_ids}")
    
    # Test concentración
    print("\\n2️⃣ Aplicando concentración...")
    engine.set_macro_concentration(result, 0.5)
    print("   ✅ Concentración aplicada")
    
    # Test update
    print("\\n3️⃣ Ejecutando update...")
    for _ in range(5):
        engine.update()
    print("   ✅ Updates ejecutados")
    
    print("\\n✅ SISTEMA FUNCIONAL")
else:
    print(f"   ❌ FALLO: create_macro retornó: {result}")
'''
    
    exec(test_code)

def run_complete_test():
    """Ejecutar el test completo del sistema"""
    
    print("\n📋 Ejecutando test completo...")
    
    import subprocess
    result = subprocess.run(['python', 'test_delta_final_fixed.py'], 
                          capture_output=True, text=True)
    
    # Mostrar solo el resumen
    lines = result.stdout.split('\n')
    show = False
    for line in lines:
        if 'RESUMEN FINAL' in line:
            show = True
        if show:
            print(line)
    
    if result.stderr:
        print("\nERRORES:")
        print(result.stderr[-500:])  # Solo últimos 500 chars

if __name__ == "__main__":
    print("🔧 FIXING MACROS UNDERSCORE")
    print("=" * 60)
    
    fix_macros_underscore()
    
    try:
        run_tests()
        
        print("\n" + "=" * 60)
        input("\n📋 Presiona ENTER para ejecutar test completo...")
        run_complete_test()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()