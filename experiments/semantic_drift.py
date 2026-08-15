"""Semantic Drift Machine: Meaning evolution through usage.

Start with a tiny lexicon whose words occupy overlapping semantic regions.
Usage gradually moves those regions. Reproduce processes resembling narrowing,
broadening, metaphor, metonymy, amelioration, pejoration, bleaching, and
grammaticalization without encoding those categories as outcomes.
"""

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from language_evolution.semantics import SemanticSpace, SemanticVector, create_basic_semantic_space
from language_evolution.framework import History, Observable, HistoryGenerator
from typing import Dict, List, Tuple, Set
import random
from collections import defaultdict


class SemanticDriftSimulator(HistoryGenerator):
    """Simulates semantic change through usage patterns."""
    
    def __init__(self, space: SemanticSpace):
        super().__init__()
        self.space = space
        self.usage_contexts: Dict[str, List[SemanticVector]] = defaultdict(list)
        self.total_usage: Dict[str, int] = defaultdict(int)
        
        # Record initial state
        self.history.metadata['initial_space'] = {
            word: (region.center.dimensions, region.radius, region.label)
            for word, region in space.regions.items()
        }
    
    def use_word(self, word_id: str, context_point: SemanticVector):
        """Use a word in a particular semantic context."""
        if word_id not in self.space.regions:
            return
        
        # Record usage context
        self.usage_contexts[word_id].append(context_point)
        self.total_usage[word_id] += 1
        
        # Words drift toward their contexts of use
        region = self.space.regions[word_id]
        
        # Probabilistic drift - not every usage causes shift
        if random.random() < 0.3:
            # Move slightly toward this usage context
            drift_magnitude = 0.05
            region.center = region.center.move_toward(context_point, drift_magnitude)
    
    def step(self, time: int):
        """Simulate one time step of semantic evolution."""
        
        # Generate communicative events
        num_events = random.randint(5, 15)
        
        for _ in range(num_events):
            # Choose a word to use
            word = random.choice(list(self.space.regions.keys()))
            
            # Generate a context point - usually near the word's current meaning
            # but occasionally extended to new contexts
            region = self.space.regions[word]
            
            if random.random() < 0.8:
                # Normal usage: near current meaning
                context = region.center.add_noise(region.radius * 0.5)
            else:
                # Extended usage: farther from prototypical meaning
                context = region.center.add_noise(region.radius * 2.0)
            
            old_center = region.center
            self.use_word(word, context)
            new_center = region.center
            
            # Record significant shifts
            if old_center.distance_to(new_center) > 0.01:
                self.history.record(
                    time, 'semantic_shift',
                    word=word,
                    from_coord=old_center.dimensions,
                    to_coord=new_center.dimensions,
                    distance=old_center.distance_to(new_center)
                )
        
        # Occasional broadening or narrowing based on usage patterns
        for word in self.space.regions.keys():
            if word not in self.usage_contexts or not self.usage_contexts[word]:
                continue
            
            # Measure variance in usage contexts
            contexts = self.usage_contexts[word]
            if len(contexts) < 3:
                continue
            
            region = self.space.regions[word]
            avg_distance = sum(region.center.distance_to(ctx) for ctx in contexts) / len(contexts)
            
            # High variance → broadening
            if avg_distance > region.radius * 1.5 and random.random() < 0.1:
                old_radius = region.radius
                self.space.broaden_meaning(word, 0.05)
                
                self.history.record(
                    time, 'broadening',
                    word=word,
                    old_radius=old_radius,
                    new_radius=region.radius,
                    reason='diverse_usage'
                )
            
            # Low variance + high frequency → narrowing (specialization)
            elif avg_distance < region.radius * 0.5 and self.total_usage[word] > 20 and random.random() < 0.05:
                old_radius = region.radius
                self.space.narrow_meaning(word, 0.03)
                
                self.history.record(
                    time, 'narrowing',
                    word=word,
                    old_radius=old_radius,
                    new_radius=region.radius,
                    reason='specialized_usage'
                )
        
        # Clear old contexts periodically (memory decay)
        if time % 5 == 0:
            for word in self.usage_contexts:
                if len(self.usage_contexts[word]) > 10:
                    self.usage_contexts[word] = self.usage_contexts[word][-10:]
    
    def get_observable(self, time: int) -> Observable:
        """Extract observable semantic state."""
        # Observable is just current word meanings, not usage history
        language_state = {
            word: {
                'center': region.center.dimensions,
                'radius': region.radius,
                'label': region.label
            }
            for word, region in self.space.regions.items()
        }
        
        return Observable(
            time=time,
            languages={0: language_state},
            metadata={'num_words': len(self.space.regions)}
        )
    
    def classify_change(self, word: str) -> List[str]:
        """Classify what kind of semantic change occurred (post-hoc analysis)."""
        
        if word not in self.history.metadata['initial_space']:
            return []
        
        old_center_tuple, old_radius, old_label = self.history.metadata['initial_space'][word]
        new_region = self.space.regions[word]
        new_center = new_region.center
        new_radius = new_region.radius
        
        old_center = SemanticVector(old_center_tuple)
        
        changes = []
        
        # Measure change
        distance = old_center.distance_to(new_center)
        radius_change = new_radius - old_radius
        
        # Broadening vs narrowing
        if radius_change > 0.1:
            changes.append('BROADENING')
        elif radius_change < -0.1:
            changes.append('NARROWING')
        
        # Drift direction (simplified - would need semantic dimension labels)
        if distance > 0.2:
            # Check which dimension changed most
            dims_old = old_center_tuple
            dims_new = new_center.dimensions
            
            max_change_dim = max(range(len(dims_old)), 
                                key=lambda i: abs(dims_new[i] - dims_old[i]))
            
            if max_change_dim == 0:  # Concrete ↔ Abstract
                if dims_new[0] < dims_old[0]:
                    changes.append('ABSTRACTION')
                else:
                    changes.append('CONCRETIZATION')
            elif max_change_dim == 1:  # Positive ↔ Negative
                if dims_new[1] > dims_old[1]:
                    changes.append('AMELIORATION')
                elif dims_new[1] < dims_old[1]:
                    changes.append('PEJORATION')
        
        # Check for increased overlap (metaphorical extension)
        initial_overlaps = set()
        current_overlaps = set()
        
        for other_word, other_region in self.space.regions.items():
            if other_word == word:
                continue
            
            # Would need to reconstruct initial overlaps properly
            # Simplified for now
            overlap = new_region.overlap_with(other_region)
            if overlap > 0.3:
                current_overlaps.add(other_word)
        
        if len(current_overlaps) > 0:
            changes.append('METAPHOR/EXTENSION')
        
        return changes if changes else ['STABLE']


