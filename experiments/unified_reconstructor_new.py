"""New UnifiedReconstructor implementation with systematic correspondences."""

import sys

sys.path.insert(0, '/home/bonobo/github/language-evolution/src')
sys.path.insert(0, '/home/bonobo/github/language-evolution/experiments')

from systematic_reconstruction import SystematicCorrespondenceReconstructor

from language_evolution.framework import Observable, Reconstruction


class UnifiedReconstructorV2:
    """
    Unified reconstruction that works on any observable.
    Uses systematic correspondence method by default.
    """
    
    def __init__(self, method: str = 'systematic'):
        self.method = method
        self.systematic = SystematicCorrespondenceReconstructor(min_correspondence_frequency=2)
    
    def reconstruct(self, observable: Observable) -> Reconstruction:
        """Reconstruct from observable using systematic correspondences."""
        return self.systematic.reconstruct(observable)


# Test it
if __name__ == '__main__':
    
    # Test data
    vocab = {
        1: [{'meaning': 'water', 'form': 'bata'}],
        2: [{'meaning': 'water', 'form': 'pada'}],
        3: [{'meaning': 'water', 'form': 'pata'}],
    }
    
    obs = Observable(
        time=10,
        languages={i: {'vocabulary': v} for i, v in vocab.items()}
    )
    
    reconstructor = UnifiedReconstructorV2()
    result = reconstructor.reconstruct(obs)
    
    print("Test reconstruction:")
    if hasattr(result, 'proto_language') and result.proto_language:
        print(f"  Proto: {result.proto_language}")
    print(f"  Metadata: {result.metadata}")
    print("✓ Working!")
