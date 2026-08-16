# Dialect Continuum Analysis

## Experiment Complete

**File**: `experiments/dialect_continuum.py`  
**Type**: Environment experiment (first of this category)  
**Status**: ✅ Working

## Research Question

**When do mutually intelligible varieties become distinct languages?**

This question has no objective answer because linguistic boundaries are **observer-constructed**, not inherent in the evolutionary process.

## Model Architecture

### NON-TREE Diffusion

Unlike `phonological_drift.py` (population on a branching tree), this models:
- **Continuous** 2D geographic space
- **Local** diffusion between neighbors
- **No** discrete branching points
- **Emergent** dialect areas from accumulation

### Parameters

- Grid: 10×10 space
- Speakers: 60 (randomly placed)
- Influence radius: 1.5 (how far changes diffuse)
- Generations: 50 innovations with probabilistic diffusion

### Evolution Process

1. **Innovation**: Random speaker develops a sound change
2. **Diffusion**: Change spreads to geographic neighbors with probability proportional to distance
3. **Accumulation**: Over generations, nearby speakers remain similar, distant speakers diverge

## Results

### Example Run (seed=42)

**Initial state**: All 60 speakers share proto-language with inventory `[a, i, k, p, t, u]`

**After 50 generations**:

| Corner | Inventory | Changes |
|--------|-----------|---------|
| Southwest | `[a, i, kʱ, p, t, u]` | k→kʱ voicing |
| Southeast | `[a, i, kʱ, p, t, u]` | k→kʱ voicing |
| Northwest | `[a, i, k, p, tʱ, u]` | t→tʱ voicing |
| Northeast | `[a, i, k, p, t, u]` | (original) |

### Phonological Distances

| Pair | Distance | Interpretation |
|------|----------|----------------|
| SW ↔ SE | 0.00 | Identical (same innovation spread) |
| SW ↔ NW | 0.50 | Different changes |
| SW ↔ NE | 0.29 | Partial overlap |
| SE ↔ NW | 0.50 | Different changes |
| SE ↔ NE | 0.29 | Partial overlap |
| NW ↔ NE | 0.29 | Partial overlap |

### Dialect Areas (Threshold: 0.3)

Clustering by phonological similarity identified **4 dialect areas**:
- Area A: 4 speakers
- Area B: 48 speakers (majority)
- Area C: 7 speakers
- Area D: 1 speaker

## Key Insights

### 1. Boundaries Are Observer-Constructed

The actual process is **continuous spatial diffusion**. There are no inherent boundaries between "languages."

The number of dialect areas depends on:
- Similarity threshold chosen
- Sampling locations
- Time of observation

### 2. Mutual Intelligibility Is Gradient

- SW and SE: 0.00 distance (mutually intelligible)
- SW and NW: 0.50 distance (partially intelligible?)
- Geographic distance correlates with linguistic distance

### 3. Family Trees Are Simplifications

Traditional family trees show:
```
Proto
  ├─ Language A
  └─ Language B
```

Reality is continuous variation:
```
Speaker 1 ←→ Speaker 2 ←→ Speaker 3 ←→ ...
  (0.1 diff)    (0.1 diff)    (0.1 diff)
```

Accumulated small differences create larger gaps, but the process has no discrete branching points.

## H → O_t → Ĥ Protocol

### Ground Truth H (Retained)

- All 60 speakers (including undocumented)
- All 32 innovation events (who, where, when, what)
- All 34 diffusion events (from → to, distance, adoption)
- Complete temporal ordering (128 total events)

### Observable O_t

- 20 documented speakers (33.3% coverage)
- Phonological inventories at time t
- Geographic locations
- **Missing**: temporal sequence, diffusion paths, undocumented speakers

### What Reconstruction Must Infer

From geographic distribution of phonological patterns, infer:
- Which innovations occurred?
- Where did they originate?
- How did they spread?
- What was the original proto-language?

**Challenge**: Multiple histories could produce similar observable patterns (recoverability problem).

## Connection to Theoretical Framework

