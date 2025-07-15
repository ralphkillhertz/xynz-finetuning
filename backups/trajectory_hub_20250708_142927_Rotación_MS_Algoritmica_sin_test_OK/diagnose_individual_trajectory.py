# === diagnose_individual_trajectory.py ===
# 🔧 Fix: Buscar dónde está IndividualTrajectory
# ⚡ Diagnóstico rápido del sistema

import os
import glob

def find_individual_trajectory():
    print("🔍 Buscando IndividualTrajectory en el proyecto...")
    
    # Buscar en todos los archivos .py
    found = False
    for file in glob.glob("trajectory_hub/**/*.py", recursive=True):
        try:
            with open(file, 'r') as f:
                content = f.read()
                if "IndividualTrajectory" in content:
                    print(f"\n✅ Encontrado en: {file}")
                    # Mostrar contexto
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "IndividualTrajectory" in line:
                            print(f"  Línea {i+1}: {line.strip()}")
                            # Mostrar 3 líneas antes y después
                            for j in range(max(0, i-3), min(len(lines), i+4)):
                                if j != i:
                                    print(f"  {j+1}: {lines[j][:80]}...")
                    found = True
        except:
            pass
    
    if not found:
        print("❌ IndividualTrajectory no encontrado")
        print("\n🔍 Buscando referencias a trayectorias individuales...")
        
        # Buscar patrones relacionados
        patterns = ["individual", "trajectory", "source.*trajectory", "set_individual"]
        
        for pattern in patterns:
            print(f"\n📝 Patrón '{pattern}':")
            for file in glob.glob("trajectory_hub/core/*.py"):
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if pattern.lower() in line.lower() and "class" in line:
                                print(f"  {file}: Línea {i+1}: {line.strip()}")
                except:
                    pass
    
    # Verificar estructura de motion_components.py
    print("\n📄 Clases en motion_components.py:")
    mc_file = "trajectory_hub/core/motion_components.py"
    if os.path.exists(mc_file):
        with open(mc_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith("class "):
                    print(f"  {line.strip()}")

if __name__ == "__main__":
    find_individual_trajectory()