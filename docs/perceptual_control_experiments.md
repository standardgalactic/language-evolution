# Perceptual Control Theory and Ecological Language Evolution

## New Experiments

This update adds three new experiments based on **Perceptual Control Theory** (William Powers) and **ecological dynamics** (William Calvin), representing a fundamentally different approach to modeling language evolution.

### 1. Borrowing Detection (`borrowing_detector.py`)

**Purpose**: Distinguish borrowed words from inherited vocabulary using distributional patterns.

**Key Insight**: Borrowed words show IRREGULAR patterns that distinguish them from systematically inherited vocabulary:
- Violate systematic sound correspondences
- Appear in geographical/cultural subsets  
- Cluster in cultural/technological domains
- May contain foreign phonotactic patterns

**Usage**:
```bash
python3 experiments/borrowing_detector.py
```

**Output**: Evidence-based classification of likely borrowings with confidence scores.

**Integration**: Can be used with any `Observable` containing multi-language vocabulary data.

---

### 2. Perceptual Control Language (`perceptual_control_language.py`)

**Purpose**: Model language users as active controllers of their perceptions through negative feedback loops.

**Theoretical Foundation**:

Traditional models assume language users **respond to stimuli**:
```
Stimulus → Response
```

Perceptual Control Theory (PCT) says they **control perceptions**:
```
Reference Signal (goal) → Perceptual Signal (current) → Error → Output → Environment
                            ↑_______________________________________________|
```

**Core Components**:

1. **PerceptualState**: What an agent perceives
   - Meaning understood (comprehension)
   - Social alignment (conformity)
   - Articulatory ease (effort)
   - Distinctiveness (contrast)

2. **ReferenceSignal**: Desired perceptual state (control goal)
   - Target comprehension (want to be understood)
   - Target conformity (want to sound normal)
   - Target ease (want comfortable production)
   - Target distinctiveness (want to avoid ambiguity)

3. **ControlLoop**: Continuous error-correction
   - Perceive current state
   - Compare to reference (compute error)
   - Generate output to reduce error
   - Observe result, repeat

**Key Difference from Stimulus-Response**:

- **S-R models**: "Speakers imitate what they hear"
- **PCT models**: "Speakers monitor whether their utterance achieved the desired perceptual effect and adjust accordingly"

**Usage**:
```bash
python3 experiments/perceptual_control_language.py
```

**Parameters**:
- `num_agents`: Population size
- `num_meanings`: Vocabulary size
- `niche`: Ecological context (see EcologicalNiche)

**Demonstrates**: How different ecological niches (high noise, high conformity, efficiency-focused) create different control problems, leading to different linguistic adaptations.

---

### 3. Ecological Language Dynamics (`ecological_language_dynamics.py`)

**Purpose**: Combine PCT with ecological dynamics for realistic language evolution in changing environments.

**Key Additions to Pure PCT**:

1. **Environmental Disturbances**
   - Migration (agents move in space)
   - Contact (horizontal transmission)
   - Innovation (novel forms)
   - Bottlenecks (population changes)

2. **Resource Competition**
   - Limited acoustic space
   - Semantic distinctiveness pressure
   - Efficiency constraints

3. **Fitness as Perceptual Control Success**
   - Comprehension (understood by neighbors)
   - Distinctiveness (avoid homophony)
   - Efficiency (minimize effort)

4. **Niche Construction**
   - Agents modify their environment
   - Community norms emerge from interactions
   - Spatial structure matters

**Ecological Mechanisms**:

```
Time Step:
  1. Update neighborhoods (spatial proximity)
  2. Evaluate fitness (control success)
  3. Apply disturbances (migration, etc.)
  4. Innovation (random novel forms)
  5. Contact (horizontal transmission)
  6. Control adjustment (error correction)
```

**Usage**:
```bash
python3 experiments/ecological_language_dynamics.py
```

