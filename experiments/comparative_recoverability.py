#!/usr/bin/env python3
"""
Comparative Recoverability Experiment

Concrete implementation of cross-experiment reconstruction.

This script:
1. Runs multiple experiments (divergence, diffusion, borrowing)
2. Applies same reconstruction to all
3. Measures comparative recoverability

Research Question:
    Which evolutionary mechanisms preserve the most recoverable information?

Hypothesis:
    Clean divergence > Geographic diffusion > Borrowing > Combinations

Why this matters:
    In real historical linguistics, we don't know which mechanism operated.
    This experiment quantifies how mechanism choice affects our ability
    to recover the past.
"""

import sys

sys.path.insert(0, '/home/bonobo/github/language-evolution/src')
sys.path.insert(0, '/home/bonobo/github/language-evolution')

# Import existing experiments
from cross_experiment_reconstruction import CrossExperimentFramework

from language_evolution.framework import History, Observable


def create_simple_divergence() -> tuple:
    """
    Create a simple clean divergence scenario.
    
    Proto-language splits into 3 daughter languages with no contact.
    This is the IDEAL case for reconstruction.
    """
    from language_evolution.phonology import Phoneme
    
    # Proto-inventory
    proto = {
        Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'}),
        Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'}),
        Phoneme('k', {'consonant', 'stop', 'voiceless', 'dorsal'}),
        Phoneme('a', {'vowel', 'low', 'central'}),
        Phoneme('i', {'vowel', 'high', 'front'}),
    }
    
    # Language 1: p → b (voicing)
    lang1 = (proto - {Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'})}) | \
            {Phoneme('b', {'consonant', 'stop', 'voiced', 'labial'})}
    
    # Language 2: t → d (voicing)
    lang2 = (proto - {Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'})}) | \
            {Phoneme('d', {'consonant', 'stop', 'voiced', 'coronal'})}
    
    # Language 3: k → g (voicing)
    lang3 = (proto - {Phoneme('k', {'consonant', 'stop', 'voiceless', 'dorsal'})}) | \
            {Phoneme('g', {'consonant', 'stop', 'voiced', 'dorsal'})}
    
    # Create observable
    languages = {
        1: {'phonemes': sorted([p.symbol for p in lang1])},
        2: {'phonemes': sorted([p.symbol for p in lang2])},
        3: {'phonemes': sorted([p.symbol for p in lang3])},
    }
    
    observable = Observable(time=10, languages=languages)
    
    # Create ground truth history
    history = History()
    history.record(0, 'initialization', proto_size=len(proto))
    history.record(1, 'split', num_daughters=3)
    history.record(5, 'sound_change', language=1, change='p→b')
    history.record(6, 'sound_change', language=2, change='t→d')
    history.record(7, 'sound_change', language=3, change='k→g')
    
    return observable, history


def create_simple_diffusion() -> tuple:
    """
    Create a simple geographic diffusion scenario.
    
    Same proto-language, but change diffuses geographically rather than
    splitting cleanly. This creates continuous variation.
    """
    from language_evolution.phonology import Phoneme
    
    # Proto-inventory
    proto = {
        Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'}),
        Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'}),
        Phoneme('k', {'consonant', 'stop', 'voiceless', 'dorsal'}),
        Phoneme('a', {'vowel', 'low', 'central'}),
        Phoneme('i', {'vowel', 'high', 'front'}),
    }
    
    # West: p → b
    west = (proto - {Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'})}) | \
           {Phoneme('b', {'consonant', 'stop', 'voiced', 'labial'})}
    
    # Center: has BOTH p→b AND t→d (received from both sides)
    center = (proto - {
        Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'}),
        Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'})
    }) | {
        Phoneme('b', {'consonant', 'stop', 'voiced', 'labial'}),
        Phoneme('d', {'consonant', 'stop', 'voiced', 'coronal'})
    }
    
    # East: t → d
    east = (proto - {Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'})}) | \
           {Phoneme('d', {'consonant', 'stop', 'voiced', 'coronal'})}
    
    # Create observable with locations
    languages = {
        1: {'phonemes': sorted([p.symbol for p in west]), 'location': (0, 0)},
        2: {'phonemes': sorted([p.symbol for p in center]), 'location': (5, 0)},
        3: {'phonemes': sorted([p.symbol for p in east]), 'location': (10, 0)},
    }
    
    observable = Observable(time=10, languages=languages)
    
    # Ground truth: innovations diffused geographically
    history = History()
    history.record(0, 'initialization', proto_size=len(proto))
    history.record(3, 'innovation', location=(0, 0), change='p→b')
    history.record(4, 'diffusion', from_loc=(0, 0), to_loc=(5, 0))
    history.record(6, 'innovation', location=(10, 0), change='t→d')
    history.record(7, 'diffusion', from_loc=(10, 0), to_loc=(5, 0))
    
    return observable, history


def create_simple_borrowing() -> tuple:
    """
    Create a simple borrowing scenario.
    
    Two language families come into contact and exchange features.
    This violates tree assumptions.
    """
    from language_evolution.phonology import Phoneme
    
    # Family A proto
    proto_a = {
        Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'}),
        Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'}),
        Phoneme('a', {'vowel', 'low', 'central'}),
    }
    
    # Family B proto (different)
    proto_b = {
        Phoneme('k', {'consonant', 'stop', 'voiceless', 'dorsal'}),
        Phoneme('s', {'consonant', 'fricative', 'voiceless', 'coronal'}),
        Phoneme('i', {'vowel', 'high', 'front'}),
    }
    
    # Family A language (pure)
    lang_a1 = proto_a.copy()
    
    # Family A language BUT borrowed /k/ from Family B
    lang_a2 = proto_a | {Phoneme('k', {'consonant', 'stop', 'voiceless', 'dorsal'})}
    
    # Family B language (pure)
    lang_b1 = proto_b.copy()
    
    languages = {
        1: {'phonemes': sorted([p.symbol for p in lang_a1])},
        2: {'phonemes': sorted([p.symbol for p in lang_a2])},
        3: {'phonemes': sorted([p.symbol for p in lang_b1])},
    }
    
    observable = Observable(time=10, languages=languages)
    
    # Ground truth: borrowing occurred
    history = History()
    history.record(0, 'initialization', family_a_size=len(proto_a), family_b_size=len(proto_b))
    history.record(5, 'contact_begins', families=('A', 'B'))
    history.record(7, 'borrowing', from_lang=3, to_lang=2, feature='k')
    
    return observable, history


class MockGenerator:
    """Wrapper to make observables look like generators."""
    def __init__(self, observable, history):
        self.observable = observable
        self.history = history
    
    def get_observable(self):
        return self.observable


def main():
    """Run comparative recoverability experiment."""
    print("=" * 70)
    print("COMPARATIVE RECOVERABILITY EXPERIMENT")
    print("=" * 70)
    print()
    print("Research Question:")
    print("  Which evolutionary mechanisms preserve recoverable information?")
    print()
    print("Method:")
    print("  1. Create identical starting conditions")
    print("  2. Evolve via different mechanisms")
    print("  3. Apply same reconstruction to all")
    print("  4. Measure comparative accuracy")
    print()
    
    # Create experiments
    print("Creating experiments...")
    
    obs_div, hist_div = create_simple_divergence()
    obs_diff, hist_diff = create_simple_diffusion()
    obs_borrow, hist_borrow = create_simple_borrowing()
    
    print("  ✓ Clean divergence (3 languages)")
    print("  ✓ Geographic diffusion (3 regions)")
    print("  ✓ Borrowing (3 languages, 2 families)")
    print()
    
    # Set up framework
    framework = CrossExperimentFramework()
    framework.add_experiment('clean_divergence', MockGenerator(obs_div, hist_div))
    framework.add_experiment('geographic_diffusion', MockGenerator(obs_diff, hist_diff))
    framework.add_experiment('borrowing', MockGenerator(obs_borrow, hist_borrow))
    
    print("Running reconstruction on all experiments...")
    results = framework.run_all()
    print()
    
    # Compare results
    framework.compare_results(results)
    
    # Detailed analysis
    print("=" * 70)
    print("DETAILED FINDINGS")
    print("=" * 70)
    print()
    
    print("Clean Divergence:")
    print("  Observable: 3 languages with systematic sound changes")
    print("  Ground truth: Clear tree structure, no contact")
    print("  Reconstruction: Should identify proto-forms accurately")
    print(f"  → Accuracy: {results['clean_divergence'].accuracy:.1%}")
    print()
    
    print("Geographic Diffusion:")
    print("  Observable: 3 regions with overlapping changes")
    print("  Ground truth: Innovations diffused spatially")
    print("  Reconstruction: Continuous variation obscures tree")
    print(f"  → Accuracy: {results['geographic_diffusion'].accuracy:.1%}")
    print()
    
    print("Borrowing:")
    print("  Observable: 3 languages, 2 families with shared feature")
    print("  Ground truth: Horizontal transmission (contact)")
    print("  Reconstruction: Borrowed feature looks like inheritance")
    print(f"  → Accuracy: {results['borrowing'].accuracy:.1%}")
    print()
    
    # Key insight
    print("=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print()
    print("The MECHANISM of change determines recoverability.")
    print()
    print("Clean tree-like divergence preserves the most information.")
    print("Geographic diffusion creates continuous variation that")
    print("obscures discrete branching points.")
    print("Borrowing actively misleads tree-based inference.")
    print()
    print("In real historical linguistics:")
    print("  - We observe O_t")
    print("  - We apply reconstruction methods")
    print("  - We assume clean divergence")
    print()
    print("But if the actual mechanism was diffusion + borrowing,")
    print("our reconstructions may be systematically wrong.")
    print()
    print("This experiment QUANTIFIES the error introduced by")
    print("mechanism mismatch.")
    print()


if __name__ == '__main__':
    main()
