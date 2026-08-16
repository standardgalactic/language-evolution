#!/usr/bin/env python3
"""
Language Modality: Concrete Implementation

Demonstrates S → C → B_t → O_t → Ŝ for linguistic projection.

This connects:
  - Structural Semantics (S)
  - Perceptual Control Theory (C)
  - Semantic Relaxation Networks (B_t generation)
  - Historical Linguistics (O_t over time)
  - Comparative Reconstruction (Ŝ)
"""

import random
import sys

sys.path.insert(0, 'src')

from language_evolution.unified_framework import (
    BehavioralOutput,
    ControlState,
    InverseEngine,
    Modality,
    Observable,
    Projector,
    ReconstructedStructure,
    StructuralObject,
)


class LanguageProjector(Projector):
    """
    Projects semantic structure into linear linguistic sequence.
    
    Implements Semantic Relaxation Network logic:
      Semantic constraints → Admissible linearizations → Selected sequence
    """

    def __init__(self, lexicon: dict[str, list[str]] | None = None):
        """
        Args:
            lexicon: Maps concepts to possible word forms
        """
        self.lexicon = lexicon or self._default_lexicon()
    
    def _default_lexicon(self) -> dict[str, list[str]]:
        """Generate default proto-lexicon."""
        vowels = 'aeiou'
        consonants = 'ptkbdgmnlrsw'
        
        lexicon = {}
        for i in range(10):
            concept = f'concept_{i}'
            # Multiple lexical variants (synonyms)
            variants = []
            for _ in range(2):
                length = random.randint(2, 4)
                form = ''
                for j in range(length):
                    if j % 2 == 0:
                        form += random.choice(consonants)
                    else:
                        form += random.choice(vowels)
                variants.append(form)
            lexicon[concept] = variants
        
        return lexicon
    
    def project_structure(
        self,
        structure: StructuralObject,
        control: ControlState,
        time: int,
    ) -> BehavioralOutput:
        """
        Project semantic structure into linguistic behavior.
        
        Process:
          1. Extract semantic core
          2. Consider relational structure
          3. Select linearization based on control goals
          4. Choose lexical forms
        """
        # Extract concepts
        concepts = list(structure.semantic_core.keys())
        
        # Linearize based on relational structure
        # (Simple: follow relations)
        ordered_concepts = self._linearize(concepts, structure.relational_structure)
        
        # Select lexical forms based on control goals
        forms = []
        for concept in ordered_concepts:
            if concept in self.lexicon:
                variants = self.lexicon[concept]
                
                # Control goals affect lexical selection
                if control.target_ease > 0.7:
                    # Prefer shorter forms
                    form = min(variants, key=len)
                elif control.target_expressiveness > 0.7:
                    # Prefer longer forms (more expressive)
                    form = max(variants, key=len)
                else:
                    # Random choice
                    form = random.choice(variants)
                
                forms.append(form)
        
        output_data = {
            'concepts': ordered_concepts,
            'forms': forms,
            'sequence': ' '.join(forms),
        }
        
        return BehavioralOutput(
            time=time,
            modality=Modality.LANGUAGE,
            output_data=output_data,
            structural_source=structure,
            control_state=control,
        )
    
    def _linearize(
        self,
        concepts: list[str],
        relations: list[tuple],
    ) -> list[str]:
        """
        Linearize concepts based on relational structure.
        
        This is where Semantic Relaxation Networks apply:
        constraints determine admissible orderings.
        """
        if not relations:
            return concepts
        
        # Simple: follow 'modifies' relations
        ordered = []
        used = set()
        
        # Build dependency structure
        dependencies = {}
        for c1, rel, c2 in relations:
            if rel == 'modifies':
                dependencies[c1] = c2
        
        # Topological sort (simplified)
        for concept in concepts:
            if concept not in used:
                ordered.append(concept)
                used.add(concept)
                # Add dependent
                if concept in dependencies:
                    dependent = dependencies[concept]
                    if dependent not in used:
                        ordered.append(dependent)
                        used.add(dependent)
        
        # Add any remaining
        for concept in concepts:
            if concept not in used:
                ordered.append(concept)
                used.add(concept)
        
        return ordered
    
    def render_observable(self, behavior: BehavioralOutput) -> Observable:
        """
        Render behavior as observable.
        
        LOSSY: Loses semantic structure, control state, alternatives.
        Observable contains ONLY the surface sequence.
        """
        observed_data = {
            'sequence': behavior.output_data['sequence'],
            'forms': behavior.output_data['forms'],
        }
        
        # Hidden information (not in real observables):
        # - Original semantic structure
        # - Control goals
        # - Alternative linearizations
        # - Rejected lexical variants
        
        return Observable(
            time=behavior.time,
            modality=behavior.modality,
            observed_data=observed_data,
        )


