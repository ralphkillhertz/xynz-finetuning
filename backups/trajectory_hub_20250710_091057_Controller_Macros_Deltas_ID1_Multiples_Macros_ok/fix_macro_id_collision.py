#!/usr/bin/env python3
"""
🔧 Fix: IDs únicos para cada source en macros
⚡ Evita colisión de IDs al crear múltiples macros
"""

def fix_ids():
    print("🔧 FIX COLISIÓN DE IDS EN MACROS")
    print("=" * 50)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    # Buscar create_macro
    lines = content.split('\n')
    
    # Añadir contador global si no existe
    print("1️⃣ Añadiendo contador global de sources...")
    
    # Buscar __init__
    for i, line in enumerate(lines):
        if "def __init__" in line and "self" in line:
            # Buscar donde inicializar
            j = i + 1
            while j < len(lines) and (lines[j].strip() == "" or lines[j].strip().startswith('"')):
                j += 1
            
            # Buscar si ya existe
            found_counter = False
            for k in range(j, min(j+20, len(lines))):
                if "_next_source_id" in lines[k]:
                    found_counter = True
                    break
            
            if not found_counter:
                # Añadir después de las inicializaciones
                for k in range(j, min(j+30, len(lines))):
                    if "self._" in lines[k] and "=" in lines[k]:
                        lines.insert(k+1, "        self._next_source_id = 1  # Contador global para IDs únicos")
                        print("   ✅ Contador añadido")
                        break
            break
    
    # Fix create_macro para usar IDs únicos
    print("\n2️⃣ Arreglando create_macro...")
    
    for i, line in enumerate(lines):
        if "def create_macro" in line:
            # Buscar donde se crean sources
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("def "):
                if "for i in range" in lines[j] and "create_source" in content[j:j+500]:
                    # Encontrar la línea de create_source
                    for k in range(j, min(j+20, len(lines))):
                        if "create_source" in lines[k] and "source_id" not in lines[k]:
                            print(f"   ❌ Línea {k+1}: {lines[k].strip()}")
                            # Cambiar para usar ID único
                            indent = len(lines[k]) - len(lines[k].lstrip())
                            # Añadir línea para generar ID
                            lines.insert(k, " " * indent + "source_id = self._next_source_id")
                            lines.insert(k+1, " " * indent + "self._next_source_id += 1")
                            k += 2
                            # Modificar create_source para incluir source_id
                            if "create_source(" in lines[k]:
                                lines[k] = lines[k].replace("create_source(", "create_source(source_id=source_id, ")
                            print(f"   ✅ Arreglado para usar IDs únicos")
                            break
                j += 1
            break
    
    # Guardar
    with open(engine_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print("\n✅ Sistema de IDs únicos implementado")
    print("\n🎯 Ahora cada source tendrá un ID único global")

if __name__ == "__main__":
    fix_ids()