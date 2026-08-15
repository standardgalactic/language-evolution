# Roadmap

## Vision

`language-evolution` is especially well suited to becoming an experimental laboratory rather than a conventional linguistics repository. Each project should be a small executable model of one question about how languages change.

**Governing Principle**: Historical linguistics with ground truth. Instead of merely simulating plausible language change, `language-evolution` becomes a laboratory for asking which facts about history remain inferable after history has erased its own evidence.

## Near-term
- Establish reproducible core examples.
- Add baseline tests and documentation.

## Mid-term
- Expand comparative experiments and benchmarks.

## Long-term
- Publish reusable research artifacts and tutorials.

## Experimental Projects

### Core Evolution Experiments

#### Phonological Drift
A simulator in which a population begins with a shared phoneme inventory and sound changes propagate probabilistically through speakers and generations. Instead of merely implementing rules like Grimm's Law, model competing innovations, incomplete adoption, geographical isolation, prestige effects, and chain shifts. The interesting output would be the family tree that emerges from nothing more than local interactions.

#### The Dialect Continuum
Deliberately avoid a tree model. Put speakers on a one- or two-dimensional space, allow neighboring speakers to influence one another, and ask when mutually intelligible varieties become recognizable languages. Experiment with mountains, political borders, migration, trade routes, schooling, and mass communication. This would nicely expose how much the familiar language-family tree is an observational simplification.

#### Lexical Natural Selection
Model word competition rather than language competition. Give synonymous forms properties such as length, articulatory cost, regularity, prestige, memorability, ambiguity, and frequency. Let a population repeatedly communicate and watch which variants survive. Crucially, don't hard-code "fitness" as a single score; let survival emerge from interactions among constraints.

#### Semantic Drift Machine
Start with a tiny lexicon whose words occupy overlapping semantic regions. Usage gradually moves those regions. Reproduce processes resembling narrowing, broadening, metaphor, metonymy, amelioration, pejoration, bleaching, and grammaticalization without necessarily encoding those categories as outcomes. The program could then ask afterward which description best characterizes the trajectory.

### Reconstruction & Methodology

#### Reconstruct
An experimental historical-linguistics game. Generate a hidden proto-language, evolve it independently into five or six daughter languages, throw away the ancestor, and give another algorithm only the descendants. It has to reconstruct the proto-forms. Because you possess the ground truth, you can quantitatively investigate exactly where the comparative method succeeds and where information has become genuinely unrecoverable.

#### False Cognate Laboratory
Generate thousands of unrelated miniature languages and measure how often convincing-looking correspondences arise accidentally. Then progressively require semantic similarity, recurring sound correspondences, morphological agreement, geographical plausibility, and larger cognate sets. An empirical demonstration of why individual look-alike words constitute weak historical evidence.

#### Borrowing Without Ancestry
Start several independently generated languages, place their populations in contact, and let vocabulary, phonemes, constructions, and morphology cross boundaries at different rates. Then feed the resulting data to a naïve family-tree reconstruction algorithm. Measure precisely when horizontal transmission makes vertical ancestry misleading.

### Emergence & Complexity

#### The Babel Experiment
Invert the typical approach. Start 1,000 agents speaking one language. Agents communicate only with selected neighbors and learn imperfectly from what they hear. Give the system *no explicit instruction to create languages*. Run it for ten thousand simulated generations and see whether dialects, standards, creoles, isolates, convergence zones, or extinction events emerge. Change only the communication topology and compare outcomes.

#### Minimum Language
Begin with an extremely small symbolic system—perhaps a dozen roots and a few compositional operations—and let agents invent constructions only when existing expressions cannot efficiently distinguish intended meanings. Instead of asking how languages decay or diverge, ask how grammatical complexity can arise from communicative pressure.

#### Maximum Language
The opposite experiment. Start with absurdly rich morphology, hundreds of distinctions and enormous paradigms. Introduce imperfect transmission and see what survives. The comparison between Minimum Language and Maximum Language might reveal whether populations approach similar complexity regimes from opposite directions.

### Writing & Modality

#### Glyph Evolution
Start with pictographic signs represented as simple strokes. Copying introduces tiny errors; frequently written signs experience pressure toward faster production; ambiguous signs experience pressure toward differentiation. After thousands of generations, see whether recognizable phenomena emerge: simplification, ligatures, systematic stroke inventories, phonetic reuse, or families of visually related characters.

#### ASL Handshape Drift
An analogous experiment in a multidimensional articulatory space. Represent signs by handshape, orientation, location and movement, then model production/perception confusion and articulatory economy. Rather than treating signed languages as spoken-language analogues, the experiment would let modality itself change the evolutionary landscape.

### Memory & Transmission

#### The Last Similar Thing
Instead of assuming linguistic change is primarily influenced by the most recent utterance, maintain several candidate precedents ranked by different notions of similarity. Compare recency-only transmission against phonological, semantic, syntactic and social similarity. Measure when LIFO-like linguistic memory works remarkably well and precisely where it breaks down.

### Integration

#### Language Earth
The most ambitious project: agents migrate, reproduce culturally, encounter neighbors, borrow words, undergo sound change, regularize morphology, invent constructions, develop writing, form prestige centers and lose contact. Every event is retained in an append-only history. At any later point you can freeze the simulated world, observe only its contemporary languages, attempt historical reconstruction, and then compare the inferred history against the *actual* history.
