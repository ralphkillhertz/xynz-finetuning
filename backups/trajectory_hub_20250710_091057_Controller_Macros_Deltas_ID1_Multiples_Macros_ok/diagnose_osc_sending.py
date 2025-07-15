#!/usr/bin/env python3
"""
🔍 Diagnóstico: ¿Por qué solo 16 sources llegan a Spat?
"""

def diagnose():
    print("🔍 DIAGNÓSTICO OSC SENDING")
    print("=" * 50)
    
    # 1. Verificar el método update
    print("\n1️⃣ Verificando método update()...")
    
    with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
        content = f.read()
    
    # Buscar update method
    start = content.find("def update(")
    if start == -1:
        print("❌ No se encontró método update")
        return
    
    end = content.find("\n    def", start + 1)
    if end == -1:
        end = start + 2000
    
    update_method = content[start:end]
    
    # Buscar límites en update
    print("\n2️⃣ Buscando límites en update()...")
    lines = update_method.split('\n')
    
    for i, line in enumerate(lines):
        if "[:16]" in line or "16" in line:
            print(f"   ⚠️ Línea {i}: {line.strip()}")
        if "for sid in" in line:
            print(f"   📍 Loop OSC: {line.strip()}")
            # Ver las siguientes líneas
            for j in range(i+1, min(i+10, len(lines))):
                if "send" in lines[j] or "osc" in lines[j].lower():
                    print(f"      → {lines[j].strip()}")
    
    # 3. Buscar en OSC Bridge
    print("\n3️⃣ Verificando OSC Bridge...")
    
    with open("trajectory_hub/core/spat_osc_bridge.py", 'r') as f:
        osc_content = f.read()
    
    # Buscar send_source_positions
    if "send_source_positions" in osc_content:
        start = osc_content.find("def send_source_positions")
        end = osc_content.find("\n    def", start + 1)
        method = osc_content[start:end if end > 0 else start + 500]
        
        print("\n📋 Método send_source_positions:")
        for i, line in enumerate(method.split('\n')[:15]):
            if "16" in line or "limit" in line.lower() or "max" in line.lower():
                print(f"   ⚠️ {line.strip()}")
    
    print("\n4️⃣ TEORÍA:")
    print("   - El límite parece estar en el loop de update()")
    print("   - Solo se envían las primeras 16 sources por OSC")
    print("   - Las sources 17-40 existen pero no se transmiten")

if __name__ == "__main__":
    diagnose()