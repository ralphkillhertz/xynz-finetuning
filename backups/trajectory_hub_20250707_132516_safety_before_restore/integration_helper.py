#!/usr/bin/env python3
"""
🔧 HELPER: Integrar componentes en el engine
"""

print("""
Para integrar los nuevos componentes:

1. En enhanced_trajectory_engine.py, añadir imports:
   from trajectory_hub.core.trajectory_component import TrajectoryComponent
   from trajectory_hub.core.rotation_component import RotationComponent

2. En set_individual_trajectory(), usar el nuevo sistema:
   if sid in self._source_motions:
       motion = self._source_motions[sid]
       if 'trajectory' not in motion.motion_components:
           motion.motion_components['trajectory'] = TrajectoryComponent()
       motion.motion_components['trajectory'].set_trajectory(trajectory)
       motion.use_delta_system = True

3. En set_macro_algorithmic_rotation(), similar:
   for sid in macro.source_ids:
       if sid in self._source_motions:
           motion = self._source_motions[sid]
           if 'rotation' not in motion.motion_components:
               motion.motion_components['rotation'] = RotationComponent()
           motion.motion_components['rotation'].set_rotation(angular_velocity, center)
           motion.use_delta_system = True

4. En update(), proveer contexto:
   for sid, motion in self._source_motions.items():
       context = {
           'source_id': sid,
           'macro_center': self.get_macro_center(sid),
           'time': self._time
       }
       motion.update(dt, context)
""")
