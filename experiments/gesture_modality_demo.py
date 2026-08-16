#!/usr/bin/env python3
"""
Gesture Modality: Embodied Semantic Reconstruction

Implements S → C → B_t → O_t → Ŝ for gestural communication.

Key Insight:
    Gesture isn't "observed configuration → class label"
    It's "partial observation → reconstruct latent embodied semantic trajectory"

Based on:
    - From Classifier to Inverse Engine
    - Configurational accessibility
    - Motor manifold constraints
    - Temporal trajectories (not frozen frames)
"""

import random
import sys
from dataclasses import dataclass

sys.path.insert(0, 'src')

from language_evolution.unified_framework import (
    BehavioralOutput,
    ControlState,
    InverseEngine,
    Modality,
    Observable,
    Projector,
    ReconstructedStructure,
    StructuralObject,
)


@dataclass
class GestureConfiguration:
    """A single gesture configuration (partial observation)."""

    hand_position: tuple[float, float, float]  # 3D position
    hand_orientation: tuple[float, float, float]  # Euler angles
    handshape: str  # Open, closed, pointing, etc.
    velocity: tuple[float, float, float]  # Movement vector


@dataclass
class GestureTrajectory:
    """Complete gesture as temporal trajectory."""

    configurations: list[GestureConfiguration]
    semantic_intent: str  # What this gesture MEANS
    affective_quality: str  # How it's expressed (emphatic, gentle, etc.)
    duration: float  # Total time


