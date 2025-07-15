# Manual Rotation Fix - Orientation Only

## The Problem:
Manual Rotation MS is supposed to:
- Change ONLY the orientation (Pitch, Roll, Yaw) 
- NOT move the macro's position
- Be a static adjustment, not continuous rotation

## Current Issue:
The current implementation treats manual rotation as a position transformation, which causes the macro to move/rotate continuously.

## Solution Needed:
1. Manual Rotation should only set orientation values (PRY)
2. These values should be sent to Spat for visual orientation 
3. The macro position should remain unchanged
4. After setting orientation once, no further updates

## Key Understanding:
- Position (X,Y,Z) = Where the object is in space
- Orientation (P,R,Y) = How the object is rotated/facing
- Manual Rotation MS should ONLY affect orientation, not position