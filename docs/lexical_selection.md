# Lexical Natural Selection

**Category**: History Generator  
**Type**: Word Competition  
**Lines**: ~250

---

## Purpose

Model word competition based on multiple interacting constraints rather than a single "fitness" score. Demonstrates how survival emerges from complex interactions among length, articulatory cost, regularity, prestige, memorability, and ambiguity.

---

## Research Question

**Which word variants survive when synonyms compete, and which constraints drive selection?**

Traditional approach: Assign each variant a "fitness" score.

This approach: Let survival emerge from interactions among multiple constraints that vary by context.

---

## The Framework

### H: Complete Competition History

Ground truth includes:
- All competing variants for each meaning
- Properties of each variant (length, cost, prestige, etc.)
- Every usage event with context
- Frequency trajectories over time
- Extinction events

### O_t: Surviving Vocabulary

Observable at time t:
- Which variants remain in use
- Current frequency distribution
- (Lost: intermediate frequencies, extinct variants, usage contexts)

### Ĥ: Reconstructed Selection Pressures

Infer from survivors:
- Which constraints drove selection
- Context preferences
- Extinction causes
- (May be unrecoverable: timing, frequency trajectories)

---

## Model Architecture

### WordVariant

Each competing form has six properties:

```python
@dataclass
class WordVariant:
    form: str              # The actual word
    length: int            # Phonemes/characters
    articulatory_cost: float  # Production effort (0-1)
    regularity: float      # Fit to morphological patterns (0-1)
    prestige: float        # Social prestige (0-1)
    memorability: float    # Learning ease (0-1)
    ambiguity: float       # Confusion potential (0-1)
    frequency: int = 0     # Usage count (increases over time)
```

**Key insight**: No single "fitness" score. Constraints interact differently in different contexts.

### Selection Mechanism

Probabilities computed from **interacting constraints**:

```python
# Base from frequency (success breeds success)
freq_score = log(frequency + 1) / log(max_frequency + 2)

# Length penalty
length_score = 1.0 / (1.0 + length / 5.0)

# Articulatory ease
ease_score = 1.0 - articulatory_cost

# Context-dependent factors
if context == 'formal':
    # Favor prestige and regularity
    context_score = prestige * 0.6 + regularity * 0.4
elif context == 'informal':
    # Favor brevity and ease
    context_score = length_score * 0.5 + ease_score * 0.5
else:
    # Balanced
    context_score = prestige * 0.3 + length * 0.3 + ease * 0.2 + memorability * 0.2

# Ambiguity penalty
clarity_score = 1.0 - ambiguity

# Combined (emergent from interactions)
score = freq * 0.3 + length * 0.2 + ease * 0.15 + context * 0.2 + clarity * 0.15
```

**Crucial**: Weights change by context. A variant optimal for formal speech may be suboptimal for informal.

### Extinction

Variants that fall too far behind are removed:

```python
# If relative frequency drops below 5%
if variant.frequency / total_frequency < 0.05:
    extinct.append(variant)
```

This creates **path-dependence**: Early lead can compound through frequency advantage.

---

## Example Simulation

### Initial State

Meaning: "GOOD" (expressing approval)

Variants:
1. "good" - length=4, cost=0.2, prestige=0.7, regularity=0.8
2. "gr8" - length=3, cost=0.1, prestige=0.3, regularity=0.2  
3. "excellent" - length=9, cost=0.5, prestige=0.9, regularity=0.8
4. "nice" - length=4, cost=0.2, prestige=0.6, regularity=0.7

### Selection Pressures

**Formal context** (20% of usage):
- "excellent" wins (high prestige, regular)
- "gr8" loses (low prestige, irregular)

**Informal context** (20% of usage):
- "gr8" wins (short, easy)
- "excellent" loses (long, effortful)

**Neutral context** (60% of usage):
- "good" and "nice" compete
- Balanced properties

### Possible Outcomes

**Outcome 1: Stable competition**
- "excellent" survives in formal contexts
- "good"/"nice" survive in neutral contexts
- "gr8" goes extinct (too restricted)

**Outcome 2: Winner-take-all**
- Early frequency advantage compounds
- "good" dominates all contexts
- Others go extinct

**Outcome 3: Register split**
- "excellent" (formal) vs "good" (all others)
- Context specialization

### Observable Evidence (O_t)

At time t=1000:
- Survivors: "excellent" (freq=150), "good" (freq=850)
- Extinct: "gr8", "nice"

### Reconstruction Challenge (Ĥ)

From survivors alone, can we infer:
- ✅ "excellent" has some advantage in formal contexts (prestige)
- ✅ "good" is more general-purpose (balanced properties)
- ❌ Why "gr8" died (was it irregularity or low prestige?)
- ❌ When "nice" went extinct
- ❌ Whether "good" won by quality or by early frequency advantage

---

## Key Findings

### 1. **Emergent Selection**

No variant is "fittest" in all contexts. Survival emerges from:
- Context distribution (formal vs informal usage)
- Frequency compounding (success breeds success)
- Constraint interactions (short + irregular may lose to long + regular)

### 2. **Path Dependence**

Same initial setup → different outcomes:
- Early random fluctuations compound
- Frequency advantage self-reinforces
- Different survivors from identical parameters

### 3. **Information Loss**

From final vocabulary (O_t) alone:
- ❌ Cannot recover timing of extinctions
- ❌ Cannot distinguish quality advantage from frequency luck
- ❌ Cannot identify failed innovations
- ✅ Can identify context specialization (if survivors differ by register)

