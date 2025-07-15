#!/usr/bin/env python3
"""
🔍 Verificar si realmente hay límite en OSC
"""

def verify():
    print("🔍 VERIFICANDO LÍMITE OSC")
    print("=" * 50)
    
    with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
        content = f.read()
    
    # Buscar el método update
    start = content.find("def update(")
    end = content.find("\n    def", start + 1)
    update_method = content[start:end]
    
    print("📋 Código relevante en update():")
    print("-" * 50)
    
    # Buscar la parte de OSC
    lines = update_method.split('\n')
    for i, line in enumerate(lines):
        if "for sid in" in line or "positions" in line or "osc" in line.lower():
            print(f"{i:3d}: {line}")
    
    # Buscar si hay algún slice
    if "[:16]" in update_method:
        print("\n❌ ENCONTRADO LÍMITE [:16]")
    elif "[:" in update_method and "]" in update_method:
        print("\n⚠️ Hay algún slice, verificar...")
    else:
        print("\n✅ No hay límites aparentes")
    
    # Verificar el comentario
    if "# Max 16 sources" in update_method:
        print("\n⚠️ El comentario 'Max 16 sources' está presente pero puede ser obsoleto")

if __name__ == "__main__":
    verify()