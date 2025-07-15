#!/usr/bin/env python3
"""
add_concentration_methods.py - Agrega los métodos de concentración que faltan
"""

import os
from datetime import datetime

def add_concentration_methods():
    """Agregar los métodos de concentración al engine"""
    print("🔧 AGREGANDO MÉTODOS DE CONCENTRACIÓN...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup_name = f"{filepath}.backup_methods_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya existen los métodos
    if "def set_macro_concentration" in content:
        print("✅ Los métodos de concentración ya existen")
        return True
    
    # Métodos a agregar
    concentration_methods = '''
    # =========== SISTEMA DE CONCENTRACIÓN ===========
    
    def set_macro_concentration(self, macro_id: str, factor: float, 
                               duration: float = 0.0, mode: str = "fixed_point",
                               target_point: Optional[np.ndarray] = None) -> bool:
        """
        Establecer concentración para un macro
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        factor : float
            Factor de concentración (0=concentrado, 1=disperso)
        duration : float
            Duración de la animación (0 para cambio inmediato)
        mode : str
            Modo: "fixed_point", "follow_macro", "dynamic"
        target_point : np.ndarray, optional
            Punto objetivo (por defecto centro del macro)
            
        Returns
        -------
        bool
            True si se aplicó correctamente
        """
        macro = self._macros.get(macro_id)
        if not macro:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        # Calcular punto objetivo si no se especifica
        if target_point is None:
            positions = []
            for sid in macro.source_ids:
                if sid in self._source_motions:
                    positions.append(self._source_motions[sid].state.position)
            
            if positions:
                target_point = np.mean(positions, axis=0)
            else:
                target_point = np.zeros(3)
                
        # Importar clases necesarias
        from trajectory_hub.core.motion_components import ConcentrationComponent, ConcentrationMode
                
        # Configurar concentración para cada fuente
        for sid in macro.source_ids:
            if sid not in self._source_motions:
                continue
                
            motion = self._source_motions[sid]
            
            # Obtener o crear componente
            if 'concentration' not in motion.components:
                motion.components['concentration'] = ConcentrationComponent()
                
            concentration = motion.components['concentration']
            
            # Configurar parámetros
            concentration.target_point = target_point
            concentration.mode = ConcentrationMode[mode.upper().replace(" ", "_")]
            
            # Configurar atenuación
            concentration.include_macro_trajectory = not (mode == "follow_macro")
            
            # Aplicar
            if duration > 0:
                concentration.start_animation(factor, duration)
            else:
                concentration.set_factor(factor)
                
        # Guardar estado en macro
        macro.concentration_active = (factor < 1.0)
        macro.concentration_point = target_point
        
        logger.info(f"Concentración establecida para {macro_id}: factor={factor}")
        return True
        
    def animate_macro_concentration(self, macro_id: str, target_factor: float,
                                   duration: float = 2.0, 
                                   curve: str = "ease_in_out") -> bool:
        """Animar transición de concentración"""
        macro = self._macros.get(macro_id)
        if not macro:
            return False
            
        # Importar necesario
        from trajectory_hub.core.motion_components import ConcentrationCurve
            
        # Convertir string a enum
        curve_enum = ConcentrationCurve[curve.upper().replace(" ", "_")]
        
        for sid in macro.source_ids:
            if sid in self._source_motions:
                concentration = self._source_motions[sid].components.get('concentration')
                if concentration:
                    concentration.animation_curve = curve_enum
                    
        return self.set_macro_concentration(macro_id, target_factor, duration)
        
    def get_macro_concentration_state(self, macro_id: str) -> Dict:
        """Obtener estado actual de concentración"""
        macro = self._macros.get(macro_id)
        if not macro or not macro.source_ids:
            return {"error": "Macro no encontrado"}
            
        # Obtener del primer source
        first_sid = next(iter(macro.source_ids))
        if first_sid not in self._source_motions:
            return {"error": "Source no encontrado"}
            
        concentration = self._source_motions[first_sid].components.get('concentration')
        if not concentration:
            return {
                "enabled": False,
                "factor": 1.0,
                "mode": "fixed_point",
                "animating": False
            }
            
        return {
            "enabled": concentration.enabled,
            "factor": concentration.factor,
            "mode": concentration.mode.value,
            "animating": concentration.animation_active,
            "target_point": concentration.target_point.tolist(),
            "include_macro_trajectory": concentration.include_macro_trajectory
        }
        
    def toggle_macro_concentration(self, macro_id: str) -> bool:
        """Alternar entre concentrado y disperso"""
        state = self.get_macro_concentration_state(macro_id)
        if state.get("error"):
            return False
            
        current_factor = state.get("factor", 1.0)
        target_factor = 0.0 if current_factor > 0.5 else 1.0
        
        return self.animate_macro_concentration(macro_id, target_factor, 2.0)
        
    def set_concentration_parameters(self, macro_id: str, **params) -> bool:
        """Configurar parámetros avanzados de concentración"""
        macro = self._macros.get(macro_id)
        if not macro:
            return False
            
        for sid in macro.source_ids:
            if sid in self._source_motions:
                concentration = self._source_motions[sid].components.get('concentration')
                if concentration:
                    for key, value in params.items():
                        if hasattr(concentration, key):
                            setattr(concentration, key, value)
                            
        return True
'''
    
    # Buscar dónde insertar (antes del final de la clase)
    # Buscar el método apply_concentration existente
    apply_conc_pos = content.find("def apply_concentration")
    
    if apply_conc_pos != -1:
        # Insertar después de apply_concentration
        # Buscar el siguiente método
        next_def_pos = content.find("\n    def ", apply_conc_pos + 1)
        if next_def_pos != -1:
            insert_pos = next_def_pos
        else:
            # Si no hay siguiente método, buscar el final de la clase
            insert_pos = content.rfind("\nclass ", 0, len(content))
            if insert_pos == -1:
                insert_pos = len(content)
    else:
        # Buscar un buen lugar para insertar (después de update)
        update_pos = content.find("def update(self")
        if update_pos != -1:
            # Buscar el siguiente método después de update
            next_def = content.find("\n    def ", update_pos + 1)
            if next_def != -1:
                insert_pos = next_def
            else:
                insert_pos = len(content)
        else:
            print("❌ No se encontró un lugar adecuado para insertar")
            return False
    
    # Insertar los métodos
    content = content[:insert_pos] + "\n" + concentration_methods + content[insert_pos:]
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Métodos de concentración agregados")
    return True

def fix_update_call():
    """Corregir la llamada a update() para que no requiera dt"""
    print("\n🔧 CORRIGIENDO LLAMADA A UPDATE...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar la firma de update
    update_match = content.find("def update(self")
    if update_match != -1:
        # Buscar hasta el cierre del paréntesis
        paren_close = content.find(")", update_match)
        if paren_close != -1:
            signature = content[update_match:paren_close+1]
            print(f"Firma actual: {signature}")
            
            if "dt" in signature:
                print("⚠️  update() requiere parámetro dt")
                print("Cambiando a update(self) sin parámetros...")
                
                # Reemplazar la firma
                new_signature = "def update(self)"
                content = content[:update_match] + new_signature + content[paren_close+1:]
                
                # Guardar
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print("✅ Firma de update() corregida")
            else:
                print("✅ update() ya tiene la firma correcta")

def create_final_test():
    """Crear test final"""
    test_code = '''#!/usr/bin/env python3
"""
test_concentration_final.py - Test final del sistema de concentración
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

def test_concentration():
    print("🧪 TEST FINAL DEL SISTEMA DE CONCENTRACIÓN\\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro
    print("1. Creando macro con 10 fuentes...")
    macro_id = engine.create_macro("test_concentration", 10, 
                                   formation="circle", spacing=2.0)
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Test concentración inmediata
    print("\\n2. Test concentración inmediata (factor 0.5)")
    result = engine.set_macro_concentration(macro_id, 0.5)
    print(f"   ✅ Concentración aplicada: {result}")
    
    # Obtener estado
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   Factor: {state.get('factor', 'N/A')}")
    print(f"   Habilitado: {state.get('enabled', False)}")
    
    # Test animación
    print("\\n3. Test animación (0.5 → 0.0 en 2s)")
    engine.animate_macro_concentration(macro_id, 0.0, 2.0, "ease_in_out")
    
    # Simular algunos frames
    print("\\n4. Simulando updates...")
    for i in range(10):
        engine.update()
        if i % 5 == 0:
            state = engine.get_macro_concentration_state(macro_id)
            print(f"   Frame {i}: factor={state.get('factor', 'N/A'):.2f}")
    
    # Test toggle
    print("\\n5. Test toggle")
    engine.toggle_macro_concentration(macro_id)
    print("   ✅ Toggle ejecutado")
    
    # Verificar componentes
    print("\\n6. Verificando componentes...")
    if hasattr(engine, '_source_motions') and hasattr(engine, '_macros'):
        macro = engine._macros.get(macro_id)
        if macro and hasattr(macro, 'source_ids'):
            first_sid = next(iter(macro.source_ids))
            if first_sid in engine._source_motions:
                motion = engine._source_motions[first_sid]
                if 'concentration' in motion.components:
                    conc = motion.components['concentration']
                    print(f"   ✅ ConcentrationComponent activo")
                    print(f"   - Factor: {conc.factor:.2f}")
                    print(f"   - Enabled: {conc.enabled}")
                    print(f"   - Mode: {conc.mode.value}")
    
    print("\\n✅ TODOS LOS TESTS COMPLETADOS")

if __name__ == "__main__":
    test_concentration()
'''
    
    with open("test_concentration_final.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("\n✅ test_concentration_final.py creado")

def main():
    print("="*60)
    print("🔧 AGREGANDO MÉTODOS DE CONCENTRACIÓN FALTANTES")
    print("="*60)
    
    # Agregar métodos
    if add_concentration_methods():
        # Corregir update
        fix_update_call()
        
        # Crear test
        create_final_test()
        
        print("\n" + "="*60)
        print("✅ CORRECCIONES APLICADAS")
        print("\nPróximos pasos:")
        print("1. Reinicia Python o la terminal")
        print("2. Ejecuta: python test_concentration_final.py")
        print("3. Usa opción 31 en el controlador interactivo")
    else:
        print("\n❌ No se pudieron agregar los métodos")

if __name__ == "__main__":
    main()