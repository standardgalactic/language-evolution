"""
Reconstruction Adapter: Convert systematic_reconstruction output to recoverability metrics format

Bridges systematic_reconstruction.py output → recoverability_metrics.py input.

ACTUAL STRUCTURE (confirmed via inspection):
- Tree is NOT a hierarchical object, just metadata: {'type', 'closest_pair', 'distance', 'all_languages'}
- Correspondences are counts (int), not detailed patterns
- Proto-forms are in result.proto_language['vocabulary']
"""

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from typing import Dict, List, Set
from language_evolution.framework import Reconstruction as FrameworkReconstruction
from recoverability_metrics import Reconstruction


class AdapterExtractionError(Exception):
    """Raised when adapter produces suspiciously empty output."""
    pass


def extract_clusters_from_tree(result: FrameworkReconstruction, config_label: str) -> Dict[int, int]:
    """
    Extract language clustering from reconstruction tree metadata.
    
    ACTUAL STRUCTURE: tree = {'type': 'binary_tree', 'closest_pair': (lang1, lang2), 
                              'distance': float, 'all_languages': [ids...]}
    
    Strategy: Use closest_pair to group languages. If distance < threshold,
    put pair in same cluster; otherwise all separate.
    
    CRITICAL: This is a MINIMAL tree representation - systematic_reconstruction
    doesn't build a full dendrogram, just identifies closest pair.
    """
    tree = result.metadata.get('tree', {})
    all_languages = tree.get('all_languages', [])
    
    if not all_languages:
        raise AdapterExtractionError(
            f"[{config_label}] tree metadata missing 'all_languages' - "
            f"reconstruction returned no language list"
        )
    
    clusters = {}
    closest_pair = tree.get('closest_pair')
    distance = tree.get('distance', float('inf'))
    
    # Clustering threshold - if closest pair distance < this, group them
    DISTANCE_THRESHOLD = 0.5
    
    if closest_pair and distance < DISTANCE_THRESHOLD:
        # Put closest pair in cluster 0, others each get their own
        lang1, lang2 = closest_pair
        cluster_id = 1
        
        for lang_id in all_languages:
            if lang_id == lang1 or lang_id == lang2:
                clusters[lang_id] = 0  # Paired cluster
            else:
                clusters[lang_id] = cluster_id
                cluster_id += 1
    else:
        # No meaningful grouping - each language separate
        for i, lang_id in enumerate(all_languages):
            clusters[lang_id] = i
    
    return clusters


def extract_correspondences_from_result(result: FrameworkReconstruction, config_label: str) -> List[Dict]:
    """
    Extract sound correspondences from reconstruction.
    
    ACTUAL STRUCTURE: 
    - result.inferred_events: list (currently empty in practice)
    - result.metadata['systematic_correspondences']: int (count, not patterns)
    - result.metadata['total_correspondences']: int (count, not patterns)
    
    LIMITATION: systematic_reconstruction doesn't expose detailed correspondence
    patterns (which phonemes, which languages, etc.) in current implementation.
    We can only detect WHETHER correspondences were found, not their details.
    
    For now: return empty list if no correspondences found, which will
    correctly score as correspondence=0.0 when ground truth exists.
    """
    correspondences = []
    
    # Check if ANY correspondences were detected
    systematic_count = result.metadata.get('systematic_correspondences', 0)
    total_count = result.metadata.get('total_correspondences', 0)
    
    # If reconstruction found correspondences but we can't extract details,
    # at least flag it
    if systematic_count > 0 or total_count > 0:
        # Correspondence was detected but details not exposed
        # For scoring purposes, this is better than nothing
        # Add a placeholder that at least indicates "something was found"
        correspondences.append({
            'pattern': 'detected_but_not_detailed',
            'affected_agents': [],  # Not exposed by systematic_reconstruction
            'frequency': systematic_count,
        })
    
    # Check inferred_events (usually empty)
    if hasattr(result, 'inferred_events'):
        for event in result.inferred_events:
            if isinstance(event, dict) and event.get('type') == 'sound_correspondence':
                correspondences.append({
                    'pattern': event.get('pattern', ''),
                    'affected_agents': event.get('languages', []),
                    'frequency': event.get('frequency', 0),
                })
    
    return correspondences


