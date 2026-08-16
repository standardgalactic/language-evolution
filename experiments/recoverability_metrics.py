"""
Recoverability Metrics for Language Evolution Reconstruction

Three-way decomposition:
1. Topology recoverability - did we recover the tree structure?
2. Correspondence recoverability - did we identify systematic sound laws?
3. Form recoverability - how close are reconstructed proto-forms?

This separates structural preservation (equivalence classes) from
exact reconstruction (specific representatives).
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
from sklearn.metrics import adjusted_rand_score
import numpy as np
from collections import defaultdict


@dataclass
class Reconstruction:
    """Expected output from comparative method."""
    clusters: Dict[int, int]  # lang_id -> cluster_id
    correspondences: List[Dict]  # [{'pattern': str, 'affected_agents': List[int], ...}]
    proto_forms: Dict[str, str]  # meaning -> reconstructed form


@dataclass
class GroundTruth:
    """Extracted from history.events."""
    lineages: Dict[int, int]  # agent_id -> lineage_root (true clusters)
    regional_sound_changes: List[Dict]  # [{'region_id': int, 'affected_agents': List[int], ...}]
    proto_vocab: Dict[str, str]  # meaning -> true proto-form


@dataclass
class RecoverabilityScores:
    """Three-way recoverability measurement."""
    topology: float  # 0-1, Adjusted Rand Index on clustering
    correspondence: float  # 0-1, overlap of affected-agent sets
    form_exact: float  # 0-1, exact proto-form match rate
    form_similarity: float  # 0-1, average edit-distance similarity
    
    def summary(self) -> str:
        return (
            f"Topology:       {self.topology:.3f}\n"
            f"Correspondence: {self.correspondence:.3f}\n"
            f"Form (exact):   {self.form_exact:.3f}\n"
            f"Form (similar): {self.form_similarity:.3f}"
        )


def topology_recoverability(
    reconstruction: Reconstruction,
    ground_truth: GroundTruth,
) -> float:
    """
    Measures clustering accuracy using Adjusted Rand Index.
    
    ARI corrects for chance agreement — important when cluster sizes
    are skewed (some lineages reproduce more than others).
    
    Returns:
        float in [-1, 1], where 1 = perfect agreement, 0 = random,
        negative = worse than random (shouldn't happen)
    """
    # Get common agent set
    common_agents = set(reconstruction.clusters.keys()) & set(ground_truth.lineages.keys())
    if not common_agents:
        return 0.0
    
    # Extract labels for common agents
    inferred = [reconstruction.clusters[aid] for aid in sorted(common_agents)]
    true = [ground_truth.lineages[aid] for aid in sorted(common_agents)]
    
    ari = adjusted_rand_score(true, inferred)
    return max(0.0, ari)  # Clamp negative to 0 (shouldn't happen with real data)


def correspondence_recoverability(
    reconstruction: Reconstruction,
    ground_truth: GroundTruth,
) -> float:
    """
    Measures how well inferred sound correspondences match true regional changes.
    
    Key design: scores on affected-agent overlap, not symbol identity.
    A method that gets "who changed together" right but mislabels which
    phoneme shifted still scores well.
    
    Matching strategy:
    - For each true regional change, find best-matching inferred correspondence
      (highest Jaccard similarity of affected-agent sets)
    - Average across all true changes
    - Small bonus (+10%) if pattern text also matches
    
    Returns:
        float in [0, 1], where 1 = all regional changes recovered
    """
    if not ground_truth.regional_sound_changes:
        # No changes to recover
        return 1.0 if not reconstruction.correspondences else 0.5
    
    if not reconstruction.correspondences:
        # Changes exist but none inferred
        return 0.0
    
    scores = []
    
    for true_change in ground_truth.regional_sound_changes:
        true_agents = set(true_change['affected_agents'])
        
        # Find best-matching inferred correspondence
        best_overlap = 0.0
        best_pattern_match = False
        
        for inferred_corr in reconstruction.correspondences:
            inferred_agents = set(inferred_corr.get('affected_agents', []))
            
            if not (true_agents | inferred_agents):
                continue
            
            # Jaccard similarity
            intersection = len(true_agents & inferred_agents)
            union = len(true_agents | inferred_agents)
            overlap = intersection / union if union > 0 else 0.0
            
            # Check pattern match (optional bonus)
            pattern_match = (
                true_change.get('change') == inferred_corr.get('pattern')
            )
            
            if overlap > best_overlap or (overlap == best_overlap and pattern_match):
                best_overlap = overlap
                best_pattern_match = pattern_match
        
        # Score this true change
        score = best_overlap
        if best_pattern_match:
            score = min(1.0, score * 1.1)  # 10% bonus for pattern match
        
        scores.append(score)
    
    return np.mean(scores) if scores else 0.0


def edit_distance(s1: str, s2: str) -> int:
    """Levenshtein distance."""
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def edit_similarity(s1: str, s2: str) -> float:
    """Edit distance normalized to [0, 1], where 1 = identical."""
    if not s1 and not s2:
        return 1.0
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1.0 - (edit_distance(s1, s2) / max_len)


def form_recoverability(
    reconstruction: Reconstruction,
    ground_truth: GroundTruth,
) -> Tuple[float, float]:
    """
    Measures proto-form reconstruction accuracy.
    
    Returns both:
    - exact_match: proportion of forms reconstructed character-perfectly
    - similarity: average edit-distance similarity (0-1)
    
    This separates the strict metric (original 0% result) from the
    softer metric (the 60% the critical-analysis doc mentioned).
    """
    common_meanings = set(reconstruction.proto_forms.keys()) & set(ground_truth.proto_vocab.keys())
    
    if not common_meanings:
        return 0.0, 0.0
    
    exact_matches = 0
    similarities = []
    
    for meaning in common_meanings:
        inferred = reconstruction.proto_forms[meaning]
        true = ground_truth.proto_vocab[meaning]
        
        if inferred == true:
            exact_matches += 1
        
        sim = edit_similarity(inferred, true)
        similarities.append(sim)
    
    exact_rate = exact_matches / len(common_meanings)
    avg_similarity = np.mean(similarities) if similarities else 0.0
    
    return exact_rate, avg_similarity


def measure_recoverability(
    reconstruction: Reconstruction,
    ground_truth: GroundTruth,
) -> RecoverabilityScores:
    """
    Main entry point: compute all three recoverability metrics.
    
    Separates:
    - Structural preservation (topology, correspondence)
    - Exact reconstruction (form exact/similar)
    
    This decomposition reveals which layers of information survive
    the H → O_t → Ĥ projection.
    """
    topo = topology_recoverability(reconstruction, ground_truth)
    corr = correspondence_recoverability(reconstruction, ground_truth)
    form_exact, form_sim = form_recoverability(reconstruction, ground_truth)
    
    return RecoverabilityScores(
        topology=topo,
        correspondence=corr,
        form_exact=form_exact,
        form_similarity=form_sim,
    )


# ============================================================================
# Ground Truth Extraction
# ============================================================================

def extract_ground_truth_from_history(history) -> GroundTruth:
    """
    Extract ground truth from LanguageEarth history.events.
    
    Returns:
        GroundTruth with:
        - lineages: agent_id -> lineage_root (from 'birth' events)
        - regional_sound_changes: list of regional change events
        - proto_vocab: original proto-language vocabulary
    """
    # Extract lineages from birth events
    lineages = {}
    for event in history.events:
        if event.event_type == 'birth':
            child_id = event.data.get('child_id')
            lineage_root = event.data.get('lineage_root')
            if child_id is not None and lineage_root is not None:
                lineages[child_id] = lineage_root
    
    # For founding agents (no birth event), lineage_root = agent_id
    # This requires access to initial agent set; assume caller handles it
    # or we add them with a separate method
    
    # Extract regional sound changes
    regional_changes = []
    for event in history.events:
        if event.event_type == 'regional_sound_change':
            regional_changes.append({
                'region_id': event.data.get('region_id'),
                'change': event.data.get('change'),
                'affected_agents': event.data.get('affected_agents', []),
                'time': event.time,
            })
    
    # Proto-vocab: assume we stored it separately or reconstruct from earliest state
    # For now, hardcode the standard 5-word vocabulary as placeholder
    proto_vocab = {
        'water': 'apa',
        'fire': 'ita',
        'stone': 'kuta',
        'sun': 'tapa',
        'tree': 'pitu',
    }
    
    return GroundTruth(
        lineages=lineages,
        regional_sound_changes=regional_changes,
        proto_vocab=proto_vocab,
    )


def add_founding_lineages(ground_truth: GroundTruth, founding_agents: List[int]) -> GroundTruth:
    """
    Add lineage_root = agent_id for all founding agents.
    
    Founding agents don't have birth events (they start at t=0),
    so their lineage must be added manually.
    """
    for agent_id in founding_agents:
        if agent_id not in ground_truth.lineages:
            ground_truth.lineages[agent_id] = agent_id
    
    return ground_truth


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    # Mock data for testing
    
    # Suppose 5 agents split into 2 lineages: {0,1,2} and {3,4}
    ground_truth = GroundTruth(
        lineages={0: 0, 1: 0, 2: 0, 3: 3, 4: 3},
        regional_sound_changes=[
            {'region_id': 0, 'change': 'p→b', 'affected_agents': [0, 1, 2]},
            {'region_id': 3, 'change': 't→d', 'affected_agents': [3, 4]},
        ],
        proto_vocab={'water': 'apa', 'fire': 'ita'},
    )
    
    # Reconstruction got topology perfect, correspondences ~80%, forms ~50%
    reconstruction = Reconstruction(
        clusters={0: 0, 1: 0, 2: 0, 3: 1, 4: 1},  # Perfect clustering
        correspondences=[
            {'pattern': 'p→b', 'affected_agents': [0, 1]},  # Missing agent 2
            {'pattern': 't→d', 'affected_agents': [3, 4]},  # Perfect
        ],
        proto_forms={
            'water': 'apa',   # Perfect
            'fire': 'itaa',   # Extra 'a'
        },
    )
    
    scores = measure_recoverability(reconstruction, ground_truth)
    
    print("=== Recoverability Scores ===\n")
    print(scores.summary())
    print("\nInterpretation:")
    print(f"  Topology perfect (ARI={scores.topology:.3f})")
    print(f"  Correspondences mostly recovered ({scores.correspondence:.1%})")
    print(f"  Forms close but not exact (exact={scores.form_exact:.1%}, similar={scores.form_similarity:.1%})")
