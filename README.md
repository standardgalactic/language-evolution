# Language Evolution

**Historical linguistics with ground truth.**

## Overview

Language Evolution is a computational laboratory that simulates language change while secretly retaining complete evolutionary histories. This enables rigorous experimental investigation of a fundamental question:

> **Which facts about history remain inferable after history has erased its own evidence?**

Unlike real historical linguistics, where we can never know the true proto-language, our simulations generate known ancestral states, evolve them through realistic processes, and then ask: given only the contemporary evidence, how much can we recover?

## The Experimental Protocol

Every experiment follows the **H → O_t → Ĥ** architecture:

- **H**: Complete history retained by the simulator (ground truth)
- **O_t**: Observable evidence at time t (what a linguist actually sees)
- **Ĥ**: Reconstructed history inferred from observables

We can then compare **H vs Ĥ** to measure reconstruction accuracy and, more importantly, identify which historical distinctions have become **genuinely unrecoverable**—cases where H₁ ≠ H₂ but O_t(H₁) ≈ O_t(H₂).

## Experiments

### History Generators

Simulations that produce complete evolutionary traces:

- **Phonological Drift** (`experiments/phonological_drift.py`): Sound changes propagate probabilistically through a population with geographical isolation and prestige effects
- **Minimum Language** (`experiments/minimum_language.py`): Grammatical complexity emerges from communicative pressure starting with ~12 roots
- **Lexical Natural Selection** (planned): Word competition based on length, cost, regularity, prestige, and ambiguity
- **Semantic Drift Machine** (planned): Meaning evolution through overlapping semantic regions

### Inference Systems

Reconstruction algorithms (coming soon):

- **Reconstruct**: Apply the comparative method to generated language families and measure accuracy against ground truth
- **False Cognate Laboratory**: Generate unrelated languages and measure accidental resemblances

### Example Output

```bash
$ python3 experiments/phonological_drift.py

=== Phonological Drift Simulation ===

Initial population: 25 speakers
Initial lexicon size: 8 words

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
