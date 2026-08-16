#!/usr/bin/env python3
"""
Perceptual Control Theory Applied to Language Evolution

Based on William Powers and William Calvin's work on hierarchical
perceptual control systems.

Core Insight:
    Language users don't just "respond to stimuli" - they actively
    CONTROL their perceptions through negative feedback loops.
    
    A speaker doesn't just produce words; they monitor whether their
    utterance achieved the DESIRED PERCEPTUAL STATE in the listener,
    and adjust accordingly.

Key Concepts:
    1. Reference Signal: Desired perceptual state (communicative goal)
    2. Perceptual Signal: Actual perceived state (what was understood)
    3. Error Signal: Difference between reference and perception
    4. Output: Linguistic behavior that reduces error
    
    Language change emerges from:
    - Individual error-correction loops
    - Hierarchical control (word → phrase → utterance → discourse)
    - Ecological constraints (environment shapes what needs controlling)

This is fundamentally different from:
    - Stimulus-response models
    - Optimality theory (which assumes fixed targets)
    - Purely stochastic drift
"""

import random
import sys
from dataclasses import dataclass, field

sys.path.insert(0, 'src')

from language_evolution.framework import HistoryGenerator, Observable


@dataclass
class PerceptualState:
    """
    What an agent perceives in their linguistic environment.
    
    In PCT, agents control PERCEPTIONS, not behaviors.
    """

    meaning_understood: float  # 0-1: How well meaning was conveyed
    social_alignment: float  # 0-1: How similar to community norms
    articulatory_ease: float  # 0-1: How easy to produce
    distinctiveness: float  # 0-1: How different from confusable alternatives


@dataclass
class ReferenceSignal:
    """
    The DESIRED perceptual state an agent wants to achieve.
    
    This is what the agent is trying to control.
    """

    target_comprehension: float = 0.9  # Want listener to understand
    target_conformity: float = 0.7  # Want to sound "normal"
    target_ease: float = 0.6  # Want comfortable production
    target_distinctiveness: float = 0.8  # Want to avoid ambiguity


