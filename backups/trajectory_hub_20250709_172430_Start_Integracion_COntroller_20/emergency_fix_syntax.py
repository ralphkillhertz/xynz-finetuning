import os
from datetime import datetime
import shutil

def emergency_fix_syntax():
    """Arreglar error de sintaxis urgente"""
    print("🚨 FIX DE EMERGENCIA - ERROR DE SINTAXIS")
    print("="*60)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print(f"❌ No existe: {engine_file}")
        return
    
    # Backup
    backup = f"{engine_file}.backup_emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, backup)
    print(f"📦 Backup: {backup}")
    
    # Leer archivo
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar la línea problemática (línea 45 aprox)
    print("\n🔍 Buscando línea problemática...")
    
    problem_found = False
    for i in range(40, min(50, len(lines))):
        if i < len(lines):
            line = lines[i]
            print(f"L{i+1}: {line.rstrip()}")
            
            # Verificar si es un import mal formateado
            if 'from trajectory_hub.control.managers.formation_manager import FormationManager' in line:
                # Verificar si tiene problemas
                if not line.strip().startswith('from'):
                    print(f"\n❌ Problema encontrado en línea {i+1}")
                    print("  El import no empieza correctamente")
                    
                    # Arreglar: asegurar que sea una línea válida
                    lines[i] = "from trajectory_hub.control.managers.formation_manager import FormationManager\n"
                    problem_found = True
                    print("✅ Línea corregida")
    
    # Si no encontramos el problema específico, buscar más amplio
    if not problem_found:
        print("\n🔍 Buscando imports de FormationManager...")
        
        for i, line in enumerate(lines):
            if 'FormationManager' in line and 'import' in line:
                print(f"\nL{i+1}: {line.rstrip()}")
                
                # Verificar formato correcto
                if line.strip() and not line.strip().startswith('#'):
                    if not (line.strip().startswith('from') or line.strip().startswith('import')):
                        print("❌ Import mal formateado")
                        
                        # Intentar arreglar
                        if 'from trajectory_hub' in line:
                            lines[i] = "from trajectory_hub.control.managers.formation_manager import FormationManager\n"
                        else:
                            lines[i] = "# " + line  # Comentar la línea problemática
                        
                        problem_found = True
                        print("✅ Línea arreglada")
    
    # Verificar indentación en la zona del error
    print("\n🔍 Verificando indentación alrededor de línea 45...")
    
    for i in range(40, min(50, len(lines))):
        if i < len(lines):
            line = lines[i]
            if line.strip() and not line.startswith(' ') and not line.startswith('from') and not line.startswith('import') and not line.startswith('#') and not line.startswith('class') and not line.startswith('def'):
                print(f"\n⚠️ Línea {i+1} podría tener problemas de indentación")
                print(f"  '{line.rstrip()}'")
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")
    
    # Verificar que se puede importar
    print("\n🧪 Verificando import...")
    try:
        import trajectory_hub
        print("✅ trajectory_hub se puede importar")
    except SyntaxError as e:
        print(f"❌ Todavía hay error de sintaxis: {e}")
        print("\n💡 Intenta restaurar desde backup:")
        
        # Listar backups disponibles
        import glob
        backups = glob.glob(f"{engine_file}.backup_*")
        backups.sort()
        
        if backups:
            print("\nBackups disponibles:")
            for i, backup in enumerate(backups[-5:]):  # Últimos 5
                print(f"  {i+1}. {backup}")
            
            print(f"\n🔧 Para restaurar el más reciente:")
            print(f"cp '{backups[-2]}' '{engine_file}'")

def quick_restore():
    """Restaurar desde el backup más reciente que funcione"""
    print("\n🔄 RESTAURACIÓN RÁPIDA")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    import glob
    backups = glob.glob(f"{engine_file}.backup_*")
    backups.sort()
    
    if not backups:
        print("❌ No hay backups disponibles")
        return
    
    # Intentar con el penúltimo backup (antes del fix que causó el problema)
    for backup in reversed(backups[:-1]):  # Excluir el más reciente
        print(f"\n🔍 Probando: {backup}")
        
        # Copiar
        shutil.copy(backup, engine_file)
        
        # Verificar
        try:
            import importlib
            import trajectory_hub
            importlib.reload(trajectory_hub)
            print("✅ Este backup funciona!")
            
            # Ahora aplicar el fix de sphere correctamente
            apply_sphere_fix_carefully()
            return
        except:
            print("❌ Este backup también tiene problemas")
            continue
    
    print("\n❌ Ningún backup funciona")

def apply_sphere_fix_carefully():
    """Aplicar el fix de sphere con cuidado"""
    print("\n🔧 Aplicando fix de sphere cuidadosamente...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Solo añadir el import si no existe
    if 'FormationManager' not in content:
        # Buscar dónde insertar el import (después de otros imports de trajectory_hub)
        lines = content.split('\n')
        
        import_added = False
        for i, line in enumerate(lines):
            if line.startswith('from trajectory_hub') and i < 50:
                # Insertar después
                lines.insert(i+1, 'from trajectory_hub.control.managers.formation_manager import FormationManager')
                import_added = True
                print("✅ Import añadido correctamente")
                break
        
        if import_added:
            content = '\n'.join(lines)
            with open(engine_file, 'w') as f:
                f.write(content)

if __name__ == "__main__":
    emergency_fix_syntax()
    
    # Si sigue sin funcionar, intentar restauración
    try:
        import trajectory_hub
    except SyntaxError:
        print("\n❌ El fix no funcionó, intentando restauración...")
        quick_restore()
    
    print("\n🚀 Intenta ejecutar de nuevo:")
    print("python -m trajectory_hub.interface.interactive_controller")