class GestureProjector(Projector):
    """
    Projects semantic structure into embodied gestural trajectory.
    
    Key: Meaning is in TRAJECTORY, not individual frames.
    """

    def __init__(self):
        # Map semantic concepts to gesture primitives
        self.gesture_lexicon = {
            'concept_0': 'point',
            'concept_1': 'grasp',
            'concept_2': 'push',
            'concept_3': 'pull',
            'concept_4': 'circle',
        }
        
        self.handshapes = {
            'point': 'extended_index',
            'grasp': 'closed_fist',
            'push': 'open_palm',
            'pull': 'hooked_fingers',
            'circle': 'curved_hand',
        }
    
    def project_structure(
        self,
        structure: StructuralObject,
        control: ControlState,
        time: int,
    ) -> BehavioralOutput:
        """
        Project semantic structure into gestural behavior.
        
        Control goals affect:
        - Expressiveness → larger, slower movements
        - Ease → smaller, faster movements
        - Distinctiveness → exaggerated articulation
        """
        concepts = list(structure.semantic_core.keys())
        
        # Generate gesture sequence
        trajectories = []
        
        for i, concept in enumerate(concepts):
            if concept in self.gesture_lexicon:
                gesture_type = self.gesture_lexicon[concept]
                
                # Generate trajectory based on control goals
                trajectory = self._generate_trajectory(
                    gesture_type,
                    control,
                    position_offset=i * 0.3,  # Space out gestures
                )
                
                trajectories.append(trajectory)
        
        output_data = {
            'trajectories': trajectories,
            'num_gestures': len(trajectories),
            'total_duration': sum(t.duration for t in trajectories),
        }
        
        return BehavioralOutput(
            time=time,
            modality=Modality.GESTURE,
            output_data=output_data,
            structural_source=structure,
            control_state=control,
        )
    
    def _generate_trajectory(
        self,
        gesture_type: str,
        control: ControlState,
        position_offset: float = 0.0,
    ) -> GestureTrajectory:
        """
        Generate gesture trajectory based on type and control goals.
        
        High expressiveness → larger movements, slower
        High ease → smaller movements, faster
        """
        # Base configuration
        base_pos = (0.0 + position_offset, 0.5, 0.2)
        handshape = self.handshapes.get(gesture_type, 'neutral')
        
        # Control affects trajectory
        scale = 1.0
        speed = 1.0
        frames = 10
        
        if control.target_expressiveness > 0.7:
            scale = 1.5  # Larger movements
            speed = 0.7  # Slower
            frames = 15
        elif control.target_ease > 0.7:
            scale = 0.7  # Smaller movements
            speed = 1.3  # Faster
            frames = 7
        
        # Generate trajectory frames
        configurations = []
        
        for i in range(frames):
            t = i / frames  # 0 to 1
            
            # Different gesture types have different trajectories
            if gesture_type == 'point':
                # Forward extension
                pos = (
                    base_pos[0],
                    base_pos[1] + t * scale * 0.3,
                    base_pos[2],
                )
                vel = (0.0, speed * 0.3, 0.0)
            
            elif gesture_type == 'grasp':
                # Inward pull
                pos = (
                    base_pos[0],
                    base_pos[1] - t * scale * 0.2,
                    base_pos[2],
                )
                vel = (0.0, -speed * 0.2, 0.0)
            
            elif gesture_type == 'push':
                # Forward push
                pos = (
                    base_pos[0],
                    base_pos[1] + t * scale * 0.4,
                    base_pos[2],
                )
                vel = (0.0, speed * 0.4, 0.0)
            
            elif gesture_type == 'circle':
                # Circular motion
                t * 2 * 3.14159
                pos = (
                    base_pos[0] + scale * 0.2 * (1 - abs(2 * t - 1)),
                    base_pos[1] + scale * 0.2 * (1 - 2 * abs(t - 0.5)),
                    base_pos[2],
                )
                vel = (speed * 0.2, speed * 0.2, 0.0)
            
            else:
                pos = base_pos
                vel = (0.0, 0.0, 0.0)
            
            # Orientation changes slightly
            orient = (0.0, t * 0.2, 0.0)
            
            config = GestureConfiguration(
                hand_position=pos,
                hand_orientation=orient,
                handshape=handshape,
                velocity=vel,
            )
            
            configurations.append(config)
        
        return GestureTrajectory(
            configurations=configurations,
            semantic_intent=gesture_type,
            affective_quality='neutral',
            duration=frames / 30.0,  # Assume 30 fps
        )
    
    def render_observable(self, behavior: BehavioralOutput) -> Observable:
        """
        Render gesture as observable.
        
        LOSSY: Observer sees only SAMPLED FRAMES, not continuous trajectory.
        Missing: Semantic intent, control goals, micro-movements.
        """
        trajectories = behavior.output_data['trajectories']
        
        # Sample frames (lossy - not all frames visible)
        sampled_frames = []
        
        for trajectory in trajectories:
            # Sample only some frames (e.g., every 3rd frame)
            sample_rate = 3
            for i in range(0, len(trajectory.configurations), sample_rate):
                config = trajectory.configurations[i]
                sampled_frames.append({
                    'position': config.hand_position,
                    'handshape': config.handshape,
                    # Lost: orientation, velocity, semantic intent
                })
        
        observed_data = {
            'frames': sampled_frames,
            'num_frames': len(sampled_frames),
        }
        
        # Hidden information:
        # - Continuous trajectory
        # - Semantic intent
        # - Affective quality
        # - Control goals
        # - Inter-frame dynamics
        
        return Observable(
            time=behavior.time,
            modality=behavior.modality,
            observed_data=observed_data,
        )


