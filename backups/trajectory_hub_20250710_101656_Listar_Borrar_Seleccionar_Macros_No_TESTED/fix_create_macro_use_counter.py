#!/usr/bin/env python3
"""
🔧 Fix: Hacer que create_macro use el contador de IDs
⚡ Solución definitiva para múltiples macros
"""

def fix_create_macro():
    print("🔧 FIX CREATE_MACRO - USAR CONTADOR IDS")
    print("=" * 50)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar create_macro
    in_create_macro = False
    fixed = False
    
    for i, line in enumerate(lines):
        if "def create_macro" in line:
            in_create_macro = True
            print(f"📍 Encontrado create_macro en línea {i+1}")
        elif in_create_macro and line.strip() and not line[0].isspace():
            in_create_macro = False
        
        # Buscar donde se usa 'sid' sin definir
        if in_create_macro and "for i in range" in line:
            print(f"\n📍 Loop encontrado en línea {i+1}: {line.strip()}")
            
            # Buscar las siguientes líneas
            for j in range(i+1, min(i+10, len(lines))):
                if "self.create_source(sid" in lines[j]:
                    print(f"❌ Línea {j+1} usa 'sid' sin definir: {lines[j].strip()}")
                    
                    # Arreglar - añadir generación de ID antes
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    
                    # Insertar líneas para generar ID único
                    new_lines = [
                        " " * indent + "# Generar ID único",
                        " " * indent + "sid = self._next_source_id",
                        " " * indent + "self._next_source_id += 1"
                    ]
                    
                    # Insertar antes de create_source
                    for new_line in reversed(new_lines):
                        lines.insert(j, new_line)
                    
                    print("\n✅ Añadidas líneas para generar ID único:")
                    for new_line in new_lines:
                        print(f"   {new_line}")
                    
                    fixed = True
                    break
            
            if fixed:
                break
    
    if not fixed:
        # Buscar patrón alternativo
        print("\n🔍 Buscando patrón alternativo...")
        for i, line in enumerate(lines):
            if in_create_macro and "sid" in line and "create_source" not in line:
                print(f"   Línea {i+1}: {line.strip()}")
    
    # Guardar si se hizo algún cambio
    if fixed:
        with open(engine_path, 'w') as f:
            f.write('\n'.join(lines))
        print("\n✅ create_macro arreglado para usar IDs únicos")
    else:
        print("\n⚠️ No se pudo arreglar automáticamente")
        print("\n💡 Mostrando contexto de create_macro...")
        
        # Mostrar más contexto
        start = content.find("def create_macro")
        end = content.find("\n    def", start + 1)
        method = content[start:end if end > 0 else start + 500]
        
        print("\n📋 Primeras 20 líneas de create_macro:")
        for i, line in enumerate(method.split('\n')[:20]):
            print(f"{i:3d}: {line}")

if __name__ == "__main__":
    fix_create_macro()