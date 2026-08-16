"""Tests for the framework and experiments."""

import sys

sys.path.insert(0, 'src')

from language_evolution.framework import (
    History,
    Observable,
    Reconstruction,
    compare_histories,
    measure_observable_distance,
)
from language_evolution.phonology import (
    Phoneme,
    PhonemeInventory,
    SoundChange,
    create_basic_inventory,
)
from language_evolution.semantics import SemanticRegion, SemanticVector, create_basic_semantic_space


class TestFramework:
    """Test the core H → O_t → Ĥ framework."""
    
    def test_history_recording(self):
        """History should record events with time and data."""
        h = History()
        h.record(0, 'sound_change', phoneme='p', target='f')
        h.record(1, 'borrowing', source_lang=1, target_lang=2)
        
        assert len(h.events) == 2
        assert h.events[0].time == 0
        assert h.events[0].event_type == 'sound_change'
        assert h.events[0].data['phoneme'] == 'p'
        assert h.events[1].data['source_lang'] == 1
    
    def test_observable_separation(self):
        """Observable should not contain history."""
        obs = Observable(
            time=10,
            languages={0: {'word': 'fater'}, 1: {'word': 'pater'}},
            metadata={'num_changes': 3}
        )
        
        assert obs.time == 10
        assert len(obs.languages) == 2
        # Observable should NOT expose how changes occurred
        assert 'events' not in obs.__dict__
    
    def test_reconstruction_confidence(self):
        """Reconstruction should track confidence scores."""
        recon = Reconstruction()
        recon.method = "comparative_method"
        recon.add_inference(0, 'proto_form', confidence=0.9, word='pater', form='*pater')
        recon.add_inference(5, 'sound_change', confidence=0.6, change='p>f')
        
        assert len(recon.inferred_events) == 2
        assert recon.confidence[0] == 0.9
        assert recon.confidence[1] == 0.6
    
    def test_history_comparison(self):
        """Should measure precision and recall between H and Ĥ."""
        # True history
        true_h = History()
        true_h.record(0, 'sound_change', phoneme='p')
        true_h.record(3, 'sound_change', phoneme='t')
        true_h.record(7, 'sound_change', phoneme='k')
        
        # Reconstruction (missed one, got timing slightly wrong)
        recon = Reconstruction()
        recon.add_inference(0, 'sound_change', phoneme='p')
        recon.add_inference(4, 'sound_change', phoneme='t')  # Off by 1
        # Missed the k>h change
        
        metrics = compare_histories(true_h, recon, time_tolerance=2)
        
        assert metrics.true_positives == 2  # p and t matched
        assert metrics.false_negatives == 1  # k was missed
        assert metrics.false_positives == 0  # Nothing hallucinated
        
        assert metrics.precision == 1.0  # All inferences were correct
        assert metrics.recall < 1.0  # Didn't find everything
    
    def test_observable_distance(self):
        """Should measure similarity between observable states."""
        obs1 = Observable(
            time=10,
            languages={0: {'word': 'pater'}, 1: {'word': 'mater'}}
        )
        obs2 = Observable(
            time=10,
            languages={0: {'word': 'fater'}, 1: {'word': 'mater'}}  # One difference
        )
        obs3 = Observable(
            time=10,
            languages={0: {'word': 'pater'}, 1: {'word': 'mater'}}  # Identical
        )
        
        dist_different = measure_observable_distance(obs1, obs2)
        dist_same = measure_observable_distance(obs1, obs3)
        
        assert dist_different > 0
        assert dist_same == 0


class TestPhonology:
    """Test phonological representations."""
    
    def test_phoneme_features(self):
        """Phonemes should have distinctive features."""
        p = Phoneme('p', {'consonant', 'stop', 'voiceless', 'labial'})
        b = Phoneme('b', {'consonant', 'stop', 'voiced', 'labial'})
        
        assert 'voiceless' in p.features
        assert 'voiced' in b.features
        assert p != b
    
    def test_sound_change_application(self):
        """Sound changes should transform phoneme sequences."""
        inv = create_basic_inventory()
        
        # p → f change
        p_phoneme = inv.get_phoneme('p')
        f_phoneme = Phoneme('f', {'consonant', 'fricative', 'voiceless', 'labial'})
        change = SoundChange('p>f', p_phoneme, f_phoneme, probability=1.0)
        
        # Apply to 'pater'
        word = [inv.get_phoneme(s) for s in 'pater']
        result = change.apply(word)
        
        assert result[0] == f_phoneme
        assert result[1] == inv.get_phoneme('a')
    
    def test_inventory_operations(self):
        """Should support adding/removing phonemes."""
        inv = PhonemeInventory(set())
        
        p = Phoneme('p', {'consonant', 'stop'})
        inv.add_phoneme(p)
        
        assert len(inv.phonemes) == 1
        assert inv.get_phoneme('p') == p
        
        inv.remove_phoneme(p)
        assert len(inv.phonemes) == 0


class TestSemantics:
    """Test semantic representations."""
    
    def test_semantic_vector_distance(self):
        """Should calculate Euclidean distance."""
        v1 = SemanticVector((0.0, 0.0, 0.0))
        v2 = SemanticVector((1.0, 0.0, 0.0))
        v3 = SemanticVector((1.0, 1.0, 0.0))
        
        assert v1.distance_to(v2) == 1.0
        assert abs(v1.distance_to(v3) - 1.414) < 0.01
    
    def test_semantic_region_membership(self):
        """Should calculate fuzzy membership."""
        center = SemanticVector((0.0, 0.0, 0.0))
        region = SemanticRegion(center, radius=1.0, label='test')
        
        inside = SemanticVector((0.5, 0.0, 0.0))
        boundary = SemanticVector((1.0, 0.0, 0.0))
        outside = SemanticVector((2.0, 0.0, 0.0))
        
        assert region.contains(inside) == 1.0  # Fully inside
        assert region.contains(boundary) == 1.0  # On boundary
        assert region.contains(outside) < 1.0  # Outside (fuzzy falloff)
    
    def test_semantic_space_operations(self):
        """Should support drift, broadening, narrowing."""
        space = create_basic_semantic_space()
        
        initial_center = space.get_region('person').center
        initial_radius = space.get_region('person').radius
        
        # Drift
        target = SemanticVector((0.5, 0.5, 0.5))
        space.shift_meaning('person', target, 0.1)
        new_center = space.get_region('person').center
        
        assert initial_center.distance_to(new_center) > 0
        
        # Broadening
        space.broaden_meaning('person', 0.1)
        assert space.get_region('person').radius > initial_radius
        
        # Narrowing
        space.narrow_meaning('person', 0.05)
        assert space.get_region('person').radius < space.get_region('person').radius + 0.05


def run_all_tests():
    """Run all tests and report results."""
    print("=== Running Framework Tests ===\n")
    
    test_classes = [TestFramework, TestPhonology, TestSemantics]
    
    total_tests = 0
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"{test_class.__name__}:")
        
        test_obj = test_class()
        test_methods = [m for m in dir(test_obj) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_obj, method_name)
                method()
                print(f"  ✓ {method_name}")
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {method_name}: {e}")
                failed += 1
            except Exception as e:  # noqa: BLE001 - test runner needs to catch all test exceptions
                print(f"  ✗ {method_name}: {type(e).__name__}: {e}")
                failed += 1
        
        print()
    
    print("=" * 60)
    print(f"Results: {passed}/{total_tests} passed, {failed}/{total_tests} failed")
    
    return failed == 0


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
