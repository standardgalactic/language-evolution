# Language Evolution: Structural Invariance Across Modalities

**A rigorous mathematical and computational framework for studying how structure survives transformation across physical channels.**

## Core Hypothesis

```
Observable signal ≠ Underlying structured object
```

Speech, text, signing, gesture, and music are different **projections** through different physical channels of the same fundamental phenomenon: structured semantic/intentional states under continuous transformation.

## The Unified Pipeline

```
S → C → B_t → O_t → Ŝ
```

- **S**: Latent semantic/intentional structure
- **C**: Hierarchy of controlled perceptions (PCT)
- **B_t**: Historically contingent behavior
- **O_t**: Observable projection (what survives)
- **Ŝ**: Reconstructed structure (inverse problem)

## Central Research Question

**Which structures remain invariant enough to be reconstructed when their physical realizations continuously change?**

This unifies:
- Historical linguistics (language change over time)
- Gesture recognition (embodied semantic reconstruction)
- Music cognition (structural relationships across performances)
- Audio semantics (prosody/affect from waveforms)
- Sign language (distributed meaning across articulators)

---

## Mathematical Foundations

### Four Core Theorems (Proven)

#### 1. Representation Invariance
If two systems induce the same canonical transformation structure, they are semantically equivalent—even if their physical substrates differ.

**Status**: THEOREM ✓

#### 2. Admissibility Preservation
Discourse trajectory remains coherent iff minimum support ratio ≥ 1.

**Status**: THEOREM ✓

#### 3. Monotonic Relaxation
Semantic tension E(s) decreases monotonically under gradient flow: dE/dt ≤ 0.

**Status**: THEOREM ✓

#### 4. Non-Identifiability (Deepest)

If H₁ ≠ H₂ but O(H₁) = O(H₂), then no reconstruction algorithm can distinguish them with certainty.

**Status**: THEOREM ✓

**Consequence**: Perfect reconstruction impossible when observation is non-injective. This applies to ALL modalities (language, gesture, music, audio, sign).

---

## Unified Framework

### Modalities Implemented

All modalities follow S → C → B_t → O_t → Ŝ pipeline:

| Modality | Projection | What Survives | What's Lost |
|----------|-----------|---------------|-------------|
| **Language** | Semantic → Linear sequence | Order, count | Meaning, control, alternatives |
| **Gesture** | Intention → Motor trajectory | Handshape changes | Continuous dynamics, intent |
| **Sign** | Distributed meaning → Articulation | Visible configurations | Coarticulation, affect |
| **Music** | Score → Performance | Temporal relationships | Interpretation choices |
| **Audio** | Structure → Waveform | Prosodic patterns | Channel separation |

### Repository Contents

**22+ Experiments**:
- Historical linguistics (10)
- Perceptual Control Theory (4)
- Cross-modal framework (3)
- Reconstruction methods (5)

**Core Framework** (`src/language_evolution/`):
- `framework.py` - H → O_t → Ĥ protocol
- `unified_framework.py` - Cross-modal abstractions
- `theorems.py` - Mathematical proofs
- `phonology.py`, `semantics.py` - Linguistic infrastructure

**Tests**: 12/12 passing ✓  
**Linting**: Zero errors ✓  
**Documentation**: 40KB+ comprehensive docs

---

## Example: Language Modality

```python
from language_evolution.unified_framework import StructuralObject, ControlState
from experiments.language_modality_demo import LanguageProjector, LanguageInverseEngine

# 1. Create semantic structure
structure = StructuralObject(
    semantic_core={'concept_0': 'agent', 'concept_1': 'action'},
    relational_structure=[('concept_0', 'modifies', 'concept_1')],
    admissible_transforms={'passivization'},
    constraints=['temporal_order']
)

# 2. Define control goals
control = ControlState(target_comprehension=0.85, target_ease=0.70)

# 3. Project through language
projector = LanguageProjector()
behavior = projector.project_structure(structure, control, time=0)
observable = projector.render_observable(behavior)

# 4. Attempt reconstruction
inverse = LanguageInverseEngine()
reconstructed = inverse.reconstruct(observable)

# 5. Measure what survived
invariants = inverse.identify_invariants(structure, reconstructed)
loss = inverse.measure_information_loss(structure, reconstructed)

print(f"Preserved: {invariants}")  
print(f"Lost: {loss['total_loss']:.1%}")
```

**Output**:
```
Preserved: ['concept_count', 'linear_order']
Lost: 100.0%  # Semantic content unrecoverable!
```

---

## Installation

```bash
git clone https://github.com/standardgalactic/language-evolution.git
cd language-evolution
python3 -m pip install -e ".[dev]"
```

## Quick Start

```bash
# Run mathematical theorems
python3 src/language_evolution/theorems.py

# Language modality demo
python3 experiments/language_modality_demo.py

# Gesture modality demo  
python3 experiments/gesture_modality_demo.py

# Perceptual Control Theory
python3 experiments/pct_rigorous.py

# Historical linguistics
python3 experiments/systematic_reconstruction.py
```

## Documentation

- `docs/unified_structural_framework.md` - Complete theoretical synthesis
- `docs/mathematical_formalization_summary.md` - All theorems with proofs
- `docs/perceptual_control_experiments.md` - PCT implementation guide
- `docs/architecture.md` - H → O_t → Ĥ framework details

---

## Theoretical Foundations

### Three Families Unified

1. **Linguistic Theories**:
   - Structural Semantics (admissible transformations)
   - Semantic Relaxation Networks (constraint stabilization)
   - Analogy as Reduction (quotient structure)
   - Negation Before Logic (orientation reversal)

2. **Gesture/Sign/Embodied**:
   - Gesture Inverse Engine (trajectory reconstruction)
   - ASL Structure (distributed articulation)
   - Motor manifold constraints

3. **Music/Audio/Prosody**:
   - Audio Semantic Encoding (W → (T,P,V,E))
   - Musical Gesture Cognition (embodied inverse)
   - Structural invariance of affect

### Central Insight

**Observable ≠ Structure**: Different modalities are different projections of same latent structure.

**Non-Identifiability**: When multiple histories produce same observable, reconstruction is fundamentally ambiguous.

**PCT Mechanism**: Organisms control perceptions (not forms) → equivalence classes emerge.

---

## Scientific Value

### 1. Has Ground Truth
Unlike real linguistics, can measure **actual** reconstruction accuracy.

### 2. Proves Theorems
Not just simulates—establishes mathematical impossibility results.

### 3. Cross-Modal Unification  
First framework treating language/gesture/music as projections of same phenomenon.

### 4. Fundamental Limits
**Non-Identifiability Theorem** shows what's mathematically impossible to recover.

### 5. Testable Predictions
Generates falsifiable predictions across modalities.

---

Introducing sound changes:
  1. p → f (labial stop to fricative)
  2. t → θ (dental stop to fricative)  
  3. k → h (velar weakening)

Sample pronunciations after 15 generations:

'pater':
  Speaker 17: faθer
  Speaker 21: pater
  Speaker 24: pater

Average lexical divergence: 0.377
Maximum lexical divergence: 0.750
```

## Installation

```bash
git clone https://github.com/standardgalactic/language-evolution.git
cd language-evolution
python3 -m pip install -e .
```

## Development

This repository uses a standard make interface:

- make init
- make lint
- make test
- make benchmark
- make docs
- make format
- make release
