"""Minimum Language: Emergence of grammatical complexity from communicative pressure.

Begin with an extremely small symbolic system (a dozen roots and a few compositional
operations) and let agents invent constructions only when existing expressions cannot
efficiently distinguish intended meanings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
import random
from collections import defaultdict

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')


@dataclass
class Meaning:
    """A meaning to be expressed."""
    concept: str
    arguments: Tuple[str, ...] = field(default_factory=tuple)
    modifiers: Dict[str, str] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.concept, self.arguments, tuple(sorted(self.modifiers.items()))))
    
    def __eq__(self, other):
        return (isinstance(other, Meaning) and 
                self.concept == other.concept and
                self.arguments == other.arguments and
                self.modifiers == other.modifiers)
    
    def __repr__(self):
        args = f"({', '.join(self.arguments)})" if self.arguments else ""
        mods = f"[{', '.join(f'{k}={v}' for k, v in self.modifiers.items())}]" if self.modifiers else ""
        return f"{self.concept}{args}{mods}"


@dataclass
class Expression:
    """A linguistic expression."""
    symbols: Tuple[str, ...]
    
    def __hash__(self):
        return hash(self.symbols)
    
    def __eq__(self, other):
        return isinstance(other, Expression) and self.symbols == other.symbols
    
    def __repr__(self):
        return ' '.join(self.symbols)
    
    def __len__(self):
        return len(self.symbols)


@dataclass
class Construction:
    """A grammatical construction: a mapping from meaning pattern to expression pattern."""
    name: str
    meaning_pattern: str
    expression_builder: callable
    cost: int = 1
    
    def can_express(self, meaning: Meaning) -> bool:
        """Check if this construction can express a meaning."""
        # Simplified check - in reality would pattern-match
        return True
    
    def build(self, meaning: Meaning, lexicon: 'Lexicon') -> Optional[Expression]:
        """Build an expression for a meaning."""
        try:
            return self.expression_builder(meaning, lexicon)
        except (KeyError, AttributeError):
            return None


class Lexicon:
    """The minimal lexicon and grammar of the language."""
    
    def __init__(self):
        # Core roots
        self.roots: Dict[str, str] = {}
        
        # Meaning to expression mappings
        self.expressions: Dict[Meaning, Set[Expression]] = defaultdict(set)
        
        # Available constructions
        self.constructions: List[Construction] = []
        
        # Usage statistics
        self.usage_count: Dict[Expression, int] = defaultdict(int)
    
    def add_root(self, concept: str, symbol: str):
        """Add a root morpheme."""
        self.roots[concept] = symbol
        meaning = Meaning(concept)
        self.expressions[meaning].add(Expression((symbol,)))
    
    def add_construction(self, construction: Construction):
        """Add a grammatical construction."""
        self.constructions.append(construction)
    
    def express(self, meaning: Meaning) -> Optional[Expression]:
        """Find the best expression for a meaning."""
        # First check if we have a direct expression
        if meaning in self.expressions:
            # Return most frequently used
            candidates = self.expressions[meaning]
            if candidates:
                return min(candidates, key=lambda e: (-self.usage_count[e], len(e)))
        
        # Try to build expression using constructions
        for construction in self.constructions:
            if construction.can_express(meaning):
                expr = construction.build(meaning, self)
                if expr:
                    self.expressions[meaning].add(expr)
                    return expr
        
        return None
    
    def learn_expression(self, meaning: Meaning, expression: Expression):
        """Learn a new meaning-expression mapping."""
        self.expressions[meaning].add(expression)
    
    def record_usage(self, expression: Expression):
        """Record that an expression was used."""
        self.usage_count[expression] += 1


@dataclass
class Agent:
    """A communicating agent."""
    id: int
    lexicon: Lexicon
    
    def communicate(self, meaning: Meaning) -> Optional[Expression]:
        """Try to express a meaning."""
        expr = self.lexicon.express(meaning)
        if expr:
            self.lexicon.record_usage(expr)
        return expr
    
    def understand(self, expression: Expression, possible_meanings: Set[Meaning]) -> Optional[Meaning]:
        """Try to understand an expression given context."""
        # Find meanings that could match this expression
        candidates = set()
        for meaning in possible_meanings:
            if expression in self.lexicon.expressions[meaning]:
                candidates.add(meaning)
        
        # Return most likely meaning (simplified)
        if candidates:
            return random.choice(list(candidates))
        return None


def create_minimal_lexicon() -> Lexicon:
    """Create the minimal starting lexicon."""
    lex = Lexicon()
    
    # Core roots (about a dozen)
    lex.add_root('person', 'ka')
    lex.add_root('thing', 'to')
    lex.add_root('place', 'li')
    lex.add_root('time', 'su')
    lex.add_root('do', 'ma')
    lex.add_root('be', 'na')
    lex.add_root('big', 'da')
    lex.add_root('small', 'pi')
    lex.add_root('good', 'ko')
    lex.add_root('bad', 'hu')
    lex.add_root('this', 'ti')
    lex.add_root('that', 'ta')
    
    # Simple juxtaposition (the only initial construction)
    def juxtapose(meaning: Meaning, lexicon: Lexicon) -> Optional[Expression]:
        """Simple juxtaposition of roots."""
        if meaning.concept in lexicon.roots and meaning.arguments:
            symbols = [lexicon.roots[meaning.concept]]
            for arg in meaning.arguments:
                if arg in lexicon.roots:
                    symbols.append(lexicon.roots[arg])
                else:
                    return None
            return Expression(tuple(symbols))
        return None
    
    lex.add_construction(Construction('juxtapose', 'concept(args)', juxtapose, cost=1))
    
    return lex


def invent_construction(
    lexicon: Lexicon,
    ambiguous_pairs: List[Tuple[Meaning, Meaning]]
) -> Optional[Construction]:
    """Invent a new construction to distinguish ambiguous meanings."""
    
    # Analyze what distinctions are needed
    # For now, implement a simple marker system
    
    if not ambiguous_pairs:
        return None
    
    # Count what kinds of distinctions we need
    needs_agent_marker = False
    needs_patient_marker = False
    needs_modifier = False
    
    for m1, m2 in ambiguous_pairs:
        if m1.concept == m2.concept:
            if m1.arguments != m2.arguments:
                needs_agent_marker = True
    
    # Invent agent-marking construction
    if needs_agent_marker and len(lexicon.roots) > 0:
        def mark_agent(meaning: Meaning, lexicon: Lexicon) -> Optional[Expression]:
            if meaning.arguments and len(meaning.arguments) >= 1:
                # Add 'ga' marker after agent
                agent = meaning.arguments[0]
                if agent in lexicon.roots and meaning.concept in lexicon.roots:
                    symbols = [lexicon.roots[agent], 'ga', lexicon.roots[meaning.concept]]
                    return Expression(tuple(symbols))
            return None
        
        construction = Construction('agent_marker', 'X(agent) -> X-ga', mark_agent, cost=2)
        return construction
    
    return None


def run_simulation(communication_rounds: int = 100, ambiguity_threshold: int = 3):
    """Run the minimum language simulation."""
    print("=== Minimum Language Simulation ===\n")
    
    # Create agents with minimal lexicon
    lexicon = create_minimal_lexicon()
    agents = [Agent(i, lexicon) for i in range(5)]
    
    print(f"Initial lexicon: {len(lexicon.roots)} roots")
    print(f"Roots: {', '.join(f'{c}={s}' for c, s in lexicon.roots.items())}")
    print(f"Constructions: {len(lexicon.constructions)}")
    print()
    
    # Set of meanings we might want to express
    meanings = [
        Meaning('person'),
        Meaning('thing'),
        Meaning('big', modifiers={'size': 'large'}),
        Meaning('do', arguments=('person', 'thing')),
        Meaning('be', arguments=('person', 'big')),
        Meaning('do', arguments=('thing', 'person')),  # Ambiguous with previous
        Meaning('good', modifiers={'degree': 'very'}),
    ]
    
    # Track ambiguities
    ambiguities = defaultdict(list)
    failed_communications = []
    
    # Run communication rounds
    for round_num in range(communication_rounds):
        # Random agent tries to express random meaning
        speaker = random.choice(agents)
        meaning = random.choice(meanings)
        
        expr = speaker.communicate(meaning)
        
        if expr is None:
            failed_communications.append((round_num, meaning))
            continue
        
        # Check if this expression is ambiguous
        other_meanings = [m for m in meanings if m != meaning]
        for other in other_meanings:
            other_expr = lexicon.express(other)
            if other_expr == expr:
                ambiguities[expr].append((meaning, other))
        
        # Every N rounds, check if we need new constructions
        if round_num > 0 and round_num % 20 == 0:
            # Find highly ambiguous expressions
            for expr, pairs in ambiguities.items():
                if len(pairs) >= ambiguity_threshold:
                    print(f"\nRound {round_num}: Expression '{expr}' is ambiguous ({len(pairs)} pairs)")
                    print(f"  Inventing construction to distinguish meanings...")
                    
                    construction = invent_construction(lexicon, pairs)
                    if construction:
                        lexicon.add_construction(construction)
                        print(f"  Added construction: {construction.name}")
                        ambiguities[expr].clear()  # Reset after invention
    
    print(f"\n=== After {communication_rounds} Communication Rounds ===\n")
    print(f"Final constructions: {len(lexicon.constructions)}")
    for construction in lexicon.constructions:
        print(f"  - {construction.name}: {construction.meaning_pattern}")
    
    print(f"\nFailed communications: {len(failed_communications)}")
    print(f"Unique expressions learned: {len(lexicon.expressions)}")
    
    # Show example expressions
    print(f"\nExample expressions:")
    for meaning in meanings[:5]:
        expr = lexicon.express(meaning)
        if expr:
            count = lexicon.usage_count[expr]
            print(f"  {meaning} → '{expr}' (used {count} times)")
    
    # Show most frequent expressions
    if lexicon.usage_count:
        print(f"\nMost frequent expressions:")
        top_exprs = sorted(lexicon.usage_count.items(), key=lambda x: -x[1])[:5]
        for expr, count in top_exprs:
            print(f"  '{expr}': {count} uses")


if __name__ == '__main__':
    run_simulation(communication_rounds=150, ambiguity_threshold=2)
