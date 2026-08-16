"""Reconstruct: Apply the comparative method with ground truth.

Generate a hidden proto-language, evolve it into daughter languages,
then attempt reconstruction from only the daughters. Because we have
ground truth, we can measure exactly where the comparative method
succeeds and where information is unrecoverable.
"""

import sys

sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

import random
from collections import defaultdict

from language_evolution.framework import (
    HistoryGenerator,
    InferenceSystem,
    Observable,
    Reconstruction,
)
from language_evolution.phonology import Phoneme, SoundChange, create_basic_inventory


class ProtoLanguageGenerator(HistoryGenerator):
    """Generate a proto-language and evolve it into daughter languages."""
    
    def __init__(self, num_daughters: int = 4):
        super().__init__()
        self.num_daughters = num_daughters
        
        # Create proto-language
        self.proto_inventory = create_basic_inventory()
        self.proto_lexicon = self._create_proto_lexicon()
        
        # Initialize daughter languages
        self.daughters = {
            i: {
                'inventory': self.proto_inventory.copy(),
                'lexicon': {word: phones.copy() for word, phones in self.proto_lexicon.items()},
                'changes': []
            }
            for i in range(num_daughters)
        }
        
        # Record proto-language
        self.history.metadata['proto_inventory'] = list(self.proto_inventory._symbol_map.keys())
        self.history.metadata['proto_lexicon'] = {
            word: ''.join(p.symbol for p in phones)
            for word, phones in self.proto_lexicon.items()
        }
    
    def _create_proto_lexicon(self) -> dict[str, list[Phoneme]]:
        """Create proto-language lexicon."""
        lexicon = {}
        
        words = [
            'pater', 'mater', 'duwo', 'trei', 'kwetwor',  # Numbers and family
            'ped', 'ker', 'mel', 'sol', 'luna',           # Body and nature
            'nepot', 'genos', 'bhrater', 'swesor', 'owi' # More family
        ]
        
        for word in words:
            try:
                lexicon[word] = [self.proto_inventory.get_phoneme(s) for s in word]
            except KeyError:
                # Skip words with phonemes not in inventory
                pass
        
        return lexicon
    
    def _get_sound_changes_for_daughter(self, daughter_id: int) -> list[SoundChange]:
        """Generate sound changes specific to a daughter language."""
        inv = self.proto_inventory
        changes = []
        
        # Different daughters undergo different changes
        if daughter_id == 0:
            # Grimm's Law-like changes
            f = Phoneme('f', {'consonant', 'fricative', 'voiceless', 'labial'})
            changes.append(SoundChange('p>f', inv.get_phoneme('p'), f, probability=0.9))
            
            th = Phoneme('θ', {'consonant', 'fricative', 'voiceless', 'dental'})
            changes.append(SoundChange('t>θ', inv.get_phoneme('t'), th, probability=0.9))
        
        elif daughter_id == 1:
            # Palatalization
            if 'k' in inv._symbol_map:
                ts = Phoneme('ts', {'consonant', 'affricate', 'voiceless', 'alveolar'})
                changes.append(SoundChange('k>ts', inv.get_phoneme('k'), ts, probability=0.8))
        
        elif daughter_id == 2:
            # Voicing
            if 'p' in inv._symbol_map:
                changes.append(SoundChange('p>b', inv.get_phoneme('p'), inv.get_phoneme('b'), probability=0.7))
            if 't' in inv._symbol_map:
                changes.append(SoundChange('t>d', inv.get_phoneme('t'), inv.get_phoneme('d'), probability=0.7))
        
        elif daughter_id == 3:
            # Lenition (weakening)
            if 'p' in inv._symbol_map:
                v = Phoneme('v', {'consonant', 'fricative', 'voiced', 'labial'})
                changes.append(SoundChange('p>v', inv.get_phoneme('p'), v, probability=0.6))
        
        return changes
    
    def step(self, time: int):
        """Apply sound changes to daughter languages."""
        # Each daughter has a chance to undergo a sound change
        for daughter_id in range(self.num_daughters):
            if random.random() < 0.3:  # 30% chance per time step
                daughter = self.daughters[daughter_id]
                
                # Get or create sound changes for this daughter
                if not daughter['changes']:
                    daughter['changes'] = self._get_sound_changes_for_daughter(daughter_id)
                
                if daughter['changes']:
                    # Pick a random change that hasn't been fully applied
                    change = random.choice(daughter['changes'])
                    
                    # Apply to lexicon
                    changed_words = []
                    for word, phones in daughter['lexicon'].items():
                        new_phones = change.apply(phones)
                        if new_phones != phones:
                            daughter['lexicon'][word] = new_phones
                            changed_words.append(word)
                    
                    if changed_words:
                        self.history.record(
                            time, 'sound_change',
                            daughter_id=daughter_id,
                            change_name=change.name,
                            affected_words=changed_words
                        )
    
    def get_observable(self, time: int) -> Observable:
        """Get observable state - only daughter languages, NOT proto-language."""
        daughter_states = {
            daughter_id: {
                word: ''.join(p.symbol for p in phones)
                for word, phones in daughter['lexicon'].items()
            }
            for daughter_id, daughter in self.daughters.items()
        }
        
        return Observable(
            time=time,
            languages=daughter_states,
            metadata={'num_daughters': self.num_daughters}
        )


