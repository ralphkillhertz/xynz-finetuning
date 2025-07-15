# === fix_manual_individual_rotation.py ===
# 🔧 Fix: Corregir ManualIndividualRotation
# ⚡ Arreglar center, update y sincronización

def fix_manual_rotation():
    """Corregir problemas en ManualIndividualRotation"""
    
    print("🔧 FIX: ManualIndividualRotation")
    print("=" * 60)
    
    import os
    file_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_applied = []
    
    # Fix 1: Corregir el método update para que tenga la firma correcta
    print("\n1️⃣ Corrigiendo firma de update()...")
    
    # Buscar la definición del método update en ManualIndividualRotation
    old_update = """    def update(self, state: 'MotionState', current_time: float, dt: float):"""
    new_update = """    def update(self, current_time: float, dt: float):"""
    
    if old_update in content:
        content = content.replace(old_update, new_update)
        fixes_applied.append("Firma de update() corregida")
    
    # Fix 2: Asegurar que calculate_delta use el centro correcto
    print("\n2️⃣ Verificando calculate_delta...")
    
    # Buscar el método set_manual_individual_rotation en enhanced_trajectory_engine.py
    engine_file = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(engine_file, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # Buscar y corregir el método
    import re
    
    # Patrón para encontrar set_manual_individual_rotation
    pattern = r'def set_manual_individual_rotation\(self,[^}]+?\n\s+return'
    match = re.search(pattern, engine_content, re.DOTALL)
    
    if match:
        method_text = match.group(0)
        
        # Verificar si el center se está configurando mal
        if 'center=self._positions[source_id]' in method_text or 'center=position' in method_text:
            print("   ❌ Encontrado: center se configura con la posición")
            
            # Reemplazar para usar [0,0,0] como centro por defecto
            new_method = method_text.replace(
                'center=self._positions[source_id]',
                'center=np.array([0.0, 0.0, 0.0])'
            ).replace(
                'center=position',
                'center=np.array([0.0, 0.0, 0.0])'
            )
            
            engine_content = engine_content.replace(method_text, new_method)
            fixes_applied.append("Center configurado correctamente a [0,0,0]")
    
    # Fix 3: Inicializar current_yaw correctamente
    print("\n3️⃣ Corrigiendo inicialización de current_yaw...")
    
    # En ManualIndividualRotation, buscar donde se calcula current_yaw inicial
    old_init = """self.current_yaw = np.arctan2(position[1], position[0])"""
    new_init = """self.current_yaw = 0.0  # Siempre empezar desde 0"""
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        fixes_applied.append("current_yaw inicializado a 0")
    
    # Guardar archivos
    if fixes_applied:
        print("\n📝 Aplicando correcciones...")
        
        # Backup
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        shutil.copy(file_path, f"{file_path}.backup_{timestamp}")
        shutil.copy(engine_file, f"{engine_file}.backup_{timestamp}")
        
        # Escribir archivos corregidos
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        with open(engine_file, 'w', encoding='utf-8') as f:
            f.write(engine_content)
        
        print("\n✅ Correcciones aplicadas:")
        for fix in fixes_applied:
            print(f"   - {fix}")
    else:
        print("\n⚠️ No se encontraron los patrones esperados")
        print("   Revisando manualmente...")
    
    # Test rápido
    print("\n4️⃣ Test rápido:")
    try:
        from trajectory_hub.core.motion_components import ManualIndividualRotation
        component = ManualIndividualRotation()
        print(f"   Center por defecto: {component.center}")
        print(f"   Current yaw inicial: {component.current_yaw}")
        print("   ✅ Componente creado correctamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📋 Próximo paso: python test_manual_is_fixed.py")

if __name__ == "__main__":
    fix_manual_rotation()