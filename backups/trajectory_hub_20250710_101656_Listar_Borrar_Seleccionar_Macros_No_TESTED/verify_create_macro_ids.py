#!/usr/bin/env python3
"""
🔍 Verificar que create_macro usa IDs únicos
"""

def verify():
    print("🔍 VERIFICANDO CREATE_MACRO")
    print("=" * 50)
    
    with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
        content = f.read()
    
    # Buscar create_macro
    start = content.find("def create_macro")
    if start == -1:
        print("❌ No se encontró create_macro")
        return
    
    end = content.find("\n    def", start + 1)
    if end == -1:
        end = len(content)
    
    method = content[start:end]
    
    print("📋 Método create_macro:")
    print("-" * 50)
    
    # Mostrar solo las líneas relevantes
    lines = method.split('\n')
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in ['source_id', 'create_source', '_next_source_id', 'for i in range']):
            print(f"{i:3d}: {line}")
    
    # Verificar si usa _next_source_id
    if "_next_source_id" in method:
        print("\n✅ Usa _next_source_id")
    else:
        print("\n❌ NO usa _next_source_id - Los IDs colisionarán")
        print("\n💡 El problema es que create_macro no está usando el contador")

if __name__ == "__main__":
    verify()