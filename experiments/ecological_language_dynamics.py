#!/usr/bin/env python3
"""
Ecological Disturbance and Language Adaptation

Combining Perceptual Control Theory with ecological dynamics.

Key Idea:
    Languages exist in CHANGING environments. Perceptual control
    loops must continuously adapt to:
    - Resource competition (limited acoustic space)
    - Environmental disturbances (contact, migration, innovation)
    - Niche construction (speakers modify their own environment)
    
Based on:
    - William Powers: Hierarchical perceptual control
    - William Calvin: Selection in neural populations
    - Ecological dynamics: Niche construction and disturbance
"""

import random
import sys
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, 'src')

from language_evolution.framework import HistoryGenerator, Observable


@dataclass
class DisturbanceEvent:
    """Environmental change that perturbs linguistic equilibrium."""

    time: int
    event_type: str  # 'migration', 'contact', 'innovation', 'bottleneck'
    affected_agents: list[int]
    intensity: float  # 0-1: How disruptive?
    data: dict = field(default_factory=dict)


class EcologicalLanguageSystem(HistoryGenerator):
    """
    Language evolution in a dynamic ecological context.
    
    Unlike pure PCT (which assumes stable reference signals),
    this models:
    - Environmental disturbances
    - Resource competition (acoustic/semantic space)
    - Population structure
    - Niche construction (agents modify environment)
    """

    def __init__(
        self,
        num_agents: int = 50,
        num_concepts: int = 15,
        innovation_rate: float = 0.05,
        migration_rate: float = 0.02,
        contact_rate: float = 0.1,
        seed: int | None = None,
    ):
        super().__init__()
        if seed is not None:
            random.seed(seed)
        
        self.num_agents = num_agents
        self.num_concepts = num_concepts
        self.innovation_rate = innovation_rate
        self.migration_rate = migration_rate
        self.contact_rate = contact_rate
        
        # Initialize population
        self.concepts = [f'concept_{i}' for i in range(num_concepts)]
        
        # Each agent has forms for each concept
        # Plus "fitness" - how well their forms achieve control goals
        self.agents: dict = {}
        
        # Proto-language: shared initial forms
        proto_forms = self._generate_proto_language()
        self.history.metadata['proto_forms'] = proto_forms
        
        for agent_id in range(num_agents):
            self.agents[agent_id] = {
                'forms': dict(proto_forms),  # Copy proto forms
                'location': (random.random(), random.random()),  # 2D space
                'fitness': 1.0,  # Perceptual control success
                'neighbors': [],  # Filled during simulation
            }
        
        self.time = 0
        self.disturbances: list[DisturbanceEvent] = []
    
    def _generate_proto_language(self) -> dict[str, str]:
        """Generate shared proto-language."""
        vowels = 'aeiou'
        consonants = 'ptkbdgmnlrsw'
        
        forms = {}
        for concept in self.concepts:
            # CVC or CVCV structure
            if random.random() < 0.5:
                form = (
                    random.choice(consonants)
                    + random.choice(vowels)
                    + random.choice(consonants)
                )
            else:
                form = (
                    random.choice(consonants)
                    + random.choice(vowels)
                    + random.choice(consonants)
                    + random.choice(vowels)
                )
            forms[concept] = form
        
        return forms
    
    def step(self):
        """One time step of ecological dynamics."""
        self.time += 1
        
        # Update neighborhood structure
        self._update_neighborhoods()
        
        # Evaluate fitness (perceptual control success)
        self._evaluate_fitness()
        
        # Apply ecological disturbances
        self._apply_disturbances()
        
        # Innovation pressure
        if random.random() < self.innovation_rate:
            self._introduce_innovation()
        
        # Contact and transmission
        self._linguistic_contact()
        
        # Selection: low-fitness forms get adjusted
        self._perceptual_control_adjustment()
    
    def _update_neighborhoods(self):
        """Update who interacts with whom based on spatial proximity."""
        interaction_radius = 0.3
        
        for agent_id, agent in self.agents.items():
            neighbors = []
            for other_id, other in self.agents.items():
                if other_id != agent_id:
                    dist = self._spatial_distance(
                        agent['location'],
                        other['location'],
                    )
                    if dist < interaction_radius:
                        neighbors.append(other_id)
            
            agent['neighbors'] = neighbors
    
    def _spatial_distance(self, loc1: tuple, loc2: tuple) -> float:
        """Euclidean distance in 2D space."""
        return ((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2) ** 0.5
    
    def _evaluate_fitness(self):
        """
        Compute perceptual control success (fitness).
        
        Agents succeed when they:
        1. Are understood by neighbors (forms similar to community)
        2. Distinguish different concepts (forms dissimilar to each other)
        3. Use efficient forms (shorter is better)
        """
        for agent in self.agents.values():
            fitness_scores = []
            
            for concept, form in agent['forms'].items():
                # 1. Community alignment (comprehension)
                if agent['neighbors']:
                    neighbor_forms = [
                        self.agents[n]['forms'][concept] for n in agent['neighbors']
                    ]
                    alignment = sum(
                        self._string_similarity(form, nf) for nf in neighbor_forms
                    ) / len(neighbor_forms)
                else:
                    alignment = 0.5
                
                # 2. Distinctiveness (avoid homophony)
                other_concepts = [c for c in self.concepts if c != concept]
                if other_concepts:
                    distinctiveness = 1.0 - max(
                        self._string_similarity(form, agent['forms'][oc])
                        for oc in other_concepts
                    )
                else:
                    distinctiveness = 0.8
                
                # 3. Efficiency (length penalty)
                efficiency = max(0.0, 1.0 - len(form) / 10.0)
                
                # Combined fitness
                concept_fitness = (alignment * 0.4 + distinctiveness * 0.4 + efficiency * 0.2)
                fitness_scores.append(concept_fitness)
            
            agent['fitness'] = sum(fitness_scores) / len(fitness_scores)
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """1 - normalized edit distance."""
        if not s1 or not s2:
            return 0.0
        dist = self._edit_distance(s1, s2)
        max_len = max(len(s1), len(s2))
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
    
    def _apply_disturbances(self):
        """Apply random environmental disturbances."""
        # Migration: agents move
        if random.random() < self.migration_rate:
            agent_id = random.choice(list(self.agents.keys()))
            old_loc = self.agents[agent_id]['location']
            new_loc = (
                min(1.0, max(0.0, old_loc[0] + random.gauss(0, 0.2))),
                min(1.0, max(0.0, old_loc[1] + random.gauss(0, 0.2))),
            )
            self.agents[agent_id]['location'] = new_loc
            
            self.history.record(
                self.time,
                'migration',
                agent_id=agent_id,
                old_location=old_loc,
                new_location=new_loc,
            )
            
            self.disturbances.append(
                DisturbanceEvent(
                    time=self.time,
                    event_type='migration',
                    affected_agents=[agent_id],
                    intensity=0.3,
                ),
            )
    
    def _introduce_innovation(self):
        """Introduce novel linguistic form (innovation)."""
        agent_id = random.choice(list(self.agents.keys()))
        concept = random.choice(self.concepts)
        old_form = self.agents[agent_id]['forms'][concept]
        
        # Generate novel form
        new_form = self._mutate_form(old_form)
        self.agents[agent_id]['forms'][concept] = new_form
        
        self.history.record(
            self.time,
            'innovation',
            agent_id=agent_id,
            concept=concept,
            old_form=old_form,
            new_form=new_form,
        )
    
    def _mutate_form(self, form: str) -> str:
        """Create variant of existing form."""
        if not form:
            return 'ba'
        
        vowels = 'aeiou'
        consonants = 'ptkbdgmnlrsw'
        
        mutation_type = random.choice(['substitute', 'delete', 'insert'])
        
        if mutation_type == 'substitute' and form:
            i = random.randint(0, len(form) - 1)
            if form[i] in vowels:
                new_char = random.choice(vowels)
            else:
                new_char = random.choice(consonants)
            return form[:i] + new_char + form[i + 1 :]
        
        elif mutation_type == 'delete' and len(form) > 2:
            i = random.randint(0, len(form) - 1)
            return form[:i] + form[i + 1 :]
        
        elif mutation_type == 'insert':
            i = random.randint(0, len(form))
            char = random.choice(vowels + consonants)
            return form[:i] + char + form[i:]
        
        return form
    
    def _linguistic_contact(self):
        """Agents adopt forms from neighbors (horizontal transmission)."""
        for agent_id, agent in self.agents.items():
            if not agent['neighbors']:
                continue
            
            if random.random() < self.contact_rate:
                # Pick a neighbor
                neighbor_id = random.choice(agent['neighbors'])
                neighbor = self.agents[neighbor_id]
                
                # Pick a concept to potentially adopt
                concept = random.choice(self.concepts)
                
                neighbor_form = neighbor['forms'][concept]
                own_form = agent['forms'][concept]
                
                # Adopt if neighbor form is similar enough (comprehensible)
                if self._string_similarity(neighbor_form, own_form) > 0.4 and random.random() < 0.3:
                    agent['forms'][concept] = neighbor_form
                    
                    self.history.record(
                        self.time,
                        'contact_adoption',
                        agent_id=agent_id,
                        source_agent=neighbor_id,
                        concept=concept,
                        adopted_form=neighbor_form,
                    )
    
    def _perceptual_control_adjustment(self):
        """
        Low-fitness agents adjust forms to improve perceptual control.
        
        This is the PCT error-correction mechanism.
        """
        for agent_id, agent in self.agents.items():
            if agent['fitness'] < 0.6:  # Below threshold
                # Pick worst-performing concept
                worst_concept = None
                worst_fitness = 1.0
                
                for concept in self.concepts:
                    # Recompute fitness just for this concept
                    form = agent['forms'][concept]
                    
                    # Alignment with neighbors
                    if agent['neighbors']:
                        neighbor_forms = [
                            self.agents[n]['forms'][concept] for n in agent['neighbors']
                        ]
                        alignment = sum(
                            self._string_similarity(form, nf) for nf in neighbor_forms
                        ) / len(neighbor_forms)
                    else:
                        alignment = 0.5
                    
                    if alignment < worst_fitness:
                        worst_fitness = alignment
                        worst_concept = concept
                
                # Adjust worst concept toward community norm
                if worst_concept and agent['neighbors']:
                    # Adopt most common neighbor form
                    neighbor_forms = [
                        self.agents[n]['forms'][worst_concept]
                        for n in agent['neighbors']
                    ]
                    if neighbor_forms:
                        # Pick most common
                        form_counts = defaultdict(int)
                        for nf in neighbor_forms:
                            form_counts[nf] += 1
                        most_common = max(form_counts.items(), key=lambda x: x[1])[0]
                        
                        old_form = agent['forms'][worst_concept]
                        agent['forms'][worst_concept] = most_common
                        
                        self.history.record(
                            self.time,
                            'control_adjustment',
                            agent_id=agent_id,
                            concept=worst_concept,
                            old_form=old_form,
                            new_form=most_common,
                            reason='low_fitness',
                            fitness=agent['fitness'],
                        )
    
    def get_observable(self) -> Observable:
        """Extract observable linguistic state."""
        languages = {}
        
        for agent_id, agent in self.agents.items():
            vocabulary = {}
            for concept, form in agent['forms'].items():
                vocabulary[concept] = {'form': form}
            
            languages[agent_id] = {
                'vocabulary': vocabulary,
                'location': agent['location'],
                'fitness': agent['fitness'],
            }
        
        return Observable(
            time=self.time,
            languages=languages,
            metadata={
                'num_agents': self.num_agents,
                'disturbances': len(self.disturbances),
            },
        )


def demonstrate_ecological_dynamics():
    """Demonstrate ecological language evolution."""
    print("=" * 70)
    print("ECOLOGICAL LANGUAGE DYNAMICS")
    print("=" * 70)
    print()
    print("Language evolution in changing environments:")
    print("  - Environmental disturbances (migration)")
    print("  - Innovation pressure")
    print("  - Contact and transmission")
    print("  - Perceptual control (error correction)")
    print()
    
    sim = EcologicalLanguageSystem(
        num_agents=30,
        num_concepts=8,
        innovation_rate=0.08,
        migration_rate=0.05,
        contact_rate=0.15,
        seed=42,
    )
    
    proto = sim.history.metadata['proto_forms']
    print("Proto-language (sample):")
    for concept, form in list(proto.items())[:5]:
        print(f"  {concept}: {form}")
    print()
    
    # Run simulation
    steps = 50
    for _ in range(steps):
        sim.step()
    
    print(f"After {steps} time steps:\n")
    
    # Show final state
    obs = sim.get_observable()
    sample_agents = list(obs.languages.items())[:3]
    
    for agent_id, data in sample_agents:
        vocab = data['vocabulary']
        fitness = data['fitness']
        print(f"Agent {agent_id} (fitness: {fitness:.2f}):")
        for concept, word in list(vocab.items())[:3]:
            proto_form = proto[concept]
            current_form = word['form']
            if current_form != proto_form:
                print(f"  {concept}: {proto_form} → {current_form}")
            else:
                print(f"  {concept}: {current_form} (unchanged)")
        print()
    
    # Statistics
    events_by_type = defaultdict(int)
    for event in sim.history.events:
        events_by_type[event.event_type] += 1
    
    print("Event Summary:")
    for event_type, count in sorted(events_by_type.items()):
        print(f"  {event_type}: {count}")
    print()
    
    # Diversity metric
    all_forms = set()
    for agent_data in obs.languages.values():
        for word_data in agent_data['vocabulary'].values():
            all_forms.add(word_data['form'])
    
    print(f"Linguistic diversity: {len(all_forms)} unique forms")
    print(f"Environmental disturbances: {len(sim.disturbances)}")
    print()
    
    print("=" * 70)
    print()
    print("KEY INSIGHTS:")
    print()
    print("1. Language adapts to ecological disturbances")
    print("2. Perceptual control (error correction) maintains comprehension")
    print("3. Innovation + contact create diversity")
    print("4. Fitness = successful perceptual control in environment")
    print()
    print("This combines PCT with ecological dynamics for realistic")
    print("language evolution.")


if __name__ == '__main__':
    random.seed(42)
    demonstrate_ecological_dynamics()