**Parameters**:
- `num_agents`: Population size
- `num_concepts`: Number of meanings
- `innovation_rate`: Probability of novel form per step
- `migration_rate`: Probability of agent movement
- `contact_rate`: Probability of form adoption from neighbor

**Output**:
- Agent-level fitness scores
- Event statistics (innovations, migrations, adoptions, adjustments)
- Linguistic diversity metrics
- Full H → O_t history

**Example Output**:
```
Agent 15 (fitness: 0.74):
  concept_0: pibe → pike (innovation)
  concept_1: tut (unchanged)
  concept_2: pate → pat (simplification)

Event Summary:
  contact_adoption: 54
  innovation: 4
  migration: 1
  control_adjustment: 12

Linguistic diversity: 9 unique forms
Environmental disturbances: 1
```

---

## Theoretical Significance

### 1. Beyond Stimulus-Response

Traditional linguistic models treat speakers as passive responders:
- Hear form X → Produce form X
- Social pressure → Conform
- Effort → Simplify

PCT treats speakers as active controllers:
- **Goal**: Be understood, sound normal, speak easily
- **Perception**: Am I achieving my goals?
- **Error**: How far from goal?
- **Action**: Whatever reduces error

This explains phenomena like:
- **Hypercorrection**: Overshooting target due to error signal
- **Accommodation**: Adjusting to reduce comprehension gap
- **Resistance to change**: Stable control loops resist disturbance

### 2. Ecological Context Matters

Languages don't evolve in vacuum - they adapt to **ecological niches**:

**High Noise Environment**:
- Reference signal: MAXIMIZE comprehension
- Adaptation: Redundancy, longer forms, distinctive contrasts
- Example: Ship communication, noisy factories

**High Conformity Environment**:
- Reference signal: MAXIMIZE social alignment
- Adaptation: Rapid convergence, prestige following
- Example: Social class markers, professional registers

**Efficiency-Focused Environment**:
- Reference signal: MINIMIZE effort
- Adaptation: Simplification, contraction, deletion
- Example: High-frequency phrases, casual speech

### 3. Information Loss from Ecological Perspective

The H → O_t → Ĥ framework now includes:

**What's Observable**:
- Final linguistic forms
- Spatial distribution
- Fitness outcomes

**What's Hidden** (and unrecoverable):
- **Reference signals**: What agents were trying to control
- **Error histories**: How close/far from goals over time
- **Ecological pressures**: What environmental factors shaped adaptation
- **Individual control loops**: Internal perceptual states

**Implication**: Reconstruction can recover patterns but NOT the control processes that produced them.

---

## Integration with Existing Framework

All three experiments follow the H → O_t → Ĥ protocol:

### History (H)
```python
class PerceptualControlLanguage(HistoryGenerator):
    def step(self):
        # Record control adjustments, innovations, etc.
        self.history.record(time, event_type, **data)
```

### Observable (O_t)
```python
def get_observable(self) -> Observable:
    # Returns ONLY externally visible state
    # (forms, locations, fitness)
    # NOT internal control loops or reference signals
```

### Reconstruction (Ĥ)
```python
# BorrowingDetector can be applied to any Observable
detector = BorrowingDetector()
borrowings = detector.detect_borrowings(observable)

# Reveals PATTERNS but not underlying control processes
```

---

## Comparison to Existing Experiments

| Experiment | Mechanism | Theory | Observable Properties |
|------------|-----------|--------|---------------------|
| Phonological Drift | Sound changes propagate | Population dynamics | Geographic distribution |
| Babel | Imperfect transmission | Stochastic errors | Diversity from uniformity |
| Dialect Continuum | Spatial diffusion | Network effects | Continuous variation |
| **PCT Language** | **Error correction** | **Perceptual control** | **Fitness, stability** |
| **Ecological Dynamics** | **Niche adaptation** | **Ecology + PCT** | **Environment-specific patterns** |

**Unique Contributions**:
- First **goal-directed** model (agents have targets, not just responses)
- First **fitness-based** model (success = perceptual control)
- First **ecological niche** model (environment shapes adaptation)
- First **hierarchical control** framework (nested control loops)

