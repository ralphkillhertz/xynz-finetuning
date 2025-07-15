#!/usr/bin/env python3
"""
🔧 Fix: Cierra correctamente la definición de create_macro
⚡ Arregla: Falta ): al final de los parámetros
🎯 Impacto: CRÍTICO - Sistema no arranca
"""

def fix_create_macro():
    """Arregla la definición de create_macro"""
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    # Leer archivo
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    print("🔍 Buscando línea con **kwargs...")
    
    # Buscar la línea con **kwargs
    fixed = False
    for i in range(len(lines)):
        if "**kwargs" in lines[i] and "def create_macro" in ''.join(lines[max(0, i-10):i+1]):
            print(f"📍 Encontrado en línea {i+1}: {lines[i].strip()}")
            
            # Verificar si ya tiene ):
            if not lines[i].rstrip().endswith('):'):
                # Añadir ): al final
                lines[i] = lines[i].rstrip() + '):\n'
                fixed = True
                print("✅ Añadido ): al final de la línea")
            else:
                print("⚠️ Ya tiene ): al final")
            break
    
    if fixed:
        # Backup
        backup_path = f"{engine_path}.backup_fix_create_macro"
        with open(backup_path, 'w') as f:
            f.writelines(lines)
        
        # Escribir archivo corregido
        with open(engine_path, 'w') as f:
            f.writelines(lines)
        
        print(f"\n✅ create_macro cerrado correctamente")
        print(f"📁 Backup: {backup_path}")
        
        # Verificar resultado
        print("\n🔍 Verificando fix...")
        with open(engine_path, 'r') as f:
            lines = f.readlines()
        
        # Mostrar líneas 305-315
        print("\nCONTEXTO DESPUÉS DEL FIX:")
        print("-" * 60)
        for i in range(304, min(len(lines), 315)):
            print(f"{i+1:4d}    {lines[i]}", end='')
        print("-" * 60)
        
    else:
        print("❌ No se encontró el problema o ya estaba arreglado")
    
    return fixed

if __name__ == "__main__":
    if fix_create_macro():
        print("\n🎯 Ahora ejecuta: python check_current_implementation.py")
    else:
        print("\n⚠️ Revisa manualmente enhanced_trajectory_engine.py")