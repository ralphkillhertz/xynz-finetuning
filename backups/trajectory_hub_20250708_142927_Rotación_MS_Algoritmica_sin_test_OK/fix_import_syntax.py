# === fix_import_syntax.py ===
# 🔧 Corregir el error de sintaxis en los imports
# ⚡ Los imports están en múltiples líneas

from pathlib import Path

print("🔧 Corrigiendo error de sintaxis en imports...")

engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

# Buscar la línea problemática
problem_line = content.find("from trajectory_hub.core.motion_components import (, MacroRotation")
if problem_line > 0:
    print("❌ Error de sintaxis encontrado")
    print("🔧 Corrigiendo...")
    
    # Buscar el inicio real de los imports
    import_start = content.find("from trajectory_hub.core.motion_components import")
    if import_start == -1:
        import_start = content.find("from .motion_components import")
    
    if import_start > 0:
        # Buscar el paréntesis de cierre
        paren_close = content.find(")", import_start)
        if paren_close > 0:
            # Extraer todo el bloque de imports
            import_block = content[import_start:paren_close+1]
            print(f"Bloque de imports actual:\n{import_block}")
            
            # Si MacroRotation no está, añadirla antes del paréntesis de cierre
            if "MacroRotation" not in import_block:
                # Encontrar el último import antes del )
                last_comma = import_block.rfind(",")
                if last_comma > 0:
                    # Insertar después de la última coma
                    new_import_block = import_block[:paren_close-import_start] + ",\n    MacroRotation" + import_block[paren_close-import_start:]
                else:
                    # Insertar antes del paréntesis
                    new_import_block = import_block[:paren_close-import_start] + ",\n    MacroRotation" + import_block[paren_close-import_start:]
                
                # Reemplazar en el contenido
                content = content[:import_start] + new_import_block + content[paren_close+1:]
            else:
                # Si ya está pero mal formateado, reconstruir
                print("🔧 Reconstruyendo imports...")
                
                # Extraer todos los imports
                imports = []
                lines = import_block.split('\n')
                for line in lines:
                    # Limpiar y extraer nombres
                    line = line.strip()
                    if line and not line.startswith('from') and line != '(' and line != ')':
                        # Quitar comas y espacios
                        items = line.rstrip(',').split(',')
                        for item in items:
                            item = item.strip()
                            if item and item != '(' and item != ')':
                                imports.append(item)
                
                # Añadir MacroRotation si no está
                if "MacroRotation" not in imports:
                    imports.append("MacroRotation")
                
                # Reconstruir el import
                new_import = "from trajectory_hub.core.motion_components import (\n"
                for i, imp in enumerate(imports):
                    if i < len(imports) - 1:
                        new_import += f"    {imp},\n"
                    else:
                        new_import += f"    {imp}\n"
                new_import += ")"
                
                # Reemplazar
                content = content[:import_start] + new_import + content[paren_close+1:]
            
            # Guardar
            engine_path.write_text(content)
            print("✅ Imports corregidos")
else:
    print("🔍 Verificando estructura de imports...")
    
    # Buscar y mostrar la estructura actual
    import_start = content.find("from trajectory_hub.core.motion_components import")
    if import_start > 0:
        # Mostrar las siguientes 10 líneas
        lines = content[import_start:].split('\n')[:10]
        print("Estructura actual:")
        for line in lines:
            print(f"  {line}")

print("\n✅ Archivo corregido")
print("📝 Ejecuta: python test_rotation_final_working.py")