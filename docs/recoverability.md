# Recoverability in Historical Linguistics

## The Fundamental Question

Given only contemporary evidence, **which facts about linguistic history remain knowable?**

In real historical linguistics, we can never answer this definitively—we don't have ground truth. But in simulation, we can secretly retain complete evolutionary traces and measure exactly what information survives to the present.

## The H → O_t → Ĥ Framework

Every `language-evolution` experiment follows this protocol:

### H: Complete History (Ground Truth)

The simulator retains everything that happened:
- Every sound change, with exact timing
- Every borrowing event, with source and target
- Every semantic shift
- Every structural innovation
- Complete genealogical relationships

**In real linguistics, this is forever lost.**

### O_t: Observable Evidence

What remains visible at time t:
- Contemporary language states (phonology, lexicon, grammar)
- Geographical distribution
- Written records (when they exist)
- Typological patterns

**This is all a historical linguist actually has.**

### Ĥ: Reconstructed History

What we infer from observables:
- Proto-forms via comparative method
- Sound correspondence rules
- Proposed genealogies
- Estimated divergence times

**This is our best guess at H.**

## Measuring Recoverability

The key experimental quantity is **comparison accuracy**: how well does Ĥ match H?

Standard metrics:
- **Precision**: Of inferred events, how many actually happened?
- **Recall**: Of events that happened, how many did we infer?
- **Temporal error**: How accurately can we date events?

But the deeper question is **recoverability**: which distinctions remain observable?

## Observational Indistinguishability

Two different histories H₁ ≠ H₂ can produce identical (or nearly identical) present states:

```
O_t(H₁) ≈ O_t(H₂)
```

### Example: Sound Change Order

Consider two histories:

**History A:**
1. p → f at time 5
2. t → θ at time 12

**History B:**  
1. t → θ at time 3
2. p → f at time 18

Both produce the same final language state, but:
- Different events happened at different times
- Intermediate forms were different
- The actual historical trajectory was completely different

**From contemporary evidence alone, these are indistinguishable.**

### Example: Change Frequency

**History X:** p → f applied once at time 10

**History Y:** p → f attempted 7 times (time 3, 5, 8, 10, 12, 15, 18), finally succeeded at time 18

Both produce the same result: contemporary /f/ where proto-language had /p/.

Observable evidence cannot distinguish:
- One early change vs one late change
- One successful change vs many failed attempts  
- Gradual spread vs sudden adoption

## What's Recoverable vs Unrecoverable

### Generally Recoverable

- **Sound correspondences**: Regular patterns across cognates leave clear traces
- **Shared innovations**: Multiple languages undergoing the same change indicates common ancestry
- **Relative chronology**: When changes interact (e.g., chain shifts), order sometimes inferable

### Partially Recoverable

- **Absolute timing**: We can order events but rarely date them precisely
- **Intermediate stages**: Later changes overwrite earlier traces
- **Failed innovations**: Changes that started but didn't spread leave no trace

### Generally Unrecoverable  

- **Borrowing vs inheritance**: Look-alike words may be cognates or loans; distinguishing requires external evidence
- **Parallel development**: Independent populations may innovate identically
- **Change mechanism**: Final state doesn't reveal whether change was gradual, abrupt, prestige-driven, or articulatory
- **Lost intermediates**: If A → B → C → D, intermediate B and C may be completely erased

## The Recoverability Experiment

`experiments/recoverability.py` demonstrates this empirically:

```python
$ python3 experiments/recoverability.py

Generating 10 independent evolution histories...

Histories 0 and 3: DIFFERENT histories, SIMILAR observables
  Observable distance: 0.000
  History 0: 3 events
  History 3: 7 events
  → These histories are OBSERVATIONALLY INDISTINGUISHABLE
  
Found 24 pairs of distinct histories that produced 
observationally similar outcomes.
```

**Interpretation**: More than half of the generated histories are indistinguishable from at least one other history. The information required to distinguish them **genuinely no longer exists**.

## Implications for Historical Linguistics

### 1. Some Questions Are Unanswerable

Not because our methods are bad, but because the required information has been irreversibly lost.

### 2. Confidence Should Vary by Event Type

- Sound correspondences: High confidence
- Proto-form reconstructions: Medium confidence  
- Absolute chronology: Low confidence
- Individual borrowing events: Very low confidence

### 3. Alternative Histories May Be Equally Plausible

When H₁ and H₂ both produce O_t, preferring one over the other requires external criteria (simplicity, typological plausibility, etc.)—not empirical evidence.

### 4. The Comparative Method Has Fundamental Limits

Even perfect application of the comparative method cannot recover information that no longer exists in the signal.

## Research Questions

`language-evolution` enables quantitative investigation of:

1. **Which event types leave the strongest traces?**
   - Generate histories with varying proportions of sound change, borrowing, semantic shift
   - Measure recovery accuracy by category

2. **How does recoverability decay with time?**
   - Plot recovery accuracy vs. time depth
   - Identify temporal horizons beyond which certain information becomes unrecoverable

3. **When do horizontal and vertical signals become confusable?**
   - Generate languages with known borrowing vs inheritance
   - Measure when tree-building algorithms fail

4. **What sample size is required for reliable reconstruction?**
   - Vary number of daughter languages
   - Measure reconstruction accuracy as function of sample size

5. **How much does writing help?**
   - Compare recoverability with vs without intermediate written records
   - Quantify information preservation from documentation

## Philosophical Point

In real historical linguistics, we can never know whether a failed reconstruction indicates:
- A bad method
- Insufficient data
- **Information that genuinely no longer exists**

With ground truth, we can finally distinguish these cases.

This is why `language-evolution` is not just another simulation framework—it's a laboratory for investigating **the limits of knowability in historical science**.