def adapt_reconstruction(result: FrameworkReconstruction, config_label: str = "unknown") -> Reconstruction:
    """
    Convert systematic_reconstruction output to recoverability_metrics format.
    
    Args:
        result: Reconstruction from systematic_reconstruction
        config_label: Config name (for error messages)
        
    Returns:
        Reconstruction with clusters, correspondences, proto_forms
        
    Raises:
        AdapterExtractionError: If extraction produces suspiciously empty results
    """
    # Extract clusters
    clusters = extract_clusters_from_tree(result, config_label)
    
    if not clusters:
        raise AdapterExtractionError(
            f"[{config_label}] extract_clusters_from_tree returned empty - "
            f"tree structure: {result.metadata.get('tree')}"
        )
    
    # Extract correspondences (may be empty legitimately if no sound change)
    correspondences = extract_correspondences_from_result(result, config_label)
    
    # Warn if sound change was ON but no correspondences found
    if 'S' in config_label and not correspondences:
        # Not fatal - might be genuine failure to detect - but log it
        import warnings
        warnings.warn(
            f"[{config_label}] Sound change enabled but no correspondences extracted. "
            f"Systematic count: {result.metadata.get('systematic_correspondences', 0)}"
        )
    
    # Extract proto-forms
    proto_forms = {}
    if hasattr(result, 'proto_language') and result.proto_language:
        proto_forms = result.proto_language.get('vocabulary', {})
    
    return Reconstruction(
        clusters=clusters,
        correspondences=correspondences,
        proto_forms=proto_forms,
    )


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/bonobo/github/language-evolution/src')
    sys.path.insert(0, '/home/bonobo/github/language-evolution/experiments')
    
    from language_earth import LanguageEarth, MechanismConfig
    from systematic_reconstruction import SystematicCorrespondenceReconstructor
    from language_evolution.framework import Observable
    from recoverability_metrics import (
        measure_recoverability, extract_ground_truth_from_history,
        add_founding_lineages
    )
    
    print("Testing reconstruction adapter...\n")
    
    # Create test case
    sim = LanguageEarth(world_size=(8, 8), num_agents=6, seed=42,
                        config=MechanismConfig(migration=True, sound_change=True, 
                                              borrowing=False, reproduction=True))
    for t in range(1, 31):
        sim.step(t)
    
    # Extract observable
    obs = sim.extract_observable(include_lineage=False)
    adapted_obs = Observable(
        time=obs.time,
        languages={
            lid: {'vocabulary': [{'meaning': m, 'form': f}
                                for m, f in ld['vocabulary'].items()]}
            for lid, ld in obs.languages.items()
        }
    )
    
    # Reconstruct
    reconstructor = SystematicCorrespondenceReconstructor(min_correspondence_frequency=1)
    result = reconstructor.reconstruct(adapted_obs)
    
    # Adapt
    reconstruction = adapt_reconstruction(result)
    
    print(f"Clusters: {reconstruction.clusters}")
    print(f"Correspondences: {len(reconstruction.correspondences)}")
    print(f"Proto-forms: {len(reconstruction.proto_forms)}")
    
    # Extract ground truth
    gt = extract_ground_truth_from_history(sim.history)
    gt = add_founding_lineages(gt, list(range(6)))
    
    print(f"\nGround truth:")
    print(f"  Lineages: {gt.lineages}")
    print(f"  Regional changes: {len(gt.regional_sound_changes)}")
    
    # Measure
    scores = measure_recoverability(reconstruction, gt)
    print(f"\nRecoverability:")
    print(scores.summary())
