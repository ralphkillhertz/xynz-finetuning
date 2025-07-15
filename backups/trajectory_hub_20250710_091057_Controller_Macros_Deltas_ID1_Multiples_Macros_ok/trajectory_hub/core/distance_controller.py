"""
distance_controller.py - Sistema de control de distancias para trayectorias
Permite especificar distancias mínimas, máximas y medias de forma intuitiva
"""
import numpy as np
from typing import Dict, Tuple, Optional, Callable, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DistanceProfile:
    """Perfil de distancias para una trayectoria"""
    min_distance: float      # Distancia mínima al oyente
    max_distance: float      # Distancia máxima al oyente
    mean_distance: float     # Distancia media
    vertical_range: float    # Rango vertical (altura)
    
    def __post_init__(self):
        # Validar rangos
        if self.min_distance < 0:
            self.min_distance = 0.5
        if self.max_distance > 100:
            self.max_distance = 100
        if self.mean_distance < self.min_distance or self.mean_distance > self.max_distance:
            self.mean_distance = (self.min_distance + self.max_distance) / 2
            
    @property
    def range(self) -> float:
        """Rango total de la trayectoria"""
        return self.max_distance - self.min_distance
        
    @property
    def radius(self) -> float:
        """Radio aproximado para trayectorias circulares"""
        return self.range / 2


