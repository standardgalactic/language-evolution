#!/usr/bin/env python3
"""
Borrowing Detection Algorithm

Distinguishes horizontal transmission (borrowing) from vertical inheritance
using distributional patterns in cognate sets.

Key Insight:
    Borrowed words show IRREGULAR patterns:
    - Violate systematic sound correspondences
    - Appear in only subset of related languages
    - Often show cultural/semantic clustering

Inherited words show REGULAR patterns:
    - Follow systematic correspondences
    - Present across all daughters (or regular losses)
    - Distributed across semantic domains
"""

import random
import sys
from collections import defaultdict
from dataclasses import dataclass

sys.path.insert(0, 'src')

from language_evolution.framework import Observable


@dataclass
class BorrowingEvidence:
    """Evidence that a word was borrowed rather than inherited."""

    word: str
    meaning: str
    irregular_pattern: bool  # Violates systematic correspondences
    partial_distribution: bool  # Only in subset of languages
    cultural_semantic: bool  # In cultural/technological domain
    phonotactic_foreign: bool  # Violates native phonotactics
    confidence: float  # 0-1 probability of borrowing


class BorrowingDetector:
    """Detects borrowed words in language data."""

    def __init__(
        self,
        min_confidence: float = 0.6,
        cultural_domains: set[str] | None = None,
    ):
        self.min_confidence = min_confidence
        self.cultural_domains = cultural_domains or {
            'technology',
            'food',
            'government',
            'religion',
            'trade',
        }

    def detect_borrowings(
        self,
        observable: Observable,
        systematic_correspondences: dict | None = None,
    ) -> list[BorrowingEvidence]:
        """
        Identify likely borrowed words from observable data.

        Args:
            observable: Language data
            systematic_correspondences: Known regular sound patterns

        Returns:
            List of borrowing evidence for suspicious words
        """
        borrowings = []

        # Extract vocabularies
        vocabularies = self._extract_vocabularies(observable)
        if not vocabularies:
            return []

        # Find cognate sets (words with same meaning)
        cognate_sets = self._find_cognate_sets(vocabularies)

        # Analyze each cognate set
        for meaning, word_forms in cognate_sets.items():
            # Check distribution
            partial = self._is_partial_distribution(word_forms, len(vocabularies))

            # Check phonotactics
            foreign = self._has_foreign_phonotactics(word_forms)

            # Check semantic domain
            cultural = self._is_cultural_domain(meaning)

            # Check regularity (if correspondences provided)
            irregular = False
            if systematic_correspondences:
                irregular = self._violates_correspondences(
                    word_forms,
                    systematic_correspondences,
                )

            # Calculate confidence
            evidence_count = sum([partial, foreign, cultural, irregular])
            confidence = evidence_count / 4.0

            if confidence >= self.min_confidence:
                # Pick most common form as representative
                representative = max(
                    word_forms.items(),
                    key=lambda x: len(x[1]),
                )[0]

                borrowings.append(
                    BorrowingEvidence(
                        word=representative,
                        meaning=meaning,
                        irregular_pattern=irregular,
                        partial_distribution=partial,
                        cultural_semantic=cultural,
                        phonotactic_foreign=foreign,
                        confidence=confidence,
                    ),
                )

        return sorted(borrowings, key=lambda b: b.confidence, reverse=True)

    def _extract_vocabularies(self, observable: Observable) -> dict:
        """Extract word lists from observable."""
        vocabularies = {}

        for lang_id, lang_data in observable.languages.items():
            if isinstance(lang_data, dict) and 'vocabulary' in lang_data:
                vocab = lang_data['vocabulary']
                if isinstance(vocab, list):
                    vocabularies[lang_id] = vocab
                elif isinstance(vocab, dict):
                    # Convert dict to list of {meaning, form} entries
                    vocab_list = []
                    for meaning, data in vocab.items():
                        if isinstance(data, dict) and 'form' in data:
                            vocab_list.append({'meaning': meaning, 'form': data['form']})
                        elif isinstance(data, str):
                            vocab_list.append({'meaning': meaning, 'form': data})
                    vocabularies[lang_id] = vocab_list

        return vocabularies

    def _find_cognate_sets(self, vocabularies: dict) -> dict[str, dict]:
        """Group words by meaning across languages."""
        cognate_sets: dict = defaultdict(lambda: defaultdict(list))

        for vocab in vocabularies.values():
            for entry in vocab:
                meaning = entry.get('meaning')
                form = entry.get('form')
                if meaning and form:
                    cognate_sets[meaning][form].append(entry)

        return cognate_sets

    def _is_partial_distribution(
        self,
        word_forms: dict,
        total_languages: int,
    ) -> bool:
        """Check if word appears in only subset of languages."""
        # Count how many languages have this word
        languages_with_word = sum(len(entries) for entries in word_forms.values())

        # Borrowed words often appear in <50% of related languages
        return languages_with_word < total_languages * 0.5

    def _has_foreign_phonotactics(self, word_forms: dict) -> bool:
        """Check if word violates typical native phonotactics."""
        # Simple heuristic: look for unusual clusters or sequences
        for form in word_forms:
            # Foreign words often have:
            # - Initial clusters (sp-, st-, sk- in Germanic loanwords)
            # - Unusual vowel sequences
            # - Three consonant clusters
            if any(
                [
                    form.startswith(('sp', 'st', 'sk', 'sh', 'zh')),
                    'sch' in form,
                    'tsch' in form,
                    # Three consonants in a row
                    any(
                        all(c not in 'aeiou' for c in form[i : i + 3])
                        for i in range(len(form) - 2)
                    ),
                ],
            ):
                return True

        return False

    def _is_cultural_domain(self, meaning: str) -> bool:
        """Check if meaning is in cultural/technological domain."""
        # Cultural words are more likely to be borrowed
        for domain in self.cultural_domains:
            if domain in meaning.lower():
                return True

        # Check for specific cultural indicators
        cultural_keywords = [
            'law',
            'king',
            'church',
            'temple',
            'trade',
            'merchant',
            'wine',
            'tea',
            'coffee',
            'rice',
            'paper',
            'book',
            'school',
            'university',
        ]

        return any(keyword in meaning.lower() for keyword in cultural_keywords)

    def _violates_correspondences(
        self,
        word_forms: dict,
        systematic_correspondences: dict,
    ) -> bool:
        """Check if word violates known systematic sound correspondences."""
        # This is a simplified check
        # A real implementation would check if sound correspondences
        # in this word match the regular patterns

        # For now, just check if forms are highly divergent
        # (suggesting irregularity)
        forms = list(word_forms.keys())
        if len(forms) < 2:
            return False

        # Calculate edit distance between forms
        avg_distance = 0
        comparisons = 0
        for i, form1 in enumerate(forms):
            for form2 in forms[i + 1 :]:
                avg_distance += self._edit_distance(form1, form2)
                comparisons += 1

        if comparisons > 0:
            avg_distance /= comparisons

            # High edit distance suggests irregularity
            # (borrowed words don't follow regular sound laws)
            max_length = max(len(f) for f in forms)
            return avg_distance > max_length * 0.7

        return False

    def _edit_distance(self, s1: str, s2: str) -> int:
        """Simple Levenshtein distance."""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