This experiment operationalizes several concepts from the reconstruction/repair cluster:

### Observability Is Restorability

The question "which dialect areas exist?" has no ground-truth answer because dialect areas are **observational categories**, not historical facts.

What survives as "diagnostic coordinates":
- ✓ Phonological inventories (directly observable)
- ✓ Geographic distribution (directly observable)
- ✗ Temporal sequence (unobservable)
- ✗ Diffusion paths (must be inferred)
- ✗ Innovation origins (must be inferred)

### Distinguishability Geometry

Two different histories H₁ ≠ H₂ can produce observationally indistinguishable states O_t(H₁) ≈ O_t(H₂):

**Example**: 
- H₁: Innovation at SW, diffuses east
- H₂: Innovation at SE, diffuses west
- Both produce: SW and SE with same phonology

Without temporal data, these are indistinguishable.

### Restorability Boundary

As generations increase:
- More innovations accumulate
- Undocumented speakers carry hidden variation
- Observable coverage (33%) leaves 67% unknown

At some point, the information needed to reconstruct the exact diffusion history has been **irreversibly lost**.

## Comparison With Other Experiments

| Experiment | Model Type | Key Feature |
|------------|-----------|--------------|
| `phonological_drift.py` | Population tree | Branching structure explicit |
| `dialect_continuum.py` | Geographic continuum | NO branching, continuous variation |
| `borrowing.py` | Contact between families | Horizontal transmission |

**Dialect Continuum** is unique: it demonstrates that **linguistic boundaries are useful fictions** we impose on continuous variation for practical purposes.

## Implications for Historical Linguistics

### Why "How many languages?" is ill-defined

The observable facts:
- 60 speakers
- Phonological distances ranging 0.00–0.50
- Continuous geographic distribution

The observer's choice:
- Similarity threshold determines # of "languages"
- No threshold is objectively correct
- Different thresholds serve different purposes

### Why Comparative Method Has Limits

The comparative method assumes:
- Discrete languages descended from common ancestor
- Primarily vertical (tree-like) transmission

Dialect continuum shows:
- Languages are arbitrary groupings of continuous variation
- "Common ancestor" may be an entire region, not a single point
- Geographic diffusion ≠ branching descent

### What Can Be Reconstructed

✓ **Proto-inventory** (shared features across all speakers)  
✓ **Innovation existence** (kʱ appeared somewhere)  
✓ **Geographic patterns** (which regions share which changes)  

✗ **Temporal ordering** (which innovation happened first?)  
✗ **Diffusion paths** (exactly how did it spread?)  
✗ **Undocumented variation** (67% of speakers missing)  

## Future Work

### Barriers

Add geographic barriers (mountains, rivers) and measure:
- How barriers create linguistic boundaries
- When continuous variation becomes discrete separation

### Migration

Allow speakers to move over time:
- How does migration blur dialect boundaries?
- Can linguistic geography recover migration history?

### Writing Systems

Introduce written standards in some areas:
- Do written norms slow phonological change?
- How do prescriptive standards interact with natural diffusion?

### Reconstruction Challenge

Build an inference system that:
1. Receives only O_t (20 sampled speakers)
2. Attempts to reconstruct diffusion history
3. Compares inferred history Ĥ against ground truth H

Measure: **What can actually be recovered from geographic distribution alone?**

## Code Statistics

- **480 lines** total
- **~180 lines** core algorithm (DialectContinuum class)
- **~150 lines** analysis/visualization
- **~150 lines** documentation

All changes diffuse in ~50 generations with simple voicing innovations.

## Reproducibility

```bash
python3 experiments/dialect_continuum.py
```

Deterministic with `seed=42`. Output includes:
- Phonological distances between geographic corners
- Dialect area clustering
- ASCII visualization
- H vs. O_t comparison
- Event statistics (32 innovations, 34 diffusions)

---

**Status**: First environment experiment complete ✓  
**Category**: Non-tree diffusion models  
**Next**: Babel Experiment (emergence from uniform origins)
