# Theoretical Connections: Reconstruction and Diagnostic Coordinates

## The Core Isomorphism

This repository's central question:

> **Which facts about history remain inferable after history has erased its own evidence?**

is a direct instance of the reconstruction/repair cluster's fundamental problem in a new domain. The H → O_t → Ĥ protocol operationalizes **What Survives Reconstruction** with an unusual advantage: we retain ground truth H, so reconstruction accuracy can be measured rather than merely argued for.

## Observability Is Restorability

The repository demonstrates **Observability Is Restorability** empirically:

### The Observation Map

O_t : H → Observable

is a **lossy projection** that partitions history-space into equivalence classes. Two ancestral states H₁ ≠ H₂ become observationally indistinguishable when:

O_t(H₁) ≈ O_t(H₂)

This is precisely a **restorability-boundary statement** in the distinguishability-geometry sense.

### Empirical Measurements

The **Recoverability Stress Test** directly measures this partition coarsening:

- 10 different evolutionary trajectories (distinct H)
- Same parameters, different random seeds
- Result: 25% to 100% reconstruction accuracy

This variation quantifies **when the observation map's kernel becomes too large** — equivalence classes grow until distinct histories become indistinguishable.

### The Borrowing Threshold

**Borrowing Without Ancestry** found: ~30% horizontal transmission exceeds recoverability limit.

In reconstruction vocabulary: at 30% borrowing, the **diagnostic coordinates** surviving in O_t no longer uniquely identify genetic ancestry. The observation map has lost too much information.

## Reconstruction as Inverse Continuation

### Forward: Monotonic Continuation

Standard admissible-trajectory continuation:

S_t → S_{t+1}

Each generation advances a trajectory forward, maintaining admissibility constraints.

### Backward: Reconstruction

Comparative method's job:

O_t → R(S_0)

Infer an ancestral admissible state from observables at time t. This runs **backward** — recovering an earlier state from a later one.

**Key insight**: Reconstruction is **inverse continuation**.

The comparative method attempts to invert the observation map composed with evolutionary drift:

Ĥ = R(O_t(H))

Success requires:
1. O_t preserves enough information (observation map not too lossy)
2. R correctly identifies diagnostic coordinates (reconstructor is admissible)
3. Evolutionary trajectory hasn't obliterated distinguishing features

## Diagnostic Coordinates in Language Evolution

### What Diagnostic Coordinates Are

In the reconstruction/repair cluster, **diagnostic coordinates** are:

> Observable features that uniquely identify or constrain ancestral states

### Linguistic Diagnostic Coordinates

This repository identifies specific diagnostic coordinates for proto-language reconstruction:

**Strong diagnostics** (survive well):
- Systematic sound correspondences across cognate sets
- Core vocabulary (resistant to borrowing)
- Morphological patterns
- Regular phonological rules

**Weak diagnostics** (degrade quickly):
- Individual word forms (accidental resemblance baseline: 0.165%)
- Cultural vocabulary (borrowed frequently)
- Irregular correspondences (ambiguous signal)
- Timing/ordering of changes (lost in O_t)

### Coordinate Degradation Curves

The experiments measure **how diagnostic capacity shrinks** as drift accumulates:

**Phonological Drift → Reconstruction**:
- Generation 0: Perfect reconstruction (no drift)
- Generation 5: High accuracy (diagnostic coordinates intact)
- Generation 15: 68.8% average accuracy (some coordinates lost)
- Generation 30+: Expected further degradation (not yet measured)

This is an empirical **degradation curve for diagnostic coordinates**.

**False Cognate Laboratory** provides the **noise floor**:
- Even with perfect preservation, 0.165% false-positive rate
- This sets minimum distinguishability for any reconstruction method

**Borrowing Without Ancestry** identifies a **coordinate-replacement threshold**:
- 30% borrowing replaces genetic signal with contact signal
- Observation map now reflects contact geography, not ancestry
- True diagnostic coordinates obscured by false ones

## Restorability Boundaries

### Definition

A **restorability boundary** occurs when:

Information required to distinguish H₁ from H₂ no longer exists in O_t

### Measured Boundaries in This Repository

1. **Temporal boundary**: ~15-30 generations (phonological drift)
2. **Contact boundary**: ~30% lexical borrowing
3. **Stochastic boundary**: Random variation → 25-100% reconstruction accuracy
4. **Baseline boundary**: 0.165% false-positive floor (unrelated languages)

### Boundary Geometry

These aren't sharp thresholds. They're **probability transitions**:

- Below boundary: Reconstruction mostly succeeds
- At boundary: Reconstruction becomes unreliable
- Beyond boundary: Information genuinely lost

The **Recoverability Stress Test** maps this transition empirically.

## Admissibility Structure

### What Makes a Reconstruction Admissible?

