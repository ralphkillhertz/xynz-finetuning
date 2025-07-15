"""
scale_adjuster.py - Utilidad para ajustar escalas de trayectorias a rangos perceptuales óptimos
"""
import numpy as np

class ScaleConfig:
    """Configuración de escalas para diferentes contextos"""
    
    # Rangos óptimos para Spat Revolution (en metros)
    INTIMATE_RANGE = (0.5, 3.0)      # Muy cerca, íntimo
    CLOSE_RANGE = (2.0, 8.0)         # Cercano, detallado
    MEDIUM_RANGE = (5.0, 15.0)       # Medio, balanced
    FAR_RANGE = (10.0, 30.0)         # Lejano, ambiental
    EXTREME_RANGE = (20.0, 50.0)     # Muy lejano, efectos especiales
    
    # Configuración por defecto recomendada
    DEFAULT_CONFIG = {
        'formation_spacing': 1.0,      # Espaciado entre fuentes en formación
        'trajectory_radius': 3.0,      # Radio base para trayectorias circulares
        'trajectory_height': 1.0,      # Variación vertical máxima
        'breathing_amplitude': 0.5,    # Amplitud de respiración
        'force_field_radius': 4.0,     # Radio de campos de fuerza
        'random_movement_range': 0.3,  # Rango de movimiento aleatorio
        'macro_trajectory_scale': 8.0, # Escala de trayectoria macro
    }
    
    @staticmethod
    def get_scaled_trajectory(base_func, scale_factor=1.0, center_offset=None):
        """
        Escalar y centrar una función de trayectoria
        
        Parameters
        ----------
        base_func : callable
            Función de trayectoria original
        scale_factor : float
            Factor de escala (0.1 = 10% del tamaño original)
        center_offset : np.ndarray, optional
            Offset del centro (default: origen)
        """
        if center_offset is None:
            center_offset = np.zeros(3)
            
        def scaled_trajectory(t):
            pos = base_func(t)
            return pos * scale_factor + center_offset
            
        return scaled_trajectory
    
    @staticmethod
    def create_perceptual_zones(n_zones=3):
        """
        Crear zonas perceptuales concéntricas
        
        Returns
        -------
        list of dict
            Zonas con nombre, rango y características
        """
        zones = [
            {
                'name': 'intimate',
                'range': ScaleConfig.INTIMATE_RANGE,
                'description': 'Zona íntima - máximo detalle espacial',
                'suggested_sources': 1-4,
                'movement_scale': 0.3
            },
            {
                'name': 'personal',
                'range': ScaleConfig.CLOSE_RANGE,
                'description': 'Zona personal - movimientos claros',
                'suggested_sources': 4-12,
                'movement_scale': 0.6
            },
            {
                'name': 'social',
                'range': ScaleConfig.MEDIUM_RANGE,
                'description': 'Zona social - balance percepción/espacio',
                'suggested_sources': 8-20,
                'movement_scale': 1.0
            },
            {
                'name': 'public',
                'range': ScaleConfig.FAR_RANGE,
                'description': 'Zona pública - movimientos amplios',
                'suggested_sources': 15-40,
                'movement_scale': 1.5
            }
        ]
        
        return zones[:n_zones]


def create_scaled_shapes(scale_config=None):
    """
    Crear funciones de forma pre-escaladas para el rango óptimo
    """
    if scale_config is None:
        scale_config = ScaleConfig.DEFAULT_CONFIG
        
    shapes = {
        "circle": lambda t: np.array([
            scale_config['trajectory_radius'] * np.cos(t),
            scale_config['trajectory_radius'] * np.sin(t),
            0
        ]),
        
        "lissajous": lambda t: np.array([
            scale_config['trajectory_radius'] * 0.8 * np.sin(3 * t),
            scale_config['trajectory_radius'] * 0.8 * np.sin(4 * t + np.pi/4),
            scale_config['trajectory_height'] * 0.3 * np.sin(5 * t)
        ]),
        
        "spiral": lambda t: np.array([
            (scale_config['trajectory_radius'] * 0.3 + 0.02 * t) * np.cos(t),
            (scale_config['trajectory_radius'] * 0.3 + 0.02 * t) * np.sin(t),
            scale_config['trajectory_height'] * 0.1 * t
        ]),
        
        "helix": lambda t: np.array([
            scale_config['trajectory_radius'] * 0.7 * np.cos(t),
            scale_config['trajectory_radius'] * 0.7 * np.sin(t),
            scale_config['trajectory_height'] * 0.2 * t
        ]),
        
        "figure8": lambda t: np.array([
            scale_config['trajectory_radius'] * np.sin(t),
            scale_config['trajectory_radius'] * 0.5 * np.sin(t) * np.cos(t),
            0
        ])
    }
    
    return shapes


