"""Phonological Drift → Reconstruct: Complete vertical slice.

This experiment demonstrates the full H → O_t → Ĥ protocol using
Phonological Drift as the history generator and comparative reconstruction
as the inference system.

Research Question:
  Given realistic population-based sound change with geographical and
  prestige effects, how much of the proto-language can be recovered
  from daughter languages alone?
"""

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from language_evolution.framework import compare_histories, RecoverabilityAnalysis
from language_evolution.phonology import Phoneme, SoundChange, create_basic_inventory
from typing import Dict, List, Set
from collections import defaultdict, Counter
import random


# Import from existing experiments
import importlib.util

# Load phonological_drift module
spec = importlib.util.spec_from_file_location(
    "phonological_drift",
    "/home/bonobo/github/language-evolution/experiments/phonological_drift.py"
)
phonological_drift = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phonological_drift)


class PopulationBasedReconstructor:
    """Reconstruct proto-language from geographically distributed daughter languages.
    
    This reconstructor receives only:
    - Current word forms from multiple speakers
    - Geographical positions (optional)
    
    It must NOT access:
    - The actual proto-language
    - Sound change history
    - Intermediate forms
    """
    
    def __init__(self, use_geography: bool = True):
        self.use_geography = use_geography
        self.reconstructed_forms = {}
        self.confidence_scores = {}
    
    def reconstruct_from_population(self, observable) -> Dict[str, str]:
        """Reconstruct proto-forms from population snapshot."""
        
        # Extract all attested forms per word
        word_forms = defaultdict(list)
        speaker_positions = {}
        
        for speaker_id, speaker_data in observable.languages.items():
            # Extract lexicon and position
            if isinstance(speaker_data, dict):
                lexicon = speaker_data.get('lexicon', {})
                position = speaker_data.get('position')
                if position:
                    speaker_positions[speaker_id] = position
            else:
                continue
            
            for word, form in lexicon.items():
                word_forms[word].append((speaker_id, form))
        
        # Reconstruct each word
        for word, forms in word_forms.items():
            proto_form = self._reconstruct_word(word, forms, speaker_positions)
            confidence = self._calculate_confidence(word, forms, speaker_positions)
            
            self.reconstructed_forms[word] = proto_form
            self.confidence_scores[word] = confidence
        
        return self.reconstructed_forms
    
    def _reconstruct_word(
        self, 
        word: str, 
        forms: List[tuple],
        positions: Dict
    ) -> str:
        """Reconstruct a single word.
        
        Strategy:
        1. If geography available, identify conservative vs innovative regions
        2. Weight forms by geographical clustering
        3. Use majority rule with conservative bias
        """
        
        # Extract just the forms (ignore speaker IDs for simple majority)
        form_list = [form for _, form in forms]
        
        # Find most common form (conservative assumption)
        form_counts = Counter(form_list)
        most_common_form = form_counts.most_common(1)[0][0]
        
        # If we have geography, check if this form clusters
        if self.use_geography and positions:
            # Simple heuristic: if most common form is geographically peripheral,
            # it may be conservative (assumption: innovations spread from centers)
            # This is simplified - real comparative method is more sophisticated
            pass
        
        # For now, return most common form as proto-form
        # (This is a simplification - real reconstruction would use
        # systematic correspondences)
        return most_common_form
    
    def _calculate_confidence(
        self,
        word: str,
        forms: List[tuple],
        positions: Dict
    ) -> float:
        """Calculate reconstruction confidence."""
        
        form_list = [form for _, form in forms]
        
        if not form_list:
            return 0.0
        
        # Confidence based on:
        # 1. Number of attestations
        num_attestations = len(form_list)
        attestation_score = min(num_attestations / 10.0, 1.0)
        
        # 2. Agreement among forms
        form_counts = Counter(form_list)
        most_common_count = form_counts.most_common(1)[0][1]
        agreement_score = most_common_count / num_attestations
        
        # 3. Diversity (lower diversity = higher confidence)
        diversity = len(form_counts) / num_attestations
        diversity_penalty = 1.0 - (diversity * 0.5)
        
        confidence = (
            attestation_score * 0.3 +
            agreement_score * 0.5 +
            diversity_penalty * 0.2
        )
        
        return confidence