### 4. **Constraint Interactions**

Traditional approach assumes additive fitness:
```
fitness(variant) = w₁·length + w₂·cost + w₃·prestige + ...
```

This model shows **context-dependent interactions**:
```
selection(variant|context) = f(length, cost, prestige, ..., context)
```

Same variant can be optimal or suboptimal depending on context.

---

## Theoretical Connections

### Language Change

Models real phenomena:
- **Lexical replacement**: "television" → "TV" (length pressure)
- **Register splitting**: "commence" (formal) vs "start" (informal)
- **Frequency effects**: High-frequency words resist phonological reduction
- **Analogical leveling**: Irregular forms regularize (frequency-dependent)

### Evolutionary Biology

Analogous to:
- **Frequency-dependent selection**: Rare advantage lost as variant becomes common
- **Niche construction**: Context creates selection pressure
- **Red Queen dynamics**: Optimal strategy changes as population changes

### Information Theory

- **H** contains complete frequency trajectories (high information)
- **O_t** contains only final frequencies (compressed)
- **Compression is lossy**: Cannot uniquely recover H from O_t

---

## H → O_t → Ĥ Protocol

### History (H)

```python
class LexicalSelectionSimulator(HistoryGenerator):
    def __init__(self, meanings: list[Meaning]):
        self.meanings = {m.concept: m for m in meanings}
        
        # Record initial state
        self.history.metadata['initial_variants'] = {
            concept: [v.form for v in meaning.variants]
            for concept, meaning in self.meanings.items()
        }
    
    def step(self, time: int):
        # Generate usage events
        # Select variants probabilistically
        # Update frequencies
        # Record extinctions
```

### Observable (O_t)

```python
class LexicalObservable(Observable):
    def extract(self, history, time):
        return {
            'survivors': [(v.form, v.frequency) for v in current_variants],
            'properties': {v.form: properties(v) for v in current_variants}
        }
        # Lost: extinct variants, frequency trajectories, contexts
```

### Reconstruction (Ĥ)

```python
class LexicalReconstructor(Reconstruction):
    def infer(self, observable):
        # From survivor properties, infer selection pressures
        # From frequency distribution, infer context distribution
        # CANNOT infer: timing, extinct variants, path-dependence
```

---

## Running the Experiment

```bash
python experiments/lexical_selection.py
```

### Output

```
=== Lexical Natural Selection ===

Initial Variants:
  GOOD: good, gr8, excellent, nice
  FAST: quick, speedy, rapid, fast
  BIG: large, huge, big, massive

Time t=0:
  All variants at freq=0

Time t=500:
  GOOD: good (450), excellent (50)
  FAST: fast (300), quick (200)
  BIG: huge (280), big (220)

Time t=1000:
  GOOD: good (850), excellent (150)
  FAST: fast (650), quick (350)
  BIG: huge (550), big (450)

Extinctions:
  t=350: "gr8" (GOOD) - fell to <5%
  t=420: "nice" (GOOD) - fell to <5%
  t=480: "speedy" (FAST) - fell to <5%
  t=510: "rapid" (FAST) - fell to <5%
  t=670: "large" (BIG) - fell to <5%
  t=720: "massive" (BIG) - fell to <5%

Observable (O_t=1000):
  Survivors: good, excellent, fast, quick, huge, big
  
Reconstruction:
  ✓ "excellent" specialized for formal contexts (high prestige)
  ✓ "good" general-purpose (balanced properties)
  ✗ Why "gr8" died not recoverable (irregularity or prestige?)
  ✗ Timing of "nice" extinction not recoverable
  ✗ Whether "fast" won by quality or frequency luck not recoverable
```

---

## Extensions

### 1. Social Networks

Add prestige diffusion through social graph:
- High-prestige speakers influence others
- Variants spread through network
- Community boundaries affect selection

### 2. Borrowing

Add contact with another language:
- Borrowed variants have different property profiles
- Prestige from foreign source
- Cultural associations affect selection

### 3. Semantic Drift

Combine with semantic_drift.py:
- Variants start synonymous
- Meanings drift apart over time
- Selection pressure changes as meanings separate

### 4. Morphological Productivity

Add productivity metric:
- Regular variants can generate new forms
- Irregular variants memorized individually
- Frequency threshold for irregularity survival

---

## Comparison to Other Experiments

| Experiment | Selection Pressure | Path-Dependence | Context-Dependence |
|------------|-------------------|-----------------|-------------------|
| **Lexical Selection** | Multi-constraint | ✓ High | ✓ High |
| **Phonological Drift** | Articulatory | ✓ Medium | ✗ Low |
| **Semantic Drift** | Communicative | ✓ High | ✓ Medium |
| **Minimum Language** | Efficiency | ✓ Low | ✗ Low |

**Unique contribution**: Only experiment modeling **emergent selection from constraint interactions**.

---

## References

**Theoretical**:
- Bybee (2007) - Frequency effects in grammar
- Lieberman et al. (2007) - Frequency and irregularity
- Wedel (2006) - Exemplar models

**Evolutionary**:
- Nowak & Krakauer (1999) - Evolutionary dynamics of language
- Nettle (1999) - Linguistic diversity

**Implementation**:
- `src/language_evolution/framework.py` - H → O_t → Ĥ protocol
- `experiments/lexical_selection.py` - This experiment

---

## Status

✅ **Implemented**  
✅ **Tested**  
✅ **Documented**  
🚧 **Reconstruction method** - needs improvement

**Next**: Combine with semantic drift for co-evolution of form and meaning.
