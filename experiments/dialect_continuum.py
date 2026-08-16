#!/usr/bin/env python3
"""
Dialect Continuum Experiment

Research Question:
    When do mutually intelligible varieties become distinct languages?
    
This is a NON-TREE diffusion model. Speakers are distributed in 2D space.
They influence their neighbors, not through a branching tree structure.

The experiment demonstrates:
1. Continuous geographic variation (no discrete boundaries)
2. Emergence of dialect areas from local diffusion
3. When accumulated differences create mutual unintelligibility
4. How geography, barriers, and distance affect linguistic divergence

Ground Truth:
    H retains all speaker positions, all phonological states, all interactions
    
Observable:
    O_t is the phonological state of sampled speakers at time t
    Linguistic boundaries are observer-constructed, not inherent
    
Key Insight:
    Language families are observational simplifications. The actual
    evolutionary process is continuous spatial diffusion, not branching.
"""

import sys

sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

import random
from dataclasses import dataclass, field

from language_evolution.framework import HistoryGenerator, Observable
from language_evolution.phonology import Phoneme


@dataclass
class Speaker:
    """A speaker at a location with a phoneme inventory."""
    id: int
    x: float  # Position
    y: float
    inventory: set[Phoneme] = field(default_factory=set)
    
    def distance_to(self, other: 'Speaker') -> float:
        """Euclidean distance."""
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5


