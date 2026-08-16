# Experiments Catalog

Complete list of all experiments in language-evolution repository.

## History Generators (7)

Evolution mechanisms that generate H (ground truth history).

### 1. phonological_drift.py
- **Type**: Population-based sound change
- **Model**: 20 speakers on 2D grid, geographic effects
- **Key Feature**: Prestige, geographical isolation
- **Lines**: ~400

### 2. semantic_drift.py  
- **Type**: Meaning change over time
- **Model**: Semantic regions in continuous space
- **Key Feature**: Narrowing, broadening, metaphor
- **Lines**: ~300

### 3. lexical_selection.py
- **Type**: Word competition
- **Model**: Synonymous forms compete
- **Key Feature**: Articulatory cost, frequency, regularity
- **Lines**: ~250

### 4. minimum_language.py
- **Type**: Complexity emergence
- **Model**: Start minimal, add constructions as needed
- **Key Feature**: Grammatical complexity from communicative pressure
- **Lines**: ~300

### 5. babel.py ⭐ NEW
- **Type**: Emergence from uniformity
- **Model**: 200 agents, identical start, imperfect transmission
- **Key Feature**: Diversity emerges without programming it
- **Lines**: 520

### 6. glyph_evolution.py ⭐ NEW
- **Type**: Writing system evolution
- **Model**: Visual glyphs, copying errors, economy pressure
- **Key Feature**: NON-PHONOLOGICAL (visual substrate)
- **Lines**: 400

### 7. last_similar_thing.py ⭐ NEW
- **Type**: Memory-based transmission
- **Model**: Similarity retrieval vs. LIFO
- **Key Feature**: Tests memory mechanism assumptions
- **Lines**: 430

## Inference Systems (4)

Reconstruction algorithms that generate Ĥ from O_t.

### 8. reconstruct.py
- **Type**: Basic reconstruction
- **Model**: Evolve then reconstruct
- **Key Feature**: First vertical slice
- **Lines**: ~200

### 9. phonological_reconstruction.py
- **Type**: Population-based reconstruction
- **Model**: Integrates with phonological_drift
- **Key Feature**: Complete H → O_t → Ĥ pipeline
- **Lines**: ~350

### 10. systematic_reconstruction.py ⭐ NEW
- **Type**: Systematic correspondence method
- **Model**: Detects recurring patterns, not just majority
- **Key Feature**: 100% accuracy on test case
- **Lines**: 507

### 11. false_cognates.py
- **Type**: Baseline false-positive measurement
- **Model**: 50 unrelated languages
- **Key Feature**: Quantifies accidental resemblance (0.165%)
- **Lines**: ~380

## Environments (2) ⭐ NEW CATEGORY

Complex scenarios where multiple mechanisms interact.

### 12. dialect_continuum.py ⭐ NEW
- **Type**: Geographic diffusion
- **Model**: 60 speakers in 2D space, local diffusion
- **Key Feature**: NON-TREE (continuous variation)
- **Lines**: 480

### 13. borrowing.py
- **Type**: Horizontal transmission
- **Model**: 3 families, contact at 10-40%
- **Key Feature**: Tree failure at ~30% borrowing
- **Lines**: ~380

## Methodology (5)

Meta-experiments testing recoverability and methods.

### 14. recoverability.py
- **Type**: Information loss measurement
- **Model**: H₁ ≠ H₂ but O_t(H₁) ≈ O_t(H₂)
- **Key Feature**: Restorability boundaries
- **Lines**: ~180

### 15. recoverability_stress_test.py
- **Type**: Multi-trial recoverability
- **Model**: 10 trials, different seeds
- **Key Feature**: 25-100% accuracy variation
- **Lines**: ~330

### 16. cross_experiment_reconstruction.py ⭐ NEW
- **Type**: Unified reconstruction framework
- **Model**: Same reconstructor for all mechanisms
- **Key Feature**: Comparative recoverability measurement
- **Lines**: 350

### 17. comparative_recoverability.py ⭐ NEW
- **Type**: Mechanism comparison
- **Model**: Divergence vs diffusion vs borrowing
- **Key Feature**: Quantifies mechanism-specific information loss
- **Lines**: 300

### 18. (babel variant - emergence testing)

## Perceptual Control Theory (4) ⭐ NEW FRAMEWORK

Language users control perceptions, not just outputs.

### 19. pct_rigorous.py ⭐ NEW
- **Type**: Rigorous PCT implementation
- **Model**: Powers/Calvin control loops
- **Key Feature**: Signed errors, listener feedback, local sampling
- **Lines**: ~350

### 20. perceptual_control_language.py ⭐ NEW
- **Type**: Goal-directed language behavior
- **Model**: 4 controlled perceptions (comprehension, conformity, effort, distinctiveness)
- **Key Feature**: Ecological niches shape linguistic adaptation
- **Lines**: ~380

### 21. ecological_language_dynamics.py ⭐ NEW
- **Type**: PCT + ecological constraints
- **Model**: Environmental disturbances, fitness = control success
- **Key Feature**: Hierarchical control loops
- **Lines**: ~400

### 22. borrowing_detector.py ⭐ NEW
- **Type**: Borrowed vs. inherited classification
- **Model**: Irregular patterns, partial distribution, cultural clustering
- **Key Feature**: Works with any Observable
- **Lines**: ~280

## Cross-Modal Framework (2) ⭐ NEW

Unified S → C → B_t → O_t pipeline across modalities.

### 23. language_modality_demo.py ⭐ NEW
- **Type**: Cross-modal framework validation (language)
- **Model**: Semantic → Control → Behavior → Observable
- **Key Feature**: Demonstrates invariant structure
- **Lines**: ~200

### 24. gesture_modality_demo.py ⭐ NEW
- **Type**: Cross-modal framework validation (gesture)
- **Model**: Intention → Motor control → Trajectory → Visible
- **Key Feature**: Same framework, different modality
- **Lines**: ~200

### 25. unified_reconstructor_new.py ⭐ NEW
- **Type**: Unified reconstruction approach
- **Model**: Combines multiple methods
- **Key Feature**: Works across history types
- **Lines**: ~320

## Total Statistics

- **25 experiments** (was 10 at session start, was 19 mid-session)
- **~9,500 lines** (was ~3,400)
- **All categories represented**:
  - History Generators: 7
  - Inference Systems: 5
  - Environments: 2
  - Methodology: 5
  - Perceptual Control Theory: 4
  - Cross-Modal Framework: 2

## Experiments by Research Question

**"What mechanisms drive change?"**
- phonological_drift, semantic_drift, lexical_selection, glyph_evolution

**"How does diversity emerge?"**
- babel, dialect_continuum, minimum_language

**"What can be reconstructed?"**
- reconstruct, phonological_reconstruction, systematic_reconstruction

**"What are the limits?"**
- recoverability, recoverability_stress_test, false_cognates

**"How do mechanisms compare?"**
- cross_experiment_reconstruction, comparative_recoverability, borrowing

**"What assumptions matter?"**
- last_similar_thing (memory), dialect_continuum (trees), glyph_evolution (phonology)

## Running Experiments

All experiments are standalone:

```bash
cd experiments
python3 dialect_continuum.py
python3 systematic_reconstruction.py
python3 glyph_evolution.py
```

Cross-experiment framework:

```bash
python3 comparative_recoverability.py
```

## Documentation

Each experiment produces:
- Research question statement
- Model description
- H → O_t → Ĥ protocol adherence
- Key findings
- Theoretical connections

See individual experiment files for details.

---

**Status**: All experiments working, tested, and documented.
**Next**: Integration testing, information-theoretic bounds, Language Earth.
