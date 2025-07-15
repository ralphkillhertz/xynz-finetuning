import os
import re

def diagnose_sphere():
    """Diagnosticar por qué sphere crea círculo 2D"""
    print("🔍 DIAGNÓSTICO: SPHERE CREANDO CÍRCULO")
    print("="*60)
    
    # 1. Buscar dónde se procesa la formación "sphere"
    print("\n1️⃣ BUSCANDO PROCESAMIENTO DE 'sphere'...")
    
    # Archivos clave
    files_to_check = [
        "trajectory_hub/control/processors/command_processor.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/control/managers/formation_manager.py"
    ]
    
    sphere_processing = {}
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"\n📄 Analizando: {filepath}")
            
            with open(filepath, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Buscar dónde se procesa sphere
            for i, line in enumerate(lines):
                if 'sphere' in line and ('==' in line or 'case' in line or 'if' in line):
                    # Mostrar contexto
                    start = max(0, i-5)
                    end = min(len(lines), i+15)
                    
                    print(f"\n   📍 Línea {i+1}: Procesamiento de sphere")
                    for j in range(start, end):
                        marker = ">>>" if j == i else "   "
                        print(f"   {marker} {j+1}: {lines[j]}")
                    
                    sphere_processing[filepath] = i+1
    
    # 2. Verificar si existe _calculate_sphere_positions
    print("\n\n2️⃣ VERIFICANDO MÉTODOS DE CÁLCULO...")
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Buscar métodos
            sphere_method = "_calculate_sphere_positions" in content or "_create_sphere_formation" in content
            circle_method = "_calculate_circle_positions" in content
            
            print(f"\n📄 {os.path.basename(filepath)}:")
            print(f"   {'✅' if sphere_method else '❌'} Tiene método sphere")
            print(f"   {'✅' if circle_method else '❌'} Tiene método circle")
            
            # Si tiene sphere, verificar si es 3D
            if sphere_method:
                if 'y = 1 -' in content and 'golden_angle' in content:
                    print("   ✅ Implementación parece ser 3D")
                else:
                    print("   ❌ Implementación NO parece ser 3D")
    
    # 3. Buscar el problema específico
    print("\n\n3️⃣ BUSCANDO EL PROBLEMA...")
    
    # Buscar en CommandProcessor cómo maneja sphere
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            content = f.read()
        
        # Buscar handle_create_macro
        handle_match = re.search(r'def handle_create_macro.*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
        
        if handle_match:
            method = handle_match.group(0)
            
            # Ver si sphere está siendo procesado
            if 'sphere' not in method:
                print("\n❌ PROBLEMA: handle_create_macro NO procesa sphere")
                print("   Sphere aparece en el menú pero no en la lógica")
                
                # Buscar cómo se procesan las formaciones
                if 'formation_manager' in method.lower():
                    print("   ✅ Usa FormationManager")
                    print("   → Verificar FormationManager")
                elif 'engine' in method and 'create_macro' in method:
                    print("   ✅ Delega a engine.create_macro")
                    print("   → El problema está en engine")
    
    print("\n\n4️⃣ DIAGNÓSTICO FINAL:")
    print("-" * 40)
    print("PROBLEMA: Sphere está en el menú pero NO en la lógica de procesamiento")
    print("CAUSA: El mapeo formation='sphere' no llega al método correcto")
    print("SOLUCIÓN: Agregar el caso sphere donde se procesan las formaciones")

if __name__ == "__main__":
    diagnose_sphere()
    
    print("\n\n💡 PARA ARREGLAR MANUALMENTE:")
    print("1. Busca donde dice 'elif formation == \"random\"'")
    print("2. Añade después:")
    print('   elif formation == "sphere":')
    print('       positions = self._calculate_sphere_positions(...)')
    print("\n🔧 O ejecuta: python fix_sphere_mapping.py")