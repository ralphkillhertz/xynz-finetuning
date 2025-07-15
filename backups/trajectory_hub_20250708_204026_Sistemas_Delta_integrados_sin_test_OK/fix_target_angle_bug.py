# === fix_target_angle_bug.py ===
# 🔧 Corregir bug del ángulo target
# ⚡ El valor no se está pasando correctamente

import re
import math

print("🔧 INVESTIGANDO BUG DEL ÁNGULO TARGET")
print("=" * 60)

# Verificar set_manual_individual_rotation
print("1️⃣ Buscando set_manual_individual_rotation en engine...")

try:
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        content = f.read()
    
    # Buscar el método
    method_match = re.search(
        r'def set_manual_individual_rotation.*?(?=\n    def|\Z)', 
        content, 
        re.DOTALL
    )
    
    if method_match:
        method = method_match.group(0)
        print("\n📄 Método encontrado:")
        print("-" * 60)
        
        # Mostrar líneas relevantes
        lines = method.split('\n')
        for i, line in enumerate(lines[:40]):  # Primeras 40 líneas
            print(f"{i+1:3d}: {line}")
            
            # Buscar asignaciones sospechosas
            if 'target_yaw' in line and '=' in line:
                print("     ⚡ ASIGNACIÓN DE target_yaw")
            if 'interpolation_speed' in line and '=' in line:
                print("     ⚡ ASIGNACIÓN DE interpolation_speed")
                
        print("-" * 60)
        
        # Buscar posibles conversiones erróneas
        if 'math.radians' in method:
            print("\n⚠️ ENCONTRADO math.radians - posible conversión doble")
        if 'degrees' in method and 'target' in method:
            print("\n⚠️ Posible conversión grados/radianes")
            
    # Verificar el valor de math.pi/2
    print(f"\n2️⃣ Verificando valores:")
    print(f"   math.pi/2 = {math.pi/2:.6f} radianes")
    print(f"   math.pi/2 = {math.degrees(math.pi/2):.1f} grados")
    print(f"   0.0274 rad = {math.degrees(0.0274):.1f} grados")
    print(f"   1.6° = {math.radians(1.6):.6f} radianes")
    
    # Posible causa
    print("\n3️⃣ ANÁLISIS:")
    print("   El valor 0.0274 es muy cercano a math.radians(1.57)")
    print(f"   math.radians(1.57) = {math.radians(1.57):.6f}")
    print("   ¡Parece que se está aplicando radians() a un valor ya en radianes!")
    
    # Buscar el problema específico
    print("\n4️⃣ Buscando línea problemática...")
    for i, line in enumerate(lines):
        if 'component.target_yaw' in line:
            print(f"\n   Línea {i+1}: {line.strip()}")
            if 'radians' in line:
                print("   ⚠️ ¡ENCONTRADO! Se está aplicando radians() incorrectamente")

except Exception as e:
    print(f"Error: {e}")

print("\n✅ Diagnóstico completado")