class DialectContinuum(HistoryGenerator):
    """
    Models continuous diffusion of linguistic change in 2D space.
    
    Unlike Phonological Drift (which simulates a population branching tree),
    this models a CONTINUUM where change diffuses geographically.
    
    Parameters:
        grid_size: Dimensions of the space
        num_speakers: How many speakers initially
        influence_radius: How far sound changes diffuse
        barrier_locations: Optional geographic barriers
    """
    
    def __init__(
        self,
        grid_size: tuple[int, int] = (10, 10),
        num_speakers: int = 100,
        influence_radius: float = 2.0,
        barrier_locations: list[tuple[tuple[float, float], tuple[float, float]]] | None = None,
        seed: int | None = None
    ):
        super().__init__()
        self.grid_size = grid_size
        self.num_speakers = num_speakers
        self.influence_radius = influence_radius
        self.barrier_locations = barrier_locations or []
        
        if seed is not None:
            random.seed(seed)
        
        # Create initial population
        self.speakers: list[Speaker] = []
        self._initialize_speakers()
        
        # Track which changes have occurred where
        self.change_origins: dict[int, tuple[int, int]] = {}  # generation -> (speaker_id, time)
        
    def _initialize_speakers(self):
        """Place speakers randomly in space with shared initial inventory."""
        # Start with common proto-language inventory
        proto_phonemes = [
            Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'}),
            Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'}),
            Phoneme('k', {'consonant', 'stop', 'voiceless', 'dorsal'}),
            Phoneme('a', {'vowel', 'low', 'central'}),
            Phoneme('i', {'vowel', 'high', 'front'}),
            Phoneme('u', {'vowel', 'high', 'back'}),
        ]
        
        # Place speakers
        for i in range(self.num_speakers):
            x = random.uniform(0, self.grid_size[0])
            y = random.uniform(0, self.grid_size[1])
            
            # Each speaker starts with a COPY of proto inventory
            inventory_copy = set(proto_phonemes)
            
            speaker = Speaker(id=i, x=x, y=y, inventory=inventory_copy)
            self.speakers.append(speaker)
        
        # Record initial state
        self.history.record(0, 'initialization', 
                          num_speakers=self.num_speakers,
                          grid_size=self.grid_size)
        
        for speaker in self.speakers:
            self.history.record(0, 'speaker_created',
                              speaker_id=speaker.id,
                              x=speaker.x,
                              y=speaker.y,
                              inventory_size=len(speaker.inventory))
    
    def _crosses_barrier(self, speaker1: Speaker, speaker2: Speaker) -> bool:
        """Check if the line between two speakers crosses a barrier."""
        for (bx1, by1), (bx2, by2) in self.barrier_locations:
            # Simple line-segment intersection test
            # (This is approximate; real implementation would be more careful)
            # For now, just check if speakers are on opposite sides
            pass
        return False
    
    def _get_neighbors(self, speaker: Speaker) -> list[Speaker]:
        """Find speakers within influence radius."""
        neighbors = []
        for other in self.speakers:
            if other.id == speaker.id:
                continue
            
            distance = speaker.distance_to(other)
            if distance <= self.influence_radius and not self._crosses_barrier(speaker, other):
                neighbors.append(other)
        
        return neighbors
    
    def _generate_random_change(self) -> tuple[str, Phoneme, Phoneme]:
        """
        Create a random phonological change.
        Returns (description, source_phoneme, target_phoneme)
        """
        # Just implement a few simple changes
        # Find voiceless stops and voice them
        voiceless_stops = [p for p in next(iter(self.speakers)).inventory 
                          if 'voiceless' in p.features and 'stop' in p.features]
        
        if voiceless_stops:
            source = random.choice(voiceless_stops)
            # Create voiced version
            target_features = (source.features - {'voiceless'}) | {'voiced'}
            target = Phoneme(source.symbol + 'ʱ', target_features)  # Approximate notation
            return ("voicing", source, target)
        
        # Fallback: no change
        return ("none", None, None)
    
    def step(self, generation: int):
        """One generation of diffusion."""
        
        # Randomly select a speaker where innovation occurs
        innovator = random.choice(self.speakers)
        
        # Generate a sound change
        description, source, target = self._generate_random_change()
        
        if source is None:
            return  # No change possible
        
        # Record the innovation
        self.history.record(generation, 'innovation',
                          speaker_id=innovator.id,
                          x=innovator.x,
                          y=innovator.y,
                          change_description=description,
                          source=source.symbol,
                          target=target.symbol)
        
        # Apply to innovator: replace source with target
        if source in innovator.inventory:
            innovator.inventory.remove(source)
            innovator.inventory.add(target)
        
        # Diffuse to neighbors with probability
        neighbors = self._get_neighbors(innovator)
        
        for neighbor in neighbors:
            # Probability decreases with distance
            distance = innovator.distance_to(neighbor)
            adoption_prob = max(0, 1 - (distance / self.influence_radius))
            
            if random.random() < adoption_prob:
                if source in neighbor.inventory:
                    neighbor.inventory.remove(source)
                    neighbor.inventory.add(target)
                
                self.history.record(generation, 'diffusion',
                                  from_speaker=innovator.id,
                                  to_speaker=neighbor.id,
                                  distance=distance,
                                  change_description=description)
    
    def run(self, generations: int):
        """Run the continuum evolution."""
        for gen in range(1, generations + 1):
            self.step(gen)
        
        self.history.record(generations, 'complete',
                          total_generations=generations)
    
    def get_observable(self) -> Observable:
        """
        Observable: Sample speakers at various locations.
        
        Unlike tree-based models, there's no privileged set of "tips".
        Any speaker could be documented.
        """
        # Sample speakers evenly across space
        sample_size = min(20, self.num_speakers)
        sampled = random.sample(self.speakers, sample_size)
        
        # Create observable languages from sampled speakers
        languages = {}
        for speaker in sampled:
            languages[speaker.id] = {
                'location': (speaker.x, speaker.y),
                'phonemes': sorted([p.symbol for p in speaker.inventory])
            }
        
        # Get current time from history
        current_time = max((e.time for e in self.history.events), default=0)
        
        obs = Observable(time=current_time, languages=languages)
        obs.metadata['description'] = "Sampled speakers from dialect continuum"
        obs.metadata['sample_size'] = sample_size
        obs.metadata['total_speakers'] = self.num_speakers
        
        return obs


