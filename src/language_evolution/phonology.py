"""Phonological representation and sound change."""

import random
from dataclasses import dataclass, field


@dataclass
class Phoneme:
    """A phoneme with distinctive features."""
    symbol: str
    features: set[str]
    
    def __hash__(self):
        return hash(self.symbol)
    
    def __eq__(self, other):
        return isinstance(other, Phoneme) and self.symbol == other.symbol


@dataclass
class SoundChange:
    """A sound change rule that can apply probabilistically."""
    name: str
    source: Phoneme
    target: Phoneme
    context_before: set[Phoneme] = field(default_factory=set)
    context_after: set[Phoneme] = field(default_factory=set)
    probability: float = 1.0
    
    def applies(self, phoneme: Phoneme, before: Phoneme | None, after: Phoneme | None) -> bool:
        """Check if this change applies in the given context."""
        if phoneme != self.source:
            return False
        
        if self.context_before and before not in self.context_before:
            return False
            
        if self.context_after and after not in self.context_after:
            return False
        
        return random.random() < self.probability
    
    def apply(self, word: list[Phoneme]) -> list[Phoneme]:
        """Apply this sound change to a word."""
        result = []
        for i, phoneme in enumerate(word):
            before = word[i-1] if i > 0 else None
            after = word[i+1] if i < len(word)-1 else None
            
            if self.applies(phoneme, before, after):
                result.append(self.target)
            else:
                result.append(phoneme)
        
        return result


class PhonemeInventory:
    """A language's phoneme inventory."""
    
    def __init__(self, phonemes: set[Phoneme]):
        self.phonemes = phonemes
        self._symbol_map = {p.symbol: p for p in phonemes}
    
    def get_phoneme(self, symbol: str) -> Phoneme:
        """Get a phoneme by its symbol."""
        return self._symbol_map[symbol]
    
    def add_phoneme(self, phoneme: Phoneme):
        """Add a new phoneme to the inventory."""
        self.phonemes.add(phoneme)
        self._symbol_map[phoneme.symbol] = phoneme
    
    def remove_phoneme(self, phoneme: Phoneme):
        """Remove a phoneme from the inventory."""
        self.phonemes.discard(phoneme)
        self._symbol_map.pop(phoneme.symbol, None)
    
    def copy(self) -> 'PhonemeInventory':
        """Create a copy of this inventory."""
        return PhonemeInventory(self.phonemes.copy())
    
    def __repr__(self):
        return f"PhonemeInventory({sorted(p.symbol for p in self.phonemes)})"


def create_basic_inventory() -> PhonemeInventory:
    """Create a basic Proto-Indo-European-like inventory."""
    phonemes = {
        # Stops
        Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'}),
        Phoneme('t', {'consonant', 'stop', 'voiceless', 'coronal'}),
        Phoneme('k', {'consonant', 'stop', 'voiceless', 'dorsal'}),
        Phoneme('b', {'consonant', 'stop', 'voiced', 'labial'}),
        Phoneme('d', {'consonant', 'stop', 'voiced', 'coronal'}),
        Phoneme('g', {'consonant', 'stop', 'voiced', 'dorsal'}),
        
        # Fricatives
        Phoneme('s', {'consonant', 'fricative', 'voiceless', 'coronal'}),
        Phoneme('h', {'consonant', 'fricative', 'voiceless', 'glottal'}),
        
        # Nasals
        Phoneme('m', {'consonant', 'nasal', 'voiced', 'labial'}),
        Phoneme('n', {'consonant', 'nasal', 'voiced', 'coronal'}),
        
        # Liquids
        Phoneme('l', {'consonant', 'liquid', 'lateral', 'voiced', 'coronal'}),
        Phoneme('r', {'consonant', 'liquid', 'rhotic', 'voiced', 'coronal'}),
        
        # Vowels
        Phoneme('i', {'vowel', 'high', 'front'}),
        Phoneme('e', {'vowel', 'mid', 'front'}),
        Phoneme('a', {'vowel', 'low', 'central'}),
        Phoneme('o', {'vowel', 'mid', 'back'}),
        Phoneme('u', {'vowel', 'high', 'back'}),
    }
    return PhonemeInventory(phonemes)