In this domain, an admissible reconstruction Ĥ must:

1. **Respect sound-change directionality**: Don't infer impossible changes
2. **Maintain phonological coherence**: Proto-inventory must be pronounceable
3. **Explain daughter languages**: Ĥ must evolve into observed O_t
4. **Minimize ad-hoc assumptions**: Prefer regular correspondences
5. **Respect typological plausibility**: Proto-language should be realistic

The **comparative method** is an **admissibility-preserving reconstruction operator**.

### Admissibility Violations

**Borrowing Without Ancestry** shows how contact **violates tree-admissibility**:

- Tree-based reconstruction assumes: Similarity ⇒ Common ancestry
- But borrowing creates: Similarity ⇒ Contact
- These are **different admissibility structures**

A reconstruction admissible under tree-geometry may be inadmissible under contact-network geometry.

## The Testbed Advantage

### What This Repository Provides

Unlike most reconstruction work, this repository:

1. **Retains H explicitly**: Ground truth is available
2. **Measures accuracy directly**: Can compare Ĥ vs H
3. **Quantifies boundaries empirically**: Not just theoretical claims
4. **Generates real numbers**: 68.8%, 30%, 0.165% are measurements

### What Becomes Measurable

Questions usually unanswerable:

❌ "How accurate is our proto-language reconstruction?"  
   → Unknown. Can't check against truth.

✅ "What is the average reconstruction accuracy given N generations of drift?"  
   → 68.8% at generation 15 (measured in stress test)

❌ "Are these languages related or is this accidental?"  
   → Ambiguous. Depends on priors.

✅ "What is the baseline rate of accidental resemblance?"  
   → 0.165% with semantic agreement (measured in false cognate lab)

❌ "Can borrowing fully obscure genetic relationships?"  
   → Debated. Hard to prove.

✅ "At what borrowing rate does tree reconstruction fail?"  
   → ~30% lexical replacement (measured in borrowing experiment)

## Diagnostic Coordinates as Bridge Vocabulary

The term **diagnostic coordinates** provides precise language for what linguists informally call "reliable evidence":

**Informal**: "Core vocabulary is more reliable than borrowings"

**Precise**: "Core vocabulary functions as stronger diagnostic coordinates because it resists replacement, maintaining higher mutual information with ancestral state"

**Informal**: "You need multiple cognate sets to establish relationship"

**Precise**: "Single coordinates have high noise (0.165% false positives); multiple independent diagnostic coordinates reduce equivalence-class ambiguity"

**Informal**: "Sound changes are regular but borrowing is sporadic"

**Precise**: "Regular sound changes preserve coordinate structure systematically; borrowing injects noise that obscures diagnostic signal"

## Potential Extensions

### 1. Quantify Diagnostic Capacity

For each feature type, measure **mutual information** with ancestral state:

I(feature_type ; H | O_t)

This quantifies how much each coordinate type constrains reconstruction.

### 2. Multi-Coordinate Reconstruction

Current reconstructor uses single coordinate (lexical similarity).

Better approach:
- Phonological correspondences
- Morphological patterns  
- Semantic fields
- Geographic distribution
- Typological features

Measure: How much does adding coordinates improve boundary?

### 3. Information-Theoretic Bounds

Shannon's theorem gives fundamental limits on reconstruction:

If H has entropy H(H) and O_t loses I bits:
- Lower bound: H(H) - I bits recoverable
- This bound is **achievable** with optimal reconstruction

Measure empirically: How close to theoretical limit is comparative method?

### 4. Coordinate Degradation Functions

For each diagnostic coordinate type, measure:

Capacity(t) = I(coordinate ; H | t generations)

This gives explicit **degradation curves** for each coordinate.

### 5. Boundary Phase Transitions

Study whether restorability boundaries are:
- Smooth degradation (gradual information loss)
- Sharp phase transition (sudden collapse)
- Mixed (different coordinates degrade differently)

## Conclusion

This repository is more than a historical linguistics simulator. It's an **empirical testbed** for the reconstruction/repair cluster's core questions:

**Theoretical claim** (reconstruction cluster):  
"Observability determines restorability; diagnostic coordinates degrade under drift"

**Empirical operationalization** (this repository):  
"Generate H, measure O_t, attempt Ĥ, compare accuracy, quantify boundaries"

The connection suggests natural extensions:

1. **Explicit diagnostic coordinate analysis** (measure I(feature ; H))
2. **Information-theoretic bounds** (compare to Shannon limits)
3. **Multi-coordinate reconstruction** (combine evidence types)
4. **Degradation function measurement** (explicit coordinate decay)
5. **Bridge essay** ("Diagnostic Coordinates in Language Evolution")

The repository already provides what the reconstruction cluster usually lacks: **ground truth for measuring reconstruction accuracy**.

That makes it a rare and valuable empirical exemplar.