class GestureInverseEngine(InverseEngine):
    """
    Reconstructs semantic structure from gesture observations.
    
    Challenge: Must reconstruct TRAJECTORY from SAMPLED FRAMES.
    """

    def reconstruct(self, observable: Observable) -> ReconstructedStructure:
        """
        Attempt to reconstruct semantic intent from observed frames.
        
        Have: Sampled positions and handshapes
        Need: Semantic intent, trajectory, relations
        """
        frames = observable.observed_data.get('frames', [])
        
        if not frames:
            return ReconstructedStructure(
                reconstructed_semantic={},
                reconstructed_relations=[],
                confidence=0.0,
                ambiguity=[],
                lost_information=['all'],
            )
        
        # Try to infer gestures from handshape changes
        reconstructed_gestures = []
        current_handshape = frames[0]['handshape']
        
        for i, frame in enumerate(frames):
            if frame['handshape'] != current_handshape or i == len(frames) - 1:
                # New gesture detected
                reconstructed_gestures.append(current_handshape)
                current_handshape = frame['handshape']
        
        # Map back to concepts (very uncertain!)
        reconstructed_semantic = {}
        for i, handshape in enumerate(reconstructed_gestures):
            # Guess concept from handshape
            reconstructed_semantic[f'concept_{i}'] = f'inferred_from_{handshape}'
        
        # Try to infer relations from spatial proximity
        reconstructed_relations = []
        for i in range(len(reconstructed_gestures) - 1):
            # Assume sequential gestures are related
            reconstructed_relations.append(
                (f'concept_{i}', 'followed_by', f'concept_{i+1}'),
            )
        
        # Very low confidence - lots of ambiguity
        confidence = 0.3
        
        # Many alternative interpretations
        ambiguity = [
            'different_semantic_intent',
            'different_affective_quality',
            'different_trajectory',
        ]
        
        # Lost information
        lost = [
            'continuous_trajectory',
            'velocity_profile',
            'orientation_changes',
            'semantic_intent',
            'affective_quality',
            'control_goals',
            'micro_movements',
            'co-articulation',
        ]
        
        return ReconstructedStructure(
            reconstructed_semantic=reconstructed_semantic,
            reconstructed_relations=reconstructed_relations,
            confidence=confidence,
            ambiguity=ambiguity,
            lost_information=lost,
        )
    
    def identify_invariants(
        self,
        original: StructuralObject,
        reconstructed: ReconstructedStructure,
    ) -> list[str]:
        """
        What survived gesture projection?
        
        Usually:
          ✓ Number of gestures
          ✓ Approximate sequence
          ✗ Semantic content
          ✗ Continuous dynamics
          ✗ Affective qualities
        """
        invariants = []
        
        # Gesture count might match concept count
        if len(original.semantic_core) == len(reconstructed.reconstructed_semantic):
            invariants.append('gesture_count')
        
        # Sequential order might be preserved
        if len(original.relational_structure) == len(
            reconstructed.reconstructed_relations,
        ):
            invariants.append('sequential_order')
        
        # Handshapes might be distinguishable
        invariants.append('handshape_changes')
        
        return invariants
    
    def measure_information_loss(
        self,
        original: StructuralObject,
        reconstructed: ReconstructedStructure,
    ) -> dict:
        """
        Quantify information lost in gesture projection.
        
        Major losses:
          - Continuous trajectory → sampled frames
          - Semantic intent → handshape guesses
          - Dynamics → static positions
          - Control goals → unobservable
        """
        losses = {}
        
        # Semantic content
        losses['semantic_content'] = 1.0  # Completely lost
        
        # Trajectory continuity
        losses['trajectory_dynamics'] = 0.8  # Mostly lost (sampled)
        
        # Affective quality
        losses['affective_quality'] = 1.0  # Completely lost
        
        # Control goals
        losses['control_goals'] = 1.0  # Completely lost
        
        # Micro-movements
        losses['micro_movements'] = 0.9  # Almost completely lost
        
        # Total
        losses['total_loss'] = sum(losses.values()) / len(losses)
        
        return losses


