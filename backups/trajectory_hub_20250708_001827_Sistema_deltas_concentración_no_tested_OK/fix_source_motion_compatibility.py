#!/usr/bin/env python3
"""
🔧 Fix: Hace SourceMotion compatible con el engine
⚡ Error: 'SourceMotion' object has no attribute 'components'
🎯 Solución: Añadir estructura esperada por el engine
"""

def fix_source_motion_structure():
    """Actualiza SourceMotion para tener la estructura esperada"""
    print("🔧 Actualizando SourceMotion para compatibilidad...\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar la clase SourceMotion
    import re
    source_motion_match = re.search(
        r'(class SourceMotion:.*?)(?=\nclass|\n@dataclass|\Z)',
        content,
        re.DOTALL
    )
    
    if not source_motion_match:
        print("❌ No se encuentra SourceMotion")
        return False
    
    # Nuevo SourceMotion compatible
    new_source_motion = '''class SourceMotion:
    """Gestiona el movimiento y componentes de una fuente"""
    
    def __init__(self, source_id: int):
        self.source_id = source_id
        self.id = source_id  # Alias para compatibilidad
        self.state = MotionState()
        self.position = np.zeros(3)
        self.orientation = np.zeros(3)
        
        # Sistema antiguo (diccionario) para compatibilidad
        self.components = {}
        
        # Sistema nuevo (lista) para deltas
        self.active_components = []
        
    def add_component(self, component, name=None):
        """Añade un componente de movimiento"""
        if component not in self.active_components:
            self.active_components.append(component)
            
        # También añadir al diccionario si tiene nombre
        if name:
            self.components[name] = component
            
    def remove_component(self, component):
        """Elimina un componente"""
        if component in self.active_components:
            self.active_components.remove(component)
            
        # También eliminar del diccionario
        for name, comp in list(self.components.items()):
            if comp == component:
                del self.components[name]
                
    def update(self, current_time: float, dt: float) -> MotionState:
        """Actualiza todos los componentes y retorna el estado"""
        # Actualizar componentes activos (sistema nuevo)
        for component in self.active_components:
            if hasattr(component, 'update'):
                self.state = component.update(self.state, current_time, dt)
                
        # También actualizar componentes del diccionario (compatibilidad)
        for name, component in self.components.items():
            if component not in self.active_components and hasattr(component, 'update'):
                self.state = component.update(self.state, current_time, dt)
                
        return self.state
        
    def update_with_deltas(self, current_time: float, dt: float) -> 'MotionDelta':
        """Versión con deltas - retorna cambio incremental"""
        deltas = []
        
        # Procesar componentes activos
        for component in self.active_components:
            if hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, current_time, dt)
                deltas.append(delta)
            elif hasattr(component, 'update'):
                # Fallback para componentes sin calculate_delta
                old_pos = self.state.position.copy()
                new_state = component.update(self.state, current_time, dt)
                delta = MotionDelta(
                    position=new_state.position - old_pos,
                    source=component.__class__.__name__
                )
                deltas.append(delta)
                self.state = new_state
        
        # Componer deltas
        if not deltas:
            return MotionDelta()
            
        total_weight = sum(d.weight for d in deltas if d.weight > 0)
        if total_weight == 0:
            total_weight = 1.0
            
        result = MotionDelta()
        for delta in deltas:
            if delta.weight > 0:
                w = delta.weight / total_weight
                result.position += delta.position * w
                result.orientation += delta.orientation * w
            
        # Actualizar estado interno
        self.state.position += result.position
        self.state.orientation += result.orientation
        
        return result
'''
    
    # Reemplazar
    content = content.replace(source_motion_match.group(0), new_source_motion)
    
    with open(motion_file, 'w') as f:
        f.write(content)
    
    print("✅ SourceMotion actualizado con compatibilidad completa")
    return True

def add_missing_components():
    """Asegura que existan los componentes que el engine espera"""
    print("\n🔍 Verificando componentes necesarios...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Componentes que pueden faltar
    if 'class IndividualTrajectory' not in content:
        print("⚠️ Falta IndividualTrajectory - añadiendo versión básica...")
        
        individual_trajectory = '''

class IndividualTrajectory(MotionComponent):
    """Trayectoria individual de una fuente"""
    
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.trajectory_type = "static"
        self.position = np.zeros(3)
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualiza según la trayectoria"""
        if not self.enabled:
            return state
            
        # Por ahora, solo retorna el estado sin cambios
        return state
'''
        content += individual_trajectory
        
        with open(motion_file, 'w') as f:
            f.write(content)
        
        print("✅ IndividualTrajectory añadido")

def update_create_macro():
    """Actualiza create_macro para ser compatible con el nuevo sistema"""
    print("\n🔧 Actualizando create_macro en el engine...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar la sección problemática en create_source
    old_pattern = r"motion\.components\['individual_trajectory'\]\.enabled = False"
    
    if old_pattern in content:
        # Reemplazar con código compatible
        new_code = """# Compatibilidad con sistema de componentes
        if hasattr(motion, 'components') and 'individual_trajectory' in motion.components:
            motion.components['individual_trajectory'].enabled = False
        elif hasattr(motion, 'active_components'):
            # Sistema nuevo - buscar y desactivar IndividualTrajectory
            for comp in motion.active_components:
                if comp.__class__.__name__ == 'IndividualTrajectory':
                    comp.enabled = False"""
        
        content = content.replace(
            "motion.components['individual_trajectory'].enabled = False",
            new_code
        )
        
        with open(engine_file, 'w') as f:
            f.write(content)
        
        print("✅ create_source actualizado para compatibilidad")

def main():
    print("🔧 FIX DE COMPATIBILIDAD SOURCEMOTION")
    print("=" * 60)
    
    # 1. Actualizar SourceMotion
    if not fix_source_motion_structure():
        print("\n❌ No se pudo actualizar SourceMotion")
        return
    
    # 2. Añadir componentes faltantes
    add_missing_components()
    
    # 3. Actualizar el engine
    update_create_macro()
    
    print("\n✅ COMPATIBILIDAD COMPLETADA")
    print("\n📋 Ahora ejecuta:")
    print("$ python test_delta_concentration_final.py")

if __name__ == "__main__":
    main()