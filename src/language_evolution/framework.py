"""Core framework for the H → O_t → Ĥ experimental protocol.

This module defines the fundamental architecture:
- History (H): Complete evolution trace retained by simulator
- Observable (O_t): Evidence visible at time t
- Reconstruction (Ĥ): Inferred history from observable evidence
- Recoverability: Measuring which historical distinctions remain inferable
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar('T')


@dataclass
class HistoricalEvent:
    """A single event in the evolution history."""
    time: int
    event_type: str
    agent_id: int | None
    data: dict[str, Any]
    
    def __repr__(self):
        return f"t={self.time} {self.event_type} agent={self.agent_id}"


class History:
    """Complete retained history H.
    
    The simulator secretly keeps everything that happened. This is ground truth.
    In real historical linguistics, you never have this.
    """
    
    def __init__(self):
        self.events: list[HistoricalEvent] = []
        self.metadata: dict[str, Any] = {}
    
    def record(self, time: int, event_type: str, agent_id: int | None = None, **data):
        """Record a historical event."""
        event = HistoricalEvent(time, event_type, agent_id, data)
        self.events.append(event)
    
    def get_events_by_type(self, event_type: str) -> list[HistoricalEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_at_time(self, time: int) -> list[HistoricalEvent]:
        """Get all events at a specific time."""
        return [e for e in self.events if e.time == time]
    
    def get_events_for_agent(self, agent_id: int) -> list[HistoricalEvent]:
        """Get all events involving a specific agent."""
        return [e for e in self.events if e.agent_id == agent_id]
    
    def to_json(self) -> str:
        """Serialize history for storage/analysis."""
        data = {
            'events': [
                {
                    'time': e.time,
                    'type': e.event_type,
                    'agent': e.agent_id,
                    'data': e.data
                }
                for e in self.events
            ],
            'metadata': self.metadata
        }
        return json.dumps(data, indent=2)
    
    def __len__(self):
        return len(self.events)
    
    def __repr__(self):
        return f"History({len(self.events)} events, t=0..{max((e.time for e in self.events), default=0)})"


@dataclass
class Observable:
    """Observable evidence O_t at time t.
    
    This is what a historical linguist actually sees: contemporary languages,
    written records, geographical distribution, etc. Critical information has
    been lost.
    """
    time: int
    languages: dict[int, Any]  # agent_id -> language state
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"Observable(t={self.time}, {len(self.languages)} languages)"


class HistoryGenerator(ABC):
    """Base class for evolution simulators that generate H."""
    
    def __init__(self):
        self.history = History()
    
    @abstractmethod
    def step(self, time: int):
        """Simulate one time step, recording all events to history."""
    
    @abstractmethod
    def get_observable(self, time: int) -> Observable:
        """Extract observable evidence at time t, hiding internal history."""
    
    def run(self, num_steps: int) -> tuple[History, Observable]:
        """Run simulation and return both H and O_t."""
        for t in range(num_steps):
            self.step(t)
        
        observable = self.get_observable(num_steps - 1)
        return self.history, observable


class Reconstruction:
    """Reconstructed history Ĥ.
    
    This is what the inference algorithm thinks happened, based only on O_t.
    """
    
    def __init__(self):
        self.inferred_events: list[HistoricalEvent] = []
        self.confidence: dict[int, float] = {}  # event_index -> confidence
        self.method: str = "unknown"
    
    def add_inference(self, time: int, event_type: str, confidence: float = 1.0, 
                     agent_id: int | None = None, **data):
        """Add an inferred historical event."""
        event = HistoricalEvent(time, event_type, agent_id, data)
        idx = len(self.inferred_events)
        self.inferred_events.append(event)
        self.confidence[idx] = confidence
    
    def __len__(self):
        return len(self.inferred_events)
    
    def __repr__(self):
        return f"Reconstruction({len(self.inferred_events)} inferred events, method={self.method})"


class InferenceSystem(ABC):
    """Base class for reconstruction algorithms that produce Ĥ from O_t."""
    
    @abstractmethod
    def reconstruct(self, observable: Observable) -> Reconstruction:
        """Infer history from observable evidence."""


@dataclass
class ComparisonMetrics:
    """Metrics for comparing H and Ĥ."""
    
    # Event-level metrics
    true_positives: int = 0  # Correctly inferred events
    false_positives: int = 0  # Incorrectly inferred events
    false_negatives: int = 0  # Missed events
    
    # Temporal accuracy
    temporal_error: list[int] = field(default_factory=list)  # Time mismatches
    
    # Type accuracy
    type_matches: int = 0
    type_mismatches: int = 0
    
    @property
    def precision(self) -> float:
        """Precision: TP / (TP + FP)."""
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom > 0 else 0.0
    
    @property
    def recall(self) -> float:
        """Recall: TP / (TP + FN)."""
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom > 0 else 0.0
    
    @property
    def f1_score(self) -> float:
        """F1 score: harmonic mean of precision and recall."""
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    
    @property
    def avg_temporal_error(self) -> float:
        """Average error in timing of events."""
        return sum(self.temporal_error) / len(self.temporal_error) if self.temporal_error else 0.0
    
    def __repr__(self):
        return (f"Metrics(P={self.precision:.3f}, R={self.recall:.3f}, "
                f"F1={self.f1_score:.3f}, temporal_err={self.avg_temporal_error:.2f})")


def compare_histories(true_history: History, reconstruction: Reconstruction,
                     time_tolerance: int = 5) -> ComparisonMetrics:
    """Compare ground truth H with reconstruction Ĥ.
    
    Args:
        true_history: The actual history H
        reconstruction: The inferred history Ĥ
        time_tolerance: How many time steps off we allow for a match
    
    Returns:
        Comparison metrics
    """
    metrics = ComparisonMetrics()
    
    # Match inferred events to true events
    matched_true = set()
    
    for inf_idx, inf_event in enumerate(reconstruction.inferred_events):
        # Find matching true event
        best_match = None
        best_time_diff = float('inf')
        
        for true_idx, true_event in enumerate(true_history.events):
            if true_idx in matched_true:
                continue
            
            # Check type match
            if true_event.event_type != inf_event.event_type:
                continue
            
            # Check temporal proximity
            time_diff = abs(true_event.time - inf_event.time)
            if time_diff <= time_tolerance and time_diff < best_time_diff:
                best_match = true_idx
                best_time_diff = time_diff
        
        if best_match is not None:
            metrics.true_positives += 1
            metrics.type_matches += 1
            metrics.temporal_error.append(best_time_diff)
            matched_true.add(best_match)
        else:
            metrics.false_positives += 1
    
    # Count missed events
    metrics.false_negatives = len(true_history.events) - len(matched_true)
    
    return metrics


@dataclass
class RecoverabilityAnalysis:
    """Analysis of what historical information remains recoverable.
    
    Key question: Given H1 ≠ H2, can we distinguish O_t(H1) from O_t(H2)?
    """
    
    # Pairs of distinct histories that produce similar observables
    indistinguishable_pairs: list[tuple[History, History, float]] = field(default_factory=list)
    
    # Events that leave vs don't leave traces
    recoverable_event_types: set[str] = field(default_factory=set)
    unrecoverable_event_types: set[str] = field(default_factory=set)
    
    # Information bottlenecks
    information_loss_points: list[tuple[int, str]] = field(default_factory=list)  # (time, reason)
    
    def add_indistinguishable_pair(self, h1: History, h2: History, similarity: float):
        """Record two histories with similar observables."""
        self.indistinguishable_pairs.append((h1, h2, similarity))
    
    def mark_recoverable(self, event_type: str):
        """Mark an event type as leaving recoverable traces."""
        self.recoverable_event_types.add(event_type)
    
    def mark_unrecoverable(self, event_type: str):
        """Mark an event type as not leaving sufficient traces."""
        self.unrecoverable_event_types.add(event_type)
    
    def record_information_loss(self, time: int, reason: str):
        """Record a point where historical information became unrecoverable."""
        self.information_loss_points.append((time, reason))
    
    def __repr__(self):
        return (f"RecoverabilityAnalysis("
                f"indistinguishable={len(self.indistinguishable_pairs)}, "
                f"recoverable_types={len(self.recoverable_event_types)}, "
                f"unrecoverable_types={len(self.unrecoverable_event_types)})")


def measure_observable_distance(obs1: Observable, obs2: Observable) -> float:
    """Measure how similar two observable states are.
    
    If this distance is small but the histories differ, the distinction
    has become unrecoverable.
    """
    # Simple language-based distance
    if obs1.time != obs2.time:
        return float('inf')
    
    # Check if same languages exist
    if set(obs1.languages.keys()) != set(obs2.languages.keys()):
        return 1.0
    
    # This would be extended with actual language distance metrics
    # For now, just check exact equality
    differences = 0
    for lang_id in obs1.languages:
        if obs1.languages[lang_id] != obs2.languages[lang_id]:
            differences += 1
    
    return differences / len(obs1.languages) if obs1.languages else 0.0


def find_unrecoverable_distinctions(
    histories: list[History],
    observables: list[Observable],
    threshold: float = 0.1
) -> RecoverabilityAnalysis:
    """Find pairs of histories that are observationally similar.
    
    This reveals fundamental limits of historical reconstruction.
    """
    analysis = RecoverabilityAnalysis()
    
    for i in range(len(histories)):
        for j in range(i + 1, len(histories)):
            h1, h2 = histories[i], histories[j]
            o1, o2 = observables[i], observables[j]
            
            distance = measure_observable_distance(o1, o2)
            
            if distance < threshold:
                # Histories differ but observables are similar
                analysis.add_indistinguishable_pair(h1, h2, distance)
    
    return analysis


if __name__ == '__main__':
    # Demonstration
    print("=== H → O_t → Ĥ Framework ===\n")
    
    # Create a sample history
    history = History()
    history.record(0, 'sound_change', agent_id=1, change='p>f', phoneme='p')
    history.record(3, 'sound_change', agent_id=1, change='t>θ', phoneme='t')
    history.record(5, 'borrowing', agent_id=2, source=1, word='pater')
    history.record(7, 'sound_change', agent_id=2, change='k>h', phoneme='k')
    
    print(f"True history H: {history}")
    print(f"Events: {len(history.events)}")
    for event in history.events:
        print(f"  {event}")
    
    # Create a reconstruction
    reconstruction = Reconstruction()
    reconstruction.method = "comparative_method"
    reconstruction.add_inference(0, 'sound_change', confidence=0.9, agent_id=1, change='p>f')
    reconstruction.add_inference(4, 'sound_change', confidence=0.7, agent_id=1, change='t>θ')
    reconstruction.add_inference(7, 'sound_change', confidence=0.8, agent_id=2, change='k>h')
    # Note: missed the borrowing event
    
    print(f"\nReconstruction Ĥ: {reconstruction}")
    for i, event in enumerate(reconstruction.inferred_events):
        conf = reconstruction.confidence[i]
        print(f"  {event} [confidence={conf:.2f}]")
    
    # Compare
    metrics = compare_histories(history, reconstruction, time_tolerance=2)
    print("\nComparison metrics:")
    print(f"  {metrics}")
    print(f"  True positives: {metrics.true_positives}")
    print(f"  False positives: {metrics.false_positives}")
    print(f"  False negatives: {metrics.false_negatives}")
    print("\nInterpretation:")
    print(f"  - Reconstruction correctly identified {metrics.true_positives} sound changes")
    print(f"  - Missed {metrics.false_negatives} events (borrowing is often unrecoverable)")
    print(f"  - Average timing error: {metrics.avg_temporal_error:.1f} time steps")
