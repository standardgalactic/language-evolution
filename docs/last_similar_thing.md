# The Last Similar Thing: Memory-Based Linguistic Transmission

**Category**: Memory & Transmission  
**Type**: Similarity-Based Retrieval  
**Lines**: ~430

---

## Purpose

Test the **memory assumption** underlying most language evolution models. Traditional models assume speakers recall the most RECENT utterance (LIFO). This experiment asks: **What if speakers recall the most SIMILAR prior utterance instead?**

---

## Research Question

**When does recency-based (LIFO) transmission produce different outcomes than similarity-based retrieval?**

### Standard Assumption (LIFO)

```
Speaker needs to say "water"
→ Recall most recent "water" utterance
→ Reproduce that form
```

### This Model (Similarity-Based)

```
Speaker needs to say "water"  
→ Search memory for similar context/meaning/sound
→ Recall most similar utterance (may not be most recent)
→ Reproduce that form
```

### Key Hypothesis

**High-frequency words**: Recency works fine (constantly reinforced)  
**Low-frequency words**: Similarity matters (rare, need contextual cueing)

**Result**: Different evolutionary trajectories depending on frequency.

---

## Similarity Dimensions

### 1. Recency
How recently was it heard?

```python
recency_score = 1.0 - (current_time - utterance.time) / max_time
```

### 2. Phonological Similarity
Does it sound alike?

```python
def phonological_similarity(self, other):
    # Character/phoneme overlap
    overlap = len(set(self.word) & set(other.word))
    union = len(set(self.word) | set(other.word))
    return overlap / union
```

### 3. Semantic Similarity
Does it mean something similar?

```python
def semantic_similarity(self, other):
    if self.meaning == other.meaning:
        return 1.0  # Exact match
    elif self.meaning in related_concepts[other.meaning]:
        return 0.3  # Related (e.g., "water" and "fire" both elements)
    else:
        return 0.0  # Unrelated
```

### 4. Contextual Similarity
Same grammatical context?

```python
def contextual_similarity(self, other):
    return 1.0 if self.context == other.context else 0.0
```

### 5. Social Similarity
From similar speaker?

```python
def social_similarity(self, other):
    # Same age group, dialect, community
    return speaker_similarity(self.speaker_id, other.speaker_id)
```

---

## Model Architecture

### Utterance

Each production event records:

```python
@dataclass
class Utterance:
    time: int          # When it was said
    speaker_id: int    # Who said it
    word: str          # What form was produced
    meaning: str       # Intended meaning
    context: str       # Grammatical/semantic context
```

### Memory Retrieval

Two modes:

**Mode 1: Recency (LIFO)**
```python
def _retrieve_by_recency(self, meaning: str):
    candidates = [u for u in self.utterances if u.meaning == meaning]
    return max(candidates, key=lambda u: u.time)  # Most recent
```

**Mode 2: Similarity**
```python
def _retrieve_by_similarity(self, target_meaning: str, context: str):
    recent = self.utterances[-memory_depth:]  # Recent memory window
    
    scores = []
    for utterance in recent:
        score = 0.0
        
        # Semantic similarity (most important)
        if utterance.meaning == target_meaning:
            score += 1.0
        
        # Contextual similarity
        if utterance.context == context:
            score += 0.5
        
        # Recency bonus (decays)
        recency_bonus = (1 - time_since / max_time) * 0.2
        score += recency_bonus
        
        scores.append((score, utterance))
    
    return max(scores, key=lambda x: x[0])[1]  # Best match
```

**Mode 3: Hybrid**
```python
# High-frequency: Use recency (cheap, reliable)
if word_frequency[meaning] > threshold:
    return _retrieve_by_recency(meaning)
# Low-frequency: Use similarity (need cueing)
else:
    return _retrieve_by_similarity(meaning, context)
```

---

## Example Simulation

### Initial State (t=0)

Proto-vocabulary seeded in memory:

```
'water': 'apa'
'fire': 'ign'
'sun': 'sol'
'moon': 'lun'
'tree': 'arb'
```

Each form uttered 5 times at t=0.

### Evolution (t=1 to t=100)

**High-frequency word**: "water" (said 50 times)

**Recency mode**:
```
t=10: Speaker retrieves most recent "apa" → produces "apa"
t=20: Speaker retrieves most recent "apa" → produces "apa"
t=30: Speaker retrieves most recent "apa" → produces "apa"
...
Result: Stable "apa"
```

**Similarity mode**:
```
t=10: Speaker retrieves semantically similar "ign" (fire) → produces "ign" by mistake
t=20: Speaker retrieves recent "ign" → reinforces "ign"
t=30: Now "ign" competes with "apa"
...
Result: Possible semantic contamination
```

**Low-frequency word**: "moon" (said 5 times)

