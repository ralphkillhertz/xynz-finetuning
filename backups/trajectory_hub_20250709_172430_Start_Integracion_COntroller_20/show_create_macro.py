def show_create_macro():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    print("📄 CONTENIDO DE create_macro")
    print("="*60)
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Mostrar líneas 265-272
    start = 264  # índice 264 = línea 265
    end = 272
    
    print(f"Líneas {start+1} a {end}:\n")
    
    for i in range(start, min(end, len(lines))):
        print(f"{i+1:4d}: {lines[i]}", end='')
    
    print("\n" + "="*60)
    
    # Buscar si el método continúa
    print("\n🔍 Buscando continuación del método...")
    
    # Mostrar más líneas para ver si continúa
    for i in range(end, min(end+20, len(lines))):
        line = lines[i]
        if line.strip() and not line.startswith(' '):
            print(f"\n⚠️ Nuevo método/clase encontrado en línea {i+1}")
            break
        if "return" in line:
            print(f"✅ Return encontrado en línea {i+1}: {line.strip()}")
        print(f"{i+1:4d}: {lines[i]}", end='')

if __name__ == "__main__":
    show_create_macro()