def demonstrate_borrowing_detection():
    """Demonstrate borrowing detection with example data."""
    print("=" * 70)
    print("BORROWING DETECTION")
    print("=" * 70)
    print()
    print("Distinguishing borrowed words from inherited vocabulary")
    print()

    # Create test data with mixture of inherited and borrowed words
    # Three related languages with some borrowed words from external source

    vocabularies = {
        1: {
            'water': {'form': 'watar'},  # Inherited
            'fire': {'form': 'fyr'},  # Inherited
            'church': {'form': 'kirche'},  # Borrowed (cultural + foreign phonotactics)
            'book': {'form': 'buk'},  # Borrowed
        },
        2: {
            'water': {'form': 'water'},  # Inherited
            'fire': {'form': 'fire'},  # Inherited
            'church': {'form': 'church'},  # Borrowed (only in some languages)
        },
        3: {
            'water': {'form': 'vatn'},  # Inherited
            'fire': {'form': 'eld'},  # Inherited (different root, but regular)
            'tea': {'form': 'te'},  # Borrowed (cultural, not in all languages)
        },
    }

    obs = Observable(time=100, languages=vocabularies)

    detector = BorrowingDetector(min_confidence=0.5)
    borrowings = detector.detect_borrowings(obs)

    print("Detected Borrowings:")
    print()

    if not borrowings:
        print("  No borrowings detected with current confidence threshold")
    else:
        for b in borrowings:
            print(f"  '{b.word}' ({b.meaning})")
            print(f"    Confidence: {b.confidence:.1%}")
            print("    Evidence:")
            if b.irregular_pattern:
                print("      • Violates systematic correspondences")
            if b.partial_distribution:
                print("      • Partial distribution (not in all languages)")
            if b.cultural_semantic:
                print("      • Cultural/technological domain")
            if b.phonotactic_foreign:
                print("      • Foreign phonotactic patterns")
            print()

    print("-" * 70)
    print()
    print("KEY INSIGHT:")
    print()
    print("Borrowed words show IRREGULAR patterns that distinguish them")
    print("from systematically inherited vocabulary:")
    print()
    print("  1. Violate systematic sound correspondences")
    print("  2. Appear in geographical/cultural subsets")
    print("  3. Cluster in cultural/technological domains")
    print("  4. May contain foreign phonotactic patterns")
    print()
    print("This allows reconstruction of both:")
    print("  - Vertical transmission (family tree)")
    print("  - Horizontal transmission (contact relationships)")


if __name__ == '__main__':
    random.seed(42)
    demonstrate_borrowing_detection()