def demonstrate_gesture_modality():
    """Demonstrate gesture modality in unified framework."""
    print("=" * 70)
    print("GESTURE MODALITY: S → C → B_t → O_t → Ŝ")
    print("=" * 70)
    print()
    print("Key Insight: Meaning is in TRAJECTORY, not frozen frames")
    print()
    
    # 1. Semantic structure
    structure = StructuralObject(
        semantic_core={
            'concept_0': 'indicate',
            'concept_1': 'acquire',
            'concept_2': 'transfer',
        },
        relational_structure=[
            ('concept_0', 'enables', 'concept_1'),
            ('concept_1', 'enables', 'concept_2'),
        ],
        admissible_transforms={'reversal', 'emphasis'},
        constraints=['temporal_sequence', 'spatial_coherence'],
    )
    
    print("1. Semantic Structure (S):")
    print(f"   Core: {structure.semantic_core}")
    print(f"   Relations: {structure.relational_structure}")
    print()
    
    # 2. Control state
    control_expressive = ControlState(
        target_expressiveness=0.9,
        target_ease=0.3,
    )
    
    control_efficient = ControlState(
        target_expressiveness=0.3,
        target_ease=0.9,
    )
    
    print("2. Control States (C):")
    print(f"   Expressive: expressiveness={control_expressive.target_expressiveness}")
    print(f"   Efficient: ease={control_efficient.target_ease}")
    print()
    
    # 3. Project through gesture with DIFFERENT control
    projector = GestureProjector()
    
    behavior_expressive = projector.project_structure(
        structure,
        control_expressive,
        time=0,
    )
    behavior_efficient = projector.project_structure(structure, control_efficient, time=0)
    
    print("3. Behavioral Outputs (B_t):")
    print(f"   Expressive: {behavior_expressive.output_data['num_gestures']} gestures, "
          f"{behavior_expressive.output_data['total_duration']:.2f}s")
    print(f"   Efficient: {behavior_efficient.output_data['num_gestures']} gestures, "
          f"{behavior_efficient.output_data['total_duration']:.2f}s")
    print()
    
    # 4. Render observables
    obs_expressive = projector.render_observable(behavior_expressive)
    obs_efficient = projector.render_observable(behavior_efficient)
    
    print("4. Observables (O_t):")
    print(f"   Expressive: {obs_expressive.observed_data['num_frames']} sampled frames")
    print(f"   Efficient: {obs_efficient.observed_data['num_frames']} sampled frames")
    print("   [Hidden: continuous trajectory, semantic intent, control goals]")
    print()
    
    # 5. Reconstruct
    inverse = GestureInverseEngine()
    recon_expressive = inverse.reconstruct(obs_expressive)
    recon_efficient = inverse.reconstruct(obs_efficient)
    
    print("5. Reconstructed Structures (Ŝ):")
    print(f"   Expressive: {len(recon_expressive.reconstructed_semantic)} concepts, "
          f"confidence={recon_expressive.confidence:.2f}")
    print(f"   Efficient: {len(recon_efficient.reconstructed_semantic)} concepts, "
          f"confidence={recon_efficient.confidence:.2f}")
    print()
    
    # 6. Measure invariance
    invariants_exp = inverse.identify_invariants(structure, recon_expressive)
    loss_exp = inverse.measure_information_loss(structure, recon_expressive)
    
    print("6. Structural Analysis (Expressive):")
    print(f"   Invariants: {', '.join(invariants_exp)}")
    print(f"   Information loss: {loss_exp['total_loss']:.1%}")
    print("   Lost components:")
    for component, loss_val in loss_exp.items():
        if component != 'total_loss':
            print(f"     - {component}: {loss_val:.1%}")
    print()
    
    print("=" * 70)
    print()
    print("KEY INSIGHT:")
    print()
    print("Same semantic structure (S) + different control (C)")
    print("→ different trajectories (B_t)")
    print("→ both lose ~90% information in observable (O_t)")
    print()
    print("Continuous dynamics, semantic intent, and control goals")
    print("are FUNDAMENTALLY UNRECOVERABLE from sampled frames.")
    print()
    print("This is why gesture recognition needs inverse engines,")
    print("not just classifiers.")


if __name__ == '__main__':
    random.seed(42)
    demonstrate_gesture_modality()
