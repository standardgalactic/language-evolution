"""Semantic representations for meaning evolution."""

import math
import random
from dataclasses import dataclass


@dataclass
class SemanticVector:
    """A point in semantic space representing word meaning."""
    dimensions: tuple[float, ...]  # Coordinates in semantic space
    
    def distance_to(self, other: 'SemanticVector') -> float:
        """Euclidean distance to another vector."""
        if len(self.dimensions) != len(other.dimensions):
            raise ValueError("Vectors must have same dimensionality")
        
        return math.sqrt(sum((a - b)**2 for a, b in zip(self.dimensions, other.dimensions)))
    
    def move_toward(self, target: 'SemanticVector', step: float) -> 'SemanticVector':
        """Move this vector toward another by step amount."""
        new_dims = tuple(
            a + step * (b - a) 
            for a, b in zip(self.dimensions, target.dimensions)
        )
        return SemanticVector(new_dims)
    
    def add_noise(self, magnitude: float) -> 'SemanticVector':
        """Add random noise to position."""
        new_dims = tuple(
            d + random.gauss(0, magnitude)
            for d in self.dimensions
        )
        return SemanticVector(new_dims)
    
    def __repr__(self):
        coords = ', '.join(f'{d:.2f}' for d in self.dimensions)
        return f"⟨{coords}⟩"


@dataclass
class SemanticRegion:
    """A region in semantic space with fuzzy boundaries."""
    center: SemanticVector
    radius: float
    label: str  # Human-readable description
    
    def contains(self, point: SemanticVector, fuzziness: float = 0.5) -> float:
        """Returns probability that point is in this region (fuzzy membership)."""
        distance = self.center.distance_to(point)
        
        # Smooth falloff from center to boundary
        if distance < self.radius:
            return 1.0
        else:
            # Exponential decay beyond boundary
            excess = distance - self.radius
            return math.exp(-excess / (self.radius * fuzziness))
    
    def overlap_with(self, other: 'SemanticRegion') -> float:
        """Measure overlap between two regions (0-1)."""
        center_distance = self.center.distance_to(other.center)
        combined_radius = self.radius + other.radius
        
        if center_distance >= combined_radius:
            return 0.0
        elif center_distance <= abs(self.radius - other.radius):
            # One region contains the other
            return 1.0
        else:
            # Partial overlap - simplified calculation
            return 1.0 - (center_distance / combined_radius)


class SemanticSpace:
    """A semantic space where word meanings exist as overlapping regions."""
    
    def __init__(self, dimensions: int = 3):
        self.dimensions = dimensions
        self.regions: dict[str, SemanticRegion] = {}
    
    def add_region(self, word_id: str, center: SemanticVector, radius: float, label: str):
        """Add a semantic region for a word."""
        self.regions[word_id] = SemanticRegion(center, radius, label)
    
    def get_region(self, word_id: str) -> SemanticRegion:
        """Get the semantic region for a word."""
        return self.regions[word_id]
    
    def find_overlapping(self, word_id: str, threshold: float = 0.3) -> list[tuple[str, float]]:
        """Find words whose regions overlap with the given word."""
        region = self.regions[word_id]
        overlaps = []
        
        for other_id, other_region in self.regions.items():
            if other_id == word_id:
                continue
            
            overlap = region.overlap_with(other_region)
            if overlap >= threshold:
                overlaps.append((other_id, overlap))
        
        return sorted(overlaps, key=lambda x: -x[1])
    
    def get_nearest_words(self, point: SemanticVector, max_words: int = 5) -> list[tuple[str, float]]:
        """Find words whose regions are nearest to a point."""
        distances = [
            (word_id, region.center.distance_to(point))
            for word_id, region in self.regions.items()
        ]
        distances.sort(key=lambda x: x[1])
        return distances[:max_words]
    
    def shift_meaning(self, word_id: str, direction: SemanticVector, magnitude: float):
        """Shift a word's meaning in semantic space."""
        region = self.regions[word_id]
        region.center = region.center.move_toward(direction, magnitude)
    
    def broaden_meaning(self, word_id: str, amount: float):
        """Broaden a word's meaning (increase region size)."""
        self.regions[word_id].radius += amount
    
    def narrow_meaning(self, word_id: str, amount: float):
        """Narrow a word's meaning (decrease region size)."""
        region = self.regions[word_id]
        region.radius = max(0.1, region.radius - amount)