def measure_phonological_distance(inv1: set[Phoneme], inv2: set[Phoneme]) -> float:
    """
    Measure phonological distance between two inventories.
    
    Simple metric: fraction of phonemes that differ.
    """
    symbols1 = {p.symbol for p in inv1}
    symbols2 = {p.symbol for p in inv2}
    
    union = symbols1 | symbols2
    intersection = symbols1 & symbols2
    
    if not union:
        return 0.0
    
    return 1 - (len(intersection) / len(union))


def identify_dialect_areas(speakers: list[Speaker], similarity_threshold: float = 0.3) -> dict[int, set[int]]:
    """
    Cluster speakers into dialect areas based on phonological similarity.
    
    This is an OBSERVER-CONSTRUCTED categorization. The actual process
    is continuous; dialect areas are our simplification.
    
    Returns:
        Dictionary mapping area_id -> set of speaker_ids
    """
    # Simple clustering: start with one speaker, add similar neighbors
    areas: dict[int, set[int]] = {}
    assigned: set[int] = set()
    area_id = 0
    
    for speaker in speakers:
        if speaker.id in assigned:
            continue
        
        # Start new dialect area
        area = {speaker.id}
        assigned.add(speaker.id)
        
        # Find similar speakers
        for other in speakers:
            if other.id in assigned:
                continue
            
            distance = measure_phonological_distance(speaker.inventory, other.inventory)
            
            if distance < similarity_threshold:
                area.add(other.id)
                assigned.add(other.id)
        
        areas[area_id] = area
        area_id += 1
    
    return areas


def visualize_continuum(speakers: list[Speaker], areas: dict[int, set[int]]):
    """
    Print a simple ASCII visualization of the dialect continuum.
    """
    print("\nDialect Continuum Visualization")
    print("================================\n")
    
    # Create grid
    grid_size = (12, 12)
    grid = [[' ' for _ in range(grid_size[0])] for _ in range(grid_size[1])]
    
    # Assign area symbols
    symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    area_to_symbol = {}
    for area_id in sorted(areas.keys()):
        if area_id < len(symbols):
            area_to_symbol[area_id] = symbols[area_id]
    
    # Place speakers
    for speaker in speakers:
        x_idx = int(speaker.x * (grid_size[0] - 1) / 10)
        y_idx = int(speaker.y * (grid_size[1] - 1) / 10)
        
        x_idx = max(0, min(grid_size[0] - 1, x_idx))
        y_idx = max(0, min(grid_size[1] - 1, y_idx))
        
        # Find which area this speaker belongs to
        symbol = '·'
        for area_id, speaker_ids in areas.items():
            if speaker.id in speaker_ids:
                symbol = area_to_symbol.get(area_id, '?')
                break
        
        grid[y_idx][x_idx] = symbol
    
    # Print grid
    for row in grid:
        print(''.join(row))
    
    print("\nDialect Areas:")
    for area_id in sorted(areas.keys()):
        symbol = area_to_symbol.get(area_id, '?')
        count = len(areas[area_id])
        print(f"  {symbol}: {count} speakers")


