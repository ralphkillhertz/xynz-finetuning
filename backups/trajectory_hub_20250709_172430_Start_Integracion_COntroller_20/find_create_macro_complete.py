def find_and_fix_create_macro():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    print("🔍 BÚSQUEDA COMPLETA DE create_macro")
    print("="*60)
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar desde línea 265
    start_line = 264  # índice 264 = línea 265
    method_lines = []
    return_line_idx = -1
    
    # Buscar hasta encontrar return
    for i in range(start_line, len(lines)):
        line = lines[i]
        method_lines.append((i, line))
        
        # Buscar return que no esté en docstring
        if "return" in line and not line.strip().startswith('"') and not line.strip().startswith('#'):
            return_line_idx = len(method_lines) - 1
            print(f"✅ Return encontrado en línea {i+1}: {line.strip()}")
            break
    
    print(f"📏 Método completo: {len(method_lines)} líneas")
    
    # Verificar si tiene send_position
    has_send = any("send_position" in line[1] for line in method_lines)
    print(f"{'✅' if has_send else '❌'} Contiene send_position: {has_send}")
    
    if not has_send and return_line_idx > 0:
        print("\n🔧 APLICANDO FIX...")
        
        # Código OSC a insertar
        osc_lines = [
            "        # Enviar posiciones iniciales a Spat\n",
            "        if self.osc_bridge and hasattr(self, '_positions'):\n",
            "            for i, sid in enumerate(source_ids):\n",
            "                if sid < len(self._positions):\n",
            "                    self.osc_bridge.send_position(sid, self._positions[sid])\n",
            "                    self.osc_bridge.send_source_name(sid, f\"{name}_{i}\")\n",
            "            print(f\"📡 Enviadas {len(source_ids)} posiciones a Spat\")\n",
            "\n"
        ]
        
        # Insertar antes del return
        insert_at = method_lines[return_line_idx][0]
        
        # Reconstruir archivo
        new_lines = lines[:insert_at] + osc_lines + lines[insert_at:]
        
        # Backup y escribir
        import shutil
        from datetime import datetime
        backup = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup)
        print(f"✅ Backup: {backup}")
        
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
        
        print("✅ Fix aplicado correctamente")
        
        # Test
        print("\n🧪 Creando test...")
        test_code = '''from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
print("Stats antes:", engine.osc_bridge.get_stats()['messages_sent'])

# Crear macro debe enviar posiciones ahora
macro = engine.create_macro("test_osc_fix", 5, formation="circle")

stats = engine.osc_bridge.get_stats()
print(f"Stats después: {stats['messages_sent']} mensajes")
print(f"✅ Verifica en Spat que aparezcan 5 fuentes")
'''
        
        with open("test_osc_fix_final.py", "w") as f:
            f.write(test_code)
        
        print("🚀 Ejecuta: python test_osc_fix_final.py")
    else:
        if has_send:
            print("\n✅ Ya tiene send_position implementado")
        else:
            print("\n❌ No se pudo aplicar fix")

if __name__ == "__main__":
    find_and_fix_create_macro()