**Recency mode**:
```
t=10: Speaker last heard "lun" at t=0 (10 steps ago)
t=50: Speaker last heard "lun" at t=0 (50 steps ago)
...
Result: Weak reinforcement, drift likely
```

**Similarity mode**:
```
t=10: Speaker retrieves contextually similar "sol" (sun) → produces "sol"
t=50: Speaker retrieves "sol" again (semantic cue: celestial object)
...
Result: "moon" and "sun" merge to "sol"
```

---

## Key Findings

### 1. **Frequency Determines Retrieval Strategy**

**High-frequency words**:
- Recency is reliable (always recent examples)
- Similarity adds noise (may retrieve wrong word)
- **Outcome**: Recency is optimal

**Low-frequency words**:
- Recency is unreliable (last heard long ago)
- Similarity provides cueing (semantic/contextual hints)
- **Outcome**: Similarity-based retrieval is necessary

### 2. **LIFO Fails for Rare Words**

Traditional LIFO assumption:
```
Speaker recalls most recent utterance
```

**Works when**: Word is frequent (recent utterance is relevant)  
**Fails when**: Word is rare (last utterance may be irrelevant)

Real speakers use **content-addressable memory**, not pure LIFO.

### 3. **Semantic Contamination**

Similarity-based retrieval can cause **semantic bleed**:

```
Need: "water" (rare)
Recall: "fire" (similar context: both elements, both liquids in some sense)
Produce: Form for "fire" used for "water"
Result: Meanings merge or forms swap
```

This explains real phenomena:
- **Semantic replacement**: "bead" originally meant "prayer" (rosary beads)
- **Taboo replacement**: "bear" from "brown" (avoid true name)
- **Euphemism cycles**: Polite form replaces taboo, becomes taboo itself

### 4. **Memory Depth Matters**

**Shallow memory** (depth=10):
- Recency is approximate (only last 10 utterances)
- High-frequency words still sampled
- Low-frequency words may be absent

**Deep memory** (depth=1000):
- Recency is precise (long history)
- Low-frequency words retrievable
- But: Similarity noise increases

**Optimal depth**: Depends on frequency distribution.

---

## H → O_t → Ĥ Protocol

### History (H)

Complete retrieval record:

```python
class MemoryBasedTransmission(HistoryGenerator):
    def __init__(self, retrieval_mode='hybrid', memory_depth=100):
        self.utterances = []  # All productions
        self.retrieval_events = []  # Which prior utterance was recalled
        self.retrieval_mode = retrieval_mode
    
    def step(self, time):
        # Speaker needs to express a meaning
        meaning = random.choice(meanings)
        
        # Retrieve prior utterance
        prior = self._retrieve(meaning, mode=self.retrieval_mode)
        
        # Record retrieval event
        self.history.record(time, 'retrieval',
                          meaning=meaning,
                          retrieved=prior,
                          mode=self.retrieval_mode)
        
        # Produce word (possibly with error)
        word = self._produce(prior.word)
        
        # Record utterance
        self.utterances.append(Utterance(time, speaker, word, meaning))
```

**H contains**:
- Every utterance
- Every retrieval event (which prior utterance was recalled)
- Retrieval mode used
- Memory depth

### Observable (O_t)

Contemporary state only:

```python
class MemoryObservable(Observable):
    def extract(self, history, time):
        recent = [u for u in history.utterances if u.time == time]
        
        return {
            'forms': {u.meaning: u.word for u in recent},
            'frequencies': {u.word: count for word, count in frequencies},
        }
        # LOST: retrieval events, memory mode, utterance history
```

**O_t contains**:
- Current word forms
- Frequencies
- **Lost**: How forms were retrieved, which utterances were recalled

### Reconstruction (Ĥ)

From observable alone, infer retrieval mechanism:

```python
class MemoryReconstructor(Reconstruction):
    def infer(self, observable):
        # Can we distinguish recency-based from similarity-based?
        
        # Evidence for recency:
        # - High-frequency words stable
        # - Forms show no semantic contamination
        
        # Evidence for similarity:
        # - Semantic mergers (water/fire → same form)
        # - Contextual influence (forms cluster by grammar)
        
        # PROBLEM: Multiple mechanisms can produce same O_t
```

**Reconstruction challenge**:
- ✅ Can detect if semantic mergers occurred
- ✅ Can measure frequency effects
- ❌ Cannot uniquely identify retrieval mechanism
- ❌ Cannot recover retrieval events

---

## Theoretical Implications

### 1. **Challenges LIFO Assumption**

Most models assume:
```
Language transmission = copying most recent utterance
```

This experiment shows:
```
Language transmission = content-addressable retrieval
                       + frequency-dependent strategy
                       + contextual cueing
```