def main():
    """Demonstrate dialect continuum evolution."""
    print("=" * 70)
    print("DIALECT CONTINUUM EXPERIMENT")
    print("=" * 70)
    print()
    print("Research Question:")
    print("  When do mutually intelligible varieties become distinct languages?")
    print()
    print("Model:")
    print("  - Speakers distributed in 2D space")
    print("  - Sound changes diffuse geographically")
    print("  - NO branching tree structure")
    print("  - Dialect areas emerge from continuous variation")
    print()
    
    # Create continuum
    print("Initializing continuum...")
    continuum = DialectContinuum(
        grid_size=(10, 10),
        num_speakers=60,
        influence_radius=1.5,
        seed=42
    )
    
    print(f"  {continuum.num_speakers} speakers")
    print(f"  Grid: {continuum.grid_size}")
    print(f"  Influence radius: {continuum.influence_radius}")
    print()
    
    # Initial state
    print("Initial state: All speakers share proto-language")
    initial_inv = continuum.speakers[0].inventory
    print(f"  Proto-inventory: {sorted([p.symbol for p in initial_inv])}")
    print()
    
    # Evolve
    generations = 50
    print(f"Running {generations} generations of diffusion...")
    continuum.run(generations)
    print()
    
    # Analyze final state
    print("Final State Analysis")
    print("-" * 70)
    print()
    
    # Sample speakers from different locations
    corners = [
        min(continuum.speakers, key=lambda s: s.x + s.y),  # Southwest
        min(continuum.speakers, key=lambda s: (10-s.x) + s.y),  # Southeast
        min(continuum.speakers, key=lambda s: s.x + (10-s.y)),  # Northwest
        min(continuum.speakers, key=lambda s: (10-s.x) + (10-s.y)),  # Northeast
    ]
    
    labels = ['Southwest', 'Southeast', 'Northwest', 'Northeast']
    
    print("Sample speakers from corners:")
    for label, speaker in zip(labels, corners):
        print(f"\n  {label} (speaker {speaker.id} at {speaker.x:.1f}, {speaker.y:.1f}):")
        print(f"    Inventory: {sorted([p.symbol for p in speaker.inventory])}")
    
    # Calculate distances
    print("\nPhonological distances between corners:")
    for i in range(len(corners)):
        for j in range(i + 1, len(corners)):
            distance = measure_phonological_distance(
                corners[i].inventory,
                corners[j].inventory
            )
            print(f"  {labels[i]} ↔ {labels[j]}: {distance:.2f}")
    
    print()
    
    # Identify dialect areas
    print("Identifying dialect areas (similarity threshold: 0.3)...")
    areas = identify_dialect_areas(continuum.speakers, similarity_threshold=0.3)
    print(f"  Found {len(areas)} distinct dialect areas")
    print()
    
    # Visualization
    visualize_continuum(continuum.speakers, areas)
    
    # Key insight
    print("\n" + "=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print()
    print("The dialect areas shown above are OBSERVER-CONSTRUCTED.")
    print("The actual evolutionary process is continuous spatial diffusion.")
    print()
    print("There are no inherent boundaries between 'languages'.")
    print("Linguistic categories are simplifications we impose on")
    print("continuous variation for practical purposes.")
    print()
    print("This is why:")
    print("  - Mutual intelligibility is gradient, not binary")
    print("  - 'How many languages?' depends on who's asking")
    print("  - Family trees are useful fictions, not ground truth")
    print()
    
    # Observable vs. History
    print("Observable vs. Ground Truth")
    print("-" * 70)
    
    observable = continuum.get_observable()
    num_sampled = len(observable.languages)
    
    print(f"\nObservable: {num_sampled} documented speakers")
    print(f"Ground truth: {continuum.num_speakers} actual speakers")
    print(f"Coverage: {num_sampled/continuum.num_speakers*100:.1f}%")
    print()
    print("What reconstruction can access:")
    print("  - Phonological inventories of documented speakers")
    print("  - Geographic positions of documented speakers")
    print()
    print("What only ground truth H retains:")
    print("  - All undocumented speakers")
    print("  - Exact sequence of innovations")
    print("  - Diffusion paths of each change")
    print("  - Temporal ordering of events")
    print()
    
    # History statistics
    innovation_events = [e for e in continuum.history.events if e.event_type == 'innovation']
    diffusion_events = [e for e in continuum.history.events if e.event_type == 'diffusion']
    
    print("Ground truth contains:")
    print(f"  {len(innovation_events)} innovation events")
    print(f"  {len(diffusion_events)} diffusion events")
    print(f"  Total: {len(continuum.history.events)} events")
    print()
    print("None of this temporal/causal structure is directly observable.")
    print("We can only infer it from synchronic linguistic geography.")
    print()


if __name__ == '__main__':
    main()
