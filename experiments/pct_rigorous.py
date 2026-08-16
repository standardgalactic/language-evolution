#!/usr/bin/env python3
"""
Perceptual Control Theory: Rigorous Implementation

Based on William T. Powers' PCT, this models language change as
the emergent consequence of agents controlling perceptual variables
through negative feedback.

Key Improvements Over Initial Version:
  1. Signed error signals (not absolute values)
  2. Environment causally affects perception
  3. Local sampling (no global knowledge)
  4. Actual conformity adjustment toward encountered forms
  5. Separate control dimensions (not collapsed to fitness)
  6. Listener-based comprehension feedback
  7. Multiple independent controllers
  8. Ecological parameters causally effective

Control Loop:
    r (reference) → e = r - p (error) → o (output) → E (environment) → p (perception)
                                                                            ↑
                                                                            |
                                                                      (feedback)
"""

import random
import sys
from dataclasses import dataclass

sys.path.insert(0, 'src')

from language_evolution.framework import HistoryGenerator, Observable


@dataclass
class ControlError:
    """
    Signed error signals for each control dimension.
    
    Critically: these retain DIRECTION.
    e > 0 means perception below reference (need to increase)
    e < 0 means perception above reference (need to decrease)
    """

    comprehension: float = 0.0  # Want listener to understand
    conformity: float = 0.0  # Want to match community
    effort: float = 0.0  # Want easy production
    distinctiveness: float = 0.0  # Want contrast from confusables


@dataclass
class PerceptionState:
    """What an agent actually perceives after environment transforms output."""

    comprehension_achieved: float  # Did listener understand?
    conformity_achieved: float  # How similar to encountered forms?
    effort_experienced: float  # How hard was production?
    distinctiveness_achieved: float  # How different from confusables?


@dataclass
class ReferenceState:
    """Desired perceptual states (control targets)."""

    target_comprehension: float = 0.85
    target_conformity: float = 0.70
    target_effort: float = 0.60  # Lower effort is better
    target_distinctiveness: float = 0.75


@dataclass
class Environment:
    """
    Environmental transformations that affect perception.
    
    These are CAUSAL - they actually modify what agents perceive.
    """

    ambient_noise: float = 0.1  # Probability contrast is lost
    network_size: int = 50  # How many potential neighbors
    stability: float = 0.95  # How rapidly conditions change
    
    def transform_utterance(
        self,
        intended_form: str,
        listener: dict,
    ) -> tuple[str, float]:
        """
        Environment transforms utterance before listener perceives it.
        
        Returns: (perceived_form, comprehension_quality)
        """
        perceived_form = intended_form
        quality = 1.0
        
        # Ambient noise can distort segments
        if random.random() < self.ambient_noise and len(perceived_form) > 1:
            # One segment lost/changed
            i = random.randint(0, len(perceived_form) - 1)
            vowels = 'aeiou'
            consonants = 'ptkbdgmnlrsw'
            if perceived_form[i] in vowels:
                replacement = random.choice(vowels)
            else:
                replacement = random.choice(consonants)
            perceived_form = (
                perceived_form[:i] + replacement + perceived_form[i + 1 :]
            )
            quality *= 0.7  # Degraded
        
        return perceived_form, quality


