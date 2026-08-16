"""
Ablation Study for Language Earth Mechanisms

Tests which mechanism combinations affect each layer of recoverability:
- Topology (tree structure)
- Correspondence (sound law patterns)
- Form (proto-language reconstruction)

Design: 8 configurations × multiple seeds
- Divergence only (D): baseline drift
- +Sound change (DS): regional systematic changes
- +Borrowing (DB): contact-induced convergence
- +Reproduction (DR): population branching
- Full combinations: DSB, DSR, DBR, DSBR

Expected findings:
- Borrowing should wreck correspondence recovery (breaks regularity)
- Reproduction affects topology measurement (creates actual tree)
- Sound change should preserve topology, affect forms
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')
sys.path.insert(0, '/home/bonobo/github/language-evolution/experiments')

from language_earth import LanguageEarth, LanguageState
from recoverability_metrics import (
    Reconstruction, GroundTruth, RecoverabilityScores,
    measure_recoverability, extract_ground_truth_from_history,
    add_founding_lineages
)
from systematic_reconstruction import SystematicCorrespondenceReconstructor
from language_evolution.framework import Observable
import numpy as np


@dataclass
class MechanismConfig:
    """Controls which mechanisms are active in simulation."""
    migration: bool = True  # Always on (baseline)
    sound_change: bool = False
    borrowing: bool = False
    reproduction: bool = False
    
    def label(self) -> str:
        """Short label for this config."""
        parts = []
        if self.migration:
            parts.append('M')  # Migration (always on)
        if self.sound_change:
            parts.append('S')
        if self.borrowing:
            parts.append('B')
        if self.reproduction:
            parts.append('R')
        return ''.join(parts) if parts else 'None'
    
    def description(self) -> str:
        """Human-readable description."""
        active = []
        if self.migration:
            active.append('migration')
        if self.sound_change:
            active.append('regional sound change')
        if self.borrowing:
            active.append('borrowing')
        if self.reproduction:
            active.append('reproduction')
        
        return ' + '.join(active) if active else 'no mechanisms'


# Standard ablation configurations
ABLATION_CONFIGS = [
    MechanismConfig(migration=True, sound_change=False, borrowing=False, reproduction=False),  # M (baseline)
    MechanismConfig(migration=True, sound_change=True, borrowing=False, reproduction=False),   # MS
    MechanismConfig(migration=True, sound_change=False, borrowing=True, reproduction=False),   # MB
    MechanismConfig(migration=True, sound_change=False, borrowing=False, reproduction=True),   # MR
    MechanismConfig(migration=True, sound_change=True, borrowing=True, reproduction=False),    # MSB
    MechanismConfig(migration=True, sound_change=True, borrowing=False, reproduction=True),    # MSR
    MechanismConfig(migration=True, sound_change=False, borrowing=True, reproduction=True),    # MBR
    MechanismConfig(migration=True, sound_change=True, borrowing=True, reproduction=True),     # MSBR (full)
]


def run_simulation_with_config(
    config: MechanismConfig,
    seed: int,
    world_size: Tuple[int, int] = (10, 10),
    num_agents: int = 10,
    n_steps: int = 50,
) -> Tuple[LanguageEarth, Observable]:
    """
    Run Language Earth with specific mechanism configuration.
    
    Returns:
        (simulation, observable) - the completed simulation and final state
    """
    sim = LanguageEarth(
        world_size=world_size,
        num_agents=num_agents,
        seed=seed,
        config=config,  # Pass config to control mechanisms
    )
    
    for t in range(1, n_steps + 1):
        sim.step(t)
    
    obs = sim.extract_observable(include_lineage=False)  # Tree-blind reconstruction
    
    return sim, obs


def adapt_observable_format(obs: Observable) -> Observable:
    """Convert Language Earth observable to systematic_reconstruction format."""
    return Observable(
        time=obs.time,
        languages={
            lang_id: {
                'vocabulary': [
                    {'meaning': meaning, 'form': form}
                    for meaning, form in lang_data['vocabulary'].items()
                ]
            }
            for lang_id, lang_data in obs.languages.items()
        }
    )


def run_comparative_method(obs: Observable) -> Reconstruction:
    """
    Run comparative method on observable.
    
    This is a wrapper around systematic_reconstruction.py that returns
    the Reconstruction format expected by recoverability_metrics.py.
    
    TODO: Adapt systematic_reconstruction output to this format.
    For now, returns a mock reconstruction for testing.
    """
    reconstructor = SystematicCorrespondenceReconstructor(min_correspondence_frequency=1)
    result = reconstructor.reconstruct(obs)
    
    # Extract clusters from tree structure
    clusters = {}
    if result.metadata.get('tree') and result.metadata['tree'].get('closest_pair'):
        # Simple heuristic: languages are clustered if they're the closest pair
        # In reality, need to extract full tree clustering
        # For now, assign each language to its own cluster
        for lang_id in obs.languages.keys():
            clusters[lang_id] = lang_id
    else:
        for lang_id in obs.languages.keys():
            clusters[lang_id] = lang_id
    
    # Extract correspondences from inferred events
    correspondences = []
    if hasattr(result, 'inferred_events'):
        for event in result.inferred_events:
            if event.get('type') == 'sound_correspondence':
                correspondences.append({
                    'pattern': event.get('pattern', ''),
                    'affected_agents': event.get('examples', []),  # Placeholder
                    'frequency': event.get('frequency', 0),
                })
    
    # Extract proto-forms
    proto_forms = {}
    if hasattr(result, 'proto_language') and result.proto_language:
        proto_forms = result.proto_language.get('vocabulary', {})
    
    return Reconstruction(
        clusters=clusters,
        correspondences=correspondences,
        proto_forms=proto_forms,
    )


def extract_ground_truth(sim: LanguageEarth) -> GroundTruth:
    """Extract ground truth from completed simulation."""
    gt = extract_ground_truth_from_history(sim.history)
    
    # Add founding agents (those present at t=0)
    founding_agents = list(range(sim.config_num_agents if hasattr(sim, 'config_num_agents') else 10))
    gt = add_founding_lineages(gt, founding_agents)
    
    return gt


def run_ablation_trial(
    config: MechanismConfig,
    seed: int,
    n_steps: int = 50,
    verbose: bool = False,
) -> RecoverabilityScores:
    """
    Single ablation trial: run sim → reconstruct → measure.
    
    Returns:
        RecoverabilityScores for this config+seed
    """
    if verbose:
        print(f"  Running {config.label()} (seed {seed})...", end=' ')
    
    # Run simulation
    sim, obs = run_simulation_with_config(config, seed, n_steps=n_steps)
    
    # Adapt observable format
    adapted_obs = adapt_observable_format(obs)
    
    # Run reconstruction
    reconstruction = run_comparative_method(adapted_obs)
    
    # Extract ground truth
    ground_truth = extract_ground_truth(sim)
    
    # Measure recoverability
    scores = measure_recoverability(reconstruction, ground_truth)
    
    if verbose:
        print(f"T={scores.topology:.2f} C={scores.correspondence:.2f} " +
              f"F={scores.form_exact:.2f}/{scores.form_similarity:.2f}")
    
    return scores


def run_full_ablation_study(
    configs: List[MechanismConfig] = ABLATION_CONFIGS,
    seeds: List[int] = [42, 43, 44, 45, 46],
    n_steps: int = 50,
    verbose: bool = True,
) -> Dict[str, List[RecoverabilityScores]]:
    """
    Run full ablation study: all configs × all seeds.
    
    Returns:
        {config_label: [scores_for_each_seed]}
    """
    results = {}
    
    for config in configs:
        if verbose:
            print(f"\n{config.label()}: {config.description()}")
        
        config_scores = []
        for seed in seeds:
            scores = run_ablation_trial(config, seed, n_steps=n_steps, verbose=verbose)
            config_scores.append(scores)
        
        results[config.label()] = config_scores
    
    return results


def summarize_ablation_results(
    results: Dict[str, List[RecoverabilityScores]]
) -> None:
    """
    Print summary table of ablation results.
    
    Format:
    Config | Topology      | Correspondence | Form (exact)  | Form (similar)
    -------|---------------|----------------|---------------|--------------
    M      | 0.95 ± 0.02   | 0.00 ± 0.00    | 1.00 ± 0.00   | 1.00 ± 0.00
    MS     | 0.93 ± 0.03   | 0.85 ± 0.05    | 0.20 ± 0.10   | 0.75 ± 0.08
    ...
    """
    print("\n" + "="*80)
    print("ABLATION STUDY RESULTS")
    print("="*80)
    print(f"{'Config':<8} | {'Topology':<13} | {'Correspondence':<15} | " +
          f"{'Form (exact)':<13} | {'Form (similar)':<13}")
    print("-" * 80)
    
    for config_label in sorted(results.keys()):
        scores_list = results[config_label]
        
        # Compute mean ± std for each metric
        topo_vals = [s.topology for s in scores_list]
        corr_vals = [s.correspondence for s in scores_list]
        form_exact_vals = [s.form_exact for s in scores_list]
        form_sim_vals = [s.form_similarity for s in scores_list]
        
        topo_mean, topo_std = np.mean(topo_vals), np.std(topo_vals)
        corr_mean, corr_std = np.mean(corr_vals), np.std(corr_vals)
        form_exact_mean, form_exact_std = np.mean(form_exact_vals), np.std(form_exact_vals)
        form_sim_mean, form_sim_std = np.mean(form_sim_vals), np.std(form_sim_vals)
        
        print(f"{config_label:<8} | {topo_mean:.2f} ± {topo_std:.2f}    | " +
              f"{corr_mean:.2f} ± {corr_std:.2f}      | " +
              f"{form_exact_mean:.2f} ± {form_exact_std:.2f}    | " +
              f"{form_sim_mean:.2f} ± {form_sim_std:.2f}")
    
    print("="*80)
    print("\nKey:")
    print("  M    = Migration only (baseline)")
    print("  S    = +Sound change")
    print("  B    = +Borrowing")
    print("  R    = +Reproduction")
    print("  MSBR = All mechanisms (full Language Earth)")


if __name__ == '__main__':
    print("="*80)
    print("LANGUAGE EARTH ABLATION STUDY")
    print("="*80)
    print("\nTesting which mechanisms affect recoverability...")
    print("(Note: This requires LanguageEarth to accept MechanismConfig)")
    print("(Integration TODO: modify LanguageEarth.__init__ and mechanism methods)")
    print()
    
    # For now, just test the framework with a single config
    print("Testing single trial...")
    config = MechanismConfig(migration=True, sound_change=True, borrowing=False, reproduction=False)
    
    try:
        scores = run_ablation_trial(config, seed=42, n_steps=20, verbose=True)
        print(f"\nResults:\n{scores.summary()}")
        print("\n✓ Framework works. Ready for full ablation once LanguageEarth integration is complete.")
    except Exception as e:
        print(f"\n✗ Integration needed: {e}")
        print("\nNext step: Modify LanguageEarth to accept and use MechanismConfig")