---

## Next Steps

### Immediate Extensions

1. **Hierarchical Control**
   - Phoneme control → Word control → Phrase control
   - Different levels have different reference signals
   - Upper levels constrain lower levels

2. **Social Reference Signals**
   - Prestige targets (want to sound like high-status speakers)
   - Identity targets (want to sound like in-group)
   - Politeness targets (want to show appropriate deference)

3. **Learning as Control**
   - Child learners have uncertain reference signals
   - Adjust both forms AND targets through experience
   - Explains language acquisition + change

### Integration with Other Experiments

1. **PCT + Reconstruction**
   - Apply systematic reconstruction to PCT-generated languages
   - Measure: Can Ĥ recover reference signals from O_t?
   - Expected: NO - control processes are unobservable

2. **PCT + False Cognates**
   - Do PCT-generated resemblances fool reconstructors?
   - Convergent control (same goals) → similar forms
   - But different histories

3. **PCT + Borrowing**
   - When agents adjust toward neighbors (high social pressure)
   - Does this look like borrowing or inheritance?
   - Test borrowing detection on PCT output

### Research Questions

1. **Do different niches produce different family tree shapes?**
   - High conformity → rapid convergence (star topology)
   - High innovation → rapid divergence (deep trees)
   - Migration → reticulation

2. **Can we infer ecological pressures from linguistic patterns?**
   - Redundancy → noisy environment?
   - Simplification → efficiency pressure?
   - Prestige following → social stratification?

3. **What are the limits of ecological reconstruction?**
   - Given O_t, can we infer the niche that produced it?
   - Multiple niches → same O_t?
   - Recoverability of ecological history

---

## References

**Perceptual Control Theory**:
- Powers, W. T. (1973). *Behavior: The Control of Perception*
- Powers, W. T. (2005). *Behavior: The Control of Perception* (2nd ed.)

**Ecological Linguistics**:
- Calvin, W. H. (1996). *How Brains Think*
- Mufwene, S. (2001). *The Ecology of Language Evolution*
- Nettle, D. (1999). "Is the rate of linguistic change constant?"

**Neural Selection**:
- Calvin, W. H. (1996). *The Cerebral Code*
- Edelman, G. (1987). *Neural Darwinism*

**Language Evolution**:
- Christiansen, M. & Kirby, S. (2003). *Language Evolution*
- Hurford, J. (2014). *Origins of Language*

---

## Technical Notes

### Performance

All three experiments run efficiently:
- **Borrowing Detector**: O(V²L) where V = vocabulary size, L = languages
- **PCT Language**: O(ANM) where A = agents, N = neighbors, M = meanings
- **Ecological Dynamics**: O(A²M) worst case (neighborhood updates)

Typical run times (50 steps):
- PCT Language: <1 second
- Ecological Dynamics: 1-2 seconds

### Reproducibility

All experiments support `seed` parameter for deterministic runs:
```python
sim = EcologicalLanguageSystem(seed=42)
# Identical results across runs
```

### Observable Format

All experiments produce standard `Observable` objects compatible with:
- Systematic reconstruction
- Borrowing detection
- Cross-experiment framework
- Recoverability analysis

---

## Summary

These three experiments introduce **Perceptual Control Theory** to the language evolution framework:

1. **Borrowing Detector**: Practical tool for identifying horizontal transmission
2. **PCT Language**: Theoretical foundation - speakers control perceptions, not responses
3. **Ecological Dynamics**: Realistic integration - PCT + environment

**Core Innovation**: Language users are active controllers with goals, not passive responders to stimuli. This fundamentally changes how we model and interpret language evolution.

**Integration**: All experiments follow H → O_t → Ĥ protocol, enabling:
- Ground truth comparison
- Recoverability analysis  
- Cross-experiment composition
- Systematic reconstruction

**Research Value**: Opens new questions about ecological adaptation, control processes, and the limits of historical inference from modern evidence.
