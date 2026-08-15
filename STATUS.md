# Language Evolution: Implementation Status

`language-evolution` is now a working computational laboratory for **historical linguistics with ground truth**. Its experiments are organized around a common protocol:

[
H \longrightarrow O_t \longrightarrow \hat{H}
]

where (H) is the complete evolutionary history retained by the simulator, (O_t) is the evidence available to an observer at time (t), and (\hat H) is the history reconstructed from that evidence.

The central research question is no longer merely whether historical reconstruction succeeds, but **which distinctions in history remain recoverable from the evidence history leaves behind**.

## Core Framework ✓

**Location:** `src/language_evolution/framework.py`

The common framework implements the (H \rightarrow O_t \rightarrow \hat H) protocol and keeps ground truth explicitly separated from observable evidence and inference.

`History` retains the complete evolutionary trace. `Observable` represents a deliberately lossy projection of that history at time (t). `Reconstruction` represents an inferred history derived from observables rather than privileged simulator state.

`HistoryGenerator` provides the base abstraction for evolutionary simulations, while `InferenceSystem` provides the corresponding abstraction for reconstruction algorithms.

The framework also provides `compare_histories()` for precision, recall, F1, and temporal-error measurements, together with `RecoverabilityAnalysis` for detecting cases in which distinct histories become observationally indistinguishable.

This separation is fundamental: reconstruction systems should never obtain privileged access to (H).

## Supporting Infrastructure ✓

### Phonology

**Location:** `src/language_evolution/phonology.py`

The phonological layer provides `Phoneme`, using distinctive-feature representations; `SoundChange`, representing probabilistic and context-sensitive transformations; `PhonemeInventory`, representing language-level sound systems; and `create_basic_inventory()`, providing a Proto-Indo-European-like starting inventory for experiments.

### Semantics

**Location:** `src/language_evolution/semantics.py`

The semantic layer represents meaning geometrically. `SemanticVector` locates meanings in semantic space, `SemanticRegion` represents fuzzy meaning boundaries, and `SemanticSpace` provides a multidimensional environment in which those meanings interact.

Implemented operations include semantic drift, broadening, narrowing, and overlap detection.

---

# History Generators

## 1. Phonological Drift ✓

**File:** `experiments/phonological_drift.py`

Phonological Drift models sound change as a population process rather than as a predetermined sequence of historical rules.

The experiment places 25 speakers on a two-dimensional geographical grid. Probabilistic sound changes spread through neighbor influence and prestige effects, including Grimm's-Law-like transformations such as (p\rightarrow f), (t\rightarrow\theta), and (k\rightarrow h). Lexical divergence is tracked across 15 generations.

A typical run produces outcomes such as:

```text
Sample pronunciations after 15 generations:

'pater':
  Speaker 17: faθer
  Speaker 21: pater

Average lexical divergence: 0.377
Maximum lexical divergence: 0.750
```

The important result is not merely that sound change occurs, but that population structure allows linguistic differentiation to emerge from local interactions.

## 2. Minimum Language ✓

**File:** `experiments/minimum_language.py`

Minimum Language investigates whether grammatical complexity can arise from communicative necessity.

The experiment begins with approximately 12 roots and simple juxtaposition. Agents invent constructions when the existing system cannot adequately distinguish intended meanings. Over 150 rounds of communication, the simulation records the emergence and reuse of constructions.

A typical result includes:

```text
Initial lexicon: 12 roots
Constructions: 1

After 150 rounds:
  'person' → 'ka' (20 uses)
  'do(person, thing)' → 'ma ka to' (22 uses)
```

Rather than beginning with a rich grammar and simplifying it, this experiment asks how structure can arise from an intentionally impoverished starting point.

## 3. Semantic Drift Machine ✓

**File:** `experiments/semantic_drift.py`

Semantic Drift Machine models meanings as regions moving through a multidimensional semantic space.

Eight words occupy a three-dimensional space representing contrasts such as concrete/abstract, positive/negative, and animate/inanimate. Usage contexts gradually modify those regions over 60 time steps.

The resulting trajectories are subsequently classified using categories such as broadening, narrowing, metaphorical extension, amelioration, and pejoration.

For example:

```text
Semantic Change Classification:

  animal: BROADENING, METAPHOR/EXTENSION
  person: CONCRETIZATION, METAPHOR/EXTENSION
  part: METAPHOR/EXTENSION

Total events: 152
  142 shifts
  10 broadenings
```

The intended methodological distinction is important: recognizable semantic-change categories describe trajectories produced by the simulation rather than simply serving as names for predetermined outcomes.

## 4. Lexical Natural Selection ✓

**File:** `experiments/lexical_selection.py`

Lexical Natural Selection models competition among synonymous forms without reducing lexical fitness to a single universal scalar.

Variants differ along dimensions including length, articulatory cost, regularity, prestige, memorability, ambiguity, and usage frequency. Their relative advantages depend upon context, including formal, informal, and neutral interactions.

Four meanings begin with three competing variants each and evolve over 150 time steps.

One run produces:

