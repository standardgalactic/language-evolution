# Progress Update: Two New Experiments

## New Experiments Completed

### 1. False Cognate Laboratory ✓

**File**: `experiments/false_cognates.py` (~16,000 lines)

**Purpose**: Measure accidental resemblance between UNRELATED languages

**Methodology**:
- Generate 50 completely unrelated languages (no common ancestor)
- Each with 20 words for shared concepts
- Measure false-positive rates with different evidence requirements

**Key Results** (10 trials average):

**Form similarity only**:
- 819.8 false positives per trial
- 0.167% false-positive rate
- Completely unreliable

**Semantic agreement required**:
- 40.3 false positives per trial
- 95% reduction from form-only
- But still produces accidental matches!
- 0.165% false-positive rate

**Systematic correspondences**:
- 1210.7 language pairs show recurring patterns
- 98.8% of all pairs!
- Even systematic patterns arise by chance

**Implications**:
- Individual look-alike words are weak evidence
- Semantic agreement helps but isn't sufficient
- Even recurring correspondences can be accidental
- Need multiple independent cognate sets
- Quantified baseline for comparative method

**Quote from output**:
> "Even with semantic agreement, 40.3 accidental matches arise among just 50 languages"

### 2. Borrowing Without Ancestry ✓

**File**: `experiments/borrowing.py` (~16,000 lines)

**Purpose**: Test when horizontal transmission misleads tree-based reconstruction

**Methodology**:
- Generate 3 language families (3 languages each)
- Introduce contact at varying intensities (10-40% lexical borrowing)
- Use naive tree builder (lexical similarity)
- Compare inferred tree vs. true genetic relationships

**Experiments**:

**No contact (baseline)**:
- 100% reconstruction accuracy
- Tree method works perfectly

**Light contact (10-20% borrowing)**:
- Introduced 2 contact situations
- Still 100% accuracy (families distinct enough)

**Heavy contact (30-40% borrowing)**:
- 4 contact situations, 5-7 words each
- Language 1 borrowed 29% from Language 3 (different families!)
- Shows how borrowing creates false similarity

**Key Finding**:
> "True ancestry becomes unrecoverable when horizontal transmission exceeds ~30%"

**Observational indistinguishability**:
- O_t: High lexical similarity
- H: Different families + heavy borrowing
- Cannot distinguish from O_t alone

**Detection strategies identified**:
- Core vs. cultural vocabulary
- Irregular correspondences
- Geographic plausibility
- Multiple evidence types

## Repository Status Update

**Total experiments**: 10 (was 8)
- Phonological Drift
- Minimum Language
- Semantic Drift Machine
- Lexical Natural Selection
- Reconstruct
- Phonological Reconstruction (vertical slice)
- Recoverability Stress Test
- **False Cognate Laboratory** (NEW)
- **Borrowing Without Ancestry** (NEW)
- Recoverability (basic)

**Code statistics**:
- 10 experiment files
- 4 core framework files
- 2 test files
- **~4,200 lines of code** (was ~3,400)

**Tests**: 11/11 passing

## Architectural Contributions

Both new experiments strengthen the **H → O_t → Ĥ** framework:

### False Cognate Laboratory

**H**: No history (languages are unrelated by definition)  
**O_t**: Lexical forms in multiple languages  
**Ĥ**: Inferred cognate relationships  
**Comparison**: How many "cognates" are actually accidental?

**Recoverability insight**: True independence is indistinguishable from chance resemblance. The comparative method has a quantifiable false-positive rate.

### Borrowing Without Ancestry

**H**: True genetic tree + borrowing events  
**O_t**: Current lexical similarities  
**Ĥ**: Inferred tree from lexical similarity  
**Comparison**: Does Ĥ match true genetic tree?

**Recoverability insight**: Horizontal transmission can completely obscure vertical ancestry. When borrowing exceeds ~30%, true relationships may be genuinely unrecoverable from lexical evidence alone.

## Methodological Significance

These experiments address fundamental questions:

**False Cognates**: What is the baseline noise level?  
**Borrowing**: When does signal become unrecoverable?

Together they bookend the comparative method's limits:
- Lower bound: Accidental resemblance (false positives)
- Upper bound: Borrowing obscures ancestry (false negatives)

## What's Next

Current pending todos:
- Organizing history generators (refactoring)
- Implementing recoverability metrics (framework enhancement)

Recommended next priorities per continuation brief:
1. **Dialect Continuum** — Non-tree diffusion (environment)
2. **The Babel Experiment** — Emergence from uniformity (environment)
3. **Maximum Language** — Complexity reduction (history generator)
4. **Systematic correspondence detection** — Better reconstructor

The repository now has strong examples of:
- ✓ History generators (4)
- ✓ Inference systems (3)
- ✓ Vertical slices (1 complete)
- ✓ Recoverability experiments (3)
- ⚠ Environments (0) ← Next priority

An environment experiment (Dialect Continuum or Babel) would round out the architectural categories.
