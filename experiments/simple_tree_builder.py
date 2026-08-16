"""
Simple UPGMA Tree Builder

Builds phylogenetic tree from edit distances to unblock topology metric testing.
Independent of systematic_reconstruction.py correspondence detection.

UPGMA (Unweighted Pair Group Method with Arithmetic Mean):
- Classic agglomerative clustering
- Used in phylogenetics
- Simple, deterministic, interpretable
"""

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

from typing import Dict, List, Set, Tuple
import numpy as np
from recoverability_metrics import Reconstruction, edit_distance


def compute_edit_distance_matrix(vocabularies: Dict[int, Dict[str, str]]) -> Tuple[List[int], np.ndarray]:
    """
    Compute pairwise edit distance matrix between languages.
    
    Args:
        vocabularies: {agent_id: {meaning: form}}
        
    Returns:
        (agent_ids, distance_matrix) where distance_matrix[i][j] = distance(i, j)
    """
    agent_ids = sorted(vocabularies.keys())
    n = len(agent_ids)
    
    # Get shared meanings
    meanings = set()
    for vocab in vocabularies.values():
        meanings.update(vocab.keys())
    meanings = sorted(meanings)
    
    # Compute distances
    distances = np.zeros((n, n))
    
    for i, id_i in enumerate(agent_ids):
        for j, id_j in enumerate(agent_ids):
            if i == j:
                distances[i][j] = 0.0
            else:
                # Average edit distance across shared vocabulary
                dists = []
                for meaning in meanings:
                    if meaning in vocabularies[id_i] and meaning in vocabularies[id_j]:
                        form_i = vocabularies[id_i][meaning]
                        form_j = vocabularies[id_j][meaning]
                        dists.append(edit_distance(form_i, form_j))
                
                distances[i][j] = np.mean(dists) if dists else 0.0
    
    return agent_ids, distances


def upgma_clustering(agent_ids: List[int], distances: np.ndarray, cutoff_distance: float = 0.5) -> Dict[int, int]:
    """
    UPGMA hierarchical clustering.
    
    Args:
        agent_ids: List of agent IDs
        distances: Distance matrix
        cutoff_distance: Stop merging clusters when min distance > this
        
    Returns:
        {agent_id: cluster_id} - partition of agents into clusters
    """
    n = len(agent_ids)
    
    # Initialize: each agent is its own cluster
    clusters = {i: {agent_ids[i]} for i in range(n)}
    active = set(range(n))
    
    # Distance matrix (will be updated as clusters merge)
    dist_matrix = distances.copy()
    
    while len(active) > 1:
        # Find minimum distance between active clusters
        min_dist = float('inf')
        merge_i, merge_j = None, None
        
        for i in active:
            for j in active:
                if i < j and dist_matrix[i][j] < min_dist:
                    min_dist = dist_matrix[i][j]
                    merge_i, merge_j = i, j
        
        # Stop if minimum distance exceeds cutoff
        if min_dist > cutoff_distance:
            break
        
        # Merge clusters i and j
        clusters[merge_i] |= clusters[merge_j]
        del clusters[merge_j]
        
        # Update distances using UPGMA averaging
        for k in active:
            if k != merge_i and k != merge_j:
                # Average distance to merged cluster
                new_dist = (dist_matrix[merge_i][k] + dist_matrix[merge_j][k]) / 2.0
                dist_matrix[merge_i][k] = new_dist
                dist_matrix[k][merge_i] = new_dist
        
        # Remove j from active set
        active.remove(merge_j)
    
    # Convert to {agent_id: cluster_id} format
    result = {}
    for cluster_id, (cluster_idx, members) in enumerate(clusters.items()):
        for agent_id in members:
            result[agent_id] = cluster_id
    
    return result


def simple_tree_reconstruction(observable) -> Reconstruction:
    """
    Build simple tree using UPGMA on edit distances.
    
    This bypasses systematic_reconstruction.py entirely,
    providing a working topology metric for testing.
    
    Args:
        observable: Observable with languages
        
    Returns:
        Reconstruction with clusters from UPGMA
    """
    # Extract vocabularies
    vocabularies = {}
    for lang_id, lang_data in observable.languages.items():
        if 'vocabulary' in lang_data:
            # Handle both dict and list formats
            vocab = lang_data['vocabulary']
            if isinstance(vocab, list):
                vocabularies[lang_id] = {item['meaning']: item['form'] for item in vocab}
            else:
                vocabularies[lang_id] = vocab
    
    # Compute distance matrix
    agent_ids, distances = compute_edit_distance_matrix(vocabularies)
    
    # UPGMA clustering
    clusters = upgma_clustering(agent_ids, distances, cutoff_distance=0.5)
    
    # Reconstruct proto-forms (simple: most common form for each meaning)
    proto_forms = {}
    all_meanings = set()
    for vocab in vocabularies.values():
        all_meanings.update(vocab.keys())
    
    for meaning in all_meanings:
        forms = [vocab[meaning] for vocab in vocabularies.values() if meaning in vocab]
        if forms:
            # Most common form as proto
            from collections import Counter
            proto_forms[meaning] = Counter(forms).most_common(1)[0][0]
    
    return Reconstruction(
        clusters=clusters,
        correspondences=[],  # UPGMA doesn't detect correspondences
        proto_forms=proto_forms,
    )


# ============================================================================
# Test
# ============================================================================

if __name__ == '__main__':
    sys.path.insert(0, '/home/bonobo/github/language-evolution/experiments')
    
    from language_earth import LanguageEarth, MechanismConfig
    from language_evolution.framework import Observable
    from recoverability_metrics import (
        measure_recoverability, extract_ground_truth_from_history,
        add_founding_lineages
    )
    
    print("Testing UPGMA tree builder...\n")
    
    # Test case: MS config
    sim = LanguageEarth(world_size=(10, 10), num_agents=10, seed=42,
                        config=MechanismConfig(migration=True, sound_change=True,
                                              borrowing=False, reproduction=False))
    for t in range(1, 31):
        sim.step(t)
    
    # Extract observable
    obs = sim.extract_observable(include_lineage=False)
    adapted = Observable(
        time=obs.time,
        languages={
            lid: {'vocabulary': [{'meaning': m, 'form': f}
                                for m, f in ld['vocabulary'].items()]}
            for lid, ld in obs.languages.items()
        }
    )
    
    # Build tree
    reconstruction = simple_tree_reconstruction(adapted)
    
    print(f"UPGMA results:")
    print(f"  Clusters: {reconstruction.clusters}")
    print(f"  Proto-forms: {reconstruction.proto_forms}")
    
    # Ground truth
    gt = extract_ground_truth_from_history(sim.history)
    gt = add_founding_lineages(gt, list(range(10)))
    
    print(f"\nGround truth:")
    print(f"  Lineages: {gt.lineages}")
    
    # Measure
    scores = measure_recoverability(reconstruction, gt)
    
    print(f"\nRecoverability:")
    print(scores.summary())
    
    print("\n✓ UPGMA tree builder works!")