class LanguageInverseEngine(InverseEngine):
    """
    Reconstructs semantic structure from linguistic observable.
    
    This is the COMPARATIVE METHOD problem:
      Given surface forms, reconstruct underlying structure.
    """

    def reconstruct(self, observable: Observable) -> ReconstructedStructure:
        """
        Attempt reconstruction from observable sequence.
        
        Limited information:
          - Surface forms
          - Linear order
        
        Missing:
          - Original semantic structure
          - Control goals
          - Alternatives
        """
        forms = observable.observed_data.get('forms', [])
        
        # Reconstruct semantic core (guess concepts from forms)
        reconstructed_semantic = {}
        for i, form in enumerate(forms):
            # Assume each form corresponds to a concept
            # (This is already a strong assumption!)
            reconstructed_semantic[f'concept_{i}'] = f'reconstructed_meaning_{i}'
        
        # Reconstruct relations (guess from linear order)
        reconstructed_relations = []
        for i in range(len(forms) - 1):
            # Assume linear adjacency → 'modifies' relation
            # (This may be wrong!)
            reconstructed_relations.append(
                (f'concept_{i}', 'modifies', f'concept_{i+1}'),
            )
        
        # Confidence based on how much structure we can infer
        confidence = 0.5  # Low - lots of ambiguity
        
        # Multiple possible structures could produce this sequence
        ambiguity = ['alternative_structure_1', 'alternative_structure_2']
        
        # Lost information
        lost = [
            'original_semantic_content',
            'control_goals',
            'rejected_alternatives',
            'admissible_transforms',
            'constraints',
            'synonyms',
            'deeper_relations',
        ]
        
        return ReconstructedStructure(
            reconstructed_semantic=reconstructed_semantic,
            reconstructed_relations=reconstructed_relations,
            confidence=confidence,
            ambiguity=ambiguity,
            lost_information=lost,
        )
    
    def identify_invariants(
        self,
        original: StructuralObject,
        reconstructed: ReconstructedStructure,
    ) -> list[str]:
        """
        Identify what structural features survived.
        
        Can we recover from O_t:
          ✓ Number of concepts
          ✓ Linear order
          ✗ Semantic content
          ✗ Deep relations
          ✗ Admissible transforms
        """
        invariants = []
        
        # Check what survived
        if len(original.semantic_core) == len(reconstructed.reconstructed_semantic):
            invariants.append('concept_count')
        
        if len(original.relational_structure) == len(
            reconstructed.reconstructed_relations,
        ):
            invariants.append('relation_count')
        
        # Linear order might be preserved
        invariants.append('linear_order')
        
        return invariants
    
    def measure_information_loss(
        self,
        original: StructuralObject,
        reconstructed: ReconstructedStructure,
    ) -> dict:
        """
        Quantify information lost in projection.
        
        What's unrecoverable:
          - Semantic content (meanings)
          - Admissible transforms
          - Constraints
          - Alternative linearizations
          - Rejected lexical choices
        """
        losses = {}
        
        # Semantic content loss
        original_meanings = set(original.semantic_core.values())
        reconstructed_meanings = set(reconstructed.reconstructed_semantic.values())
        if 'meaning' in str(reconstructed_meanings):
            # Reconstructed are generic
            losses['semantic_content'] = 1.0  # Total loss
        else:
            overlap = len(original_meanings & reconstructed_meanings)
            losses['semantic_content'] = 1.0 - (
                overlap / len(original_meanings) if original_meanings else 0.0
            )
        
        # Transform loss
        losses['admissible_transforms'] = 1.0  # Completely lost
        
        # Constraint loss
        losses['constraints'] = 1.0  # Completely lost
        
        # Total
        losses['total_loss'] = sum(losses.values()) / len(losses)
        
        return losses