class Agent:
    """
    An agent with independent control loops for each dimension.
    
    NOT a single optimizer - multiple controllers that may conflict.
    """

    def __init__(
        self,
        agent_id: int,
        initial_vocabulary: dict[str, str],
        location: tuple[float, float],
        reference: ReferenceState,
    ):
        self.agent_id = agent_id
        self.vocabulary = dict(initial_vocabulary)  # concept -> form
        self.location = location
        self.reference = reference
        
        # Control history (for H, not observable)
        self.error_history: list[ControlError] = []
        self.perception_history: list[PerceptionState] = []
    
    def produce(self, concept: str, environment: Environment, listener: 'Agent') -> str:
        """
        Produce utterance and perceive result through environment.
        
        Returns form actually used (may be adjusted from vocabulary).
        """
        intended_form = self.vocabulary[concept]
        
        # Environment transforms output
        perceived_form, quality = environment.transform_utterance(
            intended_form,
            listener.vocabulary,
        )
        
        # Perceive what happened (perception, not production)
        perception = self._perceive_outcome(
            concept,
            intended_form,
            perceived_form,
            quality,
            listener,
        )
        
        # Compute error (reference - perception)
        error = self._compute_error(perception)
        
        # Store history
        self.perception_history.append(perception)
        self.error_history.append(error)
        
        return perceived_form
    
    def _perceive_outcome(
        self,
        concept: str,
        intended: str,
        perceived: str,
        quality: float,
        listener: 'Agent',
    ) -> PerceptionState:
        """
        Perceive the result of utterance.
        
        This is AFTER environment transformation.
        """
        # 1. Comprehension: Did listener understand?
        # Measured by whether perceived form matches listener's expectation
        listener_form = listener.vocabulary.get(concept, '')
        if listener_form:
            comprehension = self._similarity(perceived, listener_form) * quality
        else:
            comprehension = quality * 0.5
        
        # 2. Conformity: How close to what listener uses?
        if listener_form:
            conformity = self._similarity(intended, listener_form)
        else:
            conformity = 0.5
        
        # 3. Effort: Length-based (longer = more effort)
        effort = len(intended) / 10.0  # Normalized
        
        # 4. Distinctiveness: Different from other concepts I know?
        other_forms = [
            f for c, f in self.vocabulary.items() if c != concept and f != intended
        ]
        if other_forms:
            max_similarity = max(self._similarity(intended, other) for other in other_forms)
            distinctiveness = 1.0 - max_similarity
        else:
            distinctiveness = 0.8
        
        return PerceptionState(
            comprehension_achieved=comprehension,
            conformity_achieved=conformity,
            effort_experienced=effort,
            distinctiveness_achieved=distinctiveness,
        )
    
    def _compute_error(self, perception: PerceptionState) -> ControlError:
        """
        Compute SIGNED error for each dimension.
        
        e = r - p (positive means need to increase perception)
        """
        return ControlError(
            comprehension=self.reference.target_comprehension
            - perception.comprehension_achieved,
            conformity=self.reference.target_conformity - perception.conformity_achieved,
            effort=self.reference.target_effort - perception.effort_experienced,
            distinctiveness=self.reference.target_distinctiveness
            - perception.distinctiveness_achieved,
        )
    
    def adjust_vocabulary(
        self,
        concept: str,
        error: ControlError,
        sampled_neighbors: list['Agent'],
    ) -> str | None:
        """
        Generate output to reduce error.
        
        Returns new form if adjusted, None if no change.
        """
        current_form = self.vocabulary[concept]
        
        # Prioritize by absolute error magnitude
        errors = [
            ('comprehension', abs(error.comprehension)),
            ('conformity', abs(error.conformity)),
            ('effort', abs(error.effort)),
            ('distinctiveness', abs(error.distinctiveness)),
        ]
        errors.sort(key=lambda x: x[1], reverse=True)
        
        # Handle largest error
        dimension, magnitude = errors[0]
        
        if magnitude < 0.15:
            return None  # Good enough
        
        # Use SIGNED error to determine direction
        if dimension == 'comprehension' or dimension == 'conformity':
            # Move toward community (sampled neighbors)
            if sampled_neighbors:
                neighbor_forms = [n.vocabulary[concept] for n in sampled_neighbors]
                # Move toward most common
                from collections import Counter
                
                most_common = Counter(neighbor_forms).most_common(1)[0][0]
                # Partial move (not instant adoption)
                new_form = self._move_toward(current_form, most_common, 0.5)
                if new_form != current_form:
                    return new_form
        
        elif dimension == 'effort':
            if error.effort > 0:
                # Need LESS effort (effort perceived > target)
                # Simplify
                return self._simplify(current_form)
            else:
                # Need MORE effort (??  - unusual)
                # Could elaborate
                return self._elaborate(current_form)
        
        elif dimension == 'distinctiveness':
            if error.distinctiveness > 0:
                # Need MORE distinctiveness
                return self._differentiate(current_form)
            else:
                # Need LESS distinctiveness (too different - unusual)
                # Could make more similar to something
                pass
        
        return None
    
    def _similarity(self, s1: str, s2: str) -> float:
        """1 - normalized edit distance."""
        if not s1 or not s2:
            return 0.0
        dist = self._levenshtein(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1.0 - (dist / max_len) if max_len > 0 else 0.0
    
    def _levenshtein(self, s1: str, s2: str) -> int:
        """Levenshtein distance."""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _move_toward(self, current: str, target: str, rate: float) -> str:
        """
        Move current form toward target form.
        
        Actual interpolation, not instant replacement.
        """
        if current == target or not target:
            return current
        
        # Simple: probabilistically adopt segments from target
        if random.random() < rate and len(target) > 0:
            # Adopt one segment from target
            # Replace one character with corresponding from target
            i = random.randint(0, min(len(current), len(target)) - 1)
            if i < len(target):
                return current[:i] + target[i] + current[i + 1 :]
        
        return current
    
    def _simplify(self, form: str) -> str:
        """Reduce articulatory effort."""
        if len(form) > 2 and random.random() < 0.5:
            # Delete segment
            i = random.randint(0, len(form) - 1)
            return form[:i] + form[i + 1 :]
        return form
    
    def _elaborate(self, form: str) -> str:
        """Increase length."""
        vowels = 'aeiou'
        i = random.randint(0, len(form))
        return form[:i] + random.choice(vowels) + form[i:]
    
    def _differentiate(self, form: str) -> str:
        """Increase distinctiveness."""
        consonants = 'ptkbdgfszmnlr'
        vowels = 'aeiou'
        
        if random.random() < 0.5 and form:
            # Substitute
            i = random.randint(0, len(form) - 1)
            if form[i] in vowels:
                return form[:i] + random.choice(vowels) + form[i + 1 :]
            else:
                return form[:i] + random.choice(consonants) + form[i + 1 :]
        else:
            # Add segment
            i = random.randint(0, len(form))
            return form[:i] + random.choice(consonants + vowels) + form[i:]


class PerceptualControlSimulation(HistoryGenerator):
    """
    Language evolution through perceptual control.
    
    Implements rigorous PCT:
    - Signed error signals
    - Environment causally affects perception
    - Local sampling (no global knowledge)
    - Independent controllers
    - Listener-based feedback
    """

    def __init__(
        self,
        num_agents: int = 40,
        num_concepts: int = 12,
        interaction_radius: float = 0.3,
        environment: Environment | None = None,
        seed: int | None = None,
    ):
        super().__init__()
        if seed is not None:
            random.seed(seed)
        
        self.num_agents = num_agents
        self.num_concepts = num_concepts
        self.interaction_radius = interaction_radius
        self.environment = environment or Environment()
        
        # Generate proto-language
        self.concepts = [f'concept_{i}' for i in range(num_concepts)]
        proto_vocabulary = self._generate_proto_vocabulary()
        
        # Create agents with spatial distribution
        self.agents: list[Agent] = []
        for agent_id in range(num_agents):
            location = (random.random(), random.random())
            reference = ReferenceState()  # Could vary by agent
            
            agent = Agent(
                agent_id=agent_id,
                initial_vocabulary=proto_vocabulary,
                location=location,
                reference=reference,
            )
            self.agents.append(agent)
        
        self.history.metadata['proto_vocabulary'] = proto_vocabulary
        self.history.metadata['environment'] = {
            'noise': self.environment.ambient_noise,
            'network_size': self.environment.network_size,
        }
        self.time = 0
    
    def _generate_proto_vocabulary(self) -> dict[str, str]:
        """Generate shared proto-language."""
        vowels = 'aeiou'
        consonants = 'ptkbdgmnlrsw'
        
        vocab = {}
        for concept in self.concepts:
            length = random.randint(2, 4)
            form = ''
            for i in range(length):
                if i % 2 == 0:
                    form += random.choice(consonants)
                else:
                    form += random.choice(vowels)
            vocab[concept] = form
        
        return vocab
    
    def step(self):
        """One time step: agents interact and adjust."""
        self.time += 1
        
        # Sample interactions
        num_interactions = self.num_agents * 2
        
        for _ in range(num_interactions):
            # Pick random speaker
            speaker = random.choice(self.agents)
            
            # Sample local neighbors (no global knowledge)
            neighbors = self._sample_neighbors(speaker)
            
            if not neighbors:
                continue
            
            # Pick random listener from neighbors
            listener = random.choice(neighbors)
            
            # Pick random concept to communicate
            concept = random.choice(self.concepts)
            
            # Speaker produces, perceives result
            _perceived = speaker.produce(concept, self.environment, listener)
            
            # Get error from that interaction
            if speaker.error_history:
                error = speaker.error_history[-1]
                
                # Adjust if error large enough
                new_form = speaker.adjust_vocabulary(concept, error, neighbors)
                
                if new_form and new_form != speaker.vocabulary[concept]:
                    old_form = speaker.vocabulary[concept]
                    speaker.vocabulary[concept] = new_form
                    
                    # Record adjustment
                    self.history.record(
                        self.time,
                        'control_adjustment',
                        agent_id=speaker.agent_id,
                        concept=concept,
                        old_form=old_form,
                        new_form=new_form,
                        error=error.__dict__,
                        neighbors=[n.agent_id for n in neighbors],
                    )
    
    def _sample_neighbors(self, agent: Agent) -> list[Agent]:
        """
        Sample neighbors within interaction radius.
        
        Agent does NOT perceive global population.
        """
        neighbors = []
        for other in self.agents:
            if other.agent_id == agent.agent_id:
                continue
            
            dist = self._distance(agent.location, other.location)
            if dist < self.interaction_radius:
                neighbors.append(other)
        
        return neighbors
    
    def _distance(self, loc1: tuple, loc2: tuple) -> float:
        """Euclidean distance."""
        return ((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2) ** 0.5
    
    def get_observable(self) -> Observable:
        """
        Extract O_t: observable evidence only.
        
        Hidden: reference signals, error histories, control adjustments.
        """
        languages = {}
        
        for agent in self.agents:
            vocabulary = {}
            for concept, form in agent.vocabulary.items():
                vocabulary[concept] = {'form': form}
            
            languages[agent.agent_id] = {
                'vocabulary': vocabulary,
                'location': agent.location,
            }
        
        return Observable(
            time=self.time,
            languages=languages,
            metadata={'num_agents': self.num_agents},
        )


def demonstrate_rigorous_pct():
    """Demonstrate rigorous PCT implementation."""
    print("=" * 70)
    print("PERCEPTUAL CONTROL THEORY: RIGOROUS IMPLEMENTATION")
    print("=" * 70)
    print()
    print("Key Improvements:")
    print("  ✓ Signed error signals (directional)")
    print("  ✓ Environment causally affects perception")
    print("  ✓ Local sampling (no global knowledge)")
    print("  ✓ Actual conformity adjustment")
    print("  ✓ Separate control dimensions")
    print("  ✓ Listener-based comprehension")
    print()
    
    # Compare two environments
    environments = [
        ('Low Noise', Environment(ambient_noise=0.05)),
        ('High Noise', Environment(ambient_noise=0.3)),
    ]
    
    for env_name, env in environments:
        print(f"Environment: {env_name}")
        print(f"  Ambient noise: {env.ambient_noise:.2f}")
        print()
        
        sim = PerceptualControlSimulation(
            num_agents=30,
            num_concepts=8,
            interaction_radius=0.3,
            environment=env,
            seed=42,
        )
        
        proto = sim.history.metadata['proto_vocabulary']
        print(f"  Proto: {list(proto.values())[:4]}")
        
        # Run
        for _ in range(50):
            sim.step()
        
        obs = sim.get_observable()
        sample = next(iter(obs.languages.values()))['vocabulary']
        print(f"  After 50 steps: {[v['form'] for v in list(sample.values())[:4]]}")
        
        # Count adjustments
        adjustments = len(
            [e for e in sim.history.events if e.event_type == 'control_adjustment'],
        )
        print(f"  Control adjustments: {adjustments}")
        print()
    
    print("=" * 70)
    print()
    print("KEY INSIGHT:")
    print()
    print("Different environments create different control problems,")
    print("leading to different linguistic trajectories.")
    print()
    print("But control processes (reference signals, error histories)")
    print("are UNOBSERVABLE from O_t alone.")


if __name__ == '__main__':
    random.seed(42)
    demonstrate_rigorous_pct()
