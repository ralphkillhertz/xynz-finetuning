# === find_motion_components.py ===
# 🔍 Buscar motion_components.py
# ⚡ Localizar el archivo correcto
# 🎯 Impacto: DIAGNÓSTICO

import os
import glob

def find_file():
    """Busca motion_components.py en toda la estructura"""
    
    print("🔍 Buscando motion_components.py...")
    print("=" * 50)
    
    # Buscar en el directorio actual y subdirectorios
    found_files = []
    
    # Método 1: Buscar con glob
    for pattern in ["motion_components.py", "*/motion_components.py", "**/motion_components.py"]:
        matches = glob.glob(pattern, recursive=True)
        found_files.extend(matches)
    
    # Método 2: Buscar con os.walk
    for root, dirs, files in os.walk("."):
        for file in files:
            if file == "motion_components.py":
                path = os.path.join(root, file)
                if path not in found_files:
                    found_files.append(path)
    
    # Eliminar duplicados
    found_files = list(set(found_files))
    
    if found_files:
        print(f"\n✅ Encontrado(s) {len(found_files)} archivo(s):")
        for f in found_files:
            size = os.path.getsize(f)
            print(f"   📄 {f} ({size:,} bytes)")
            
            # Verificar si contiene MacroRotation
            try:
                with open(f, 'r') as file:
                    content = file.read()
                    if 'class MacroRotation' in content:
                        print(f"      ✅ Contiene MacroRotation")
                        
                        # Buscar la línea problemática
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'self.enabled = bool(abs(speed_x)' in line:
                                print(f"      ⚠️ Línea problemática encontrada en línea {i+1}")
                                print(f"         {line.strip()}")
            except:
                pass
    else:
        print("\n❌ No se encontró motion_components.py")
        
    # Buscar estructura del proyecto
    print("\n📁 Estructura del proyecto:")
    dirs = [d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith('.')]
    for d in sorted(dirs):
        print(f"   📁 {d}/")
        # Listar archivos Python en cada directorio
        try:
            py_files = [f for f in os.listdir(d) if f.endswith('.py')]
            if py_files:
                for f in py_files[:5]:  # Mostrar solo los primeros 5
                    print(f"      - {f}")
                if len(py_files) > 5:
                    print(f"      ... y {len(py_files) - 5} más")
        except:
            pass

if __name__ == "__main__":
    find_file()