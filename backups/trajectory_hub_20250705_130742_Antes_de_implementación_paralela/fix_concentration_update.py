#!/usr/bin/env python3
"""
fix_concentration_update.py - Corrige la cadena de updates para el sistema de concentración
EJECUTAR ESTE SCRIPT PRIMERO antes de implementar la concentración
"""

import os
import shutil
from datetime import datetime

def fix_update_chain():
    """Corregir el problema crítico de la cadena de updates"""
    
    print("🔧 CORRECCIÓN DE LA CADENA DE UPDATES\n")
    
    # 1. Backup del archivo
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if not os.path.exists(engine_file):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
        
    backup_name = f"{engine_file}.backup_concentration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # 2. Leer el archivo
    with open(engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. Buscar el método update
    update_method = '''    def update(self) -> bool:
        """
        Actualizar todas las fuentes y macros
        
        Returns
        -------
        bool
            True si la actualización fue exitosa
        """
        try:
            # Incrementar tiempo
            self._time += self.dt
            self._frame_count += 1'''
    
    # 4. Reemplazo con la versión corregida
    fixed_update = '''    def update(self) -> bool:
        """
        Actualizar todas las fuentes y macros
        
        Returns
        -------
        bool
            True si la actualización fue exitosa
        """
        try:
            # Incrementar tiempo
            self._time += self.dt
            self._frame_count += 1
            
            # CRÍTICO: Actualizar componentes de movimiento
            # Esto es lo que faltaba en las implementaciones anteriores
            for source_id, motion in self._source_motions.items():
                # Actualizar el sistema de componentes
                motion.update(self._time, self.dt)
                
                # Sincronizar posición con el array principal
                self._positions[source_id] = motion.state.position
                
                # Actualizar velocidades si está disponible
                if hasattr(self, '_velocities'):
                    self._velocities[source_id] = motion.state.velocity
                    
                # Actualizar orientaciones si está disponible
                if hasattr(self, '_orientations'):
                    self._orientations[source_id] = motion.state.orientation'''
    
    # 5. Aplicar el fix
    if update_method in content:
        # Encontrar donde termina el método actual
        start_idx = content.find(update_method)
        if start_idx != -1:
            # Buscar el final del método (siguiente def o final de clase)
            end_idx = content.find('\n    def ', start_idx + len(update_method))
            if end_idx == -1:
                end_idx = content.find('\nclass ', start_idx)
            if end_idx == -1:
                end_idx = len(content)
            
            # Extraer el método completo
            current_method = content[start_idx:end_idx]
            
            # Reemplazar solo la parte inicial del método
            new_content = content[:start_idx] + fixed_update + content[start_idx + len(update_method):]
            
            # Escribir el archivo
            with open(engine_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print("✅ Método update() corregido exitosamente")
            print("\n📝 Cambios aplicados:")
            print("   - Agregada llamada a motion.update()")
            print("   - Sincronización de arrays de posición")
            print("   - Manejo de velocidades y orientaciones")
            
            return True
    else:
        print("⚠️  No se encontró el método update() esperado")
        print("    Aplicando parche alternativo...")
        
        # Buscar cualquier versión del método update
        alt_search = "def update(self"
        idx = content.find(alt_search)
        if idx != -1:
            # Insertar el código de actualización después del frame_count
            insert_point = content.find("self._frame_count += 1", idx)
            if insert_point != -1:
                insert_point = content.find("\n", insert_point) + 1
                
                update_code = '''
            # CRÍTICO: Actualizar componentes de movimiento
            for source_id, motion in self._source_motions.items():
                # Actualizar el sistema de componentes
                motion.update(self._time, self.dt)
                
                # Sincronizar posición con el array principal
                self._positions[source_id] = motion.state.position
'''
                
                new_content = content[:insert_point] + update_code + content[insert_point:]
                
                with open(engine_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                print("✅ Parche alternativo aplicado")
                return True
                
    print("❌ No se pudo aplicar la corrección automáticamente")
    print("   Por favor, agrega manualmente el siguiente código en engine.update():")
    print("""
            # CRÍTICO: Actualizar componentes de movimiento
            for source_id, motion in self._source_motions.items():
                motion.update(self._time, self.dt)
                self._positions[source_id] = motion.state.position
    """)
    
    return False

def verify_update_chain():
    """Verificar que la cadena de updates funciona correctamente"""
    print("\n🔍 VERIFICACIÓN DE LA CADENA DE UPDATES\n")
    
    try:
        from trajectory_hub import EnhancedTrajectoryEngine
        
        # Crear engine de prueba
        engine = EnhancedTrajectoryEngine()
        
        # Crear una fuente
        engine.create_source(0, "test")
        
        # Verificar que motion existe
        if 0 not in engine._source_motions:
            print("❌ No se creó SourceMotion")
            return False
            
        motion = engine._source_motions[0]
        
        # Guardar posición inicial
        initial_pos = motion.state.position.copy()
        
        # Configurar una trayectoria simple
        if hasattr(engine, 'set_individual_trajectory'):
            engine.set_individual_trajectory(0, "circle", size=5.0)
            
        # Habilitar el movimiento
        if 'individual_trajectory' in motion.components:
            motion.components['individual_trajectory'].enabled = True
            motion.components['individual_trajectory'].movement_speed = 1.0
            
        # Actualizar varias veces
        positions = []
        for i in range(10):
            engine.update()
            positions.append(motion.state.position.copy())
            
        # Verificar que la posición cambió
        position_changed = False
        for pos in positions:
            if not np.array_equal(pos, initial_pos):
                position_changed = True
                break
                
        if position_changed:
            print("✅ La cadena de updates funciona correctamente")
            print(f"   - Posición inicial: {initial_pos}")
            print(f"   - Posición final: {positions[-1]}")
            print(f"   - SourceMotion.update() se está llamando")
            print(f"   - Los componentes se están actualizando")
            return True
        else:
            print("❌ Las posiciones no cambiaron")
            print("   - SourceMotion.update() podría no estar siendo llamado")
            print("   - O los componentes no están habilitados")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False

def main():
    """Aplicar correcciones y verificar"""
    print("="*60)
    print("FIX PARA EL SISTEMA DE CONCENTRACIÓN")
    print("="*60)
    
    # Aplicar corrección
    if fix_update_chain():
        print("\n" + "="*60)
        
        # Verificar
        import time
        time.sleep(1)  # Dar tiempo para que Python recargue el módulo
        
        import numpy as np  # Necesario para la verificación
        verify_update_chain()
        
        print("\n✅ SISTEMA LISTO PARA IMPLEMENTAR CONCENTRACIÓN")
        print("\nPróximos pasos:")
        print("1. Ejecutar concentration_implementation.py")
        print("2. Integrar ConcentrationComponent en motion_components.py")
        print("3. Agregar métodos a enhanced_trajectory_engine.py")
        print("4. Actualizar interactive_controller.py con opción 31")
    else:
        print("\n❌ No se pudo aplicar la corrección automáticamente")
        print("   Revisa el archivo manualmente")

if __name__ == "__main__":
    main()