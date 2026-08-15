"""Lexical Natural Selection: Word competition model.

Give synonymous forms properties like length, articulatory cost, regularity,
prestige, memorability, ambiguity, and frequency. Let a population repeatedly
communicate and watch which variants survive. Survival emerges from interactions
among constraints, not from a single "fitness" score.
"""

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from language_evolution.framework import History, Observable, HistoryGenerator
from dataclasses import dataclass
from typing import List, Dict, Set
import random
import math


@dataclass
class WordVariant:
    """A competing variant for expressing a meaning."""
    form: str
    length: int  # Number of phonemes/characters
    articulatory_cost: float  # Effort to produce (0-1, lower is easier)
    regularity: float  # How well it fits morphological patterns (0-1)
    prestige: float  # Social prestige (0-1)
    memorability: float  # Ease of learning (0-1, higher is easier)
    ambiguity: float  # Potential for confusion (0-1, lower is better)
    frequency: int = 0  # Usage count
    
    def __repr__(self):
        return f"{self.form} (len={self.length}, cost={self.articulatory_cost:.2f}, freq={self.frequency})"


@dataclass
class Meaning:
    """A meaning that can be expressed by competing variants."""
    concept: str
    variants: List[WordVariant]
    
    def get_variant_probabilities(self, context: str = 'neutral') -> List[float]:
        """Calculate selection probabilities based on multiple constraints."""
        if not self.variants:
            return []
        
        scores = []
        for variant in self.variants:
            # Base score from frequency (success breeds success)
            freq_score = math.log(variant.frequency + 1) / math.log(max(v.frequency for v in self.variants) + 2)
            
            # Length penalty (shorter is better in most contexts)
            length_score = 1.0 / (1.0 + variant.length / 5.0)
            
            # Articulatory ease
            ease_score = 1.0 - variant.articulatory_cost
            
            # Context-dependent factors
            if context == 'formal':
                # Formal contexts favor prestige and regularity
                context_score = (variant.prestige * 0.6 + variant.regularity * 0.4)
            elif context == 'informal':
                # Informal contexts favor brevity and ease
                context_score = (length_score * 0.5 + ease_score * 0.5)
            else:
                # Neutral context balances factors
                context_score = (variant.prestige * 0.3 + length_score * 0.3 + ease_score * 0.2 + variant.memorability * 0.2)
            
            # Ambiguity penalty
            clarity_score = 1.0 - variant.ambiguity
            
            # Combined score (no single "fitness" - emergent from interactions)
            score = (
                freq_score * 0.3 +
                length_score * 0.2 +
                ease_score * 0.15 +
                context_score * 0.2 +
                clarity_score * 0.15
            )
            
            scores.append(max(score, 0.01))  # Ensure non-zero probability
        
        # Normalize to probabilities
        total = sum(scores)
        return [s / total for s in scores]
    
    def select_variant(self, context: str = 'neutral') -> WordVariant:
        """Select a variant probabilistically."""
        probs = self.get_variant_probabilities(context)
        return random.choices(self.variants, weights=probs)[0]


class LexicalSelectionSimulator(HistoryGenerator):
    """Simulates lexical competition and survival."""
    
    def __init__(self, meanings: List[Meaning]):
        super().__init__()
        self.meanings = {m.concept: m for m in meanings}
        
        # Record initial state
        self.history.metadata['initial_variants'] = {
            concept: [v.form for v in meaning.variants]
            for concept, meaning in self.meanings.items()
        }
    
    def step(self, time: int):
        """Simulate one time step of usage."""
        # Generate communicative events
        num_events = random.randint(20, 40)
        
        for _ in range(num_events):
            # Choose a meaning to express
            concept = random.choice(list(self.meanings.keys()))
            meaning = self.meanings[concept]
            
            # Choose context
            context = random.choices(
                ['neutral', 'formal', 'informal'],
                weights=[0.6, 0.2, 0.2]
            )[0]
            
            # Select variant
            variant = meaning.select_variant(context)
            variant.frequency += 1
            
            # Record if this is first use or a significant frequency milestone
            if variant.frequency == 1:
                self.history.record(
                    time, 'first_use',
                    concept=concept,
                    variant=variant.form,
                    context=context
                )
            elif variant.frequency % 100 == 0:
                self.history.record(
                    time, 'milestone',
                    concept=concept,
                    variant=variant.form,
                    frequency=variant.frequency
                )
        
        # Check for extinction (variants that fall too far behind)
        for meaning in self.meanings.values():
            if len(meaning.variants) <= 1:
                continue
            
            total_freq = sum(v.frequency for v in meaning.variants)
            if total_freq < 50:  # Too early to judge
                continue
            
            to_remove = []
            for variant in meaning.variants:
                proportion = variant.frequency / total_freq if total_freq > 0 else 0
                
                # Variant goes extinct if used less than 5% of the time after enough exposure
                if proportion < 0.05 and total_freq > 100:
                    to_remove.append(variant)
            
            for variant in to_remove:
                self.history.record(
                    time, 'extinction',
                    concept=meaning.concept,
                    variant=variant.form,
                    final_frequency=variant.frequency,
                    proportion=variant.frequency / total_freq
                )
                meaning.variants.remove(variant)
    
    def get_observable(self, time: int) -> Observable:
        """Extract observable state."""
        language_state = {
            concept: {
                'variants': [v.form for v in meaning.variants],
                'frequencies': {v.form: v.frequency for v in meaning.variants}
            }
            for concept, meaning in self.meanings.items()
        }
        
        return Observable(
            time=time,
            languages={0: language_state},
            metadata={'num_meanings': len(self.meanings)}
        )


