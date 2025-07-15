import os
import re

def check_osc_bridge():
    """Verificar el estado actual de OSC Bridge"""
    print("🔍 VERIFICANDO OSC BRIDGE")
    print("="*60)
    
    osc_file = "trajectory_hub/bridges/osc_bridge.py"
    
    if not os.path.exists(osc_file):
        print(f"❌ No existe: {osc_file}")
        
        # Buscar alternativas
        print("\n🔍 Buscando archivos OSC...")
        for root, dirs, files in os.walk("trajectory_hub"):
            for file in files:
                if 'osc' in file.lower() and file.endswith('.py'):
                    print(f"  Encontrado: {os.path.join(root, file)}")
        return
    
    with open(osc_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    print("\n📋 MÉTODOS EN OSC BRIDGE:")
    
    # Buscar todos los métodos
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            method_name = line.strip().split('(')[0].replace('def ', '')
            print(f"\n  {method_name}() - Línea {i+1}")
            
            # Si es send_position, mostrar detalles
            if 'send_position' in method_name:
                print(f"    Firma: {line.strip()}")
                
                # Buscar qué envía
                for j in range(i+1, min(len(lines), i+15)):
                    if 'send' in lines[j] and ('message' in lines[j] or 'osc' in lines[j]):
                        print(f"    L{j+1}: {lines[j].strip()}")
                        
                        # Ver si envía 3 valores
                        if ', z' in lines[j] or '[2]' in lines[j]:
                            print("    ✅ Envía Z")
                        elif ', y' in lines[j] and ', z' not in lines[j]:
                            print("    ❌ NO envía Z")

if __name__ == "__main__":
    check_osc_bridge()