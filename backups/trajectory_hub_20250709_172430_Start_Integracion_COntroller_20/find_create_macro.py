def find_create_macro():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    print("🔍 BÚSQUEDA MANUAL DE create_macro")
    print("="*60)
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar def create_macro
    in_method = False
    method_start = -1
    method_end = -1
    indent_level = 0
    method_lines = []
    
    for i, line in enumerate(lines):
        if "def create_macro" in line:
            print(f"✅ Encontrado en línea {i+1}: {line.strip()}")
            in_method = True
            method_start = i
            # Detectar nivel de indentación
            indent_level = len(line) - len(line.lstrip())
            method_lines.append(line)
            continue
        
        if in_method:
            # Si la línea tiene menor o igual indentación que def, terminó el método
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and current_indent <= indent_level:
                method_end = i
                break
            method_lines.append(line)
    
    if method_start >= 0:
        print(f"\n📍 Método encontrado: líneas {method_start+1} a {method_end}")
        print(f"📏 Longitud: {len(method_lines)} líneas")
        
        # Buscar si tiene send_position
        has_send = any("send_position" in line for line in method_lines)
        print(f"\n{'✅' if has_send else '❌'} Contiene send_position: {has_send}")
        
        # Buscar el return
        return_line = -1
        for i, line in enumerate(method_lines):
            if "return" in line and "macro" in line:
                return_line = i
                print(f"📍 Return encontrado en línea {i+1} del método")
                break
        
        if not has_send and return_line > 0:
            print("\n🔧 APLICANDO FIX...")
            
            # Insertar antes del return
            osc_code = [
                "\n",
                "        # Enviar posiciones iniciales a Spat\n",
                "        if self.osc_bridge:\n",
                "            for i, sid in enumerate(source_ids):\n",
                "                if sid < len(self._positions):\n",
                "                    self.osc_bridge.send_position(sid, self._positions[sid])\n",
                "                    self.osc_bridge.send_source_name(sid, f\"{name}_{i}\")\n",
                "            print(f\"📡 Enviadas {len(source_ids)} posiciones a Spat\")\n",
            ]
            
            # Insertar en la posición correcta
            method_lines[return_line:return_line] = osc_code
            
            # Reconstruir archivo
            lines[method_start:method_end] = method_lines
            
            # Backup y escribir
            import shutil
            from datetime import datetime
            backup = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(file_path, backup)
            print(f"✅ Backup: {backup}")
            
            with open(file_path, 'w') as f:
                f.writelines(lines)
            
            print("✅ Fix aplicado correctamente")
        else:
            print("\n⚠️ No se puede aplicar fix automáticamente")
    else:
        print("❌ No se encontró create_macro")

if __name__ == "__main__":
    find_create_macro()