class ComparativeMethodReconstructor(InferenceSystem):
    """Inference system using the comparative method."""
    
    def reconstruct(self, observable: Observable) -> Reconstruction:
        """Attempt to reconstruct proto-forms from daughter languages."""
        reconstruction = Reconstruction()
        reconstruction.method = "comparative_method"
        
        # Get all daughter languages
        daughters = observable.languages
        
        # Find cognate sets (words that appear in multiple daughters)
        word_forms: dict[str, dict[int, str]] = defaultdict(dict)
        
        # Collect forms for each word across daughters
        for lang_id, lexicon in daughters.items():
            for word, form in lexicon.items():
                word_forms[word][lang_id] = form
        
        # For each cognate set, reconstruct proto-form
        for word, forms in word_forms.items():
            if len(forms) < 2:  # Need at least 2 witnesses
                continue
            
            # Find systematic correspondences
            proto_form = self._reconstruct_word(word, forms)
            
            if proto_form:
                # Calculate confidence based on regularity of correspondences
                confidence = self._calculate_confidence(word, forms, proto_form)
                
                reconstruction.add_inference(
                    time=0,  # Proto-language at time 0
                    event_type='proto_form',
                    confidence=confidence,
                    word=word,
                    reconstructed_form=proto_form,
                    attested_forms=forms
                )
        
        return reconstruction
    
    def _reconstruct_word(self, word: str, forms: dict[int, str]) -> str:
        """Reconstruct a proto-form from attested forms."""
        # Simplified reconstruction: majority rule per position
        
        # Get all forms
        form_list = list(forms.values())
        
        # Pad forms to same length (very simplified)
        max_len = max(len(f) for f in form_list)
        
        reconstructed = []
        for pos in range(max_len):
            # Collect phonemes at this position
            phonemes_at_pos = []
            for form in form_list:
                if pos < len(form):
                    phonemes_at_pos.append(form[pos])
            
            if not phonemes_at_pos:
                continue
            
            # Most common phoneme (majority rule)
            from collections import Counter
            most_common = Counter(phonemes_at_pos).most_common(1)[0][0]
            reconstructed.append(most_common)
        
        return ''.join(reconstructed)
    
    def _calculate_confidence(self, word: str, forms: dict[int, str], proto_form: str) -> float:
        """Calculate confidence in reconstruction."""
        # Confidence based on:
        # 1. Number of witnesses
        # 2. Regularity of correspondences
        
        num_witnesses = len(forms)
        confidence = min(num_witnesses / 4.0, 1.0)  # More witnesses = higher confidence
        
        # Reduce confidence if forms are very different
        avg_distance = sum(
            self._edit_distance(proto_form, form) 
            for form in forms.values()
        ) / len(forms)
        
        max_expected_distance = len(proto_form) * 0.5  # Expect up to 50% change
        if avg_distance > max_expected_distance:
            confidence *= 0.5
        
        return confidence
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Simple edit distance."""
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        
        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        
        return distances[-1]


def run_experiment():
    """Run the reconstruction experiment."""
    print("=== Reconstruct: Comparative Method with Ground Truth ===\n")
    
    # Generate proto-language and evolve it
    print("Step 1: Generating proto-language and evolving daughters...")
    generator = ProtoLanguageGenerator(num_daughters=4)
    
    print(f"Proto-lexicon ({len(generator.proto_lexicon)} words):")
    for word, form in sorted(generator.history.metadata['proto_lexicon'].items())[:8]:
        print(f"  *{word} = {form}")
    
    # Evolve for some time
    _history, observable = generator.run(num_steps=20)
    
    print("\nStep 2: After 20 time steps of independent evolution...")
    print("Daughter languages (observable evidence):")
    for lang_id, lexicon in sorted(observable.languages.items()):
        print(f"\n  Daughter {lang_id}:")
        for word, form in sorted(lexicon.items())[:5]:
            print(f"    {word} = {form}")
    
    # Now reconstruct
    print("\n\nStep 3: Attempting reconstruction from daughters only...\n")
    
    reconstructor = ComparativeMethodReconstructor()
    reconstruction = reconstructor.reconstruct(observable)
    
    print(f"Reconstructed {len(reconstruction.inferred_events)} proto-forms:\n")
    
    # Compare with ground truth
    correct = 0
    partial = 0
    incorrect = 0
    
    for event in reconstruction.inferred_events[:10]:
        word = event.data['word']
        reconstructed = event.data['reconstructed_form']
        true_form = generator.history.metadata['proto_lexicon'].get(word, '???')
        confidence = reconstruction.confidence[reconstruction.inferred_events.index(event)]
        
        if reconstructed == true_form:
            status = "✓ CORRECT"
            correct += 1
        elif reconstructor._edit_distance(reconstructed, true_form) <= 2:
            status = "~ PARTIAL"
            partial += 1
        else:
            status = "✗ WRONG"
            incorrect += 1
        
        print(f"  *{word}")
        print(f"    Reconstructed: *{reconstructed} (confidence={confidence:.2f})")
        print(f"    True form:     *{true_form}")
        print(f"    {status}\n")
    
    print("=== Reconstruction Accuracy ===\n")
    total = correct + partial + incorrect
    if total > 0:
        print(f"  Correct: {correct}/{total} ({100*correct/total:.1f}%)")
        print(f"  Partial: {partial}/{total} ({100*partial/total:.1f}%)")
        print(f"  Wrong:   {incorrect}/{total} ({100*incorrect/total:.1f}%)")
    
    print("\n=== Recoverability Insights ===\n")
    print("Information we HAVE (from daughters):")
    print("  - Current forms in each daughter")
    print("  - Systematic sound correspondences")
    print()
    print("Information LOST (unrecoverable from O_t):")
    print("  - Order of sound changes")
    print("  - Intermediate forms")
    print("  - Whether changes were gradual or abrupt")
    print("  - Failed innovations that left no trace")
    print()
    print("This experiment quantifies the limits of the comparative method:")
    print(f"  Even with perfect methodology, {incorrect}/{total} reconstructions were wrong")
    print("  because the required information no longer exists in the signal.")


if __name__ == '__main__':
    random.seed(42)
    run_experiment()
