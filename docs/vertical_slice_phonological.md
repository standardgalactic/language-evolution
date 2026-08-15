# Vertical Slice: Phonological Drift → Reconstruction

## Overview

This document describes the first complete **H → O_t → Ĥ vertical slice** in the `language-evolution` repository.

Unlike the isolated experiments (which demonstrate individual components), this vertical slice connects:

1. **History generation** (Phonological Drift)
2. **Observable extraction** (lossy projection)
3. **Reconstruction** (comparative method)
4. **Ground-truth comparison** (accuracy measurement)
5. **Recoverability analysis** (information loss quantification)

## Research Question

> Given realistic population-based sound change with geographical and prestige effects, how much of the proto-language can be recovered from daughter languages alone, and which historical distinctions become genuinely unrecoverable?

## Implementation

### Files

- `experiments/phonological_reconstruction.py` — Single trial demonstration
- `experiments/recoverability_stress_test.py` — Multi-trial recoverability analysis
- `tests/test_framework.py` — Framework invariant tests

### Architecture

The experiments strictly enforce the H/O_t/Ĥ separation:

```
┌─────────────────────┐
│  Phonological Drift │  ← Secretly retains complete H
│  (History Generator)│
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Observable   │  ← Lossy projection (O_t)
    │ Extraction   │    - Sample subset of speakers
    └──────┬───────┘    - Record only final forms
           │            - Discard history
           ▼
 ┌───────────────────┐
 │ Reconstructor     │  ← No privileged access
 │ (Inference System)│    - Sees only O_t
 └────────┬──────────┘    - Must infer proto-forms
          │
          ▼
   ┌─────────────┐
   │ Comparison  │  ← Measure H vs Ĥ
   │ & Analysis  │    - Accuracy metrics
   └─────────────┘    - Recoverability limits
```

### Key Methodological Distinctions

1. **History is generated, not specified**  
   Unlike classical comparative method examples with hand-crafted proto-languages, Phonological Drift generates proto-languages emergently from population dynamics.

2. **Observable is deliberately incomplete**  
   The experiment samples a subset of speakers (typically 8 of 20), representing documented vs. extinct lineages. Reconstruction operates on incomplete evidence.

3. **Reconstructor has no privileged access**  
   The `PopulationBasedReconstructor` class receives only `observable.languages`, never the actual history or proto-forms.

4. **Accuracy is quantified**  
   We can measure exact vs. close vs. wrong reconstructions because ground truth exists.

5. **Recoverability is first-class**  
   The stress test specifically searches for cases where different histories H₁ ≠ H₂ produce similar observables O_t(H₁) ≈ O_t(H₂).

## Experimental Results

### Single Trial (phonological_reconstruction.py)

Running with seed 42:

- **Population**: 20 speakers, 8 documented
- **Evolution**: 15 generations with 3 sound changes introduced at different times
- **Reconstruction accuracy**: 8/8 exact matches (100%)

However, this high accuracy reflects:
- Clean geographical split (changes didn't spread to all speakers)
- Sufficient documentation (8 of 20 speakers observed)
- Simple majority-rule reconstruction (conservative bias toward unchanged forms)

The experiment explicitly lists **information lost**:
- 12 speaker lineages undocumented
- Sound change ordering unknown
- Intermediate forms lost
- Prestige/geographical effects not directly observable

### Stress Test (recoverability_stress_test.py)

Running 10 trials with different random seeds reveals:

**Reconstruction Variation**:
```
Trial 0:  2/8 exact (25%)
Trial 1:  8/8 exact (100%)
Trial 2:  8/8 exact (100%)
...
Trial 9:  7/8 exact (88%)

Aggregate: 55/80 exact (68.8%)
```

**Key Finding**: Different evolutionary trajectories yield 25% to 100% exact reconstruction accuracy, even with identical experimental parameters.

**Varying Observation Levels** (fixed seed 100):
```
2 observed speakers:  100% accuracy
4 observed speakers:  100% accuracy
8 observed speakers:  100% accuracy
12 observed speakers: 100% accuracy
```

This particular seed happened to produce very clean splits. Other seeds show degradation with sparse observation.

## Recoverability Insights

### What Remains Recoverable

1. **Sound correspondences**: If a change affected all observed daughters consistently, the proto-form can often be inferred
2. **Conservative forms**: Unchanged forms in any daughter provide direct evidence of proto-language
3. **Systematic patterns**: Regular correspondences across cognate sets

### What Becomes Unrecoverable

1. **Timing**: When changes occurred is lost (only final state visible)
2. **Order**: Sequence of changes cannot be determined from O_t alone
3. **Mechanism**: Whether change spread via prestige, geography, or random drift
4. **Extinct lineages**: Speakers not documented leave no trace
5. **Failed innovations**: Changes that started but didn't spread
6. **Convergent evolution**: Different paths to same form are indistinguishable

### Observational Indistinguishability

The stress test searches for pairs (H₁, H₂) where H₁ ≠ H₂ but O_t(H₁) ≈ O_t(H₂).

In the current sample, no strong indistinguishability was found (observable similarity threshold 80% not met).

This suggests either:
- The current sound changes produce sufficient differentiation
- Sample size (10 trials) is too small
- Higher threshold needed

**Future work**: Increase trial count, vary sound change probabilities, or introduce borrowing/convergence to generate stronger indistinguishability cases.

## Architectural Validation

This vertical slice validates the H → O_t → Ĥ architecture by:

✅ **Generating realistic history** (population dynamics, not hand-crafted rules)  
✅ **Enforcing observational limits** (reconstruction sees only O_t)  
✅ **Measuring accuracy quantitatively** (ground truth comparison)  
✅ **Identifying information loss** (what's unrecoverable from O_t)  
✅ **Running stress tests** (variation across seeds)

## Limitations and Extensions

### Current Limitations

1. **Simple reconstructor**: Majority-rule is naive compared to real comparative method
2. **No systematic correspondences**: Doesn't identify regular sound change patterns
3. **No relative chronology**: Doesn't infer change ordering
4. **No confidence calibration**: Confidence scores not yet validated

### Planned Extensions

1. **Systematic correspondence detection**: Identify regular patterns like p:f:p across languages
2. **Subgrouping inference**: Cluster languages by shared innovations
3. **Relative chronology**: Infer ordering when changes interact
4. **Borrowing detection**: Identify non-inherited vocabulary
5. **False Cognate Laboratory**: Measure accidental similarity rates

## Conclusions

The Phonological Drift → Reconstruction vertical slice demonstrates that:

1. **Realistic evolution can be simulated** with emergent proto-languages
2. **Reconstruction is quantifiable** with ground truth comparison
3. **Accuracy varies significantly** across evolutionary trajectories
4. **Information loss is measurable** and often substantial
5. **The H → O_t → Ĥ framework works** for rigorous experiment design

Most importantly, this is the first experiment in `language-evolution` that **completes the full loop**:

[
\text{Generate }H
\rightarrow
\text{Extract }O_t
\rightarrow
\text{Infer }\hat{H}
\rightarrow
\text{Compare }\hat{H}\text{ vs }H
]

Future vertical slices should follow this pattern:
- Choose a history generator (Semantic Drift, Lexical Selection, etc.)
- Define observable extraction (what evidence survives?)
- Build an inference system (how to reconstruct?)
- Measure accuracy and recoverability

Each vertical slice becomes a quantitative investigation of **what history leaves behind** in a specific evolutionary process.
