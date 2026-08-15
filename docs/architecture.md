# Architecture

Language Evolution is a computational laboratory for historical linguistics with **ground truth**. Unlike real historical linguistics, where the actual history is forever lost, our simulations secretly retain complete evolutionary traces. This enables rigorous experimental investigation of a fundamental question: **which facts about history remain inferable after history has erased its own evidence?**

## The H → O_t → Ĥ Protocol

All experiments follow a three-stage architecture:

```
H (actual history) → O_t (observable at time t) → Ĥ (reconstructed history)
```

### H: History Generators

Simulators that produce complete evolutionary traces. These **secretly retain everything** that happened:

- **Phonological Drift**: Sound change propagation through populations
- **Semantic Drift Machine**: Meaning evolution in lexical space
- **Glyph Evolution**: Visual form change in writing systems  
- **ASL Handshape Drift**: Sign language evolution in articulatory space
- **Borrowing Without Ancestry**: Contact-induced change obscuring vertical inheritance
- **Minimum Language**: Grammatical complexity emerging from communicative pressure
- **Maximum Language**: Complexity reduction through imperfect transmission

### O_t: Observable Evidence

What remains visible at time t. Critical information has been **irreversibly lost**:

- Contemporary language states (phonology, lexicon, grammar)
- Geographical distribution
- Written records (when available)
- Typological patterns

Crucially: **H ≠ O_t**. The observable is a lossy projection of history.

### Ĥ: Inference Systems

Reconstruction algorithms that attempt to recover history from observables alone:

- **Reconstruct**: Comparative method applied to generated language families
- **False Cognate Laboratory**: Measuring accidental similarity vs. true inheritance

### Environments

Multi-mechanism frameworks where generators interact:

- **The Dialect Continuum**: Spatial diffusion without tree structure
- **The Babel Experiment**: Emergent language formation from uniform origins
- **Language Earth**: Full integration of all mechanisms

## Measuring Recoverability

The key experimental question is not "did we reconstruct correctly?" but **"was the distinction even recoverable?"**

Two different histories H₁ ≠ H₂ can produce observationally indistinguishable present states:

```
O_t(H₁) ≈ O_t(H₂)
```

At that point, reconstruction failure isn't a bad algorithm—the information required to distinguish the histories **genuinely no longer exists** in the observable state.

We measure:

1. **Precision/Recall**: Standard metrics for H vs Ĥ comparison
2. **Recoverability**: Which event types leave vs don't leave traces
3. **Information Bottlenecks**: When and why historical information becomes permanently lost
4. **Indistinguishable Pairs**: Distinct histories with similar observables

## Repository Structure

```
src/language_evolution/
  framework.py          # H → O_t → Ĥ base classes and metrics
  phonology.py          # Phonological primitives
  semantics.py          # Semantic space representations
  
experiments/
  # History Generators
  phonological_drift.py
  semantic_drift.py
  glyph_evolution.py
  minimum_language.py
  maximum_language.py
  
  # Inference Systems  
  reconstruct.py
  false_cognates.py
  
  # Environments
  dialect_continuum.py
  babel.py
  language_earth.py
```

This organization reflects the experimental protocol rather than conventional linguistic subfields.