def create_test_lexicon() -> List[Meaning]:
    """Create a lexicon with competing variants."""
    meanings = []
    
    # "father" - competing forms
    meanings.append(Meaning(
        'father',
        [
            WordVariant('pater', 5, 0.4, 0.9, 0.7, 0.6, 0.1),  # Classical, prestigious
            WordVariant('papa', 4, 0.2, 0.6, 0.3, 0.9, 0.2),   # Informal, easy
            WordVariant('pa', 2, 0.1, 0.3, 0.2, 0.95, 0.3),    # Very short, ambiguous
        ]
    ))
    
    # "mother"
    meanings.append(Meaning(
        'mother',
        [
            WordVariant('mater', 5, 0.4, 0.9, 0.7, 0.6, 0.1),
            WordVariant('mama', 4, 0.2, 0.6, 0.3, 0.9, 0.2),
            WordVariant('ma', 2, 0.1, 0.3, 0.2, 0.95, 0.3),
        ]
    ))
    
    # "water"
    meanings.append(Meaning(
        'water',
        [
            WordVariant('aqua', 4, 0.5, 0.8, 0.8, 0.5, 0.1),   # Learned, prestigious
            WordVariant('water', 5, 0.3, 0.7, 0.5, 0.7, 0.15),  # Common
            WordVariant('wasser', 6, 0.4, 0.6, 0.4, 0.6, 0.2),  # Alternative
        ]
    ))
    
    # "good"
    meanings.append(Meaning(
        'good',
        [
            WordVariant('bonus', 5, 0.4, 0.9, 0.7, 0.6, 0.1),
            WordVariant('gut', 3, 0.2, 0.5, 0.4, 0.8, 0.2),
            WordVariant('bien', 4, 0.3, 0.6, 0.5, 0.7, 0.15),
        ]
    ))
    
    return meanings


def run_simulation(steps: int = 100):
    """Run the lexical selection simulation."""
    print("=== Lexical Natural Selection ===\n")
    
    meanings = create_test_lexicon()
    
    print(f"Initial lexicon: {len(meanings)} meanings with competing variants\n")
    
    for meaning in meanings:
        print(f"{meaning.concept}:")
        for variant in meaning.variants:
            print(f"  - {variant.form}: len={variant.length}, cost={variant.articulatory_cost:.2f}, "
                  f"prestige={variant.prestige:.2f}, memorability={variant.memorability:.2f}")
    
    # Create simulator
    sim = LexicalSelectionSimulator(meanings)
    
    print(f"\nRunning {steps} time steps of communicative selection...\n")
    
    # Run simulation
    history, observable = sim.run(steps)
    
    print(f"=== After {steps} Time Steps ===\n")
    
    # Show results
    for concept, meaning in sorted(sim.meanings.items()):
        print(f"{concept}:")
        if not meaning.variants:
            print(f"  (all variants extinct!)")
            continue
        
        total = sum(v.frequency for v in meaning.variants)
        variants_sorted = sorted(meaning.variants, key=lambda v: -v.frequency)
        
        for variant in variants_sorted:
            proportion = variant.frequency / total if total > 0 else 0
            print(f"  - {variant.form}: {variant.frequency} uses ({proportion*100:.1f}%)")
        
        if len(meaning.variants) < len(history.metadata['initial_variants'][concept]):
            extinct = set(history.metadata['initial_variants'][concept]) - set(v.form for v in meaning.variants)
            print(f"    Extinct: {', '.join(extinct)}")
        print()
    
    # Show extinction events
    extinctions = [e for e in history.events if e.event_type == 'extinction']
    if extinctions:
        print(f"=== Extinction Events ({len(extinctions)}) ===\n")
        for event in extinctions:
            concept = event.data['concept']
            variant = event.data['variant']
            freq = event.data['final_frequency']
            prop = event.data['proportion']
            print(f"  t={event.time}: '{variant}' ({concept}) went extinct at {freq} uses ({prop*100:.1f}%)")
    
    print(f"\n=== Recoverability Analysis ===\n")
    print("From observable O_t, we see:")
    print("  - Which variants currently exist")
    print("  - Their relative frequencies")
    print()
    print("What we CANNOT recover:")
    print("  - Why variants succeeded or failed")
    print("  - Whether success was due to length, prestige, ease, or random drift")
    print("  - Timing: did winner emerge early or late?")
    print("  - Extinct variants leave no trace")
    print()
    print("Example: Two histories could produce same winner:")
    print("  H₁: 'papa' dominated from start (high memorability)")
    print("  H₂: 'pater' led initially, then 'papa' overtook (prestige → ease shift)")
    print("  → Identical O_t, different selective pressures")


if __name__ == '__main__':
    random.seed(42)
    run_simulation(steps=150)
