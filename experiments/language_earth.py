"""
Language Earth: Integrated Language Evolution Simulator

The most ambitious experiment in the repository.

VISION:
    A complete world where agents migrate, reproduce culturally, encounter
    neighbors, borrow words, undergo sound change, regularize morphology,
    invent constructions, develop writing, form prestige centers, and lose
    contact. Every event is retained in append-only history.
    
    At any point: freeze time, observe contemporary languages, attempt
    reconstruction, compare inferred history against actual history.

DESIGN PRINCIPLES:
    1. Complete ground truth (H): Every event logged
    2. Realistic complexity: Multiple mechanisms operating simultaneously
    3. Emergent patterns: No hard-coded language families
    4. Observable extraction: Can snapshot at any time
    5. Reconstruction validation: Test methods on realistic data

ARCHITECTURE:

    World
      ├─ Geographic Grid (terrain, barriers, resources)
      ├─ Agents (populations with languages)
      ├─ Social Networks (contact, prestige, influence)
      └─ Event History (append-only log)
    
    Agent
      ├─ Location (geographic coordinates)
      ├─ Language State (phonemes, vocabulary, grammar)
      ├─ Social Properties (prestige, network, culture)
      └─ Behavioral Rules (migration, transmission, innovation)
    
    Language State
      ├─ Phonology (inventory + phonotactics)
      ├─ Lexicon (forms + meanings)
      ├─ Morphology (paradigms + productivity)
      ├─ Syntax (constructions + constraints)
      └─ Writing (optional, if invented)
    
    Mechanisms (all operating simultaneously)
      ├─ Sound Change (phonological drift)
      ├─ Semantic Drift (meaning change)
      ├─ Borrowing (contact-induced transfer)
      ├─ Morphological Regularization (analogy)
      ├─ Construction Invention (grammaticalization)
      ├─ Geographic Diffusion (spatial spread)
      └─ Prestige Effects (social influence)

MINIMAL VIABLE PRODUCT (MVP):

    Phase 1: World + Agents
      - 2D grid (10x10 or 20x20)
      - Terrain: plains, mountains, rivers
      - ~50-100 agents
      - Migration (random walk + terrain preference)
      - Cultural reproduction (learn from neighbors)
    
    Phase 2: Language State
      - Simple phoneme inventory (5-10 phonemes)
      - Small vocabulary (~20 meanings)
      - No morphology/syntax initially
      - Transmission via contact
    
    Phase 3: Sound Change
      - Probabilistic sound changes
      - Geographic spread (innovations diffuse)
      - Isolation creates divergence
    
    Phase 4: Borrowing
      - Contact-induced vocabulary transfer
      - Prestige effects (adopt from high-prestige neighbors)
      - Cultural semantic fields
    
    Phase 5: History Logging
      - Every event recorded with timestamp
      - Events: migration, contact, sound change, borrowing, birth, death
      - Append-only (never delete)
    
    Phase 6: Snapshot + Reconstruction
      - Freeze at arbitrary time
      - Extract observable (contemporary languages only)
      - Apply reconstruction (systematic correspondences)
      - Compare to ground truth

LATER ENHANCEMENTS:
    - Morphology (paradigms, regularization)
    - Syntax (construction grammar)
    - Writing systems (if certain conditions met)
    - Trade routes (economic contact)
    - Political boundaries (language standardization)
    - Mass migration events
    - Language death (population replacement)

RESEARCH QUESTIONS:

    1. Do language families emerge without programming them?
    2. How much history is recoverable from contemporary snapshot?
    3. Which mechanisms most reduce recoverability?
    4. Can we distinguish borrowing from inheritance in observable?
    5. How do geographic barriers affect linguistic diversity?
    6. What role does prestige play in language change?

USAGE:

    # Create world
    sim = LanguageEarth(world_size=(20, 20), num_agents=50, seed=42)
    
    # Run for some time
    for t in range(1, 101):
        sim.step(t)
    
    # Extract observable (snapshot at time T)
    obs = sim.extract_observable()
    
    # Examine history
    print(f"Total events: {len(sim.history.events)}")
    
    # Attempt reconstruction
    from systematic_reconstruction import SystematicCorrespondenceReconstructor
    reconstructor = SystematicCorrespondenceReconstructor()
    result = reconstructor.reconstruct(obs)
    
    # Compare to ground truth
    # ...
"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Tuple, Optional
import random
from enum import Enum

import sys
sys.path.insert(0, '/home/bonobo/github/language-evolution/src')
from language_evolution.framework import HistoryGenerator, Observable


@dataclass
class MechanismConfig:
    """Controls which mechanisms are active in simulation."""
    migration: bool = True  # Always on (baseline)
    sound_change: bool = True
    borrowing: bool = True
    reproduction: bool = True



# ============================================================================
# DESIGN: Data Structures
# ============================================================================

class Terrain(Enum):
    """Terrain types affecting movement and contact."""
    PLAINS = 1      # Easy movement, high contact
    FOREST = 2      # Moderate movement
    MOUNTAINS = 3   # Hard movement, natural barrier
    RIVER = 4       # Barrier but also trade route
    COAST = 5       # Edge of world or water


@dataclass
class Location:
    """Geographic coordinates."""
    x: int
    y: int
    
    def distance_to(self, other: 'Location') -> float:
        """Euclidean distance."""
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
    
    def manhattan_distance_to(self, other: 'Location') -> int:
        """Manhattan distance (grid movement)."""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class LanguageState:
    """
    Complete language state for an agent.
    
    Simplified for MVP:
      - Phoneme inventory (set of symbols)
      - Vocabulary (meaning → form mapping)
      - (Later: morphology, syntax, writing)
    """
    phonemes: Set[str]
    vocabulary: Dict[str, str]  # meaning → form
    
    # Metadata
    name: str = "Unnamed"
    generation: int = 0  # How many transmission steps from proto
    
    def copy(self) -> 'LanguageState':
        """Create a copy (for cultural reproduction)."""
        return LanguageState(
            phonemes=self.phonemes.copy(),
            vocabulary=self.vocabulary.copy(),
            name=self.name,
            generation=self.generation + 1
        )
    
    def similarity_to(self, other: 'LanguageState') -> float:
        """
        Measure lexical similarity (shared cognates).
        
        Returns fraction of shared vocabulary.
        """
        if not self.vocabulary or not other.vocabulary:
            return 0.0
        
        shared_meanings = set(self.vocabulary.keys()) & set(other.vocabulary.keys())
        if not shared_meanings:
            return 0.0
        
        # Count how many forms are identical (cognates)
        cognates = sum(
            1 for meaning in shared_meanings
            if self.vocabulary[meaning] == other.vocabulary[meaning]
        )
        
        return cognates / len(shared_meanings)


@dataclass
class Agent:
    """
    A language-using agent (individual or small population).
    
    Agents:
      - Have a location (can migrate)
      - Speak a language (can change through contact)
      - Have social properties (prestige)
      - Transmit language to neighbors
    """
    id: int
    location: Location
    language: LanguageState
    prestige: float = 0.5  # 0-1, affects borrowing direction
    
    # Social network (nearby agents)
    neighbors: Set[int] = field(default_factory=set)
    
    # Lineage tracking (for reconstruction validation)
    parent_id: int | None = None
    lineage_root: int = -1  # Root ancestor of this lineage
    
    def can_contact(self, other: 'Agent', max_distance: int = 2) -> bool:
        """Can this agent contact another? (based on distance)"""
        return self.location.manhattan_distance_to(other.location) <= max_distance


@dataclass  
class WorldMap:
    """
    Geographic grid with terrain.
    
    Controls:
      - Agent movement (terrain affects difficulty)
      - Contact patterns (barriers reduce contact)
      - Innovation diffusion (spreads geographically)
    """
    width: int
    height: int
    terrain: List[List[Terrain]]  # terrain[y][x]
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Initialize with plains
        self.terrain = [[Terrain.PLAINS for _ in range(width)] for _ in range(height)]
    
    def is_valid(self, loc: Location) -> bool:
        """Is location within bounds?"""
        return 0 <= loc.x < self.width and 0 <= loc.y < self.height
    
    def get_terrain(self, loc: Location) -> Terrain:
        """Get terrain at location."""
        if not self.is_valid(loc):
            return Terrain.COAST  # Out of bounds
        return self.terrain[loc.y][loc.x]
    
    def add_mountain_range(self, x: int, y_start: int, y_end: int):
        """Add vertical mountain range (barrier)."""
        for y in range(y_start, min(y_end, self.height)):
            if 0 <= x < self.width:
                self.terrain[y][x] = Terrain.MOUNTAINS
    
    def add_river(self, y: int, x_start: int, x_end: int):
        """Add horizontal river (barrier but also contact route)."""
        for x in range(x_start, min(x_end, self.width)):
            if 0 <= y < self.height:
                self.terrain[y][x] = Terrain.RIVER


# ============================================================================
# DESIGN: Main Simulator
# ============================================================================

class LanguageEarth(HistoryGenerator):
    """
    Language Earth: Complete integrated simulation.
    
    Combines all mechanisms in one world simulation.
    """
    
    def __init__(
        self,
        world_size: Tuple[int, int] = (20, 20),
        num_agents: int = 50,
        seed: int | None = None,
        config: MechanismConfig | None = None
    ):
        super().__init__()
        
        if seed is not None:
            random.seed(seed)
        
        # Mechanism configuration
        self.config = config if config is not None else MechanismConfig()
        
        # Create world
        self.world = WorldMap(width=world_size[0], height=world_size[1])
        self._create_terrain()
        
        # Create agents
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = num_agents  # For reproduction
        self.config_num_agents = num_agents  # Store for ground truth extraction
        self._create_agents(num_agents)
        
        # Simulation state
        self.time = 0
        
        # Regional clustering (contact-connected components)
        self.regions: Dict[int, int] = {}  # agent_id -> region_id
        self._update_regions()
        
        # Log initialization
        self.history.record(0, 'world_created',
                          size=world_size,
                          num_agents=num_agents,
                          seed=seed,
                          config=str(self.config))
    
    def _create_terrain(self):
        """Create interesting terrain features."""
        w, h = self.world.width, self.world.height
        
        # Add mountain range (barrier dividing world)
        self.world.add_mountain_range(x=w//2, y_start=h//4, y_end=3*h//4)
        
        # Add river (contact route)
        self.world.add_river(y=h//2, x_start=0, x_end=w)
        
        self.history.record(0, 'terrain_created',
                          mountains=True,
                          rivers=True)
    
    def _create_agents(self, num_agents: int):
        """Create initial population with proto-language."""
        # Proto-language (shared by all initially)
        proto_language = LanguageState(
            phonemes={'p', 't', 'k', 'a', 'i', 'u'},
            vocabulary={
                'water': 'apa',
                'fire': 'ita',
                'stone': 'kuta',
                'sun': 'tapa',
                'tree': 'pitu'
            },
            name="Proto",
            generation=0
        )
        
        # Place agents randomly
        for i in range(num_agents):
            # Random location
            loc = Location(
                x=random.randint(0, self.world.width - 1),
                y=random.randint(0, self.world.height - 1)
            )
            
            # Each agent starts with copy of proto-language
            # Founders are their own lineage roots
            agent = Agent(
                id=i,
                location=loc,
                language=proto_language.copy(),
                prestige=random.uniform(0.3, 0.7),
                parent_id=None,  # Founders have no parent
                lineage_root=i   # Each founder is its own root
            )
            
            self.agents[i] = agent
        
        self.history.record(0, 'agents_created',
                          count=num_agents,
                          proto_language=list(proto_language.vocabulary.values()))
    
    def step(self, time: int):
        """
        One simulation step.
        
        Mechanisms execute in order (config controls which run):
          1. Migration (agents move)
          2. Contact (update networks)
          3. Regional clustering
          4. Sound change [conditional]
          5. Borrowing [conditional]
          6. Reproduction [conditional]
        """
        self.time = time
        
        # 1. Migration (baseline - always on)
        if self.config.migration:
            self._migrate_agents()
        
        # 2. Update contact networks
        self._update_networks()
        
        # 3. Update regional clusters (after migration)
        self._update_regions()
        
        # 4. Sound changes (regional, systematic) [conditional]
        if self.config.sound_change:
            self._apply_sound_changes()
        
        # 5. Borrowing [conditional]
        if self.config.borrowing:
            self._apply_borrowing()
        
        # 6. Reproduction (population growth) [conditional]
        if self.config.reproduction:
            self._reproduce_agents()
    
    def _migrate_agents(self):
        """Some agents move to nearby locations."""
        migration_rate = 0.1  # 10% of agents move per step
        
        migrants = random.sample(
            list(self.agents.values()),
            k=int(len(self.agents) * migration_rate)
        )
        
        for agent in migrants:
            # Try to move to adjacent cell
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_loc = Location(agent.location.x + dx, agent.location.y + dy)
                
                # Check if valid and not too difficult terrain
                if self.world.is_valid(new_loc):
                    terrain = self.world.get_terrain(new_loc)
                    if terrain != Terrain.MOUNTAINS:  # Can't cross mountains easily
                        agent.location = new_loc
                        self.history.record(self.time, 'migration',
                                          agent_id=agent.id,
                                          to=f"({new_loc.x},{new_loc.y})")
                        break
    
    def _update_networks(self):
        """Update who is in contact with whom (based on proximity)."""
        max_contact_distance = 3
        
        for agent in self.agents.values():
            agent.neighbors.clear()
            
            for other in self.agents.values():
                if agent.id != other.id:
                    if agent.can_contact(other, max_contact_distance):
                        agent.neighbors.add(other.id)
    
    def _update_regions(self):
        """
        Partition agents into contact-connected components (dialect regions).
        
        Uses union-find over the neighbor graph. Agents in the same region
        will undergo the same sound changes (systematic correspondences).
        """
        parent: Dict[int, int] = {aid: aid for aid in self.agents}
        
        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        
        def union(x: int, y: int):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
        
        # Union all neighbors
        for agent in self.agents.values():
            for nb_id in agent.neighbors:
                union(agent.id, nb_id)
        
        # Canonicalize region ids
        self.regions = {aid: find(aid) for aid in self.agents}
    
    def _apply_sound_changes(self):
        """
        REGIONAL sound changes (systematic, not per-agent).
        
        Each region has a chance to innovate a sound law that applies
        to ALL agents in that region. This creates regular correspondences
        that the comparative method can detect.
        """
        change_rate_per_region = 0.08  # Chance per region per step
        
        # Group agents by region
        region_members: Dict[int, List[int]] = {}
        for aid, rid in self.regions.items():
            region_members.setdefault(rid, []).append(aid)
        
        for region_id, member_ids in region_members.items():
            if random.random() >= change_rate_per_region:
                continue
            
            # Pick a phoneme present in this region
            candidate_phonemes: Set[str] = set()
            for aid in member_ids:
                candidate_phonemes |= self.agents[aid].language.phonemes
            if not candidate_phonemes:
                continue
            
            old_phoneme = random.choice(sorted(candidate_phonemes))
            new_phoneme = old_phoneme + "'"
            
            # Apply to ALL agents in region (systematic)
            affected: List[int] = []
            for aid in member_ids:
                agent = self.agents[aid]
                if old_phoneme not in agent.language.phonemes:
                    continue
                
                # Apply to all words containing this phoneme
                for meaning, form in list(agent.language.vocabulary.items()):
                    if old_phoneme in form:
                        agent.language.vocabulary[meaning] = form.replace(
                            old_phoneme, new_phoneme
                        )
                
                # Update phoneme inventory
                agent.language.phonemes.discard(old_phoneme)
                agent.language.phonemes.add(new_phoneme)
                affected.append(aid)
            
            if affected:
                self.history.record(
                    self.time, 'regional_sound_change',
                    region_id=region_id,
                    change=f"{old_phoneme}→{new_phoneme}",
                    affected_agents=affected
                )
    
    def _apply_borrowing(self):
        """Agents borrow words from high-prestige neighbors."""
        borrowing_rate = 0.05  # 5% chance per contact per step
        
        for agent in self.agents.values():
            if not agent.neighbors:
                continue
            
            # Choose a neighbor to potentially borrow from
            neighbor_id = random.choice(list(agent.neighbors))
            neighbor = self.agents[neighbor_id]
            
            # Borrow if neighbor has higher prestige
            if neighbor.prestige > agent.prestige:
                if random.random() < borrowing_rate:
                    # Borrow one word
                    if neighbor.language.vocabulary:
                        meaning = random.choice(list(neighbor.language.vocabulary.keys()))
                        borrowed_form = neighbor.language.vocabulary[meaning]
                        
                        agent.language.vocabulary[meaning] = borrowed_form
                        
                        self.history.record(self.time, 'borrowing',
                                          from_agent=neighbor_id,
                                          to_agent=agent.id,
                                          word=borrowed_form,
                                          meaning=meaning)
    
    def _reproduce_agents(self):
        """
        Agent reproduction (population branching).
        
        Agents spawn children at nearby locations, creating actual
        tree structure for reconstruction validation.
        """
        reproduction_rate = 0.03  # 3% chance per agent per step
        
        new_agents: List[Agent] = []
        
        for agent in list(self.agents.values()):
            if random.random() >= reproduction_rate:
                continue
            
            # Try to place child nearby
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                         (-1, -1), (1, 1), (-1, 1), (1, -1)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_loc = Location(agent.location.x + dx, agent.location.y + dy)
                if not self.world.is_valid(new_loc):
                    continue
                if self.world.get_terrain(new_loc) == Terrain.MOUNTAINS:
                    continue
                
                # Create child
                child_id = self.next_agent_id
                self.next_agent_id += 1
                
                child = Agent(
                    id=child_id,
                    location=new_loc,
                    language=agent.language.copy(),  # Bumps generation
                    prestige=min(1.0, max(0.0, agent.prestige + random.uniform(-0.05, 0.05))),
                    parent_id=agent.id,
                    lineage_root=agent.lineage_root  # Propagate root
                )
                new_agents.append(child)
                
                self.history.record(
                    self.time, 'birth',
                    parent_id=agent.id,
                    child_id=child_id,
                    lineage_root=agent.lineage_root,
                    location=f"({new_loc.x},{new_loc.y})"
                )
                break  # One child per agent per step max
        
        # Add new agents to population
        for child in new_agents:
            self.agents[child.id] = child
    
    def get_observable(self, time: int | None = None) -> Observable:
        """
        Required by HistoryGenerator: return current observable.
        """
        return self.extract_observable(time, include_lineage=False)
    
    def extract_observable(self, time: int | None = None, include_lineage: bool = False) -> Observable:
        """
        Snapshot: Extract observable at given time.
        
        Returns contemporary languages only (no access to history).
        """
        if time is None:
            time = self.time
        
        # Extract language states
        languages = {}
        for agent_id, agent in self.agents.items():
            lang_data = {
                'location': (agent.location.x, agent.location.y),
                'phonemes': sorted(agent.language.phonemes),
                'vocabulary': agent.language.vocabulary.copy(),
                'generation': agent.language.generation
            }
            
            # Optional: include lineage info (changes what you're testing)
            if include_lineage:
                lang_data['parent_id'] = agent.parent_id
                lang_data['lineage_root'] = agent.lineage_root
            
            languages[agent_id] = lang_data
        
        return Observable(
            time=time,
            languages=languages
        )


# ============================================================================
# TESTING: MVP
# ============================================================================

def main():
    """Run minimal viable version of Language Earth."""
    print("=" * 70)
    print("LANGUAGE EARTH - MVP")
    print("=" * 70)
    print()
    
    # Create simulation
    sim = LanguageEarth(
        world_size=(20, 20),
        num_agents=50,
        seed=42
    )
    
    print(f"World created: {sim.world.width}x{sim.world.height}")
    print(f"Agents: {len(sim.agents)}")
    print(f"Proto-language vocabulary: {len(sim.agents[0].language.vocabulary)} words")
    print()
    
    # Run for 100 timesteps
    print("Running simulation for 100 timesteps...")
    for t in range(1, 101):
        sim.step(t)
        
        if t % 20 == 0:
            # Report status
            obs = sim.extract_observable()
            
            # Measure diversity (how many distinct languages?)
            vocabularies = [tuple(sorted(lang['vocabulary'].items())) 
                          for lang in obs.languages.values()]
            unique_languages = len(set(vocabularies))
            
            print(f"t={t}: {unique_languages} distinct languages (from {len(sim.agents)} agents)")
    
    print()
    print("Simulation complete!")
    print()
    
    # Extract final observable
    final_obs = sim.extract_observable()
    
    # Analyze results
    print("=" * 70)
    print("FINAL STATE")
    print("=" * 70)
    print()
    
    # Count distinct languages
    vocabularies = {}
    for agent_id, lang_data in final_obs.languages.items():
        vocab_tuple = tuple(sorted(lang_data['vocabulary'].items()))
        if vocab_tuple not in vocabularies:
            vocabularies[vocab_tuple] = []
        vocabularies[vocab_tuple].append(agent_id)
    
    print(f"Distinct languages: {len(vocabularies)}")
    print()
    
    # Show language families (by similarity)
    print("Language samples:")
    for i, (vocab, agents) in enumerate(list(vocabularies.items())[:5]):
        vocab_dict = dict(vocab)
        print(f"\nLanguage {i+1} (spoken by {len(agents)} agents):")
        for meaning, form in list(vocab_dict.items())[:3]:
            print(f"  {meaning}: {form}")
    
    print()
    print("=" * 70)
    print("GROUND TRUTH HISTORY")
    print("=" * 70)
    print()
    
    # Show history statistics
    events_by_type = {}
    for event in sim.history.events:
        event_type = event.event_type
        events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
    
    print("Events recorded:")
    for event_type, count in sorted(events_by_type.items()):
        print(f"  {event_type}: {count}")
    
    print()
    print("=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print()
    print("Language diversity emerged WITHOUT programming language families.")
    print()
    print("Mechanisms:")
    print("  - Geographic isolation (mountains)")
    print("  - Migration (population movement)")
    print("  - Sound change (innovations)")  
    print("  - Borrowing (prestige effects)")
    print()
    print("All operating simultaneously in one integrated world.")
    print()
    print("Next: Apply reconstruction and measure recoverability!")


if __name__ == '__main__':
    main()