```text
father:
  pa:    418 uses (36.5%)
  papa:  398 uses (34.8%)
  pater: 329 uses (28.7%)
```

The shorter and easier form becomes most frequent without eliminating the prestigious alternative. Selection therefore emerges from interacting constraints rather than from an imposed total ordering of forms.

---

# Inference Systems

## 5. Reconstruct ✓

**File:** `experiments/reconstruct.py`

Reconstruct closes the experimental loop by attempting historical inference without access to the simulator's hidden ground truth.

The experiment generates a known proto-language, evolves it into four daughter languages over 20 time steps, conceals the ancestral state, and applies a simplified comparative method using only the surviving daughter languages.

The resulting reconstruction can then be evaluated against the history that actually occurred.

A representative run reports:

```text
Reconstruction Accuracy:

  Correct: 6/10 (60.0%)
  Partial: 4/10 (40.0%)
  Wrong:   0/10 (0.0%)
```

This is the first direct realization of the complete protocol:

[
H \rightarrow O_t \rightarrow \hat H
]

The important distinction is between **inference error** and **information that is no longer recoverable from (O_t)**.

---

# Recoverability

## 6. Recoverability Experiment ✓

**File:** `experiments/recoverability.py`

The Recoverability Experiment investigates that distinction directly.

Rather than asking only whether an algorithm can reconstruct a particular history, it generates multiple independent histories and searches for cases satisfying approximately:

[
H_1 \neq H_2
\qquad\text{but}\qquad
O_t(H_1)\approx O_t(H_2).
]

Such cases represent different pasts that have left the same, or nearly the same, surviving evidence.

A representative run finds:

```text
Histories 0 and 3:

  DIFFERENT histories
  SIMILAR observables

Observable distance: 0.000
History 0: 3 events
History 3: 7 events

→ OBSERVATIONALLY INDISTINGUISHABLE
```

Across ten generated histories, the example run identifies **24 pairs of distinct histories with similar observable outcomes**.

This is stronger than demonstrating that reconstruction is difficult. It identifies cases in which information required to distinguish histories may no longer be present in the observation at all.

---

# Current Architectural Validation

The repository now demonstrates that the (H \rightarrow O_t \rightarrow \hat H) architecture can support several distinct kinds of linguistic experiment while maintaining the same epistemic separation.

History generation is separated from observation. Observation is explicitly lossy. Reconstruction operates without privileged access to simulator history. Ground truth permits reconstruction to be evaluated afterward. Recoverability analysis additionally allows distinct histories to be compared according to the evidence they leave behind.

The experiments therefore distinguish three questions that should not be collapsed:

[
\text{What actually happened?}
]

[
\text{What evidence survived?}
]

[
\text{What can legitimately be inferred from that evidence?}
]

This distinction is becoming the repository's principal organizing idea.

## Current Coverage

The repository currently contains a functioning core framework, supporting phonological and semantic infrastructure, four history-generating experiments, one explicit inference experiment, and one dedicated recoverability experiment.

The implemented experiments already cover sound change, grammatical emergence, semantic change, lexical competition, comparative reconstruction, and observational equivalence.

The next development phase should therefore emphasize experiments that challenge the framework in qualitatively different ways rather than merely increasing the number of simulations.

# Next Experimental Targets

**False Cognate Laboratory** will measure accidental resemblance and investigate how evidential requirements alter false-positive rates.

**Dialect Continuum** will challenge genealogical tree assumptions by modeling diffusion through continuous geographical and social space.

**Borrowing Without Ancestry** will introduce horizontal transmission and test when genealogical reconstruction mistakes contact for descent.

**The Babel Experiment** will investigate whether differentiated languages and dialects emerge from an initially uniform population without explicitly encoding those outcomes.

**Maximum Language** will complement Minimum Language by beginning with excessive complexity and measuring what survives imperfect transmission.

**Glyph Evolution** will extend the framework into writing-system evolution.

**ASL Handshape Drift** will test whether the framework remains useful when linguistic evolution occurs in a different articulatory and perceptual modality.

**The Last Similar Thing** will compare recency-based transmission with retrieval based upon structural and contextual similarity.

**Language Earth** remains the long-term integration experiment: a population-scale environment combining migration, contact, divergence, borrowing, innovation, writing, prestige, isolation, reconnection, and cultural transmission while retaining a complete hidden historical record.

# Status

**Core framework:** Working
**Supporting linguistic infrastructure:** Working
**History generators:** 4 working
**Inference systems:** 1 working
**Dedicated recoverability experiments:** 1 working
**Total working experiments:** 6

The repository has therefore moved beyond its original template stage. It now contains a functioning experimental architecture for **historical linguistics with ground truth**.

Its strongest result so far is not any individual linguistic simulation. It is the establishment of a common experimental distinction between **history, surviving evidence, and justified reconstruction**.

The next goal is to stress that distinction under progressively harder conditions—especially borrowing, convergence, sparse evidence, modality changes, and non-tree evolution—and determine not merely when reconstruction fails, but **why**:

[
\boxed{
\text{Was the history inferred incorrectly, or has the evidence required to know it ceased to exist?}
}
]