def create_basic_semantic_space() -> SemanticSpace:
    """Create a basic semantic space with common concepts.
    
    Using 3D space for visualization:
    - Dimension 0: Concrete ←→ Abstract
    - Dimension 1: Positive ←→ Negative
    - Dimension 2: Animate ←→ Inanimate
    """
    space = SemanticSpace(dimensions=3)
    
    # Concrete, neutral, animate
    space.add_region(
        'person', 
        SemanticVector((0.9, 0.0, 0.9)),
        radius=0.3,
        label="human being"
    )
    
    # Concrete, neutral, inanimate
    space.add_region(
        'stone',
        SemanticVector((0.8, 0.0, 0.1)),
        radius=0.2,
        label="rock/stone"
    )
    
    # Concrete, neutral, inanimate (tool)
    space.add_region(
        'tool',
        SemanticVector((0.7, 0.0, 0.2)),
        radius=0.25,
        label="implement/instrument"
    )
    
    # Abstract, positive, inanimate
    space.add_region(
        'good',
        SemanticVector((0.2, 0.8, 0.0)),
        radius=0.4,
        label="beneficial/pleasant"
    )
    
    # Abstract, negative, inanimate
    space.add_region(
        'bad',
        SemanticVector((0.2, -0.8, 0.0)),
        radius=0.4,
        label="harmful/unpleasant"
    )
    
    # Concrete, positive, animate
    space.add_region(
        'child',
        SemanticVector((0.8, 0.4, 0.9)),
        radius=0.2,
        label="young person"
    )
    
    # Abstract, neutral, inanimate (relational)
    space.add_region(
        'part',
        SemanticVector((0.3, 0.0, 0.0)),
        radius=0.3,
        label="component/portion"
    )
    
    # Concrete, neutral, animate
    space.add_region(
        'animal',
        SemanticVector((0.9, -0.1, 0.7)),
        radius=0.3,
        label="non-human creature"
    )
    
    return space


if __name__ == '__main__':
    # Demonstration
    print("=== Semantic Space Representation ===\n")
    
    space = create_basic_semantic_space()
    
    print(f"Created semantic space with {len(space.regions)} words")
    print(f"Dimensions: {space.dimensions}\n")
    
    # Show word positions
    print("Word meanings in semantic space:")
    for word_id, region in sorted(space.regions.items()):
        print(f"  {word_id:10} {region.center} r={region.radius:.2f} [{region.label}]")
    
    # Find overlaps
    print("\nSemantic overlaps:")
    for word_id in ['person', 'good', 'tool']:
        overlaps = space.find_overlapping(word_id, threshold=0.1)
        if overlaps:
            print(f"  {word_id}:")
            for other_id, overlap in overlaps:
                print(f"    ↔ {other_id} (overlap={overlap:.2f})")
    
    # Demonstrate drift
    print("\n=== Simulating Semantic Drift ===\n")
    print("Shifting 'stone' toward 'tool' (metaphorical extension)...")
    
    original_stone = space.get_region('stone').center
    tool_center = space.get_region('tool').center
    
    space.shift_meaning('stone', tool_center, 0.3)
    
    new_stone = space.get_region('stone').center
    print(f"  Before: {original_stone}")
    print(f"  After:  {new_stone}")
    
    new_overlaps = space.find_overlapping('stone', threshold=0.1)
    print("\n  New overlaps:")
    for other_id, overlap in new_overlaps:
        print(f"    ↔ {other_id} (overlap={overlap:.2f})")
    
    print("\nBroadening 'good' (semantic expansion)...")
    original_radius = space.get_region('good').radius
    space.broaden_meaning('good', 0.2)
    new_radius = space.get_region('good').radius
    print(f"  Radius: {original_radius:.2f} → {new_radius:.2f}")
    
    new_overlaps = space.find_overlapping('good', threshold=0.1)
    print(f"  Now overlaps with: {[w for w, _ in new_overlaps]}")
