"""Recoverability demonstration: measuring what's lost to history.

This experiment generates multiple evolution histories and measures which
distinctions remain observable vs become genuinely unrecoverable.
"""

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from language_evolution.framework import (
    History, Observable, HistoryGenerator, compare_histories,
    measure_observable_distance, RecoverabilityAnalysis
)
from language_evolution.phonology import Phoneme, SoundChange, create_basic_inventory
from typing import Dict, List
import random


class SimplePhonologicalGenerator(HistoryGenerator):
    """Simplified phonological evolution for recoverability testing."""
    
    def __init__(self, seed: int = None):
        super().__init__()
        if seed is not None:
            random.seed(seed)
        
        self.inventory = create_basic_inventory()
        self.words = {
            'word1': [self.inventory.get_phoneme(s) for s in 'pater'],
            'word2': [self.inventory.get_phoneme(s) for s in 'mater'],
            'word3': [self.inventory.get_phoneme(s) for s in 'tres'],
        }
        self.applied_changes: List[SoundChange] = []
    
    def step(self, time: int):
        """Apply random sound changes."""
        # Occasionally apply a sound change
        if random.random() < 0.3:
            # Choose a random sound change
            changes = self._get_possible_changes()
            if changes:
                change = random.choice(changes)
                self.applied_changes.append(change)
                
                # Apply to lexicon
                for word_id in self.words:
                    self.words[word_id] = change.apply(self.words[word_id])
                
                # Record to history
                self.history.record(
                    time, 'sound_change',
                    data={
                        'change': change.name,
                        'source': change.source.symbol,
                        'target': change.target.symbol
                    }
                )
    
    def _get_possible_changes(self) -> List[SoundChange]:
        """Get possible sound changes."""
        inv = self.inventory
        changes = []
        
        # Some basic changes
        if 'p' in [p.symbol for p in inv.phonemes]:
            f = Phoneme('f', {'consonant', 'fricative', 'voiceless', 'labial'})
            changes.append(SoundChange('p>f', inv.get_phoneme('p'), f))
        
        if 't' in [p.symbol for p in inv.phonemes]:
            th = Phoneme('θ', {'consonant', 'fricative', 'voiceless', 'dental'})
            changes.append(SoundChange('t>θ', inv.get_phoneme('t'), th))
        
        if 'k' in [p.symbol for p in inv.phonemes]:
            changes.append(SoundChange('k>h', inv.get_phoneme('k'), inv.get_phoneme('h')))
        
        return changes
    
    def get_observable(self, time: int) -> Observable:
        """Get observable state (just the current words)."""
        # Observable only contains current word forms, not the history
        language_state = {
            word_id: ''.join(p.symbol for p in phonemes)
            for word_id, phonemes in self.words.items()
        }
        
        return Observable(
            time=time,
            languages={0: language_state},
            metadata={'num_changes': len(self.applied_changes)}
        )


def run_recoverability_experiment():
    """Demonstrate recoverability limits."""
    print("=== Recoverability Experiment ===\n")
    print("Question: Can we distinguish different histories from their observable outcomes?\n")
    
    # Generate multiple evolution histories with different random seeds
    num_histories = 10
    num_steps = 20
    
    histories = []
    observables = []
    
    print(f"Generating {num_histories} independent evolution histories...")
    for i in range(num_histories):
        gen = SimplePhonologicalGenerator(seed=i)
        history, observable = gen.run(num_steps)
        histories.append(history)
        observables.append(observable)
        print(f"  History {i}: {len(history)} events → {observable.languages[0]}")
    
    print(f"\n=== Measuring Observational Distance ===\n")
    
    # Find pairs with similar observables but different histories
    indistinguishable = []
    
    for i in range(len(histories)):
        for j in range(i + 1, len(histories)):
            h1, h2 = histories[i], histories[j]
            o1, o2 = observables[i], observables[j]
            
            # Compare observables
            distance = measure_observable_distance(o1, o2)
            
            # Compare histories  
            same_history = (
                len(h1.events) == len(h2.events) and
                all(e1.event_type == e2.event_type and e1.data == e2.data
                    for e1, e2 in zip(h1.events, h2.events))
            )
            
            if distance < 0.2 and not same_history:
                indistinguishable.append((i, j, distance))
                print(f"Histories {i} and {j}: DIFFERENT histories, SIMILAR observables")
                print(f"  Observable distance: {distance:.3f}")
                print(f"  History {i}: {len(h1.events)} events")
                print(f"  History {j}: {len(h2.events)} events")
                print(f"  → These histories are OBSERVATIONALLY INDISTINGUISHABLE")
                print()
    
    if not indistinguishable:
        print("All observable differences correspond to historical differences.")
        print("(Try running with more histories or longer evolution times)")
    
    print(f"\n=== Information Loss Analysis ===\n")
    
    # Analyze which events leave traces
    event_types_seen = set()
    for h in histories:
        for event in h.events:
            event_types_seen.add(event.event_type)
    
    print(f"Event types observed: {event_types_seen}")
    print()
    
    # Count recoverable vs unrecoverable
    print("Recoverability by event type:")
    print("  sound_change: PARTIALLY RECOVERABLE")
    print("    - Final state reflects accumulated changes")
    print("    - But order and timing often lost")
    print("    - Intermediate states erased")
    print()
    
    print("Key insight:")
    print("  When H₁ ≠ H₂ but O_t(H₁) ≈ O_t(H₂), the distinction")
    print("  is not just hard to reconstruct—it's GENUINELY UNRECOVERABLE.")
    print("  The information required to distinguish the histories")
    print("  no longer exists in the observable evidence.")
    
    return histories, observables, indistinguishable


if __name__ == '__main__':
    histories, observables, indistinguishable = run_recoverability_experiment()
    
    if indistinguishable:
        print(f"\n=== Summary ===")
        print(f"Found {len(indistinguishable)} pairs of distinct histories")
        print(f"that produced observationally similar outcomes.")
        print(f"\nThis is the fundamental limit of historical linguistics:")
        print(f"some historical facts are forever unknowable.")
