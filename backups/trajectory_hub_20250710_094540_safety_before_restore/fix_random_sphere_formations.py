# === fix_random_sphere_formations.py ===
#!/usr/bin/env python3
"""
🔧 Fix: Random y Sphere formaciones correctas
⚡ Random debe ser aleatorio, Sphere debe ser 3D
"""
import numpy as np

def fix_formations():
    print("🔧 FIX RANDOM Y SPHERE")
    print("=" * 50)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    # Buscar la sección de formaciones
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Fix Random
        if 'elif formation == "random":' in line:
            print("📍 Encontrado Random en línea", i+1)
            # Buscar las siguientes líneas
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('elif'):
                j += 1
            
            # Reemplazar con código correcto
            indent = "            "
            new_random = [
                f'{indent}elif formation == "random":',
                f'{indent}    # Formación aleatoria real',
                f'{indent}    positions = []',
                f'{indent}    for i in range(self.config["n_sources"]):',
                f'{indent}        x = np.random.uniform(-spacing*2, spacing*2)',
                f'{indent}        y = np.random.uniform(-spacing*2, spacing*2)',
                f'{indent}        z = np.random.uniform(-spacing/2, spacing/2)',
                f'{indent}        positions.append(np.array([x, y, z]))',
                f'{indent}    print(f"🎲 Random 3D: {len(positions)} posiciones aleatorias")'
            ]
            
            # Reemplazar
            lines[i:j] = new_random
            print("✅ Random arreglado")
            
        # Fix Sphere
        elif 'elif formation == "sphere":' in line:
            print("📍 Encontrado Sphere en línea", i+1)
            # Buscar las siguientes líneas
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('elif'):
                j += 1
            
            # Reemplazar con código correcto
            indent = "            "
            new_sphere = [
                f'{indent}elif formation == "sphere":',
                f'{indent}    # Formación esférica 3D real',
                f'{indent}    positions = []',
                f'{indent}    n = self.config["n_sources"]',
                f'{indent}    phi = np.pi * (3 - np.sqrt(5))  # Golden angle',
                f'{indent}    for i in range(n):',
                f'{indent}        y = 1 - (i / float(n - 1)) * 2  # -1 to 1',
                f'{indent}        radius = np.sqrt(1 - y * y)',
                f'{indent}        theta = phi * i',
                f'{indent}        x = np.cos(theta) * radius * spacing',
                f'{indent}        z = np.sin(theta) * radius * spacing',
                f'{indent}        y *= spacing',
                f'{indent}        positions.append(np.array([x, y, z]))',
                f'{indent}    print(f"🌐 Sphere 3D: {len(positions)} posiciones esféricas")'
            ]
            
            # Reemplazar
            lines[i:j] = new_sphere
            print("✅ Sphere arreglado")
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print("\n✅ Formaciones arregladas")

if __name__ == "__main__":
    fix_formations()