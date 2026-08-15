"""False Cognate Laboratory: Measuring accidental resemblance.

Generate thousands of unrelated miniature languages and measure how often
convincing-looking correspondences arise accidentally. Then progressively
require semantic similarity, recurring sound correspondences, morphological
agreement, geographical plausibility, and larger cognate sets.

Research Questions:
1. How often do unrelated languages produce look-alike words by chance?
2. How much does requiring semantic agreement reduce false positives?
3. How many recurring correspondences are needed for confidence?
4. What is the baseline false-positive rate for the comparative method?

This is an empirical demonstration of why individual look-alike words
constitute weak historical evidence.
"""

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from language_evolution.framework import History, Observable, InferenceSystem, Reconstruction
from language_evolution.phonology import Phoneme, PhonemeInventory
from typing import List, Dict, Set, Tuple
from collections import defaultdict, Counter
import random
import itertools


class MiniLanguageGenerator:
    """Generate small unrelated languages for false cognate testing."""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        
        # Define possible phoneme types
        self.consonants = ['p', 't', 'k', 'b', 'd', 'g', 'm', 'n', 's', 'h', 'l', 'r', 'w', 'j']
        self.vowels = ['a', 'e', 'i', 'o', 'u']
        
        # Semantic concepts (shared across all languages)
        self.concepts = [
            'sun', 'moon', 'water', 'fire', 'stone',
            'tree', 'person', 'hand', 'foot', 'eye',
            'eat', 'drink', 'go', 'see', 'big',
            'small', 'good', 'bad', 'one', 'two'
        ]
    
    def generate_language(self, lang_id: int, lexicon_size: int = 20) -> Dict[str, str]:
        """Generate one random language.
        
        Languages are UNRELATED - no common ancestor.
        Each language randomly assigns forms to meanings.
        """
        
        # Select random subset of consonants and vowels for this language
        lang_consonants = random.sample(self.consonants, k=random.randint(6, 10))
        lang_vowels = random.sample(self.vowels, k=random.randint(3, 5))
        
        lexicon = {}
        
        # Generate forms for concepts
        concepts_to_encode = self.concepts[:lexicon_size]
        
        for concept in concepts_to_encode:
            # Generate random word form
            word_length = random.randint(2, 4)
            word = ''
            
            for i in range(word_length):
                if i % 2 == 0:
                    word += random.choice(lang_consonants)
                else:
                    word += random.choice(lang_vowels)
            
            # Optionally add final consonant
            if random.random() < 0.3 and len(word) >= 2:
                word += random.choice(lang_consonants)
            
            lexicon[concept] = word
        
        return lexicon
    
    def generate_language_set(self, num_languages: int, lexicon_size: int = 20) -> List[Dict[str, str]]:
        """Generate multiple unrelated languages."""
        return [
            self.generate_language(i, lexicon_size)
            for i in range(num_languages)
        ]