class DistanceController:
    """Controlador para ajustar distancias de trayectorias"""
    
    # Presets de distancia con lenguaje natural
    DISTANCE_PRESETS = {
        # Muy cerca
        "íntima": DistanceProfile(0.5, 2, 1.2, 0.5),
        "muy_cercana": DistanceProfile(1, 3, 2, 0.8),
        "susurro": DistanceProfile(0.3, 1.5, 0.8, 0.3),
        
        # Cerca
        "cercana": DistanceProfile(2, 5, 3.5, 1),
        "personal": DistanceProfile(2, 6, 4, 1.2),
        "conversación": DistanceProfile(1.5, 4, 2.5, 0.8),
        
        # Media
        "media": DistanceProfile(4, 10, 7, 2),
        "normal": DistanceProfile(3, 8, 5.5, 1.5),
        "ambiente": DistanceProfile(5, 12, 8, 2.5),
        
        # Lejos
        "lejana": DistanceProfile(8, 20, 14, 3),
        "distante": DistanceProfile(10, 25, 17, 4),
        "profunda": DistanceProfile(12, 30, 20, 5),
        
        # Muy lejos
        "muy_lejana": DistanceProfile(20, 40, 30, 6),
        "extrema": DistanceProfile(30, 60, 45, 8),
        "horizonte": DistanceProfile(40, 80, 60, 10),
        
        # Especiales
        "envolvente": DistanceProfile(1, 15, 6, 3),
        "expansiva": DistanceProfile(2, 25, 10, 4),
        "focus": DistanceProfile(3, 3.5, 3.2, 0.5),
        "órbita": DistanceProfile(5, 8, 6.5, 2),
    }
    
    @staticmethod
    def parse_distance_description(description: str) -> DistanceProfile:
        """
        Parsear descripción en lenguaje natural a perfil de distancias
        
        Ejemplos:
        - "muy cercana" -> preset directo
        - "entre 2 y 10 metros" -> crear perfil
        - "5 metros constante" -> distancia fija
        - "de cerca a lejos" -> expansiva
        """
        desc_lower = description.lower().strip()
        
        # Buscar preset directo
        for key, profile in DistanceController.DISTANCE_PRESETS.items():
            if key.replace("_", " ") in desc_lower or key in desc_lower:
                return profile
                
        # Parsear rangos numéricos
        import re
        
        # Patrón: "entre X y Y metros"
        between_pattern = r'entre\s*(\d+\.?\d*)\s*y\s*(\d+\.?\d*)'
        match = re.search(between_pattern, desc_lower)
        if match:
            min_dist = float(match.group(1))
            max_dist = float(match.group(2))
            return DistanceProfile(min_dist, max_dist, (min_dist + max_dist) / 2, max_dist * 0.2)
            
        # Patrón: "X metros"
        single_pattern = r'(\d+\.?\d*)\s*metros?'
        match = re.search(single_pattern, desc_lower)
        if match:
            distance = float(match.group(1))
            # Para distancia fija, crear pequeña variación
            return DistanceProfile(distance * 0.9, distance * 1.1, distance, distance * 0.1)
            
        # Interpretaciones semánticas
        if "cerca" in desc_lower and "lejos" in desc_lower:
            return DistanceController.DISTANCE_PRESETS["expansiva"]
        elif "constante" in desc_lower or "fija" in desc_lower:
            return DistanceController.DISTANCE_PRESETS["focus"]
        elif "alrededor" in desc_lower or "órbita" in desc_lower:
            return DistanceController.DISTANCE_PRESETS["órbita"]
            
        # Default
        logger.warning(f"No se pudo interpretar '{description}', usando distancia media")
        return DistanceController.DISTANCE_PRESETS["media"]
        
    @staticmethod
    def scale_trajectory_to_profile(
        trajectory_func: Callable[[float], np.ndarray],
        profile: DistanceProfile
    ) -> Callable[[float], np.ndarray]:
        """
        Escalar una función de trayectoria para ajustarse al perfil de distancias
        """
        # Primero, analizar la trayectoria original
        sample_points = []
        for t in np.linspace(0, 2 * np.pi, 100):
            sample_points.append(trajectory_func(t))
        sample_points = np.array(sample_points)
        
        # Calcular estadísticas originales
        distances = np.linalg.norm(sample_points[:, :2], axis=1)  # Solo X,Y para distancia
        orig_min = np.min(distances)
        orig_max = np.max(distances)
        orig_mean = np.mean(distances)
        
        # Calcular factores de escala
        if orig_max - orig_min > 0:
            # Escala no uniforme para ajustar min/max
            scale_range = profile.range / (orig_max - orig_min)
        else:
            # Trayectoria de radio constante
            scale_range = profile.radius / (orig_mean if orig_mean > 0 else 1)
            
        # Offset para centrar en la distancia media correcta
        offset_distance = profile.mean_distance - orig_mean * scale_range
        
        # Escala vertical
        z_scale = profile.vertical_range / (np.max(np.abs(sample_points[:, 2])) + 0.1)
        
        def scaled_trajectory(t: float) -> np.ndarray:
            pos = trajectory_func(t)
            
            # Escalar X,Y para ajustar distancias
            xy_norm = np.linalg.norm(pos[:2])
            if xy_norm > 0:
                # Dirección radial
                xy_dir = pos[:2] / xy_norm
                # Nueva distancia
                new_distance = xy_norm * scale_range + offset_distance
                # Aplicar
                pos[0] = xy_dir[0] * new_distance
                pos[1] = xy_dir[1] * new_distance
            else:
                # En el origen, mover a distancia media
                pos[0] = profile.mean_distance
                
            # Escalar Z
            pos[2] *= z_scale
            
            return pos
            
        return scaled_trajectory
        
    @staticmethod
    def create_trajectory_with_profile(
        shape: str,
        profile: DistanceProfile
    ) -> Callable[[float], np.ndarray]:
        """
        Crear una trayectoria nueva con un perfil de distancias específico
        """
        # Formas base normalizadas
        shapes = {
            "circle": lambda t: np.array([np.cos(t), np.sin(t), 0]),
            "ellipse": lambda t: np.array([1.5 * np.cos(t), np.sin(t), 0]),
            "figure8": lambda t: np.array([np.sin(t), np.sin(t) * np.cos(t), 0]),
            "spiral": lambda t: np.array([
                (0.5 + 0.1 * t) * np.cos(t),
                (0.5 + 0.1 * t) * np.sin(t),
                0.1 * t
            ]),
            "line": lambda t: np.array([t / np.pi - 1, 0, 0]),
        }
        
        base_func = shapes.get(shape, shapes["circle"])
        return DistanceController.scale_trajectory_to_profile(base_func, profile)
        
    @staticmethod
    def analyze_trajectory(
        trajectory_func: Callable[[float], np.ndarray],
        samples: int = 200
    ) -> Dict[str, float]:
        """
        Analizar una trayectoria y devolver sus características de distancia
        """
        points = []
        for t in np.linspace(0, 2 * np.pi, samples):
            points.append(trajectory_func(t))
        points = np.array(points)
        
        # Calcular distancias al origen (oyente)
        distances = np.linalg.norm(points[:, :2], axis=1)
        
        return {
            'min_distance': np.min(distances),
            'max_distance': np.max(distances),
            'mean_distance': np.mean(distances),
            'std_distance': np.std(distances),
            'vertical_range': np.max(points[:, 2]) - np.min(points[:, 2]),
            'is_circular': np.std(distances) < 0.1 * np.mean(distances),
            'closest_point': points[np.argmin(distances)],
            'farthest_point': points[np.argmax(distances)]
        }
        
    @staticmethod
    def suggest_profile(description: str) -> List[Tuple[str, DistanceProfile]]:
        """
        Sugerir perfiles basados en una descripción
        
        Returns
        -------
        Lista de (nombre, perfil) ordenados por relevancia
        """
        suggestions = []
        desc_words = description.lower().split()
        
        for name, profile in DistanceController.DISTANCE_PRESETS.items():
            score = 0
            name_words = name.replace("_", " ").split()
            
            # Buscar coincidencias
            for word in desc_words:
                if word in name_words:
                    score += 2
                elif any(word in nw for nw in name_words):
                    score += 1
                    
            if score > 0:
                suggestions.append((score, name, profile))
                
        # Ordenar por puntuación
        suggestions.sort(reverse=True)
        return [(name, profile) for _, name, profile in suggestions[:5]]


