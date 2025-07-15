# === diagnose_update_signatures.py ===
# 🔍 Diagnóstico: Verificar todas las firmas de update()
# ⚡ Encontrar inconsistencias en orden de parámetros

def analyze_update_signatures():
    """Analizar todas las firmas de update() en motion_components.py"""
    print("🔍 ANÁLISIS DE FIRMAS update()")
    print("=" * 70)
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar todas las definiciones de update
    signatures = []
    for i, line in enumerate(lines):
        if 'def update(' in line and 'self' in line:
            # Obtener contexto: clase anterior
            class_name = "Unknown"
            for j in range(i, -1, -1):
                if 'class ' in lines[j]:
                    class_name = lines[j].strip().split()[1].split('(')[0].replace(':', '')
                    break
            
            signatures.append({
                'line': i + 1,
                'class': class_name,
                'signature': line.strip()
            })
    
    print("📋 Firmas encontradas:")
    print("-" * 70)
    for sig in signatures:
        print(f"Línea {sig['line']:4d} | {sig['class']:30s} | {sig['signature']}")
    
    # Analizar ConcentrationComponent específicamente
    print("\n🔍 Analizando ConcentrationComponent.update():")
    for i, line in enumerate(lines):
        if 'class ConcentrationComponent' in line:
            # Buscar el update dentro de esta clase
            for j in range(i, min(i+100, len(lines))):
                if 'def update(' in lines[j]:
                    print(f"\n📍 Encontrado en línea {j+1}:")
                    # Mostrar el método completo
                    for k in range(j, min(j+20, len(lines))):
                        if k > j and 'def ' in lines[k] and lines[k][0] not in ' \t':
                            break
                        print(f"{k+1:4d}: {lines[k].rstrip()}")
                    break
            break

def check_specific_error():
    """Revisar la línea 847 específicamente"""
    print("\n\n🔍 Revisando línea 847 (error específico):")
    print("-" * 70)
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Contexto alrededor de la línea 847
    start = max(0, 847 - 15)
    end = min(len(lines), 847 + 5)
    
    for i in range(start, end):
        marker = ">>> " if i == 846 else "    "
        print(f"{i+1:4d}: {marker}{lines[i].rstrip()}")

if __name__ == "__main__":
    analyze_update_signatures()
    check_specific_error()