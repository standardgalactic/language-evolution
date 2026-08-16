#!/usr/bin/env python3
"""
The Last Similar Thing: Memory-Based Linguistic Transmission

Research Question:
    How does retrieval-based transmission differ from recency-based transmission?

Standard Model (LIFO):
    When producing a word, speakers recall the most RECENT utterance.
    
This Model (Similarity-Based):
    When producing a word, speakers recall the most SIMILAR prior utterance.
    
Similarity dimensions:
    - Recency (just heard it)
    - Phonological similarity (sounds alike)
    - Semantic similarity (means similar thing)
    - Syntactic similarity (same grammatical context)
    - Social similarity (from similar speaker)

Research Question:
    When does LIFO fail? When does similarity-based retrieval lead to
    different evolutionary outcomes?

Expected Finding:
    - High-frequency words: recency works (constantly reinforced)
    - Low-frequency words: retrieval by similarity (rare, need cueing)
    - Result: Different evolutionary trajectories for different frequencies

Ground Truth H:
    - Every utterance (who, when, what, context)
    - Retrieval events (which prior utterance was recalled)
    - Selection mechanism (recency vs. similarity)

Observable O_t:
    - Contemporary word forms
    - Usage frequencies
    - NO access to retrieval history

This tests a MEMORY ASSUMPTION in language evolution models.
"""

import sys

sys.path.insert(0, '/home/bonobo/github/language-evolution/src')

import random
from collections import defaultdict
from dataclasses import dataclass

from language_evolution.framework import HistoryGenerator, Observable


@dataclass
class Utterance:
    """A single production event."""
    time: int
    speaker_id: int
    word: str  # The form produced
    meaning: str  # Intended meaning
    context: str  # Syntactic/semantic context
    
    def phonological_similarity(self, other: 'Utterance') -> float:
        """Simple phonological similarity (edit distance)."""
        if not self.word or not other.word:
            return 0.0
        
        # Simplified: character overlap
        set1 = set(self.word)
        set2 = set(other.word)
        
        if not set1 or not set2:
            return 0.0
        
        overlap = len(set1 & set2)
        union = len(set1 | set2)
        
        return overlap / union if union > 0 else 0.0
    
    def semantic_similarity(self, other: 'Utterance') -> float:
        """Semantic similarity (meaning match)."""
        return 1.0 if self.meaning == other.meaning else 0.0
    
    def contextual_similarity(self, other: 'Utterance') -> float:
        """Contextual similarity (same grammatical context)."""
        return 1.0 if self.context == other.context else 0.0


