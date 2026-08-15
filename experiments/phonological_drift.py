"""Phonological Drift: Population-based phoneme evolution simulator.

A population begins with a shared phoneme inventory and sound changes propagate
probabilistically through speakers and generations. Models competing innovations,
incomplete adoption, geographical isolation, prestige effects, and chain shifts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
import random
from collections import defaultdict

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from language_evolution.phonology import (
    Phoneme, SoundChange, PhonemeInventory, create_basic_inventory
)


@dataclass
class Speaker:
    """An individual speaker with their own phoneme inventory and lexicon."""
    id: int
    inventory: PhonemeInventory
    lexicon: Dict[str, List[Phoneme]]
    position: Tuple[float, float]  # (x, y) coordinates
    prestige: float = 1.0
    generation: int = 0
    
    def copy_with_changes(self, new_id: int, new_generation: int) -> 'Speaker':
        """Create a child speaker with potential innovations."""
        return Speaker(
            id=new_id,
            inventory=self.inventory.copy(),
            lexicon={word: phones.copy() for word, phones in self.lexicon.items()},
            position=self.position,
            prestige=self.prestige,
            generation=new_generation
        )


@dataclass
class Population:
    """A population of speakers."""
    speakers: List[Speaker]
    sound_changes: List[SoundChange] = field(default_factory=list)
    generation: int = 0
    
    def get_neighbors(self, speaker: Speaker, radius: float = 1.0) -> List[Speaker]:
        """Get speakers within geographical radius."""
        neighbors = []
        for other in self.speakers:
            if other.id == speaker.id:
                continue
            distance = ((speaker.position[0] - other.position[0])**2 + 
                       (speaker.position[1] - other.position[1])**2)**0.5
            if distance <= radius:
                neighbors.append(other)
        return neighbors
    
    def introduce_sound_change(self, change: SoundChange, initial_speakers: int = 1):
        """Introduce a new sound change in a subset of speakers."""
        self.sound_changes.append(change)
        adopters = random.sample(self.speakers, min(initial_speakers, len(self.speakers)))
        
        for speaker in adopters:
            # Apply change to entire lexicon
            for word in speaker.lexicon:
                speaker.lexicon[word] = change.apply(speaker.lexicon[word])
    
    def step_generation(self, adoption_rate: float = 0.3, neighbor_influence: float = 0.5):
        """Simulate one generation of language change."""
        self.generation += 1
        
        for change in self.sound_changes:
            # Determine which speakers adopt which changes this generation
            for speaker in self.speakers:
                # Check if neighbors have adopted this change
                neighbors = self.get_neighbors(speaker, radius=2.0)
                if not neighbors:
                    continue
                
                # Count neighbors who have the change (approximate by checking one word)
                adopter_count = 0
                total_prestige = 0
                
                for neighbor in neighbors:
                    total_prestige += neighbor.prestige
                    # Simple heuristic: if first word changed, they adopted it
                    if neighbor.lexicon:
                        test_word = list(neighbor.lexicon.keys())[0]
                        original = create_test_lexicon()[test_word]
                        if neighbor.lexicon[test_word] != original:
                            adopter_count += neighbor.prestige
                
                # Probability of adoption based on neighbors and prestige
                if total_prestige > 0:
                    adoption_prob = (adopter_count / total_prestige) * neighbor_influence
                    
                    if random.random() < adoption_prob:
                        # Adopt the change
                        for word in speaker.lexicon:
                            speaker.lexicon[word] = change.apply(speaker.lexicon[word])
    
    def compute_phoneme_divergence(self) -> Dict[Tuple[int, int], float]:
        """Compute phoneme inventory divergence between all speaker pairs."""
        divergences = {}
        
        for i, speaker1 in enumerate(self.speakers):
            for j, speaker2 in enumerate(self.speakers[i+1:], start=i+1):
                # Compute symmetric difference of inventories
                inv1 = set(p.symbol for p in speaker1.inventory.phonemes)
                inv2 = set(p.symbol for p in speaker2.inventory.phonemes)
                
                symmetric_diff = len(inv1.symmetric_difference(inv2))
                union_size = len(inv1.union(inv2))
                
                divergence = symmetric_diff / union_size if union_size > 0 else 0
                divergences[(speaker1.id, speaker2.id)] = divergence
        
        return divergences
    
    def compute_lexical_divergence(self) -> Dict[Tuple[int, int], float]:
        """Compute lexical divergence between all speaker pairs."""
        divergences = {}
        
        for i, speaker1 in enumerate(self.speakers):
            for j, speaker2 in enumerate(self.speakers[i+1:], start=i+1):
                # Compare shared vocabulary
                shared_words = set(speaker1.lexicon.keys()) & set(speaker2.lexicon.keys())
                if not shared_words:
                    divergences[(speaker1.id, speaker2.id)] = 1.0
                    continue
                
                differences = 0
                for word in shared_words:
                    if speaker1.lexicon[word] != speaker2.lexicon[word]:
                        differences += 1
                
                divergences[(speaker1.id, speaker2.id)] = differences / len(shared_words)
        
        return divergences


def create_test_lexicon() -> Dict[str, List[Phoneme]]:
    """Create a small test lexicon."""
    inv = create_basic_inventory()
    
    return {
        'pater': [inv.get_phoneme(s) for s in 'pater'],
        'mater': [inv.get_phoneme(s) for s in 'mater'],
        'tres': [inv.get_phoneme(s) for s in 'tres'],
        'nepot': [inv.get_phoneme(s) for s in 'nepot'],
        'dens': [inv.get_phoneme(s) for s in 'dens'],
        'ped': [inv.get_phoneme(s) for s in 'ped'],
        'ker': [inv.get_phoneme(s) for s in 'ker'],
        'genu': [inv.get_phoneme(s) for s in 'genu'],
    }


def create_population(size: int, grid_size: float = 10.0) -> Population:
    """Create an initial population with shared language."""
    inventory = create_basic_inventory()
    lexicon = create_test_lexicon()
    
    speakers = []
    for i in range(size):
        position = (random.uniform(0, grid_size), random.uniform(0, grid_size))
        speaker = Speaker(
            id=i,
            inventory=inventory.copy(),
            lexicon={word: phones.copy() for word, phones in lexicon.items()},
            position=position,
            prestige=random.uniform(0.8, 1.2)
        )
        speakers.append(speaker)
    
    return Population(speakers=speakers)


def run_simulation(generations: int = 10, population_size: int = 20):
    """Run the phonological drift simulation."""
    print("=== Phonological Drift Simulation ===\n")
    
    # Create initial population
    pop = create_population(population_size)
    print(f"Initial population: {population_size} speakers")
    print(f"Initial inventory: {pop.speakers[0].inventory}")
    print(f"Initial lexicon size: {len(pop.speakers[0].lexicon)} words\n")
    
    # Define some sound changes (inspired by Grimm's Law and others)
    inv = create_basic_inventory()
    
    # p > f (voiceless stop > fricative)
    p_to_f = Phoneme('f', {'consonant', 'fricative', 'voiceless', 'labial'})
    change1 = SoundChange('p_to_f', inv.get_phoneme('p'), p_to_f, probability=0.8)
    
    # t > θ
    t_to_th = Phoneme('θ', {'consonant', 'fricative', 'voiceless', 'dental'})
    change2 = SoundChange('t_to_th', inv.get_phoneme('t'), t_to_th, probability=0.7)
    
    # k > h (velar weakening)
    change3 = SoundChange('k_to_h', inv.get_phoneme('k'), inv.get_phoneme('h'), probability=0.6)
    
    print("Introducing sound changes:")
    print("  1. p → f (labial stop to fricative)")
    print("  2. t → θ (dental stop to fricative)")
    print("  3. k → h (velar weakening)\n")
    
    # Introduce changes at different times
    pop.introduce_sound_change(change1, initial_speakers=3)
    
    # Run simulation
    for gen in range(generations):
        if gen == 3:
            pop.introduce_sound_change(change2, initial_speakers=2)
        if gen == 6:
            pop.introduce_sound_change(change3, initial_speakers=2)
        
        pop.step_generation()
        
        if gen % 3 == 0:
            lex_div = pop.compute_lexical_divergence()
            avg_div = sum(lex_div.values()) / len(lex_div) if lex_div else 0
            print(f"Generation {gen}: Average lexical divergence = {avg_div:.3f}")
    
    print(f"\n=== After {generations} Generations ===\n")
    
    # Show sample words from different speakers
    sample_speakers = random.sample(pop.speakers, min(5, len(pop.speakers)))
    test_words = ['pater', 'tres', 'ker']
    
    print("Sample pronunciations across speakers:")
    for word in test_words:
        print(f"\n'{word}':")
        for speaker in sample_speakers:
            pronunciation = ''.join(p.symbol for p in speaker.lexicon[word])
            print(f"  Speaker {speaker.id} (position {speaker.position[0]:.1f},{speaker.position[1]:.1f}): {pronunciation}")
    
    # Compute final divergence
    lex_div = pop.compute_lexical_divergence()
    avg_div = sum(lex_div.values()) / len(lex_div) if lex_div else 0
    max_div = max(lex_div.values()) if lex_div else 0
    
    print(f"\nFinal statistics:")
    print(f"  Average lexical divergence: {avg_div:.3f}")
    print(f"  Maximum lexical divergence: {max_div:.3f}")
    print(f"  Number of sound changes: {len(pop.sound_changes)}")


if __name__ == '__main__':
    run_simulation(generations=15, population_size=25)