def run_simulation(steps: int = 50):
    """Run the semantic drift simulation."""
    print("=== Semantic Drift Machine ===\n")
    
    # Create initial semantic space
    space = create_basic_semantic_space()
    
    print(f"Initial lexicon: {len(space.regions)} words")
    print("\nInitial meanings:")
    for word, region in sorted(space.regions.items()):
        print(f"  {word:10} {region.center} r={region.radius:.2f} [{region.label}]")
    
    # Create simulator
    sim = SemanticDriftSimulator(space)
    
    print(f"\nRunning {steps} time steps of usage-driven drift...\n")
    
    # Run simulation
    history, observable = sim.run(steps)
    
    print(f"=== After {steps} Time Steps ===\n")
    
    # Show final meanings
    print("Final meanings:")
    for word, region in sorted(space.regions.items()):
        print(f"  {word:10} {region.center} r={region.radius:.2f}")
    
    # Analyze changes
    print("\n=== Semantic Change Classification ===\n")
    
    for word in sorted(space.regions.keys()):
        change_types = sim.classify_change(word)
        
        old_center_tuple, old_radius, old_label = history.metadata['initial_space'][word]
        new_center = space.regions[word].center
        new_radius = space.regions[word].radius
        
        # old_center_tuple is a tuple of coordinates, convert to vector
        old_center = SemanticVector(old_center_tuple)
        distance = old_center.distance_to(new_center)
        radius_change = new_radius - old_radius
        
        print(f"{word}:")
        print(f"  Drift distance: {distance:.3f}")
        print(f"  Radius change: {radius_change:+.3f}")
        print(f"  Classification: {', '.join(change_types)}")
        print()
    
    # Show event statistics
    print("=== History Statistics ===\n")
    
    event_counts = defaultdict(int)
    for event in history.events:
        event_counts[event.event_type] += 1
    
    print(f"Total events recorded: {len(history.events)}")
    for event_type, count in sorted(event_counts.items()):
        print(f"  {event_type}: {count}")
    
    # Show some example events
    print("\nExample semantic shifts (first 5):")
    shifts = [e for e in history.events if e.event_type == 'semantic_shift'][:5]
    for event in shifts:
        word = event.data['word']
        dist = event.data['distance']
        print(f"  t={event.time}: {word} shifted {dist:.3f} units")
    
    # Demonstrate recoverability issue
    print("\n=== Recoverability Analysis ===\n")
    
    print("From observable O_t (current state), we can see:")
    print(f"  - Current word meanings (centers and radii)")
    print(f"  - Current semantic overlaps")
    print()
    print("What we CANNOT recover from O_t:")
    print(f"  - Order of changes (did narrowing precede drift, or vice versa?)")
    print(f"  - Number of usage events that caused each shift")
    print(f"  - Intermediate semantic states")
    print(f"  - Whether change was gradual or had accelerations/reversals")
    print()
    print("Example: Two words could reach the same final meaning via:")
    print("  H₁: steady drift in one direction")
    print("  H₂: drift away then back, or oscillation")
    print("  → These produce identical O_t but different H")


if __name__ == '__main__':
    random.seed(42)  # For reproducibility
    run_simulation(steps=60)
