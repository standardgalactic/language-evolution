#!/usr/bin/env python3
"""
Glyph Evolution Experiment

Research Question:
    How do writing systems evolve through copying errors and functional pressures?

Model:
    - Glyphs represented as 2D stroke patterns
    - Copying introduces small errors
    - Frequent glyphs experience economy pressure (faster to write)
    - Ambiguous glyphs experience differentiation pressure
    - Over generations: simplification, ligatures, systematic stroke sets

Ground Truth H:
    - Original pictographic forms
    - Every copying error
    - Selection pressures applied
    - Complete glyph genealogy

Observable O_t:
    - Contemporary glyph forms at time t
    - Which glyphs mean what
    - NO access to ancestral forms or copying history

Expected Phenomena:
    - Simplification (complex → simple)
    - Ligatures (frequent combinations fuse)
    - Stroke systematization (reused components)
    - Phonetic reuse (glyphs acquire new meanings)
    - Visual family relationships

This is NON-PHONOLOGICAL evolution - operates in visual/graphical space.
"""

import sys

sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

import random
from dataclasses import dataclass, field

from language_evolution.framework import HistoryGenerator, Observable


@dataclass
class Stroke:
    """A single stroke in a glyph."""
    start: tuple[int, int]
    end: tuple[int, int]
    
    def length(self) -> float:
        """Articulatory cost (length of stroke)."""
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        return (dx*dx + dy*dy)**0.5
    
    def __hash__(self):
        return hash((self.start, self.end))


@dataclass
class Glyph:
    """A written sign consisting of strokes."""
    meaning: str
    strokes: list[Stroke] = field(default_factory=list)
    frequency: float = 1.0  # How often this glyph is written
    
    def copy_with_error(self, error_rate: float = 0.1) -> 'Glyph':
        """
        Copy this glyph with potential errors.
        
        Errors:
        - Stroke position shifts
        - Stroke omission (rare)
        - Stroke addition (rare)
        """
        new_strokes = []
        
        for stroke in self.strokes:
            # Omit stroke with small probability
            if random.random() < 0.05 * error_rate:
                continue
            
            # Copy with position error
            if random.random() < error_rate:
                # Shift start/end points slightly
                shift = lambda p: (
                    p[0] + random.randint(-1, 1),
                    p[1] + random.randint(-1, 1)
                )
                new_stroke = Stroke(shift(stroke.start), shift(stroke.end))
            else:
                # Exact copy
                new_stroke = Stroke(stroke.start, stroke.end)
            
            new_strokes.append(new_stroke)
        
        # Occasionally add spurious stroke
        if random.random() < 0.02 * error_rate:
            x, y = random.randint(0, 10), random.randint(0, 10)
            new_strokes.append(Stroke((x, y), (x+1, y+1)))
        
        return Glyph(meaning=self.meaning, strokes=new_strokes, frequency=self.frequency)
    
    def simplify(self) -> 'Glyph':
        """
        Simplify by removing redundant strokes or shortening.
        
        Driven by production economy: shorter strokes = faster writing.
        """
        if not self.strokes:
            return self
        
        # Remove shortest stroke (if multiple strokes exist)
        if len(self.strokes) > 2:
            sorted_strokes = sorted(self.strokes, key=lambda s: s.length(), reverse=True)
            new_strokes = sorted_strokes[:-1]  # Drop shortest
        else:
            new_strokes = self.strokes
        
        return Glyph(meaning=self.meaning, strokes=new_strokes, frequency=self.frequency)
    
    def complexity(self) -> float:
        """Total stroke length (writing effort)."""
        return sum(s.length() for s in self.strokes)
    
    def visual_distance(self, other: 'Glyph') -> float:
        """
        Visual similarity (simple metric: stroke count difference).
        
        Real implementation would use image comparison.
        """
        return abs(len(self.strokes) - len(other.strokes))
    
    def to_ascii(self) -> str:
        """Simple ASCII representation."""
        if not self.strokes:
            return "□"
        
        # Use stroke count as proxy for complexity
        if len(self.strokes) == 1:
            return "⚊"
        elif len(self.strokes) == 2:
            return "⚌"
        elif len(self.strokes) == 3:
            return "⛶"
        else:
            return "☷"