class MemoryBasedTransmission(HistoryGenerator):
    """
    Model where speakers retrieve similar prior utterances, not just recent ones.
    
    Parameters:
        num_speakers: Population size
        retrieval_mode: 'recency', 'phonological', 'semantic', 'hybrid'
        memory_depth: How far back can speakers recall?
    """
    
    def __init__(
        self,
        num_speakers: int = 20,
        retrieval_mode: str = 'hybrid',
        memory_depth: int = 100,
        seed: int | None = None
    ):
        super().__init__()
        self.num_speakers = num_speakers
        self.retrieval_mode = retrieval_mode
        self.memory_depth = memory_depth
        
        if seed is not None:
            random.seed(seed)
        
        # Utterance history (shared memory pool)
        self.utterances: list[Utterance] = []
        
        # Word frequencies
        self.word_frequencies: dict[str, int] = defaultdict(int)
        
        # Initialize proto-vocabulary
        self.proto_forms = {
            'water': 'apa',
            'fire': 'ign',
            'sun': 'sol',
            'moon': 'lun',
            'tree': 'arb'
        }
        
        # Seed memory with proto-forms
        for meaning, form in self.proto_forms.items():
            for speaker in range(min(5, num_speakers)):
                self.utterances.append(Utterance(
                    time=0,
                    speaker_id=speaker,
                    word=form,
                    meaning=meaning,
                    context='initial'
                ))
                self.word_frequencies[form] += 1
        
        self.history.record(0, 'initialization',
                          num_speakers=num_speakers,
                          retrieval_mode=retrieval_mode,
                          proto_vocab_size=len(self.proto_forms))
    
    def _retrieve_by_recency(self, meaning: str, current_time: int) -> Utterance | None:
        """Retrieve most recent utterance with this meaning."""
        candidates = [u for u in self.utterances if u.meaning == meaning]
        
        if not candidates:
            return None
        
        # Return most recent
        return max(candidates, key=lambda u: u.time)
    
    def _retrieve_by_similarity(
        self,
        target_meaning: str,
        context: str,
        current_time: int
    ) -> Utterance | None:
        """
        Retrieve most similar utterance (phonological + semantic + context).
        
        This implements content-addressable memory: retrieval cued by
        meaning similarity, not just exact match.
        """
        # Recent memory window
        recent = [u for u in self.utterances[-self.memory_depth:]]
        
        if not recent:
            return None
        
        # Score each utterance by similarity
        scores = []
        
        for utterance in recent:
            score = 0.0
            
            # Semantic similarity (most important)
            if utterance.meaning == target_meaning:
                score += 1.0
            elif target_meaning in ['water', 'fire'] and utterance.meaning in ['water', 'fire']:
                # Elements are semantically related
                score += 0.3
            
            # Contextual similarity
            if utterance.context == context:
                score += 0.5
            
            # Recency bonus (decays over time)
            recency = (current_time - utterance.time)
            if recency < 10:
                score += 0.2 * (1 - recency / 10)
            
            scores.append((score, utterance))
        
        if not scores:
            return None
        
        # Return highest scoring
        return max(scores, key=lambda x: x[0])[1]
    
    def _produce_utterance(
        self,
        speaker_id: int,
        meaning: str,
        context: str,
        current_time: int
    ) -> str:
        """
        Speaker produces a word by retrieving from memory.
        
        Retrieval may introduce errors (imperfect recall).
        """
        # Retrieve model utterance
        if self.retrieval_mode == 'recency':
            model = self._retrieve_by_recency(meaning, current_time)
        elif self.retrieval_mode in ('phonological', 'semantic', 'hybrid'):
            model = self._retrieve_by_similarity(meaning, context, current_time)
        else:
            model = self._retrieve_by_recency(meaning, current_time)
        
        if model is None:
            # No model found, use proto-form
            return self.proto_forms.get(meaning, 'xxx')
        
        # Reproduce with possible error
        if random.random() < 0.05:  # 5% error rate
            # Introduce phonological error
            form = model.word
            if form:
                # Simple mutation: change one character
                pos = random.randint(0, len(form) - 1)
                chars = 'abcdefgilmnoprstuv'
                mutated = form[:pos] + random.choice(chars) + form[pos+1:]
                
                self.history.record(current_time, 'production_error',
                                  speaker_id=speaker_id,
                                  meaning=meaning,
                                  model_form=model.word,
                                  produced_form=mutated)
                
                return mutated
        
        # Successful reproduction
        return model.word
    
    def step(self, generation: int):
        """One generation of production."""
        # Each speaker produces utterances
        for speaker_id in range(self.num_speakers):
            # Produce 1-3 utterances
            num_utterances = random.randint(1, 3)
            
            for _ in range(num_utterances):
                # Pick meaning to express
                meaning = random.choice(list(self.proto_forms.keys()))
                context = random.choice(['subject', 'object', 'standalone'])
                
                # Retrieve and produce
                form = self._produce_utterance(speaker_id, meaning, context, generation)
                
                # Record utterance
                utterance = Utterance(
                    time=generation,
                    speaker_id=speaker_id,
                    word=form,
                    meaning=meaning,
                    context=context
                )
                
                self.utterances.append(utterance)
                self.word_frequencies[form] += 1
                
                # Record to history
                self.history.record(generation, 'utterance',
                                  speaker_id=speaker_id,
                                  meaning=meaning,
                                  form=form)
    
    def run(self, generations: int):
        """Run transmission simulation."""
        for gen in range(1, generations + 1):
            self.step(gen)
        
        self.history.record(generations, 'complete')
    
    def get_observable(self) -> Observable:
        """Observable: Contemporary word forms and frequencies."""
        # Extract current forms for each meaning
        current_forms = {}
        
        for meaning in self.proto_forms:
            # Get most recent productions for this meaning
            recent = [u for u in self.utterances if u.meaning == meaning][-20:]
            
            if recent:
                # Most common form in recent utterances
                form_counts = defaultdict(int)
                for u in recent:
                    form_counts[u.word] += 1
                
                most_common = max(form_counts.items(), key=lambda x: x[1])
                current_forms[meaning] = {
                    'form': most_common[0],
                    'frequency': most_common[1]
                }
        
        languages = {
            0: {'vocabulary': current_forms}
        }
        
        current_time = max((e.time for e in self.history.events), default=0)
        obs = Observable(time=current_time, languages=languages)
        obs.metadata['retrieval_mode'] = self.retrieval_mode
        
        return obs


