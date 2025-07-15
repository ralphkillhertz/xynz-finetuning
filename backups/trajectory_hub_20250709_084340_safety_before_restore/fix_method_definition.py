# === fix_method_definition.py ===
# 🔧 Fix: Arreglar definición incompleta del método
# ⚡ Líneas 518-519 tienen la firma del método rota

import os

def fix_method_definition():
    """Arreglar definición del método set_individual_trajectory"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_method_fix', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Buscando definición del método set_individual_trajectory...")
    
    # Buscar alrededor de línea 518
    for i in range(max(0, 510), min(len(lines), 540)):
        if 'def set_individual_trajectory' in lines[i]:
            print(f"\n📍 Encontrado en línea {i+1}")
            print("📋 Contexto:")
            for j in range(max(0, i-2), min(len(lines), i+15)):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j+1}: {lines[j].rstrip()}")
            
            # Arreglar la definición del método
            # Buscar todos los parámetros esperados
            if i+1 < len(lines) and lines[i+1].strip().startswith('#'):
                print("\n✅ Arreglando definición del método...")
                
                # Reemplazar con definición completa correcta
                lines[i] = '    def set_individual_trajectory(self, macro_id, source_id: int,\n'
                lines[i+1] = '                                  shape: str, shape_params: dict = None,\n'
                # Insertar líneas faltantes
                lines.insert(i+2, '                                  movement_mode: str = "fix",\n')
                lines.insert(i+3, '                                  movement_speed: float = 1.0):\n')
                lines.insert(i+4, '        """Configurar trayectoria individual para una fuente"""\n')
                lines.insert(i+5, '        # Manejar tanto string como objeto macro\n')
                
                print("✅ Definición corregida")
                break
    
    # Guardar cambios
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo guardado")

def verify_and_test():
    """Verificar el fix y ejecutar test"""
    print("\n🧪 Verificando import...")
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        print("✅ Import exitoso!")
        
        # Test básico
        engine = EnhancedTrajectoryEngine(n_sources=10)
        print("✅ Engine creado")
        
        # Ejecutar test completo
        print("\n🚀 Ejecutando test delta_100...")
        import subprocess
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True, timeout=10)
        
        # Mostrar resultados relevantes
        if result.stdout:
            lines = result.stdout.split('\n')
            showing = False
            for line in lines:
                if 'RESUMEN' in line:
                    showing = True
                if showing or 'Error' in line or 'funcional' in line or '%' in line:
                    print(line)
        
        if result.stderr and len(result.stderr) > 50:
            print(f"\nERRORES: {result.stderr[-500:]}")
            
    except SyntaxError as e:
        print(f"❌ Error de sintaxis persistente:")
        print(f"   Archivo: {e.filename}")
        print(f"   Línea: {e.lineno}")
        print(f"   Texto: {e.text}")
        
        # Mostrar contexto
        if e.filename and e.lineno:
            with open(e.filename, 'r') as f:
                lines = f.readlines()
            print("\n📋 Contexto del error:")
            for i in range(max(0, e.lineno-5), min(len(lines), e.lineno+5)):
                marker = ">>>" if i == e.lineno-1 else "   "
                print(f"{marker} {i+1}: {lines[i].rstrip()}")
                
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)[:200]}")

if __name__ == "__main__":
    print("🔧 FIXING METHOD DEFINITION")
    print("=" * 60)
    
    fix_method_definition()
    verify_and_test()