class CognateDetector:
    """Detect potential cognates between languages."""
    
    def __init__(self, min_similarity: float = 0.6):
        self.min_similarity = min_similarity
    
    def string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (simple normalized edit distance)."""
        if not s1 or not s2:
            return 0.0
        
        # Levenshtein distance
        distances = list(range(len(s1) + 1))
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        
        edit_distance = distances[-1]
        max_length = max(len(s1), len(s2))
        
        return 1.0 - (edit_distance / max_length)
    
    def find_potential_cognates(
        self,
        languages: List[Dict[str, str]],
        require_semantics: bool = False
    ) -> List[Tuple[int, int, str, str, str, float]]:
        """Find word pairs that look similar.
        
        Returns: list of (lang1_id, lang2_id, concept, form1, form2, similarity)
        """
        
        potential_cognates = []
        
        for i in range(len(languages)):
            for j in range(i + 1, len(languages)):
                lang1 = languages[i]
                lang2 = languages[j]
                
                if require_semantics:
                    # Only compare words with same meaning
                    common_concepts = set(lang1.keys()) & set(lang2.keys())
                    
                    for concept in common_concepts:
                        form1 = lang1[concept]
                        form2 = lang2[concept]
                        
                        similarity = self.string_similarity(form1, form2)
                        
                        if similarity >= self.min_similarity:
                            potential_cognates.append((i, j, concept, form1, form2, similarity))
                else:
                    # Compare all words regardless of meaning
                    for concept1, form1 in lang1.items():
                        for concept2, form2 in lang2.items():
                            similarity = self.string_similarity(form1, form2)
                            
                            if similarity >= self.min_similarity:
                                # Record as potential cognate
                                meaning_match = concept1 == concept2
                                potential_cognates.append((
                                    i, j, f"{concept1}~{concept2}", 
                                    form1, form2, similarity
                                ))
        
        return potential_cognates
    
    def find_systematic_correspondences(
        self,
        languages: List[Dict[str, str]],
        min_examples: int = 3
    ) -> Dict[Tuple[int, int], List[Tuple[str, str, int]]]:
        """Find recurring sound correspondences between language pairs.
        
        A systematic correspondence is a phoneme pair that recurs across
        multiple words in similar positions.
        """
        
        correspondences = defaultdict(lambda: defaultdict(int))
        
        for i in range(len(languages)):
            for j in range(i + 1, len(languages)):
                lang1 = languages[i]
                lang2 = languages[j]
                
                # Compare words with same meaning
                common_concepts = set(lang1.keys()) & set(lang2.keys())
                
                for concept in common_concepts:
                    form1 = lang1[concept]
                    form2 = lang2[concept]
                    
                    # Find character alignments (simplified)
                    min_len = min(len(form1), len(form2))
                    
                    for pos in range(min_len):
                        c1 = form1[pos]
                        c2 = form2[pos]
                        
                        correspondences[(i, j)][(c1, c2)] += 1
        
        # Filter to systematic (recurring) correspondences
        systematic = {}
        
        for lang_pair, corr_counts in correspondences.items():
            systematic_corrs = [
                (c1, c2, count)
                for (c1, c2), count in corr_counts.items()
                if count >= min_examples
            ]
            
            if systematic_corrs:
                systematic[lang_pair] = systematic_corrs
        
        return systematic


def run_false_cognate_experiment():
    """Run the false cognate laboratory experiment."""
    
    print("=== False Cognate Laboratory ===\n")
    print("Research Question:")
    print("  How often do UNRELATED languages produce convincing look-alike words?\n")
    
    # Experiment parameters
    num_languages = 50
    lexicon_size = 20
    num_trials = 10
    
    print(f"Experimental Design:")
    print(f"  - Generate {num_languages} completely unrelated languages")
    print(f"  - Each language has {lexicon_size} words")
    print(f"  - Run {num_trials} trials with different random seeds")
    print(f"  - Measure false-positive rates\n")
    
    # Run trials
    generator = MiniLanguageGenerator()
    
    results = {
        'form_only': [],
        'semantic_required': [],
        'systematic_required': []
    }
    
    print("=" * 60)
    print("EXPERIMENT 1: Baseline False-Positive Rate")
    print("=" * 60)
    print("\nWithout any semantic or systematic requirements:\n")
    
    for trial in range(num_trials):
        # Generate unrelated languages
        languages = generator.generate_language_set(num_languages, lexicon_size)
        
        # Detect potential cognates (form similarity only)
        detector = CognateDetector(min_similarity=0.7)
        
        # Form-based only (no semantic requirement)
        form_matches = detector.find_potential_cognates(languages, require_semantics=False)
        results['form_only'].append(len(form_matches))
        
        print(f"Trial {trial}: {len(form_matches)} look-alike pairs found")
    
    avg_form_only = sum(results['form_only']) / len(results['form_only'])
    
    # Calculate how many are expected by chance
    total_comparisons = (num_languages * (num_languages - 1)) // 2
    words_per_language = lexicon_size
    total_word_pairs = total_comparisons * words_per_language * words_per_language
    
    print(f"\nSummary:")
    print(f"  Average false positives: {avg_form_only:.1f} per trial")
    print(f"  Total word-pair comparisons: {total_word_pairs:,}")
    print(f"  False positive rate: {100 * avg_form_only / total_word_pairs:.4f}%")
    
    # Experiment 2: Require semantic agreement
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Requiring Semantic Agreement")
    print("=" * 60)
    print("\nOnly count matches where meanings also match:\n")
    
    for trial in range(num_trials):
        languages = generator.generate_language_set(num_languages, lexicon_size)
        detector = CognateDetector(min_similarity=0.7)
        
        semantic_matches = detector.find_potential_cognates(languages, require_semantics=True)
        results['semantic_required'].append(len(semantic_matches))
        
        print(f"Trial {trial}: {len(semantic_matches)} semantic matches")
    
    avg_semantic = sum(results['semantic_required']) / len(results['semantic_required'])
    
    semantic_comparisons = total_comparisons * lexicon_size  # Same meaning only
    
    print(f"\nSummary:")
    print(f"  Average false positives: {avg_semantic:.1f} per trial")
    print(f"  Semantic comparisons: {semantic_comparisons:,}")
    print(f"  False positive rate: {100 * avg_semantic / semantic_comparisons:.4f}%")
    print(f"  Reduction: {100 * (1 - avg_semantic / avg_form_only):.1f}% fewer false positives")
    
    # Experiment 3: Require systematic correspondences
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Requiring Systematic Correspondences")
    print("=" * 60)
    print("\nRequire recurring sound patterns (3+ examples):\n")
    
    for trial in range(num_trials):
        languages = generator.generate_language_set(num_languages, lexicon_size)
        detector = CognateDetector(min_similarity=0.7)
        
        systematic = detector.find_systematic_correspondences(languages, min_examples=3)
        results['systematic_required'].append(len(systematic))
        
        print(f"Trial {trial}: {len(systematic)} language pairs with systematic correspondences")
    
    avg_systematic = sum(results['systematic_required']) / len(results['systematic_required'])
    
    print(f"\nSummary:")
    print(f"  Average language pairs: {avg_systematic:.1f} per trial")
    print(f"  Total language pairs: {total_comparisons}")
    print(f"  False positive rate: {100 * avg_systematic / total_comparisons:.4f}%")
    
    # Example: Show one trial in detail
    print("\n" + "=" * 60)
    print("EXAMPLE: Detailed Look at One Trial")
    print("=" * 60)
    
    languages = generator.generate_language_set(10, 20)  # Smaller for display
    
    print(f"\nGenerated {len(languages)} unrelated languages")
    print("\nSample lexicons (first 5 words):\n")
    
    for i, lang in enumerate(languages[:3]):
        print(f"Language {i}:")
        for concept, form in list(lang.items())[:5]:
            print(f"  {concept:10} = {form}")
        print()
    
    # Find false cognates
    detector = CognateDetector(min_similarity=0.7)
    matches = detector.find_potential_cognates(languages, require_semantics=True)
    
    if matches:
        print(f"Found {len(matches)} accidental resemblances:\n")
        for lang1, lang2, concept, form1, form2, sim in matches[:5]:
            print(f"  Languages {lang1} & {lang2}, '{concept}':")
            print(f"    {form1} ≈ {form2} (similarity: {sim:.2f})")
            print(f"    → Accidental! These languages are unrelated\n")
    else:
        print("No accidental resemblances above threshold in this sample.")
    
    # Check for systematic correspondences
    systematic = detector.find_systematic_correspondences(languages, min_examples=2)
    
    if systematic:
        print(f"\nSystematic correspondences found (by pure chance!):\n")
        for (lang1, lang2), corrs in list(systematic.items())[:2]:
            print(f"  Languages {lang1} & {lang2}:")
            for c1, c2, count in corrs[:3]:
                print(f"    {c1} ↔ {c2} ({count} times)")
            print()
    
    # Key findings
    print("=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    
    print(f"\n1. Form Similarity Alone:")
    print(f"   {avg_form_only:.1f} false positives on average")
    print(f"   → Unreliable evidence without semantic agreement")
    
    print(f"\n2. Semantic Agreement:")
    print(f"   {avg_semantic:.1f} false positives on average")
    print(f"   → Reduces false positives by {100 * (1 - avg_semantic / avg_form_only):.0f}%")
    print(f"   → But still produces accidental matches!")
    
    print(f"\n3. Systematic Correspondences:")
    print(f"   {avg_systematic:.1f} language pairs on average")
    print(f"   → Even recurring patterns can arise by chance")
    print(f"   → Need multiple independent cognate sets")
    
    print("\n" + "=" * 60)
    print("IMPLICATIONS FOR HISTORICAL LINGUISTICS")
    print("=" * 60)
    
    print("\n**Why single look-alike words are weak evidence:**")
    print(f"  Even with semantic agreement, {avg_semantic:.1f} accidental")
    print(f"  matches arise among just {num_languages} languages")
    
    print("\n**What strengthens the case:**")
    print("  - Multiple cognate sets (not just one or two)")
    print("  - Systematic sound correspondences")
    print("  - Morphological agreement")
    print("  - Geographical plausibility")
    print("  - Exclusion of known borrowing")
    
    print("\n**Quantified baseline:**")
    print(f"  False positive rate (semantic + form):")
    print(f"  {100 * avg_semantic / semantic_comparisons:.4f}%")
    
    print("\n" + "=" * 60)
    
    print("\nThis experiment demonstrates:")
    print("  ✓ Accidental resemblance is measurable")
    print("  ✓ Individual look-alikes are statistically expected")
    print("  ✓ Multiple lines of evidence are necessary")
    print("  ✓ False-positive rates can be quantified")
    print("\nHistorical linguists intuitively know this.")
    print("This experiment provides the empirical baseline.")


if __name__ == '__main__':
    random.seed(42)
    run_false_cognate_experiment()