def run_vertical_slice_experiment():
    """Run complete H → O_t → Ĥ experiment using Phonological Drift."""
    
    print("=== Phonological Drift → Reconstruct: Vertical Slice ===\n")
    print("This experiment demonstrates the complete H → O_t → Ĥ protocol:\n")
    print("  H:  Generate realistic population-based sound change")
    print("  O_t: Extract observable daughter languages")
    print("  Ĥ:  Attempt reconstruction without privileged access\n")
    
    # Step 1: Generate history using Phonological Drift
    print("=" * 60)
    print("STEP 1: Generating History (H)")
    print("=" * 60)
    
    random.seed(42)  # Reproducible
    
    # Create population
    population = phonological_drift.create_population(size=20, grid_size=10.0)
    
    print(f"\nCreated population: {len(population.speakers)} speakers")
    print(f"Proto-lexicon: {len(population.speakers[0].lexicon)} words")
    
    # Record true proto-forms
    true_proto_forms = {
        word: ''.join(p.symbol for p in phones)
        for word, phones in population.speakers[0].lexicon.items()
    }
    
    print("\nTrue proto-language (ground truth H):")
    for word, form in sorted(list(true_proto_forms.items())[:5]):
        print(f"  *{word} = {form}")
    print(f"  ... ({len(true_proto_forms)} words total)")
    
    # Introduce sound changes
    inv = create_basic_inventory()
    
    # Define sound changes
    p_to_f = Phoneme('f', {'consonant', 'fricative', 'voiceless', 'labial'})
    change1 = SoundChange('p>f', inv.get_phoneme('p'), p_to_f, probability=0.8)
    
    t_to_th = Phoneme('θ', {'consonant', 'fricative', 'voiceless', 'dental'})
    change2 = SoundChange('t>θ', inv.get_phoneme('t'), t_to_th, probability=0.7)
    
    change3 = SoundChange('k>h', inv.get_phoneme('k'), inv.get_phoneme('h'), probability=0.6)
    
    # Introduce changes at different times in different speakers
    population.introduce_sound_change(change1, initial_speakers=3)
    
    # Evolve population
    print("\nEvolving population over 15 generations...")
    for gen in range(15):
        if gen == 5:
            population.introduce_sound_change(change2, initial_speakers=2)
        if gen == 10:
            population.introduce_sound_change(change3, initial_speakers=2)
        
        population.step_generation()
    
    print("Evolution complete.")
    
    # Step 2: Extract observable
    print("\n" + "=" * 60)
    print("STEP 2: Extract Observable Evidence (O_t)")
    print("=" * 60)
    
    # Create observable - what a historical linguist would actually see
    observable_languages = {}
    
    # Sample subset of speakers as "daughter languages"
    # (Not all speakers are observed - some lineages are extinct/undocumented)
    sample_speakers = random.sample(population.speakers, min(8, len(population.speakers)))
    
    print(f"\nSampling {len(sample_speakers)} speakers as documented daughter languages")
    print("(Other speakers represent extinct/undocumented lineages)\n")
    
    for i, speaker in enumerate(sample_speakers):
        lexicon_str = {
            word: ''.join(p.symbol for p in phones)
            for word, phones in speaker.lexicon.items()
        }
        
        observable_languages[i] = {
            'lexicon': lexicon_str,
            'position': speaker.position
        }
        
        print(f"Daughter {i} (position {speaker.position[0]:.1f}, {speaker.position[1]:.1f}):")
        for word, form in sorted(list(lexicon_str.items())[:3]):
            print(f"  {word} = {form}")
        print()
    
    # Create observable object
    from language_evolution.framework import Observable
    observable = Observable(
        time=15,
        languages=observable_languages,
        metadata={'num_speakers_total': len(population.speakers)}
    )
    
    print(f"Observable contains {len(observable_languages)} daughter languages")
    print(f"(Ground truth had {len(population.speakers)} speakers total)")
    
    # Step 3: Attempt reconstruction
    print("\n" + "=" * 60)
    print("STEP 3: Reconstruct Proto-Language (Ĥ)")
    print("=" * 60)
    
    print("\nReconstructor has access to:")
    print("  ✓ Contemporary forms in daughter languages")
    print("  ✓ Geographical positions")
    print("\nReconstructor does NOT have access to:")
    print("  ✗ True proto-language")
    print("  ✗ Sound change history")
    print("  ✗ Intermediate forms")
    print("  ✗ Undocumented speaker lineages")
    
    reconstructor = PopulationBasedReconstructor(use_geography=True)
    reconstructed_forms = reconstructor.reconstruct_from_population(observable)
    
    print(f"\nReconstructed {len(reconstructed_forms)} proto-forms\n")
    
    # Step 4: Compare reconstruction against ground truth
    print("=" * 60)
    print("STEP 4: Evaluate Reconstruction Accuracy")
    print("=" * 60)
    
    correct = 0
    partial = 0
    incorrect = 0
    
    print("\nComparison of reconstructed vs. true proto-forms:\n")
    
    for word in sorted(reconstructed_forms.keys())[:8]:
        reconstructed = reconstructed_forms[word]
        true_form = true_proto_forms.get(word, '???')
        confidence = reconstructor.confidence_scores.get(word, 0.0)
        
        # Calculate edit distance
        if reconstructed == true_form:
            status = "✓ EXACT"
            correct += 1
        else:
            # Simple character difference count
            diff = sum(1 for a, b in zip(reconstructed, true_form) if a != b)
            diff += abs(len(reconstructed) - len(true_form))
            
            if diff <= 2:
                status = "≈ CLOSE"
                partial += 1
            else:
                status = "✗ WRONG"
                incorrect += 1
        
        print(f"*{word:10} {status:10}")
        print(f"  Reconstructed: {reconstructed:12} (confidence: {confidence:.2f})")
        print(f"  True form:     {true_form:12}")
        
        # Show variation in daughters
        daughter_forms = set()
        for lang_data in observable_languages.values():
            if word in lang_data['lexicon']:
                daughter_forms.add(lang_data['lexicon'][word])
        
        if len(daughter_forms) > 1:
            print(f"  Variation:     {', '.join(sorted(daughter_forms))}")
        
        print()
    
    # Summary statistics
    total = correct + partial + incorrect
    
    print("=" * 60)
    print("RECONSTRUCTION ACCURACY SUMMARY")
    print("=" * 60)
    
    if total > 0:
        print(f"\nExact matches:  {correct:2}/{total} ({100*correct/total:5.1f}%)")
        print(f"Close matches:  {partial:2}/{total} ({100*partial/total:5.1f}%)")
        print(f"Wrong:          {incorrect:2}/{total} ({100*incorrect/total:5.1f}%)")
        print(f"\nOverall success rate: {100*(correct+partial)/total:.1f}%")
    
    # Step 5: Recoverability analysis
    print("\n" + "=" * 60)
    print("STEP 5: Recoverability Analysis")
    print("=" * 60)
    
    print("\n**Information Lost:**")
    print(f"  - {len(population.speakers) - len(sample_speakers)} speaker lineages not documented")
    print(f"  - Sound change ordering and timing unknown")
    print(f"  - Intermediate forms lost")
    print(f"  - Prestige and geographic effects not directly observable")
    
    print("\n**Reconstruction Challenges:**")
    
    # Find words with high variation
    high_variation_words = []
    for word in reconstructed_forms.keys():
        forms = set()
        for lang_data in observable_languages.values():
            if word in lang_data['lexicon']:
                forms.add(lang_data['lexicon'][word])
        if len(forms) >= 3:
            high_variation_words.append((word, len(forms)))
    
    if high_variation_words:
        print(f"  - {len(high_variation_words)} words show high variation across daughters:")
        for word, num_forms in sorted(high_variation_words, key=lambda x: -x[1])[:3]:
            print(f"      {word}: {num_forms} different forms")
    
    # Find words with low confidence
    low_confidence = [(w, s) for w, s in reconstructor.confidence_scores.items() if s < 0.7]
    if low_confidence:
        print(f"  - {len(low_confidence)} reconstructions have low confidence (<0.7)")
    
    print("\n**Key Insight:**")
    print(f"  Even with {len(sample_speakers)} daughter languages and systematic method,")
    print(f"  only {correct}/{total} exact reconstructions achieved.")
    print(f"  This reflects both:")
    print(f"    (a) Limitations of simple majority-rule reconstruction")
    print(f"    (b) Genuine information loss in O_t")
    
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    
    print("\nThis vertical slice demonstrates:")
    print("  ✓ History generation with realistic population dynamics")
    print("  ✓ Observable extraction (lossy projection)")
    print("  ✓ Reconstruction without privileged access")
    print("  ✓ Quantitative accuracy measurement")
    print("  ✓ Identification of unrecoverable information")


if __name__ == '__main__':
    run_vertical_slice_experiment()
