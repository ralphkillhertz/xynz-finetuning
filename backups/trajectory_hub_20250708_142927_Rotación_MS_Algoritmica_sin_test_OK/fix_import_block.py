# === fix_import_block.py ===
# 🔧 Fix: Arreglar todo el bloque de import
# ⚡ Impacto: CRÍTICO - Import multi-línea mal formateado

import os

def fix_import_block():
    """Arreglar el bloque completo de imports"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Analizando bloque de import...")
    
    # Buscar el inicio del import problemático
    import_start = -1
    import_end = -1
    
    for i, line in enumerate(lines):
        if 'from trajectory_hub.core.motion_components import' in line:
            import_start = i
            print(f"📍 Import empieza en línea {i+1}")
            
            # Buscar el final del import
            j = i
            while j < len(lines):
                if ')' in lines[j]:
                    import_end = j
                    break
                elif lines[j].strip() and not lines[j].strip().endswith(','):
                    # Si la línea no termina en coma y no está vacía, probablemente terminó
                    if j > i and not lines[j].startswith(' '):
                        import_end = j - 1
                        break
                j += 1
            break
    
    if import_start >= 0:
        print(f"📍 Import termina en línea {import_end+1 if import_end >= 0 else '?'}")
        
        # Mostrar el bloque actual
        print("\n❌ Bloque actual:")
        for i in range(import_start, min(import_end+2 if import_end >= 0 else import_start+10, len(lines))):
            print(f"{i+1:3d}: {lines[i].rstrip()}")
        
        # Extraer todos los elementos a importar
        imports = []
        for i in range(import_start, min(import_end+1 if import_end >= 0 else import_start+10, len(lines))):
            line = lines[i]
            # Limpiar la línea
            line = line.strip()
            if line.startswith('from'):
                line = line.split('import')[1].strip()
            
            # Quitar paréntesis y comas
            line = line.replace('(', '').replace(')', '').replace(',', ' ')
            
            # Extraer nombres
            for name in line.split():
                if name and not name.startswith('#'):
                    imports.append(name)
        
        # Añadir MacroRotation si no está
        if 'MacroRotation' not in imports:
            imports.append('MacroRotation')
        
        print(f"\n✅ Elementos a importar: {imports}")
        
        # Reconstruir el import
        new_import = "from trajectory_hub.core.motion_components import (\n"
        for i, name in enumerate(imports):
            if i < len(imports) - 1:
                new_import += f"    {name},\n"
            else:
                new_import += f"    {name}\n"
        new_import += ")\n"
        
        # Reemplazar el bloque
        # Primero, eliminar las líneas del import antiguo
        del lines[import_start:import_end+1 if import_end >= 0 else import_start+1]
        
        # Insertar el nuevo import
        lines.insert(import_start, new_import)
        
        # Guardar
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("\n✅ Import corregido")
        return True
    else:
        print("❌ No se encontró el import de motion_components")
        return False

if __name__ == "__main__":
    print("🔧 Arreglando bloque de import...")
    
    if fix_import_block():
        print("\n✅ Archivo corregido")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")
    else:
        print("\n❌ Error al corregir")