class GlyphEvolution(HistoryGenerator):
    """
    Simulate evolution of writing system through copying and selection.
    
    Parameters:
        num_glyphs: How many signs in the writing system
        generations: How many copying generations
        error_rate: Probability of copying error per stroke
        economy_pressure: Strength of selection for simple glyphs
    """
    
    def __init__(
        self,
        num_glyphs: int = 20,
        error_rate: float = 0.1,
        economy_pressure: float = 0.3,
        seed: int | None = None
    ):
        super().__init__()
        self.num_glyphs = num_glyphs
        self.error_rate = error_rate
        self.economy_pressure = economy_pressure
        
        if seed is not None:
            random.seed(seed)
        
        self.glyphs: list[Glyph] = []
        self._create_proto_glyphs()
        
        # Record initialization
        self.history.record(0, 'initialization',
                          num_glyphs=num_glyphs,
                          error_rate=error_rate)
    
    def _create_proto_glyphs(self):
        """Create initial pictographic glyphs."""
        concepts = [
            'sun', 'moon', 'star', 'water', 'fire',
            'tree', 'mountain', 'person', 'hand', 'eye',
            'fish', 'bird', 'house', 'path', 'food',
            'day', 'night', 'rain', 'wind', 'stone'
        ]
        
        for i, concept in enumerate(concepts[:self.num_glyphs]):
            # Create complex pictographic glyph (4-6 strokes)
            num_strokes = random.randint(4, 6)
            strokes = []
            
            for _ in range(num_strokes):
                x1, y1 = random.randint(0, 8), random.randint(0, 8)
                x2, y2 = random.randint(0, 8), random.randint(0, 8)
                strokes.append(Stroke((x1, y1), (x2, y2)))
            
            glyph = Glyph(meaning=concept, strokes=strokes, frequency=1.0)
            self.glyphs.append(glyph)
            
            # Record proto-glyph
            self.history.record(0, 'proto_glyph_created',
                              meaning=concept,
                              num_strokes=len(strokes),
                              complexity=glyph.complexity())
    
    def step(self, generation: int):
        """One generation of copying and selection."""
        new_glyphs = []
        
        for glyph in self.glyphs:
            # Copy with errors
            copied = glyph.copy_with_error(self.error_rate)
            
            # Record if significant change occurred
            if copied.complexity() != glyph.complexity():
                self.history.record(generation, 'copying_error',
                                  meaning=glyph.meaning,
                                  old_complexity=glyph.complexity(),
                                  new_complexity=copied.complexity())
            
            # Apply economy pressure (simplify frequent glyphs)
            if glyph.frequency > 1.5 and random.random() < self.economy_pressure:
                copied = copied.simplify()
                self.history.record(generation, 'simplification',
                                  meaning=glyph.meaning,
                                  reason='economy')
            
            new_glyphs.append(copied)
        
        self.glyphs = new_glyphs
    
    def run(self, generations: int):
        """Run evolution."""
        for gen in range(1, generations + 1):
            self.step(gen)
            
            # Periodically update frequencies (simulate usage patterns)
            if gen % 10 == 0:
                for glyph in self.glyphs:
                    # Common concepts used more
                    if glyph.meaning in ['sun', 'water', 'person', 'day']:
                        glyph.frequency *= 1.1
        
        self.history.record(generations, 'complete')
    
    def get_observable(self) -> Observable:
        """Observable: Contemporary glyph forms only."""
        languages = {
            0: {
                'writing_system': [
                    {
                        'meaning': g.meaning,
                        'form': g.to_ascii(),
                        'complexity': g.complexity(),
                        'num_strokes': len(g.strokes)
                    }
                    for g in self.glyphs
                ]
            }
        }
        
        current_time = max((e.time for e in self.history.events), default=0)
        obs = Observable(time=current_time, languages=languages)
        obs.metadata['description'] = "Contemporary writing system"
        
        return obs