def apply_perceptual_scaling(engine, macro_id, zone='personal'):
    """
    Aplicar escalado perceptual a un macro existente
    
    Parameters
    ----------
    engine : EnhancedTrajectoryEngine
        Motor de trayectorias
    macro_id : str
        ID del macro a escalar
    zone : str
        Zona perceptual objetivo ('intimate', 'personal', 'social', 'public')
    """
    zones = {z['name']: z for z in ScaleConfig.create_perceptual_zones(4)}
    
    if zone not in zones:
        raise ValueError(f"Zona no válida: {zone}")
        
    zone_config = zones[zone]
    scale_factor = zone_config['movement_scale']
    
    # Obtener el macro
    if macro_id not in engine._macros:
        raise ValueError(f"Macro no encontrado: {macro_id}")
        
    macro = engine._macros[macro_id]
    
    # Escalar las posiciones actuales
    for sid in macro.source_ids:
        if sid in engine._source_motions:
            motion = engine._source_motions[sid]
            # Escalar posición actual
            motion.state.position *= scale_factor
            
            # Si tiene trayectoria individual, escalarla
            traj_component = motion.components.get('individual_trajectory')
            if traj_component and hasattr(traj_component, 'shape_func'):
                original_func = traj_component.shape_func
                traj_component.shape_func = ScaleConfig.get_scaled_trajectory(
                    original_func, scale_factor
                )
    
    # Escalar trayectoria del macro si existe
    if macro.trajectory_component and macro.trajectory_component.trajectory_func:
        original_macro_func = macro.trajectory_component.trajectory_func
        macro.trajectory_component.trajectory_func = ScaleConfig.get_scaled_trajectory(
            original_macro_func, scale_factor
        )
    
    print(f"✓ Macro '{macro.name}' escalado a zona '{zone}'")
    print(f"  Rango: {zone_config['range'][0]}-{zone_config['range'][1]}m")
    print(f"  Factor de escala: {scale_factor}")


# Funciones de utilidad para uso rápido
def make_intimate(engine, macro_id):
    """Escalar macro a zona íntima (0.5-3m)"""
    apply_perceptual_scaling(engine, macro_id, 'intimate')
    
def make_personal(engine, macro_id):
    """Escalar macro a zona personal (2-8m)"""
    apply_perceptual_scaling(engine, macro_id, 'personal')
    
def make_social(engine, macro_id):
    """Escalar macro a zona social (5-15m)"""
    apply_perceptual_scaling(engine, macro_id, 'social')
    
def make_public(engine, macro_id):
    """Escalar macro a zona pública (10-30m)"""
    apply_perceptual_scaling(engine, macro_id, 'public')


# Configuración optimizada para demos
DEMO_CONFIG = {
    'formation_spacing': 0.8,      # Fuentes más juntas
    'trajectory_radius': 2.5,      # Radio moderado
    'trajectory_height': 0.8,      # Poco movimiento vertical
    'breathing_amplitude': 0.4,    # Respiración sutil
    'force_field_radius': 3.0,     # Campos de fuerza localizados
    'random_movement_range': 0.2,  # Poco ruido
    'macro_trajectory_scale': 6.0, # Órbita contenida
}

if __name__ == "__main__":
    print("Configuración de escalas para Spat Revolution")
    print("=" * 50)
    print("\nZonas perceptuales recomendadas:")
    
    for zone in ScaleConfig.create_perceptual_zones(4):
        print(f"\n{zone['name'].upper()}:")
        print(f"  Rango: {zone['range'][0]}-{zone['range'][1]}m")
        print(f"  {zone['description']}")
        print(f"  Fuentes sugeridas: {zone['suggested_sources']}")
        
    print("\n" + "=" * 50)
    print("Configuración por defecto:")
    for key, value in ScaleConfig.DEFAULT_CONFIG.items():
        print(f"  {key}: {value}")
        
    print("\nPara usar en tu código:")
    print("  from scale_adjuster import apply_perceptual_scaling")
    print("  apply_perceptual_scaling(engine, 'mi_macro', 'personal')"