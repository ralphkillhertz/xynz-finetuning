# === fix_init_indentation.py ===
# 🔧 Fix: Arreglar indentación de __init__ y docstring
# ⚡ Docstring sin indentar y código atrapado dentro

import os

def fix_init_indentation():
    """Arreglar indentación en __init__ y sacar código de docstring"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_init_indent', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Analizando problema de __init__...")
    
    # Mostrar más contexto
    print("\n📋 Contexto extendido (líneas 106-125):")
    for i in range(105, min(125, len(lines))):
        if i < len(lines):
            marker = ">>>" if i in [109, 110, 111] else "   "
            print(f"{marker} {i+1}: {repr(lines[i])}")  # usar repr para ver espacios
    
    # Buscar y arreglar __init__
    for i in range(len(lines)):
        if 'def __init__' in lines[i]:
            print(f"\n📍 Procesando __init__ en línea {i+1}")
            
            # Encontrar dónde termina la definición
            j = i
            while j < len(lines) and not lines[j].rstrip().endswith(':'):
                j += 1
            
            if j < len(lines):
                print(f"✅ Definición termina en línea {j+1}")
                
                # Calcular indentación correcta
                base_indent = len(lines[i]) - len(lines[i].lstrip())
                body_indent = base_indent + 4
                
                print(f"📏 Indentación base: {base_indent} espacios")
                print(f"📏 Indentación del cuerpo: {body_indent} espacios")
                
                # Verificar la siguiente línea
                if j+1 < len(lines):
                    next_line = lines[j+1]
                    
                    # Si es una docstring mal indentada
                    if next_line.strip().startswith('"""'):
                        print(f"❌ Docstring mal indentada en línea {j+2}")
                        
                        # Buscar el final de la docstring
                        k = j + 1
                        docstring_end = -1
                        quotes_count = 0
                        
                        while k < len(lines):
                            quotes_count += lines[k].count('"""')
                            if quotes_count >= 2:  # Apertura y cierre
                                docstring_end = k
                                break
                            k += 1
                        
                        if docstring_end == -1:
                            # La docstring no se cierra, buscar hasta encontrar código
                            print("⚠️ Docstring no cerrada correctamente")
                            
                            # Buscar líneas que parecen código Python
                            for k in range(j+2, min(j+50, len(lines))):
                                line = lines[k].strip()
                                if line and (line.startswith('self.') or 
                                           '=' in line or 
                                           line.startswith('super()')):
                                    docstring_end = k - 1
                                    print(f"📍 Código detectado en línea {k+1}, asumiendo fin de docstring")
                                    break
                        
                        # Arreglar la indentación de la docstring
                        lines[j+1] = ' ' * body_indent + lines[j+1].lstrip()
                        
                        # Si el contenido está dentro de la docstring, sacarlo
                        if docstring_end > j+1:
                            print(f"✅ Procesando contenido entre líneas {j+2} y {docstring_end+1}")
                            
                            # Verificar si hay código real dentro
                            has_code = False
                            for m in range(j+2, docstring_end+1):
                                if 'self.' in lines[m] or 'super()' in lines[m]:
                                    has_code = True
                                    break
                            
                            if has_code:
                                print("❌ Código Python encontrado dentro de la docstring")
                                
                                # Cerrar la docstring inmediatamente
                                lines[j+1] = ' ' * body_indent + '"""Initialize the enhanced trajectory engine"""\n'
                                
                                # Indentar el código correctamente
                                for m in range(j+2, docstring_end+1):
                                    if lines[m].strip():
                                        # Quitar indentación extra si la hay
                                        lines[m] = ' ' * body_indent + lines[m].strip() + '\n'
                                
                                print("✅ Docstring cerrada y código extraído")
                        
                        else:
                            # Solo arreglar la indentación
                            print("✅ Docstring indentada correctamente")
                            
                            # Asegurar que hay algo después de la docstring
                            if j+2 < len(lines) and not lines[j+2].strip():
                                # Añadir pass temporal
                                lines.insert(j+2, ' ' * body_indent + 'pass  # TODO: implementar\n')
                                print("✅ Añadido 'pass' temporal")
            
            break  # Solo procesar el primer __init__
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")

def test_result():
    """Verificar el resultado"""
    print("\n🧪 Verificando resultado...")
    
    import subprocess
    
    # Test de sintaxis
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'trajectory_hub/core/enhanced_trajectory_engine.py'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Test rápido del sistema
        print("\n🚀 Test rápido del sistema...")
        try:
            from trajectory_hub.core import EnhancedTrajectoryEngine
            engine = EnhancedTrajectoryEngine(max_sources=5)
            print("✅ Engine creado exitosamente")
            
            # Test completo
            print("\n📊 Ejecutando test completo...")
            result = subprocess.run(['python', 'test_delta_100.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            if '100%' in result.stdout:
                print("\n🎉 ¡SISTEMA 100% FUNCIONAL!")
            else:
                # Buscar porcentaje
                import re
                match = re.search(r'(\d+)%', result.stdout)
                if match:
                    print(f"📊 Sistema al {match.group(1)}% funcional")
                    
                # Mostrar errores si hay
                if 'Error' in result.stdout:
                    print("\n⚠️ Errores encontrados:")
                    for line in result.stdout.split('\n'):
                        if 'Error:' in line:
                            print(f"   {line.strip()}")
                            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {str(e)[:200]}")
            
    else:
        print(f"❌ Error de sintaxis:\n{result.stderr}")

if __name__ == "__main__":
    print("🔧 FIXING __INIT__ INDENTATION")
    print("=" * 60)
    
    fix_init_indentation()
    test_result()