def demonstrate_language_modality():
    """Demonstrate language modality in unified framework."""
    print("=" * 70)
    print("LANGUAGE MODALITY: S → C → B_t → O_t → Ŝ")
    print("=" * 70)
    print()
    
    # 1. Generate semantic structure (S)
    structure = StructuralObject(
        semantic_core={
            'concept_0': 'agent',
            'concept_1': 'action',
            'concept_2': 'patient',
        },
        relational_structure=[
            ('concept_0', 'modifies', 'concept_1'),
            ('concept_1', 'modifies', 'concept_2'),
        ],
        admissible_transforms={'passivization', 'nominalization'},
        constraints=['temporal_order', 'case_marking'],
    )
    
    print("1. Semantic Structure (S):")
    print(f"   Core: {structure.semantic_core}")
    print(f"   Relations: {structure.relational_structure}")
    print(f"   Transforms: {structure.admissible_transforms}")
    print()
    
    # 2. Control state (C)
    control = ControlState(
        target_comprehension=0.85,
        target_ease=0.70,
    )
    
    print("2. Control State (C):")
    print(f"   Target comprehension: {control.target_comprehension}")
    print(f"   Target ease: {control.target_ease}")
    print()
    
    # 3. Project through language (B_t → O_t)
    projector = LanguageProjector()
    behavior = projector.project_structure(structure, control, time=0)
    
    print("3. Behavioral Output (B_t):")
    print(f"   Concepts: {behavior.output_data['concepts']}")
    print(f"   Forms: {behavior.output_data['forms']}")
    print(f"   Sequence: '{behavior.output_data['sequence']}'")
    print()
    
    observable = projector.render_observable(behavior)
    
    print("4. Observable (O_t):")
    print(f"   Sequence: '{observable.observed_data['sequence']}'")
    print("   [Hidden: semantic structure, control goals, alternatives]")
    print()
    
    # 4. Attempt reconstruction (Ŝ)
    inverse = LanguageInverseEngine()
    reconstructed = inverse.reconstruct(observable)
    
    print("5. Reconstructed Structure (Ŝ):")
    print(f"   Semantic: {reconstructed.reconstructed_semantic}")
    print(f"   Relations: {reconstructed.reconstructed_relations}")
    print(f"   Confidence: {reconstructed.confidence:.2f}")
    print(f"   Lost: {', '.join(reconstructed.lost_information[:3])}...")
    print()
    
    # 5. Measure invariance
    invariants = inverse.identify_invariants(structure, reconstructed)
    print("6. Structural Invariants:")
    print(f"   Preserved: {', '.join(invariants)}")
    print()
    
    loss = inverse.measure_information_loss(structure, reconstructed)
    print("7. Information Loss:")
    for component, loss_val in loss.items():
        if component != 'total_loss':
            print(f"   {component}: {loss_val:.1%}")
    print(f"   Total: {loss['total_loss']:.1%}")
    print()
    
    print("=" * 70)
    print()
    print("KEY INSIGHT:")
    print()
    print("Observable sequence preserves SOME structure (order, count)")
    print("but loses SEMANTIC CONTENT, CONTROL GOALS, and ALTERNATIVES.")
    print()
    print("This is why historical reconstruction is fundamentally limited:")
    print("Multiple S can produce same O_t through different C.")


if __name__ == '__main__':
    random.seed(42)
    demonstrate_language_modality()
