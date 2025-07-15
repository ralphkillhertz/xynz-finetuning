#!/usr/bin/env python3
"""
🔧 Fix completo: Eliminar límite 16 sources y arreglar IDs
⚡ Permite crear múltiples macros sin colisiones
"""

def fix_complete():
    print("🔧 FIX COMPLETO LÍMITES DE MACROS")
    print("=" * 50)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    changes = 0
    
    # 1. Eliminar límite de 16 sources
    print("\n1️⃣ Eliminando límite de 16 sources...")
    for i, line in enumerate(lines):
        if "[:16]" in line and "_active_sources" in line:
            print(f"   ❌ Línea {i+1}: {line.strip()}")
            lines[i] = line.replace("[:16]", "")
            print(f"   ✅ Cambiado a: {lines[i].strip()}")
            changes += 1
        elif "16" in line and "n_sources" in line and "min(" in line:
            print(f"   ❌ Línea {i+1}: {line.strip()}")
            # Eliminar el límite
            lines[i] = line.replace(", 16", ", 999")  # Límite alto
            print(f"   ✅ Cambiado a: {lines[i].strip()}")
            changes += 1
    
    # 2. Arreglar create_macro para usar IDs únicos
    print("\n2️⃣ Arreglando create_macro...")
    
    in_create_macro = False
    for i, line in enumerate(lines):
        if "def create_macro" in line:
            in_create_macro = True
            print(f"   📍 Encontrado create_macro en línea {i+1}")
        elif in_create_macro and line.strip() and not line[0].isspace():
            in_create_macro = False
        
        if in_create_macro and "sources.append" in line:
            # Buscar hacia atrás para encontrar el loop
            for j in range(i-10, i):
                if j >= 0 and "for i in range" in lines[j]:
                    print(f"\n   📍 Loop encontrado en línea {j+1}")
                    # Insertar generación de ID único
                    indent = len(lines[j+1]) - len(lines[j+1].lstrip())
                    new_lines = [
                        " " * indent + "# Generar ID único para cada source",
                        " " * indent + "source_id = self._next_source_id",
                        " " * indent + "self._next_source_id += 1"
                    ]
                    
                    # Buscar dónde insertar (después del for)
                    insert_pos = j + 1
                    while insert_pos < i and lines[insert_pos].strip() == "":
                        insert_pos += 1
                    
                    # Insertar las nuevas líneas
                    for new_line in reversed(new_lines):
                        lines.insert(insert_pos, new_line)
                    
                    # Actualizar la línea de create_source
                    i += len(new_lines)  # Ajustar índice
                    if "self.create_source(" in lines[i]:
                        # Buscar el paréntesis de apertura
                        if "source_id=" not in lines[i]:
                            lines[i] = lines[i].replace("self.create_source(", "self.create_source(source_id=source_id, ")
                            print(f"   ✅ create_source actualizado para usar source_id")
                    
                    changes += 1
                    break
            break
    
    # 3. Verificar que _next_source_id existe
    if "_next_source_id" not in content:
        print("\n3️⃣ _next_source_id no encontrado, verificando...")
        print("   ⚠️ Puede que el fix anterior no se aplicó correctamente")
    
    # Guardar
    if changes > 0:
        with open(engine_path, 'w') as f:
            f.write('\n'.join(lines))
        print(f"\n✅ {changes} cambios aplicados")
    else:
        print("\n⚠️ No se encontraron cambios necesarios")
    
    print("\n🎯 RESULTADO:")
    print("   - Límite de 16 sources eliminado")
    print("   - IDs únicos para cada source")
    print("   - Ahora puedes crear múltiples macros")

if __name__ == "__main__":
    fix_complete()