class TrajectoryDistanceAdjuster:
    """Clase para ajustar trayectorias existentes a nuevos perfiles de distancia"""
    
    def __init__(self, engine):
        self.engine = engine
        self.controller = DistanceController()
        
    def adjust_macro_distance(self, macro_id: str, distance_spec: str):
        """
        Ajustar las distancias de un macro completo
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        distance_spec : str
            Especificación de distancia (ej: "muy cercana", "entre 5 y 15 metros")
        """
        if macro_id not in self.engine._macros:
            raise ValueError(f"Macro no encontrado: {macro_id}")
            
        # Parsear especificación
        profile = DistanceController.parse_distance_description(distance_spec)
        
        logger.info(f"Ajustando {macro_id} a: min={profile.min_distance}m, "
                   f"max={profile.max_distance}m, media={profile.mean_distance}m")
        
        macro = self.engine._macros[macro_id]
        
        # Ajustar trayectoria del macro si existe
        if macro.trajectory_component and macro.trajectory_component.trajectory_func:
            original_func = macro.trajectory_component.trajectory_func
            scaled_func = DistanceController.scale_trajectory_to_profile(
                original_func, profile
            )
            macro.trajectory_component.trajectory_func = scaled_func
            
        # Ajustar trayectorias individuales
        for sid in macro.source_ids:
            if sid in self.engine._source_motions:
                motion = self.engine._source_motions[sid]
                
                # Ajustar posición actual
                current_dist = np.linalg.norm(motion.state.position[:2])
                if current_dist > 0:
                    scale = profile.mean_distance / current_dist
                    motion.state.position[:2] *= scale
                    
                # Ajustar trayectoria individual si existe
                traj = motion.components.get('individual_trajectory')
                if traj and hasattr(traj, 'shape_func'):
                    traj.shape_func = DistanceController.scale_trajectory_to_profile(
                        traj.shape_func, 
                        DistanceProfile(
                            profile.min_distance * 0.3,  # Trayectorias individuales más pequeñas
                            profile.max_distance * 0.3,
                            profile.mean_distance * 0.3,
                            profile.vertical_range * 0.5
                        )
                    )
                    
        logger.info(f"✓ Macro '{macro.name}' ajustado al perfil de distancia '{distance_spec}'")
        
    def get_current_distances(self, macro_id: str) -> Dict[str, float]:
        """Obtener las distancias actuales de un macro"""
        if macro_id not in self.engine._macros:
            raise ValueError(f"Macro no encontrado: {macro_id}")
            
        macro = self.engine._macros[macro_id]
        distances = []
        
        for sid in macro.source_ids:
            if sid in self.engine._source_motions:
                pos = self.engine._source_motions[sid].state.position
                dist = np.linalg.norm(pos[:2])  # Solo X,Y
                distances.append(dist)
                
        if distances:
            return {
                'min': np.min(distances),
                'max': np.max(distances),
                'mean': np.mean(distances),
                'std': np.std(distances)
            }
        return {}


# Funciones de conveniencia para uso rápido
def make_intimate(engine, macro_id: str):
    """Hacer que un macro esté muy cerca (0.5-2m)"""
    adjuster = TrajectoryDistanceAdjuster(engine)
    adjuster.adjust_macro_distance(macro_id, "íntima")
    
def make_close(engine, macro_id: str):
    """Hacer que un macro esté cerca (2-5m)"""
    adjuster = TrajectoryDistanceAdjuster(engine)
    adjuster.adjust_macro_distance(macro_id, "cercana")
    
def make_medium(engine, macro_id: str):
    """Hacer que un macro esté a distancia media (4-10m)"""
    adjuster = TrajectoryDistanceAdjuster(engine)
    adjuster.adjust_macro_distance(macro_id, "media")
    
def make_far(engine, macro_id: str):
    """Hacer que un macro esté lejos (10-25m)"""
    adjuster = TrajectoryDistanceAdjuster(engine)
    adjuster.adjust_macro_distance(macro_id, "lejana")
    
def set_distance_range(engine, macro_id: str, min_dist: float, max_dist: float):
    """Establecer rango de distancias específico"""
    adjuster = TrajectoryDistanceAdjuster(engine)
    adjuster.adjust_macro_distance(macro_id, f"entre {min_dist} y {max_dist} metros")


if __name__ == "__main__":
    # Demo de los presets
    print("Presets de distancia disponibles:")
    print("=" * 60)
    
    categories = [
        ("Muy cerca", ["íntima", "muy_cercana", "susurro"]),
        ("Cerca", ["cercana", "personal", "conversación"]),
        ("Media", ["media", "normal", "ambiente"]),
        ("Lejos", ["lejana", "distante", "profunda"]),
        ("Muy lejos", ["muy_lejana", "extrema", "horizonte"]),
        ("Especiales", ["envolvente", "expansiva", "focus", "órbita"])
    ]
    
    for category, presets in categories:
        print(f"\n{category}:")
        for preset in presets:
            profile = DistanceController.DISTANCE_PRESETS[preset]
            print(f"  {preset:15} -> {profile.min_distance:4.1f}m - {profile.max_distance:4.1f}m "
                  f"(media: {profile.mean_distance:4.1f}m)")
                  
    print("\n" + "=" * 60)
    print("Ejemplos de uso:")
    print('  adjuster.adjust_macro_distance("mi_macro", "muy cercana")')
    print('  adjuster.adjust_macro_distance("mi_macro", "entre 5 y 15 metros")')
    print('  adjuster.adjust_macro_distance("mi_macro", "10 metros constante")')