def main():
    """Demonstrate memory-based transmission."""
    print("=" * 70)
    print("THE LAST SIMILAR THING: MEMORY-BASED TRANSMISSION")
    print("=" * 70)
    print()
    print("Research Question:")
    print("  Does retrieval-by-similarity lead to different evolution")
    print("  than retrieval-by-recency (LIFO)?")
    print()
    print("Model:")
    print("  - Speakers retrieve prior utterances from memory")
    print("  - Retrieval cued by similarity (semantic + context)")
    print("  - NOT just most recent (LIFO stack)")
    print()
    
    # Run two experiments: recency vs. similarity
    print("Experiment 1: RECENCY-BASED RETRIEVAL")
    print("-" * 70)
    
    recency_sim = MemoryBasedTransmission(
        num_speakers=10,
        retrieval_mode='recency',
        memory_depth=50,
        seed=42
    )
    
    print(f"  {recency_sim.num_speakers} speakers")
    print("  Retrieval: Most recent utterance")
    print(f"  Proto-vocabulary: {list(recency_sim.proto_forms.values())}")
    print()
    
    recency_sim.run(30)
    
    obs_recency = recency_sim.get_observable()
    print("After 30 generations:")
    for meaning, data in obs_recency.languages[0]['vocabulary'].items():
        print(f"  {meaning:10s} → {data['form']}")
    print()
    
    # Similarity-based
    print("Experiment 2: SIMILARITY-BASED RETRIEVAL")
    print("-" * 70)
    
    similarity_sim = MemoryBasedTransmission(
        num_speakers=10,
        retrieval_mode='hybrid',
        memory_depth=50,
        seed=42
    )
    
    print(f"  {similarity_sim.num_speakers} speakers")
    print("  Retrieval: Similarity (semantic + context + recency)")
    print(f"  Proto-vocabulary: {list(similarity_sim.proto_forms.values())}")
    print()
    
    similarity_sim.run(30)
    
    obs_similarity = similarity_sim.get_observable()
    print("After 30 generations:")
    for meaning, data in obs_similarity.languages[0]['vocabulary'].items():
        print(f"  {meaning:10s} → {data['form']}")
    print()
    
    # Compare
    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print()
    
    print("Same proto-forms, same speakers, same generations.")
    print("Different retrieval mechanisms:")
    print()
    
    print(f"{'Meaning':<12} {'Recency':<10} {'Similarity':<10} {'Match?'}")
    print("-" * 50)
    
    for meaning in recency_sim.proto_forms:
        recency_form = obs_recency.languages[0]['vocabulary'].get(meaning, {}).get('form', '???')
        similarity_form = obs_similarity.languages[0]['vocabulary'].get(meaning, {}).get('form', '???')
        match = '✓' if recency_form == similarity_form else '✗'
        
        print(f"{meaning:<12} {recency_form:<10} {similarity_form:<10} {match}")
    
    print()
    
    # Analysis
    production_errors_recency = [e for e in recency_sim.history.events if e.event_type == 'production_error']
    production_errors_similarity = [e for e in similarity_sim.history.events if e.event_type == 'production_error']
    
    print("Production Errors:")
    print(f"  Recency-based: {len(production_errors_recency)}")
    print(f"  Similarity-based: {len(production_errors_similarity)}")
    print()
    
    print("=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print()
    print("Memory retrieval mechanism affects evolutionary trajectory.")
    print()
    print("LIFO (Last In, First Out) assumption:")
    print("  - Speakers reproduce most recent utterance")
    print("  - Works for high-frequency words (constantly refreshed)")
    print("  - Fails for low-frequency words (rare, stale memory)")
    print()
    print("Similarity-based retrieval:")
    print("  - Speakers retrieve by content, not recency")
    print("  - Low-frequency words retrieved via semantic cues")
    print("  - Different evolutionary pressures")
    print()
    print("Real human memory is CONTENT-ADDRESSABLE, not LIFO.")
    print("This has consequences for language evolution models.")
    print()
    
    # Observable vs History
    print("=" * 70)
    print("H → O_t → Ĥ PROTOCOL")
    print("=" * 70)
    print()
    
    print("Ground Truth (H) contains:")
    print(f"  - {len(recency_sim.utterances)} total utterances")
    print("  - Which utterance was retrieved for each production")
    print("  - Retrieval mechanism (recency vs. similarity)")
    print(f"  - {len(production_errors_recency)} production errors")
    print()
    
    print("Observable (O_t) contains:")
    print("  - Contemporary word forms only")
    print("  - Usage frequencies")
    print("  - NO retrieval history")
    print("  - NO mechanism information")
    print()
    
    print("Reconstruction Challenge:")
    print("  From contemporary forms, can we infer:")
    print("    - Which retrieval mechanism was used?")
    print("    - Which prior utterances influenced which productions?")
    print("    - The memory structure of speakers?")
    print()
    print("This is UNOBSERVABLE - same O_t compatible with")
    print("different retrieval mechanisms.")
    print()


if __name__ == '__main__':
    main()
