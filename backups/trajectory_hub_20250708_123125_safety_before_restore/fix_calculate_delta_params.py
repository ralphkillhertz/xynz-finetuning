# === fix_calculate_delta_params.py ===
# 🔧 Fix: Corregir orden de parámetros en calculate_delta
# ⚡ Líneas modificadas: ~100-120
# 🎯 Impacto: CRÍTICO

import os
import re

def fix_calculate_delta_params():
    """Corrige el orden de parámetros en calculate_delta"""
    
    print("🔧 CORRIGIENDO PARÁMETROS EN calculate_delta\n")
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    # Leer archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Analizando orden de parámetros...")
    
    # Buscar todas las definiciones de calculate_delta
    pattern = r'def calculate_delta\(self,\s*([^)]+)\):'
    matches = list(re.finditer(pattern, content))
    
    print(f"📊 Encontradas {len(matches)} definiciones de calculate_delta")
    
    # Verificar orden en cada una
    for match in matches:
        params = match.group(1).strip()
        print(f"   - Parámetros actuales: {params}")
    
    # El orden correcto debe ser: state, current_time, dt
    # Pero parece que MacroRotation está recibiendo: current_time, dt, state
    
    # Buscar específicamente la clase MacroRotation
    print("\n🔍 Buscando MacroRotation.calculate_delta...")
    
    # Patrón para encontrar el método en MacroRotation
    macro_pattern = r'(class MacroRotation.*?)(def calculate_delta\(self,\s*)([^)]+)(\).*?delta\.source_id = state\.source_id)'
    
    match = re.search(macro_pattern, content, re.DOTALL)
    if match:
        print("✅ Encontrado, corrigiendo orden de parámetros...")
        
        # El problema es que state está en la posición incorrecta
        # Necesitamos verificar qué está recibiendo realmente
        
        # Reemplazar para que coincida con la firma esperada
        # La firma correcta es: calculate_delta(self, state: MotionState, current_time: float, dt: float)
        
        # Buscar y reemplazar la implementación completa
        fixed_pattern = r'''def calculate_delta\(self, state: MotionState, current_time: float, dt: float\) -> MotionDelta:
        """Calcula el cambio de posición debido a la rotación"""
        if not self.enabled or not hasattr(state, 'source_id'):
            return MotionDelta()
            
        # Obtener posición actual
        current_pos = state.position.copy()
        
        # Trasladar al origen (restar centro)
        translated = current_pos - self.center
        
        # Aplicar rotaciones
        angle_x = self.speed_x * dt
        angle_y = self.speed_y * dt  
        angle_z = self.speed_z * dt
        
        # Rotación en Y (más común)
        if abs(angle_y) > 0:
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            new_x = translated[0] * cos_y - translated[2] * sin_y
            new_z = translated[0] * sin_y + translated[2] * cos_y
            translated[0] = new_x
            translated[2] = new_z
            
        # Rotación en X
        if abs(angle_x) > 0:
            cos_x = np.cos(angle_x)
            sin_x = np.sin(angle_x)
            new_y = translated[1] * cos_x - translated[2] * sin_x
            new_z = translated[1] * sin_x + translated[2] * cos_x
            translated[1] = new_y
            translated[2] = new_z
            
        # Rotación en Z
        if abs(angle_z) > 0:
            cos_z = np.cos(angle_z)
            sin_z = np.sin(angle_z)
            new_x = translated[0] * cos_z - translated[1] * sin_z
            new_y = translated[0] * sin_z + translated[1] * cos_z
            translated[0] = new_x
            translated[1] = new_y
        
        # Trasladar de vuelta
        new_pos = translated + self.center
        
        # Calcular delta
        delta = MotionDelta()
        delta.position = new_pos - current_pos
        delta.source_id = state.source_id
        
        return delta'''
        
        # Buscar el método calculate_delta completo en MacroRotation
        calc_pattern = r'(class MacroRotation.*?)(def calculate_delta.*?)(?=\n    def |\n\nclass |\Z)'
        calc_match = re.search(calc_pattern, content, re.DOTALL)
        
        if calc_match:
            # Reemplazar solo el método calculate_delta
            before = calc_match.group(1)
            after = content[calc_match.end():]
            
            content = before + '    ' + fixed_pattern + '\n' + after
            print("✅ Método calculate_delta corregido")
    
    # Guardar
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Archivo actualizado")
    
    # Verificar sintaxis
    print("\n🧪 Verificando sintaxis...")
    import py_compile
    try:
        py_compile.compile(motion_path, doraise=True)
        print("✅ Sintaxis correcta")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        return False

if __name__ == "__main__":
    if fix_calculate_delta_params():
        print("\n🚀 Ejecutando test...")
        os.system("python test_rotation_ms_final.py")