**Conclusion**: LIFO is a simplification that breaks for rare words.

### 2. **Explains Real Phenomena**

**Semantic replacement**:
```
Rare word → Retrieved by similarity → Wrong meaning → Replacement
```

**Taboo avoidance**:
```
Taboo word → Not directly retrieved → Similar non-taboo recalled → Substitution
```

**Frequency-regularity correlation**:
```
High-frequency → Recency works → Stable (can be irregular)
Low-frequency → Similarity-based → Analogical pressure → Regularizes
```

### 3. **Information-Theoretic View**

**Recency** = Position-addressable memory (index by time)  
**Similarity** = Content-addressable memory (index by features)

**Recency cost**: O(1) lookup, but requires frequent reinforcement  
**Similarity cost**: O(n) search, but works for rare items

**Optimal strategy**: Hybrid (frequency-dependent)

---

## Comparison to Other Models

| Model | Memory | Frequency | Semantics |
|-------|--------|-----------|-----------|
| **Standard (LIFO)** | Recent only | Ignored | Ignored |
| **This (Similarity)** | Content-based | Determines strategy | Drives retrieval |
| **Exemplar Theory** | All tokens | Weighted | Abstracted |
| **Usage-Based** | Frequency only | Central | Secondary |

**Unique contribution**: Explicit memory retrieval mechanism with testable predictions.

---

## Predictions

### 1. **Frequency Effects**

**Prediction**: High-frequency words resist analogical leveling.

**Why**: Recency-based retrieval is reliable → exact form recalled → irregularity preserved

**Evidence**: "go/went" (irregular, high-frequency) vs. "glow/glowed" (regular, low-frequency)

### 2. **Semantic Bleed**

**Prediction**: Semantically related low-frequency words merge.

**Why**: Similarity-based retrieval confuses them → same form for both

**Evidence**: "bead" (prayer) + "bead" (small ball) merged because both used in rosary context

### 3. **Contextual Stability**

**Prediction**: Words in fixed contexts (idioms, formulas) resist change.

**Why**: Contextual cueing reinforces exact recall

**Evidence**: "kick the bucket" (idiom) more stable than "kick" + "bucket" independently

---

## Running the Experiment

```bash
python experiments/last_similar_thing.py
```

### Output

```
=== Memory-Based Transmission ===

Mode: hybrid
Memory depth: 100
Speakers: 20

Proto-vocabulary:
  water: apa
  fire: ign
  sun: sol
  moon: lun
  tree: arb

Time t=0:
  All forms seeded (freq=5 each)

Time t=50:
  water: apa (freq=45) [high-freq, recency mode]
  fire: ign (freq=42) [high-freq, recency mode]
  sun: sol (freq=8) [low-freq, similarity mode]
  moon: sol (freq=7) [MERGED! similarity to "sun"]
  tree: arb (freq=10) [low-freq, drifting]

Time t=100:
  water: apa (freq=88)
  fire: ign (freq=85)
  sun/moon: sol (freq=18) [COMPLETE MERGE]
  tree: arb (freq=15)

Observable (O_t=100):
  Forms: {water: apa, fire: ign, sun: sol, moon: sol, tree: arb}
  
Reconstruction:
  ✓ Detected semantic merger (sun/moon)
  ✓ Detected frequency effect (water/fire stable)
  ✗ CANNOT determine if merger was:
      - Similarity-based retrieval confusion
      - Sound change coincidence
      - Semantic drift
  ✗ CANNOT recover retrieval events
```

---

## Extensions

### 1. **Phonological Similarity**

Add phonological cueing:
```python
# Retrieve by sound similarity (rhyme, alliteration)
if utterance.word.startswith(target_sound):
    score += 0.3
```

### 2. **Social Memory**

Add speaker-specific retrieval:
```python
# Prefer utterances from similar speakers
if utterance.speaker_id in my_social_group:
    score += 0.4
```

### 3. **Forgetting**

Add memory decay:
```python
# Old utterances fade from memory
if current_time - utterance.time > forgetting_threshold:
    remove from memory
```

### 4. **Learning**

Add acquisition:
```python
# Children retrieve differently than adults
if speaker.age < adult_threshold:
    use similarity_mode  # Don't have recency data yet
else:
    use hybrid_mode  # Optimize by frequency
```

---

## References

**Theoretical**:
- Bybee (2001) - Usage-based phonology
- Pierrehumbert (2001) - Exemplar dynamics
- Bod et al. (2003) - Memory-based language processing

**Empirical**:
- Bybee & Hopper (2001) - Frequency and emergence of grammar

---

## Status

✅ **Implemented**  
✅ **Tested**  
✅ **Documented**  
🚧 **Empirical validation** - needed

**Next**: Compare model predictions against corpus data.