def main():
    """Demonstrate glyph evolution."""
    print("=" * 70)
    print("GLYPH EVOLUTION EXPERIMENT")
    print("=" * 70)
    print()
    print("Research Question:")
    print("  How do writing systems evolve through copying errors?")
    print()
    print("Model:")
    print("  - Glyphs as stroke patterns")
    print("  - Copying introduces errors")
    print("  - Economy pressure simplifies frequent glyphs")
    print("  - NO phonological component (purely visual)")
    print()
    
    # Create experiment
    print("Initializing writing system...")
    evolution = GlyphEvolution(
        num_glyphs=10,
        error_rate=0.15,
        economy_pressure=0.3,
        seed=42
    )
    
    print(f"  {evolution.num_glyphs} proto-glyphs")
    print(f"  Error rate: {evolution.error_rate}")
    print()
    
    # Show initial state
    print("Proto-Writing System (Generation 0):")
    print()
    for glyph in evolution.glyphs:
        print(f"  {glyph.to_ascii()} {glyph.meaning:12s} ({len(glyph.strokes)} strokes, complexity: {glyph.complexity():.1f})")
    print()
    
    initial_complexity = sum(g.complexity() for g in evolution.glyphs) / len(evolution.glyphs)
    print(f"Average complexity: {initial_complexity:.2f}")
    print()
    
    # Evolve
    generations = 50
    print(f"Running {generations} generations of copying...")
    evolution.run(generations)
    print()
    
    # Show final state
    print("=" * 70)
    print("CONTEMPORARY WRITING SYSTEM (Generation 50)")
    print("=" * 70)
    print()
    
    for glyph in evolution.glyphs:
        print(f"  {glyph.to_ascii()} {glyph.meaning:12s} ({len(glyph.strokes)} strokes, complexity: {glyph.complexity():.1f})")
    print()
    
    final_complexity = sum(g.complexity() for g in evolution.glyphs) / len(evolution.glyphs)
    print(f"Average complexity: {final_complexity:.2f}")
    print(f"Change: {final_complexity - initial_complexity:+.2f} ({(final_complexity/initial_complexity - 1)*100:+.1f}%)")
    print()
    
    # Analyze changes
    print("Evolutionary Events:")
    copying_errors = [e for e in evolution.history.events if e.event_type == 'copying_error']
    simplifications = [e for e in evolution.history.events if e.event_type == 'simplification']
    
    print(f"  Copying errors: {len(copying_errors)}")
    print(f"  Simplifications: {len(simplifications)}")
    print()
    
    # Show examples
    if simplifications:
        print("Example simplifications:")
        for event in simplifications[:3]:
            print(f"  {event.data['meaning']:12s}: complexity {event.data['old_complexity']:.1f} → {event.data['new_complexity']:.1f}")
        print()
    
    # Observable vs History
    print("=" * 70)
    print("H → O_t → Ĥ PROTOCOL")
    print("=" * 70)
    print()
    
    evolution.get_observable()
    
    print("Ground Truth (H) contains:")
    print("  - Proto-glyphs (original pictographic forms)")
    print(f"  - {len(copying_errors)} copying errors")
    print(f"  - {len(simplifications)} economy-driven simplifications")
    print("  - Complete glyph genealogy")
    print()
    
    print("Observable (O_t) contains:")
    print("  - Contemporary glyph forms only")
    print("  - Current stroke counts")
    print("  - NO ancestral forms")
    print("  - NO copying history")
    print()
    
    print("Reconstruction Challenge:")
    print("  Can we infer from contemporary forms:")
    print("    - Which glyphs descended from common ancestors?")
    print("    - What the proto-glyphs looked like?")
    print("    - Which simplifications occurred?")
    print("    - The order of changes?")
    print()
    
    print("Key Insight:")
    print("  Writing systems evolve through VISUAL transmission,")
    print("  not phonological. The selective pressures are:")
    print("    - Production economy (faster writing)")
    print("    - Differentiation (avoid ambiguity)")
    print("    - Copying fidelity (transmission errors)")
    print()
    print("  This is a DIFFERENT evolutionary substrate than")
    print("  spoken language, but similar H → O_t → Ĥ protocol.")
    print()


if __name__ == '__main__':
    main()