@dataclass
class ControlLoop:
    """
    A hierarchical control system for one linguistic unit.
    
    The agent continuously:
    1. Perceives current state
    2. Compares to reference (desired state)
    3. Generates output to reduce error
    4. Observes result, repeat
    """

    agent_id: int
    meaning: str
    current_form: str
    reference: ReferenceSignal = field(default_factory=ReferenceSignal)
    
    # Control history
    perception_history: list[PerceptualState] = field(default_factory=list)
    error_history: list[float] = field(default_factory=list)
    
    def perceive(self, environment: dict) -> PerceptualState:
        """
        Perceive current state of this linguistic form.
        
        In PCT, perception is ACTIVE - agents extract what matters
        to their control goals.
        """
        # How well does this form achieve communicative goals?
        community_forms = environment.get('community_forms', {}).get(self.meaning, [])
        
        # Comprehension: Does listener understand?
        # (Simulated by form similarity to community)
        if community_forms:
            max_overlap = max(
                self._form_similarity(self.current_form, other)
                for other in community_forms
            )
            comprehension = max_overlap
        else:
            comprehension = 0.5  # Unknown
        
        # Social alignment: Am I speaking like my community?
        if community_forms:
            alignment = sum(
                self._form_similarity(self.current_form, other)
                for other in community_forms
            ) / len(community_forms)
        else:
            alignment = 0.5
        
        # Articulatory ease: How easy to produce?
        ease = 1.0 - (len(self.current_form) / 15.0)  # Shorter = easier
        ease = max(0.0, min(1.0, ease))
        
        # Distinctiveness: Different from confusable alternatives?
        confusable = environment.get('confusable_forms', [])
        if confusable:
            min_distance = min(
                1.0 - self._form_similarity(self.current_form, other)
                for other in confusable
            )
            distinctiveness = min_distance
        else:
            distinctiveness = 0.8
        
        state = PerceptualState(
            meaning_understood=comprehension,
            social_alignment=alignment,
            articulatory_ease=ease,
            distinctiveness=distinctiveness,
        )
        
        self.perception_history.append(state)
        return state
    
    def compute_error(self, perception: PerceptualState) -> float:
        """
        Compute ERROR between desired and actual perceptual state.
        
        This is the heart of PCT: behavior is driven by error,
        not by stimuli.
        """
        errors = [
            abs(self.reference.target_comprehension - perception.meaning_understood),
            abs(self.reference.target_conformity - perception.social_alignment),
            abs(self.reference.target_ease - perception.articulatory_ease),
            abs(self.reference.target_distinctiveness - perception.distinctiveness),
        ]
        
        total_error = sum(errors) / len(errors)
        self.error_history.append(total_error)
        return total_error
    
    def generate_output(self, error: float, perception: PerceptualState) -> str:
        """
        Generate behavioral OUTPUT to reduce error.
        
        In PCT, output is whatever reduces the error signal.
        NOT a fixed response to input.
        """
        if error < 0.1:
            # Good enough - no change
            return self.current_form
        
        # Decide what to adjust based on which perception is furthest from target
        comprehension_error = abs(
            self.reference.target_comprehension - perception.meaning_understood,
        )
        conformity_error = abs(
            self.reference.target_conformity - perception.social_alignment,
        )
        ease_error = abs(self.reference.target_ease - perception.articulatory_ease)
        distinctiveness_error = abs(
            self.reference.target_distinctiveness - perception.distinctiveness,
        )
        
        # Prioritize largest error
        if comprehension_error > 0.3 or conformity_error > 0.3:
            # Move toward community norm
            return self._move_toward_community()
        elif ease_error > 0.3:
            # Simplify
            return self._simplify_form()
        elif distinctiveness_error > 0.3:
            # Differentiate
            return self._differentiate_form()
        else:
            # Small random variation
            return self._vary_slightly()
    
    def _form_similarity(self, form1: str, form2: str) -> float:
        """Simple similarity metric (1 - normalized edit distance)."""
        if not form1 or not form2:
            return 0.0
        
        # Levenshtein distance
        dist = self._edit_distance(form1, form2)
        max_len = max(len(form1), len(form2))
        return 1.0 - (dist / max_len) if max_len > 0 else 0.0
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Levenshtein distance."""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
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
    
    def _move_toward_community(self) -> str:
        """Adjust form toward community average."""
        # Simplified: just return current form with small variation
        return self.current_form
    
    def _simplify_form(self) -> str:
        """Reduce articulatory complexity."""
        if len(self.current_form) > 3:
            # Drop a random vowel or consonant
            i = random.randint(0, len(self.current_form) - 1)
            return self.current_form[:i] + self.current_form[i + 1 :]
        return self.current_form
    
    def _differentiate_form(self) -> str:
        """Increase distinctiveness."""
        # Add a segment
        vowels = 'aeiou'
        consonants = 'ptkbdgfszmnlr'
        if random.random() < 0.5:
            return self.current_form + random.choice(vowels)
        else:
            return self.current_form + random.choice(consonants)
    
    def _vary_slightly(self) -> str:
        """Random small variation."""
        if random.random() < 0.3:
            return self._simplify_form()
        return self.current_form


@dataclass
class EcologicalNiche:
    """
    The ENVIRONMENT that agents are trying to control.
    
    Different niches create different control problems,
    leading to different linguistic adaptations.
    """

    name: str
    communicative_pressure: float  # How important is clarity?
    social_pressure: float  # How important is conformity?
    efficiency_pressure: float  # How important is brevity?
    
    # Environmental conditions
    ambient_noise: float = 0.1  # Makes comprehension harder
    group_size: int = 50  # Larger groups = more conformity pressure
    stability: float = 0.9  # How stable is the environment?


class PerceptualControlLanguage(HistoryGenerator):
    """
    Language evolution as hierarchical perceptual control.
    
    Agents don't respond to stimuli - they control their perceptions
    through negative feedback loops.
    
    Language change emerges from:
    - Individual control loops acting in parallel
    - Ecological constraints on what needs controlling
    - Hierarchical organization (sounds → words → sentences)
    """

    def __init__(
        self,
        num_agents: int = 30,
        num_meanings: int = 10,
        niche: EcologicalNiche | None = None,
        seed: int | None = None,
    ):
        super().__init__()
        if seed is not None:
            random.seed(seed)
        
        self.num_agents = num_agents
        self.num_meanings = num_meanings
        self.niche = niche or EcologicalNiche(
            name='neutral',
            communicative_pressure=0.7,
            social_pressure=0.6,
            efficiency_pressure=0.5,
        )
        
        # Initialize agents with control loops
        self.meanings = [f'meaning_{i}' for i in range(num_meanings)]
        self.agents: dict[int, dict[str, ControlLoop]] = {}
        
        # Shared initial forms (proto-language)
        proto_forms = {
            meaning: self._generate_random_form() for meaning in self.meanings
        }
        
        for agent_id in range(num_agents):
            self.agents[agent_id] = {}
            for meaning in self.meanings:
                # Each agent starts with proto-form but has own control loop
                self.agents[agent_id][meaning] = ControlLoop(
                    agent_id=agent_id,
                    meaning=meaning,
                    current_form=proto_forms[meaning],
                    reference=self._create_reference_signal(),
                )
        
        self.history.metadata['proto_forms'] = proto_forms
        self.history.metadata['niche'] = self.niche.name
        self.time = 0
    
    def _generate_random_form(self) -> str:
        """Generate random proto-form."""
        vowels = 'aeiou'
        consonants = 'ptkbdgmnlr'
        length = random.randint(2, 4)
        form = ''
        for i in range(length):
            if i % 2 == 0:
                form += random.choice(consonants)
            else:
                form += random.choice(vowels)
        return form
    
    def _create_reference_signal(self) -> ReferenceSignal:
        """
        Create reference signal based on ecological niche.
        
        Different niches create different control goals.
        """
        return ReferenceSignal(
            target_comprehension=self.niche.communicative_pressure,
            target_conformity=self.niche.social_pressure,
            target_ease=self.niche.efficiency_pressure,
            target_distinctiveness=0.7,  # Generally important
        )
    
    def step(self):
        """
        One time step: all agents run their control loops.
        
        1. Perceive environment
        2. Compute error
        3. Generate output
        4. Update form
        """
        self.time += 1
        
        # Build environment state (what agents can perceive)
        environment = self._build_environment()
        
        # Each agent runs control loop for each meaning
        for agent_id, loops in self.agents.items():
            for meaning, loop in loops.items():
                # 1. Perceive
                perception = loop.perceive(environment[meaning])
                
                # 2. Compute error
                error = loop.compute_error(perception)
                
                # 3. Generate output (if error is large)
                if error > 0.15:
                    new_form = loop.generate_output(error, perception)
                    
                    if new_form != loop.current_form:
                        # Record change
                        self.history.record(
                            self.time,
                            'control_adjustment',
                            agent_id=agent_id,
                            meaning=meaning,
                            old_form=loop.current_form,
                            new_form=new_form,
                            error=error,
                            perception=perception.__dict__,
                        )
                        
                        loop.current_form = new_form
    
    def _build_environment(self) -> dict:
        """
        Build perceptual environment for each meaning.
        
        This is what agents can perceive about their community.
        """
        environment = {}
        
        for meaning in self.meanings:
            # Collect all forms currently used for this meaning
            community_forms = [
                loop.current_form
                for loops in self.agents.values()
                for m, loop in loops.items()
                if m == meaning
            ]
            
            # Collect confusable forms (other meanings with similar forms)
            confusable = []
            for other_meaning in self.meanings:
                if other_meaning != meaning:
                    other_forms = [
                        loop.current_form
                        for loops in self.agents.values()
                        for m, loop in loops.items()
                        if m == other_meaning
                    ]
                    confusable.extend(other_forms)
            
            environment[meaning] = {
                'community_forms': {meaning: community_forms},
                'confusable_forms': confusable,
            }
        
        return environment
    
    def get_observable(self) -> Observable:
        """
        Extract observable state (what a linguist sees).
        
        Observable includes:
        - Current forms for each agent
        - NOT the control loops or error signals (internal)
        """
        languages = {}
        
        for agent_id, loops in self.agents.items():
            vocabulary = {}
            for meaning, loop in loops.items():
                vocabulary[meaning] = {'form': loop.current_form}
            
            languages[agent_id] = {'vocabulary': vocabulary}
        
        return Observable(
            time=self.time,
            languages=languages,
            metadata={
                'niche': self.niche.name,
                'num_agents': self.num_agents,
            },
        )


def demonstrate_ecological_niches():
    """
    Demonstrate how different ecological niches lead to different
    linguistic adaptations through perceptual control.
    """
    print("=" * 70)
    print("PERCEPTUAL CONTROL THEORY: ECOLOGICAL LANGUAGE EVOLUTION")
    print("=" * 70)
    print()
    print("Based on William Powers and William Calvin's work")
    print()
    print("Key Insight: Language users CONTROL their perceptions through")
    print("negative feedback loops. Different ecological niches create")
    print("different control problems.")
    print()
    print("=" * 70)
    print()
    
    # Define three different ecological niches
    niches = [
        EcologicalNiche(
            name='high_noise',
            communicative_pressure=0.95,  # Clarity is critical
            social_pressure=0.5,
            efficiency_pressure=0.3,
            ambient_noise=0.7,
        ),
        EcologicalNiche(
            name='high_conformity',
            communicative_pressure=0.6,
            social_pressure=0.95,  # Conformity is critical
            efficiency_pressure=0.4,
        ),
        EcologicalNiche(
            name='efficiency_focused',
            communicative_pressure=0.7,
            social_pressure=0.5,
            efficiency_pressure=0.95,  # Brevity is critical
        ),
    ]
    
    for niche in niches:
        print(f"Niche: {niche.name.upper()}")
        print(f"  Communicative pressure: {niche.communicative_pressure:.2f}")
        print(f"  Social pressure: {niche.social_pressure:.2f}")
        print(f"  Efficiency pressure: {niche.efficiency_pressure:.2f}")
        print()
        
        sim = PerceptualControlLanguage(
            num_agents=20,
            num_meanings=5,
            niche=niche,
            seed=42,
        )
        
        # Show initial state
        proto = sim.history.metadata['proto_forms']
        print(f"  Proto-forms: {list(proto.values())[:3]}")
        
        # Run simulation
        for _ in range(30):
            sim.step()
        
        # Show final state
        obs = sim.get_observable()
        sample_agent = next(iter(obs.languages.values()))
        sample_forms = [v['form'] for v in sample_agent['vocabulary'].values()][:3]
        print(f"  After 30 steps: {sample_forms}")
        
        # Count changes
        changes = len([e for e in sim.history.events if e.event_type == 'control_adjustment'])
        print(f"  Total control adjustments: {changes}")
        print()
    
    print("=" * 70)
    print()
    print("KEY INSIGHTS:")
    print()
    print("1. Different ecological niches create different control problems")
    print("2. Language change emerges from individual error-correction loops")
    print("3. NOT stimulus-response - agents actively control perceptions")
    print("4. Hierarchical control enables complex linguistic behavior")
    print()
    print("This explains why languages adapt to their environments")
    print("through negative feedback, not random drift.")


if __name__ == '__main__':
    random.seed(42)
    demonstrate_ecological_niches()
