import random
import sys
import json
import requests
import os
import subprocess
import shutil
from datetime import datetime
from uwapi import *

# Try to import pyttsx3, but don't fail if it's not available
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class ObserverBot:
    """Observer bot that connects as observer and reports game state without controlling units"""

    # Distance constants for movement analysis
    BASE_PERIMETER_DISTANCE = 700    # Distance considered "near base"
    MOVEMENT_THRESHOLD_DISTANCE = 150  # Minimum distance change to be considered significant movement

    is_configured: bool = False
    work_step: int = 0

    # Track if we've done initial setup
    setup_done: bool = False


    # Track last report time to avoid spam
    last_full_report: int = 0

    def __init__(self, server=None, port=None):
        self.server = server
        self.port = port

        # Startup data saved once
        self.main_base_positions = {}  # force_id -> position
        self.overlord_positions = {}  # force_id -> position (fallback bases)
        self.oil_deposit_positions = []  # list of positions
        # Note: Resource clusters contain 2 metals, 1 oil, 1 aether per cluster
        self.startup_data_saved = False

        # Force tracking
        self.force_types = {}  # force_id -> "technocracy" or "fucking bugs"
        self.observer_force_id = None  # Track our observer force to exclude from reports
        self.eliminated_forces = set()  # Track eliminated force IDs
        self.announced_eliminations = set()  # Track which eliminations we've already announced

        # Unit movement tracking
        self.previous_unit_positions = {}  # unit_id -> {position, distance_to_home, distance_to_closest_enemy, closest_enemy_force_id}
        self.current_unit_positions = {}   # Same structure for current analysis

        # Game state tracking for start/end messages
        self.game_start_announced = False  # Flag to ensure only one start message
        self.game_end_announced = False    # Flag to ensure only one end message
        self.previous_game_state = None    # Track game state changes
        self.game_start_time = None        # Timestamp when game started

        # AI Yapper integration
        self.report_history = []  # Store report history for AI analysis
        self.context_summary = ""  # Persistent context summary
        self.last_announcement = ""  # Store last announcement to avoid repetition
        self.current_game_id = None  # Track current game session
        self.gemini_api_key = "AIzaSyDTKBca5SbNL2mjWGPuk3EubeEogN9snC8"
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

        # Initialize text-to-speech
        self.tts_engine = None
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
            except Exception as e:
                print(f"Warning: Could not initialize pyttsx3: {e}")
                self.tts_engine = None

        # Generate game identifier based on connection info
        self.generate_game_id()

        # Load existing context if available
        self.load_context()

        uw_events.on_update(self.on_update)
        uw_events.on_force_eliminated(self.on_force_eliminated)

    def pluralize(self, word):
        """Smart pluralization that handles common cases"""
        word_lower = word.lower()

        # Already plural words
        if word_lower.endswith('s') and not word_lower.endswith('ss'):
            if word_lower in ['biomass', 'mass']:
                return word  # Don't pluralize mass nouns

        # Special cases
        special_cases = {
            'fuel rod': 'fuel rods',
            'ai shard': 'ai shards',
            'plasma cell': 'plasma cells',
        }

        if word_lower in special_cases:
            return special_cases[word_lower]

        # Already ends with 's' but not double s - likely already plural
        if word_lower.endswith('s') and len(word_lower) > 1 and word_lower[-2] != 's':
            return word

        # Add 's' for regular plurals
        return word + 's'

    def configure(self):
        """Configure as observer - don't join a force"""

        # Is configuring possible?
        if (
            self.is_configured
            or uw_game.game_state() != GameState.Session
            or uw_world.my_player_id() == 0
        ):
            return

        self.is_configured = True

        uw_game.log_info("Configuring Observer Bot")
        uw_game.log_info(f"Map state during config: {uw_game.map_state()}")

        uw_game.set_player_name("ai-yapper")
        # DON'T join a force - remain as observer
        # uw_game.player_join_force(0)  # Commented out - this would make us a player

        uw_game.log_info("Configuration done - remaining as observer")

    def get_life_percentage(self, entity):
        """Calculate life percentage for an entity."""

        # Random debug: list entity attributes (0.01% chance)
        if random.random() < 0.1:
            print(f"🔍 DEBUG: Entity attributes for {entity.proto().name if entity.proto() else 'unknown'}:")
            for attr in dir(entity):
                if not attr.startswith('_'):
                    try:
                        value = getattr(entity, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")
                    except:
                        print(f"  {attr}: <error accessing>")
            print(f"Life component: {entity.Life}")
            print(f"Life component .lofe: {entity.Life.life}")
            print(f"Proto component: {entity.proto().data.get('life', 'N/A')}")

        if not entity.Life:
            return 0

        max_life = entity.proto().data.get("life", 0)
        if max_life <= 0:
            return 0  # No max life defined

        current_life = entity.Life.life
        return (float(current_life) / max_life) * 100

    def categorize_health_status(self, life_percentage):
        """Categorize health status based on life percentage."""
        if life_percentage >= 80:
            return "full_health"
        elif life_percentage >= 50:
            return "over_50_life"
        elif life_percentage >= 30:
            return "over_30_life"
        else:
            return "almost_destroyed"

    def calculate_unit_distances(self, unit_pos, force_id):
        """Calculate distances from unit to own base and all enemy bases."""
        distances = {
            'distance_to_home': float('inf'),
            'distance_to_closest_enemy': float('inf'),
            'closest_enemy_force_id': None,
            'distances_to_enemies': {}  # enemy_force_id -> distance
        }

        # Calculate distance to own base
        own_base_pos = None
        if force_id in self.main_base_positions:
            own_base_pos = self.main_base_positions[force_id]
        elif force_id in self.overlord_positions:
            own_base_pos = self.overlord_positions[force_id]

        if own_base_pos:
            distances['distance_to_home'] = uw_map.distance_line(unit_pos, own_base_pos)

        # Calculate distances to all enemy bases
        min_enemy_distance = float('inf')
        closest_enemy = None

        # Check main bases first
        for enemy_force_id, enemy_base_pos in self.main_base_positions.items():
            if enemy_force_id != force_id:
                enemy_distance = uw_map.distance_line(unit_pos, enemy_base_pos)
                distances['distances_to_enemies'][enemy_force_id] = enemy_distance
                if enemy_distance < min_enemy_distance:
                    min_enemy_distance = enemy_distance
                    closest_enemy = enemy_force_id

        # Check overlord positions for enemies without main bases
        for enemy_force_id, enemy_overlord_pos in self.overlord_positions.items():
            if enemy_force_id != force_id and enemy_force_id not in self.main_base_positions:
                enemy_distance = uw_map.distance_line(unit_pos, enemy_overlord_pos)
                distances['distances_to_enemies'][enemy_force_id] = enemy_distance
                if enemy_distance < min_enemy_distance:
                    min_enemy_distance = enemy_distance
                    closest_enemy = enemy_force_id

        distances['distance_to_closest_enemy'] = min_enemy_distance
        distances['closest_enemy_force_id'] = closest_enemy

        return distances

    def classify_unit_movement(self, unit_id, unit_name, current_distances):
        """Classify unit movement based on current and previous distances."""
        # Get previous distances if available
        previous_data = self.previous_unit_positions.get(unit_id)

        current_home_dist = current_distances['distance_to_home']
        current_enemy_dist = current_distances['distance_to_closest_enemy']
        closest_enemy_id = current_distances['closest_enemy_force_id']

        # If no previous data, classify based on current position only
        if not previous_data:
            if current_home_dist < self.BASE_PERIMETER_DISTANCE:
                return ('near_base', None)
            elif current_enemy_dist < self.BASE_PERIMETER_DISTANCE:
                return ('breached_perimeter', closest_enemy_id)
            else:
                return ('other', None)

        prev_home_dist = previous_data['distance_to_home']
        prev_enemy_dist = previous_data['distance_to_closest_enemy']
        prev_closest_enemy = previous_data['closest_enemy_force_id']

        home_change = current_home_dist - prev_home_dist

        # Calculate enemy distance change (use same enemy as before if possible)
        enemy_change = 0
        target_enemy = closest_enemy_id
        if prev_closest_enemy and prev_closest_enemy in current_distances['distances_to_enemies']:
            # Compare to same enemy as last time
            target_enemy = prev_closest_enemy
            enemy_change = current_distances['distances_to_enemies'][target_enemy] - prev_enemy_dist
        elif closest_enemy_id:
            # New closest enemy
            enemy_change = current_enemy_dist - prev_enemy_dist

        # Classification logic with movement threshold distance
        # Priority order: near_base > breached_perimeter > advancing/retreating > expanding/falling_back > other

        # 1. Near base (highest priority)
        if current_home_dist < self.BASE_PERIMETER_DISTANCE:
            return ('near_base', None)

        # 2. Breached enemy perimeter
        if current_enemy_dist < self.BASE_PERIMETER_DISTANCE:
            return ('breached_perimeter', closest_enemy_id)

        # 3. Advancing/retreating (must be closer to enemy than home)
        if current_enemy_dist < current_home_dist:
            if enemy_change <= -self.MOVEMENT_THRESHOLD_DISTANCE:  # Closer to enemy
                return ('advancing_towards', target_enemy)
            elif enemy_change >= self.MOVEMENT_THRESHOLD_DISTANCE:  # Further from enemy
                return ('retreating_from', target_enemy)

        # 4. Expanding/falling back based on home distance change
        if home_change >= self.MOVEMENT_THRESHOLD_DISTANCE:  # Further from home
            return ('expanding', None)
        elif home_change <= -self.MOVEMENT_THRESHOLD_DISTANCE:  # Closer to home
            return ('falling_back', None)

        # 5. Other (default)
        return ('other', None)

    def get_game_overview(self):
        """Generate a comprehensive game state report with advanced metrics"""

        current_tick = uw_game.game_tick()
        game_time_minutes = current_tick / 1200  # 20 ticks per second, 60 seconds per minute

        # Clear current unit positions for this analysis
        self.current_unit_positions = {}

        report = []
        report.append("=" * 60)
        report.append(f"GAME STATE REPORT - Tick {current_tick} ({game_time_minutes:.1f} minutes)")
        report.append("=" * 60)

        # Basic game info
        report.append(f"Game State: {uw_game.game_state()}")
        report.append(f"Map State: {uw_game.map_state()}")
        if uw_game.map_state() == MapState.Loaded:
            report.append(f"Map: {uw_map._name} ({uw_map._path})")

        # Get all entities for analysis
        all_entities = uw_world.entities()
        report.append(f"Total Entities: {len(all_entities)}")

        # Collect force and player information
        force_info = {}  # force_id -> {player_name, steam_id, color}
        force_metrics = {}  # force_id -> detailed metrics

        # First pass: collect force and player information
        for entity in all_entities.values():
            # Check for player entities
            if entity.Player:
                player = entity.Player
                force_id = player.force
                if force_id != 0:
                    if force_id not in force_info:
                        force_info[force_id] = {
                            'player_name': player.name,
                            'steam_id': player.steamUserId,
                            'color': None,
                            'force_entity': None
                        }

            # Check for force entities to get color, store the force entity, and determine race
            if entity.Force:
                force = entity.Force
                # Try to match this force entity with existing force info
                for fid in force_info.keys():
                    if force_info[fid]['color'] is None:
                        force_info[fid]['color'] = force.color
                        force_info[fid]['force_entity'] = entity  # Store the force entity

                        # Determine race from Force component
                        if hasattr(force, 'intendedRace') and force.intendedRace != 0:
                            # Get race name from prototype
                            try:
                                race_proto = uw_prototypes.get(force.intendedRace)
                                race_name = race_proto.name if race_proto else f"race_{force.intendedRace}"
                                self.force_types[fid] = race_name
                            except:
                                self.force_types[fid] = f"race_{force.intendedRace}"
                        break

            # Check for force detail entities for more race info
            if entity.ForceDetails:
                force_details = entity.ForceDetails
                # Try to match with existing forces
                for fid in force_info.keys():
                    if fid not in self.force_types and hasattr(force_details, 'race') and force_details.race != 0:
                        try:
                            race_proto = uw_prototypes.get(force_details.race)
                            race_name = race_proto.name if race_proto else f"race_{force_details.race}"
                            self.force_types[fid] = race_name
                        except:
                            self.force_types[fid] = f"race_{force_details.race}"
                        break

        # Initialize metrics for each force
        for force_id in force_info.keys():
            force_metrics[force_id] = {
                'units_by_type': {},
                'buildings_by_type': {},
                'recipes_by_type': {},
                'damaged_buildings': 0,
                'destroyed_buildings': 0,
                'planned_constructions': 0,
                'total_health_lost': 0,
                'units_home': 0,
                'units_attacking': {},  # enemy_force_id -> count
                'units_on_move': {},  # unit_type -> count
                'atvs_by_type': {},
                'towers_by_type': {},
                'resources_by_type': {},
                'total_unit_score': 0,
                'total_building_score': 0,
                'furthest_unit_distance': 0,
                'furthest_unit_name': None,
                'closest_to_each_enemy': {},  # enemy_force_id -> {'distance': float, 'unit_name': str}
                # Tag-based classification
                'units_by_tags': {},  # tag_combination -> {'count': int, 'name_counts': {}}
                'buildings_by_tags': {},  # tag_combination -> {'count': int, 'name_counts': {}}
                'towers_by_tags': {},  # tag_combination -> {'count': int, 'name_counts': {}}
                'atvs_by_tags': {},  # tag_combination -> {'count': int, 'name_counts': {}}
                # Movement analysis
                'movement_analysis': {
                    'near_base': [],                    # unit names near own base
                    'breached_perimeter': {},           # enemy_force_id -> list of unit names
                    'advancing_towards': {},            # enemy_force_id -> list of unit names
                    'retreating_from': {},              # enemy_force_id -> list of unit names
                    'expanding': [],                    # unit names expanding from base
                    'falling_back': [],                 # unit names falling back to base
                    'other': []                         # unit names in other states
                },
                # Health analysis
                'units_by_life': {
                    'full_health': [],                  # 80+% life
                    'over_50_life': [],                 # 50+% life
                    'over_30_life': [],                 # 30+% life
                    'almost_destroyed': []              # <30% life
                },
                'buildings_by_life': {
                    'full_health': [],                  # 80+% life
                    'over_50_life': [],                 # 50+% life
                    'over_30_life': [],                 # 30+% life
                    'almost_destroyed': []              # <30% life
                }
            }

        # Second pass: analyze all entities
        for entity in all_entities.values():
            if entity.Proto is None:
                continue

            proto_name = entity.proto().name if entity.proto() else "Unknown"

            # Skip entities without owner (neutral)
            if not entity.Owner or entity.Owner.force == 0:
                continue

            force_id = entity.Owner.force
            if force_id not in force_metrics:
                continue

            metrics = force_metrics[force_id]

            # Use entity.type() for proper classification instead of hardcoded name matching
            entity_type = entity.type()
            proto_lower = proto_name.lower()

            # Resource laying on the ground
            is_resource = entity_type == PrototypeType.Resource

            # Constructions: planned building or destroyed building
            is_planned_building = entity_type == PrototypeType.Construction and entity.Priority != Priority.Disabled
            is_destroyed_building = entity_type == PrototypeType.Construction and entity.Priority == Priority.Disabled

            can_shoot = entity.proto().data.get('dps', 0) > 0
            can_move = False 
            try:
                print(f"Entity {entity.id} data: {entity.proto().data}") if random.random() < 0.005 else None
                can_move = len(entity.proto().data.get('speeds', {})) > 0
            except:
                pass

            is_tower = entity_type == PrototypeType.Unit and can_shoot and not can_move
            is_building = entity_type == PrototypeType.Unit and not can_shoot and not can_move

            is_overlord = 'overlord' in proto_lower
            # Exclude overlords from combat units (they're commanders/leaders, not combat units)
            is_unit = entity_type == PrototypeType.Unit and can_shoot and can_move and not is_overlord
            is_atv = entity_type == PrototypeType.Unit and not can_shoot and can_move

            # Get tag combination for classification
            tag_combination = "untagged"
            try:
                proto = entity.proto()
                if proto and hasattr(proto, 'tagsNames') and proto.tagsNames:
                    # Sort tags to ensure consistent ordering
                    tags = sorted(proto.tagsNames)
                    tag_combination = "+".join(tags)
            except:
                pass

            if is_building:
                # Track building metrics
                if proto_name not in metrics['buildings_by_type']:
                    metrics['buildings_by_type'][proto_name] = 0
                metrics['buildings_by_type'][proto_name] += 1

                # Track building by tags
                if tag_combination not in metrics['buildings_by_tags']:
                    metrics['buildings_by_tags'][tag_combination] = {'count': 0, 'name_counts': {}}
                metrics['buildings_by_tags'][tag_combination]['count'] += 1
                if proto_name not in metrics['buildings_by_tags'][tag_combination]['name_counts']:
                    metrics['buildings_by_tags'][tag_combination]['name_counts'][proto_name] = 0
                metrics['buildings_by_tags'][tag_combination]['name_counts'][proto_name] += 1

                # Add prototype score for building
                try:
                    proto = entity.proto()
                    if proto and hasattr(proto, 'data') and isinstance(proto.data, dict):
                        building_score = proto.data.get('score', 0)
                        metrics['total_building_score'] += building_score
                except:
                    pass

                # Track building health status
                life_percentage = self.get_life_percentage(entity)
                health_status = self.categorize_health_status(life_percentage)
                metrics['buildings_by_life'][health_status].append(proto_name)

            elif is_planned_building:
                # Track planned constructions
                metrics['planned_constructions'] += 1

            elif is_destroyed_building:
                # Track destroyed buildings
                metrics['destroyed_buildings'] += 1

            elif is_atv:
                # Track ATVs separately (non-combat units)
                if proto_name not in metrics['atvs_by_type']:
                    metrics['atvs_by_type'][proto_name] = 0
                metrics['atvs_by_type'][proto_name] += 1

                # Track ATV by tags
                if tag_combination not in metrics['atvs_by_tags']:
                    metrics['atvs_by_tags'][tag_combination] = {'count': 0, 'name_counts': {}}
                metrics['atvs_by_tags'][tag_combination]['count'] += 1
                if proto_name not in metrics['atvs_by_tags'][tag_combination]['name_counts']:
                    metrics['atvs_by_tags'][tag_combination]['name_counts'][proto_name] = 0
                metrics['atvs_by_tags'][tag_combination]['name_counts'][proto_name] += 1

            elif is_tower:
                # Track towers separately (static defensive units)
                if proto_name not in metrics['towers_by_type']:
                    metrics['towers_by_type'][proto_name] = 0
                metrics['towers_by_type'][proto_name] += 1

                # Track tower by tags
                if tag_combination not in metrics['towers_by_tags']:
                    metrics['towers_by_tags'][tag_combination] = {'count': 0, 'name_counts': {}}
                metrics['towers_by_tags'][tag_combination]['count'] += 1
                if proto_name not in metrics['towers_by_tags'][tag_combination]['name_counts']:
                    metrics['towers_by_tags'][tag_combination]['name_counts'][proto_name] = 0
                metrics['towers_by_tags'][tag_combination]['name_counts'][proto_name] += 1

            elif is_resource:
                # Track resources separately
                if proto_name not in metrics['resources_by_type']:
                    metrics['resources_by_type'][proto_name] = 0
                metrics['resources_by_type'][proto_name] += 1

            elif is_unit:
                # Track combat unit metrics (ATVs are handled separately)
                if proto_name not in metrics['units_by_type']:
                    metrics['units_by_type'][proto_name] = 0
                metrics['units_by_type'][proto_name] += 1

                # Track unit by tags
                if tag_combination not in metrics['units_by_tags']:
                    metrics['units_by_tags'][tag_combination] = {'count': 0, 'name_counts': {}}
                metrics['units_by_tags'][tag_combination]['count'] += 1
                if proto_name not in metrics['units_by_tags'][tag_combination]['name_counts']:
                    metrics['units_by_tags'][tag_combination]['name_counts'][proto_name] = 0
                metrics['units_by_tags'][tag_combination]['name_counts'][proto_name] += 1

                # Add prototype score for combat unit
                try:
                    proto = entity.proto()
                    if proto and hasattr(proto, 'data') and isinstance(proto.data, dict):
                        unit_score = proto.data.get('score', 0)
                        metrics['total_unit_score'] += unit_score
                except:
                    pass

                # Track unit health status
                life_percentage = self.get_life_percentage(entity)
                health_status = self.categorize_health_status(life_percentage)
                metrics['units_by_life'][health_status].append(proto_name)

                # Check if this is an overlord - save as fallback base position
                if 'overlord' in proto_lower and entity.Position and force_id not in self.overlord_positions:
                    self.overlord_positions[force_id] = entity.Position.position

                # Movement tracking and classification for combat units
                if entity.Position:
                    unit_pos = entity.Position.position
                    unit_id = entity.id

                    # Calculate distances to all bases
                    distances = self.calculate_unit_distances(unit_pos, force_id)

                    # Store current position data
                    self.current_unit_positions[unit_id] = {
                        'position': unit_pos,
                        'distance_to_home': distances['distance_to_home'],
                        'distance_to_closest_enemy': distances['distance_to_closest_enemy'],
                        'closest_enemy_force_id': distances['closest_enemy_force_id']
                    }

                    # Update legacy metrics for compatibility
                    if distances['distance_to_home'] != float('inf'):
                        if distances['distance_to_home'] > metrics['furthest_unit_distance']:
                            metrics['furthest_unit_distance'] = distances['distance_to_home']
                            metrics['furthest_unit_name'] = proto_name
                        if distances['distance_to_home'] < 500:
                            metrics['units_home'] += 1

                    # Track closest unit to each enemy force
                    for enemy_force_id, distance_to_enemy in distances['distances_to_enemies'].items():
                        if enemy_force_id not in metrics['closest_to_each_enemy']:
                            metrics['closest_to_each_enemy'][enemy_force_id] = {
                                'distance': float('inf'),
                                'unit_name': None
                            }

                        if distance_to_enemy < metrics['closest_to_each_enemy'][enemy_force_id]['distance']:
                            metrics['closest_to_each_enemy'][enemy_force_id]['distance'] = distance_to_enemy
                            metrics['closest_to_each_enemy'][enemy_force_id]['unit_name'] = proto_name

                    # Classify unit movement
                    movement_type, target_enemy = self.classify_unit_movement(unit_id, proto_name, distances)

                    # Update movement analysis metrics
                    movement_analysis = metrics['movement_analysis']

                    if movement_type == 'near_base':
                        movement_analysis['near_base'].append(proto_name)
                    elif movement_type == 'breached_perimeter':
                        if target_enemy not in movement_analysis['breached_perimeter']:
                            movement_analysis['breached_perimeter'][target_enemy] = []
                        movement_analysis['breached_perimeter'][target_enemy].append(proto_name)
                    elif movement_type == 'advancing_towards':
                        if target_enemy not in movement_analysis['advancing_towards']:
                            movement_analysis['advancing_towards'][target_enemy] = []
                        movement_analysis['advancing_towards'][target_enemy].append(proto_name)
                    elif movement_type == 'retreating_from':
                        if target_enemy not in movement_analysis['retreating_from']:
                            movement_analysis['retreating_from'][target_enemy] = []
                        movement_analysis['retreating_from'][target_enemy].append(proto_name)
                    elif movement_type == 'expanding':
                        movement_analysis['expanding'].append(proto_name)
                    elif movement_type == 'falling_back':
                        movement_analysis['falling_back'].append(proto_name)
                    else:  # other
                        movement_analysis['other'].append(proto_name)

                    # Update legacy attack metrics for compatibility
                    if distances['distance_to_closest_enemy'] < distances['distance_to_home'] and distances['closest_enemy_force_id']:
                        closest_enemy_force = distances['closest_enemy_force_id']
                        if closest_enemy_force not in metrics['units_attacking']:
                            metrics['units_attacking'][closest_enemy_force] = 0
                        metrics['units_attacking'][closest_enemy_force] += 1
                    elif distances['distance_to_home'] >= 500:  # Away from home but not attacking
                        if proto_name not in metrics['units_on_move']:
                            metrics['units_on_move'][proto_name] = 0
                        metrics['units_on_move'][proto_name] += 1

        # Generate force reports
        report.append("\nFORCES:")
        observer_force_id = uw_world.my_force_id()
        for force_id in sorted(force_info.keys()):
            # Skip observer force from reports
            if force_id == observer_force_id:
                continue
            info = force_info[force_id]
            metrics = force_metrics[force_id]

            player_name = info['player_name']
            steam_id = info['steam_id']
            color = info['color']

            color_str = ""
            if color:
                r, g, b = [int(c * 255) for c in color]
                color_name = self.rgb_to_color_name(r, g, b)
                color_str = f" ({color_name})"

            # Get force score from the stored force entity
            force_score = "unknown"
            if info.get('force_entity') and info['force_entity'].Force:
                force_score = info['force_entity'].Force.score

            # Force type info
            raw_force_type = self.force_types.get(force_id, "unknown")
            # Map API race names to display names
            force_type = "fucking bugs" if raw_force_type == "biomass" else raw_force_type

            # Add elimination status if force is eliminated
            elimination_status = " [ELIMINATED]" if force_id in self.eliminated_forces else ""

            report.append(f"  Force {force_id}: {player_name} (Steam: {steam_id}){color_str} - Type: {force_type}{elimination_status}")
            report.append(f"    Score: {force_score}")

            # Unit counts (combat units only, excluding ATVs)
            total_units = sum(metrics['units_by_type'].values())
            total_buildings = sum(metrics['buildings_by_type'].values())

            # Combat units only (excluding ATVs)
            report.append(f"    Combat Units: {total_units} total")
            # Unit tag breakdown
            if metrics['units_by_tags']:
                for tag_combo, data in sorted(metrics['units_by_tags'].items()):
                    name_breakdown = []
                    for name, count in sorted(data['name_counts'].items()):
                        name_breakdown.append(f"{count} {self.pluralize(name) if count > 1 else name}")
                    names_str = ", ".join(name_breakdown)
                    report.append(f"      {tag_combo}: {data['count']} ({names_str})")

            # Unit score breakdown
            if metrics['total_unit_score'] > 0:
                report.append(f"      Total Unit Score: {metrics['total_unit_score']}")

            # Combat Units by Life breakdown
            if metrics['units_by_life']:
                report.append(f"    Combat Units by Life:")
                if metrics['units_by_life']['full_health']:
                    unit_counts = {}
                    for unit_name in metrics['units_by_life']['full_health']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Full health (80%+): {units_str}")
                if metrics['units_by_life']['over_50_life']:
                    unit_counts = {}
                    for unit_name in metrics['units_by_life']['over_50_life']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Over 50% life: {units_str}")
                if metrics['units_by_life']['over_30_life']:
                    unit_counts = {}
                    for unit_name in metrics['units_by_life']['over_30_life']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Over 30% life: {units_str}")
                if metrics['units_by_life']['almost_destroyed']:
                    unit_counts = {}
                    for unit_name in metrics['units_by_life']['almost_destroyed']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Almost destroyed (<30%): {units_str}")

            # Combat Units by Distance section
            if (total_units > 0 or
                metrics['furthest_unit_distance'] > 0 or
                metrics['closest_to_each_enemy'] or
                any(metrics['movement_analysis'].values())):

                report.append(f"    Combat Units by Distance:")

                # Distances section
                report.append(f"      Distances:")
                if metrics['furthest_unit_distance'] > 0 and metrics['furthest_unit_name']:
                    report.append(f"        Furthest away from home: {metrics['furthest_unit_name']} at {metrics['furthest_unit_distance']:.0f}")

                # Show closest unit to each enemy force
                for enemy_force_id, closest_info in sorted(metrics['closest_to_each_enemy'].items()):
                    if closest_info['unit_name'] and closest_info['distance'] < float('inf'):
                        report.append(f"        Unit closest to Force {enemy_force_id}: {closest_info['unit_name']} at {closest_info['distance']:.0f}")

                # Movement analysis reporting
                movement = metrics['movement_analysis']

                # Near base units
                if movement['near_base']:
                    unit_counts = {}
                    for unit_name in movement['near_base']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Near base: {units_str}")

                # Breached perimeter
                for enemy_force_id, units in movement['breached_perimeter'].items():
                    if units:
                        unit_counts = {}
                        for unit_name in units:
                            unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                        units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                            for unit_name, count in sorted(unit_counts.items()))
                        report.append(f"      Breached perimeter of Force {enemy_force_id}: {units_str}")

                # Advancing towards enemies
                for enemy_force_id, units in movement['advancing_towards'].items():
                    if units:
                        unit_counts = {}
                        for unit_name in units:
                            unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                        units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                            for unit_name, count in sorted(unit_counts.items()))
                        report.append(f"      Advancing towards Force {enemy_force_id}: {units_str}")

                # Retreating from enemies
                for enemy_force_id, units in movement['retreating_from'].items():
                    if units:
                        unit_counts = {}
                        for unit_name in units:
                            unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                        units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                            for unit_name, count in sorted(unit_counts.items()))
                        report.append(f"      Retreating from Force {enemy_force_id}: {units_str}")

                # Expanding
                if movement['expanding']:
                    unit_counts = {}
                    for unit_name in movement['expanding']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Expanding from home: {units_str}")

                # Falling back
                if movement['falling_back']:
                    unit_counts = {}
                    for unit_name in movement['falling_back']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Falling back home: {units_str}")

                # Other (units not in specific movement categories)
                if movement['other']:
                    unit_counts = {}
                    for unit_name in movement['other']:
                        unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
                    units_str = ", ".join(f"{count} {self.pluralize(unit_name) if count > 1 else unit_name}"
                                        for unit_name, count in sorted(unit_counts.items()))
                    report.append(f"      Other: {units_str}")

            # Workers (non-combat)
            total_workers = sum(metrics['atvs_by_type'].values())
            if total_workers > 0:
                worker_types_list = [f"{count} {self.pluralize(atv_type)}" for atv_type, count in sorted(metrics['atvs_by_type'].items())]
                worker_types_str = f" ({', '.join(worker_types_list)})"
                report.append(f"    Workers: {total_workers} total{worker_types_str}")

            # Towers (static defensive)
            total_towers = sum(metrics['towers_by_type'].values())
            if total_towers > 0:
                report.append(f"    Towers: {total_towers} total")
                # Tower tag breakdown
                if metrics['towers_by_tags']:
                    for tag_combo, data in sorted(metrics['towers_by_tags'].items()):
                        name_breakdown = []
                        for name, count in sorted(data['name_counts'].items()):
                            name_breakdown.append(f"{count} {self.pluralize(name) if count > 1 else name}")
                        names_str = ", ".join(name_breakdown)
                        report.append(f"      {tag_combo}: {data['count']} ({names_str})")

            # Resources
            total_resources = sum(metrics['resources_by_type'].values())
            if total_resources > 0:
                resource_types_list = [f"{count} {self.pluralize(resource_type)}" for resource_type, count in sorted(metrics['resources_by_type'].items())]
                resource_types_str = f" ({', '.join(resource_types_list)})"
                report.append(f"    Resources: {total_resources} total{resource_types_str}")

            report.append(f"    Buildings: {total_buildings} total")
            # Building tag breakdown
            if metrics['buildings_by_tags']:
                for tag_combo, data in sorted(metrics['buildings_by_tags'].items()):
                    name_breakdown = []
                    for name, count in sorted(data['name_counts'].items()):
                        name_breakdown.append(f"{count} {self.pluralize(name) if count > 1 else name}")
                    names_str = ", ".join(name_breakdown)
                    report.append(f"      {tag_combo}: {data['count']} ({names_str})")

            # Building score breakdown
            if metrics['total_building_score'] > 0:
                report.append(f"      Total Building Score: {metrics['total_building_score']}")

            # Buildings by Life breakdown
            if metrics['buildings_by_life']:
                report.append(f"    Buildings by Life:")
                if metrics['buildings_by_life']['full_health']:
                    building_counts = {}
                    for building_name in metrics['buildings_by_life']['full_health']:
                        building_counts[building_name] = building_counts.get(building_name, 0) + 1
                    buildings_str = ", ".join(f"{count} {self.pluralize(building_name) if count > 1 else building_name}"
                                            for building_name, count in sorted(building_counts.items()))
                    report.append(f"      Full health (80%+): {buildings_str}")
                if metrics['buildings_by_life']['over_50_life']:
                    building_counts = {}
                    for building_name in metrics['buildings_by_life']['over_50_life']:
                        building_counts[building_name] = building_counts.get(building_name, 0) + 1
                    buildings_str = ", ".join(f"{count} {self.pluralize(building_name) if count > 1 else building_name}"
                                            for building_name, count in sorted(building_counts.items()))
                    report.append(f"      Over 50% life: {buildings_str}")
                if metrics['buildings_by_life']['over_30_life']:
                    building_counts = {}
                    for building_name in metrics['buildings_by_life']['over_30_life']:
                        building_counts[building_name] = building_counts.get(building_name, 0) + 1
                    buildings_str = ", ".join(f"{count} {self.pluralize(building_name) if count > 1 else building_name}"
                                            for building_name, count in sorted(building_counts.items()))
                    report.append(f"      Over 30% life: {buildings_str}")
                if metrics['buildings_by_life']['almost_destroyed']:
                    building_counts = {}
                    for building_name in metrics['buildings_by_life']['almost_destroyed']:
                        building_counts[building_name] = building_counts.get(building_name, 0) + 1
                    buildings_str = ", ".join(f"{count} {self.pluralize(building_name) if count > 1 else building_name}"
                                            for building_name, count in sorted(building_counts.items()))
                    report.append(f"      Almost destroyed (<30%): {buildings_str}")

            # Planned Buildings section
            if metrics['planned_constructions'] > 0:
                report.append(f"    Planned Buildings: {metrics['planned_constructions']} total")

                # Destroyed Buildings section (under Planned Buildings)
                if metrics['destroyed_buildings'] > 0:
                    report.append(f"    Destroyed Buildings: {metrics['destroyed_buildings']} total")

            # Active recipes
            if metrics['recipes_by_type']:
                recipe_count = sum(metrics['recipes_by_type'].values())
                report.append(f"    Active recipes: {recipe_count}")

            # Total score (if available)
            if hasattr(uw_game, 'get_force_score'):
                try:
                    score = uw_game.get_force_score(force_id)
                    report.append(f"    Score: {score}")
                except:
                    pass

        # Debug info: Oil deposit distances
        if self.oil_deposit_positions:
            report.append("\nDEBUG - OIL DEPOSIT DISTANCES:")
            for i, oil_pos in enumerate(self.oil_deposit_positions):
                min_distance = float('inf')
                closest_base_info = "no base"

                # Check distance to all main bases and overlords
                for force_id in force_info.keys():
                    if force_id == observer_force_id:  # Skip observer force
                        continue

                    base_pos = None
                    base_type = ""
                    if force_id in self.main_base_positions:
                        base_pos = self.main_base_positions[force_id]
                        base_type = "main base"
                    elif force_id in self.overlord_positions:
                        base_pos = self.overlord_positions[force_id]
                        base_type = "overlord"

                    if base_pos:
                        distance = uw_map.distance_line(oil_pos, base_pos)
                        if distance < min_distance:
                            min_distance = distance
                            raw_force_type = self.force_types.get(force_id, "unknown")
                            force_type = "fucking bugs" if raw_force_type == "biomass" else raw_force_type
                            closest_base_info = f"Force {force_id} ({force_type} {base_type}) at {distance:.0f}"

                report.append(f"  Oil deposit {i+1}: closest to {closest_base_info}")

        # Newly eliminated forces report
        newly_eliminated = self.eliminated_forces - self.announced_eliminations
        if newly_eliminated:
            report.append("")
            newly_eliminated_list = ", ".join(f"Force {fid}" for fid in sorted(newly_eliminated))
            report.append(f"NEWLY ELIMINATED FORCES: {newly_eliminated_list}")
            # Mark these eliminations as announced
            self.announced_eliminations.update(newly_eliminated)

        report.append("=" * 60)

        # Save current positions as previous for next analysis
        self.previous_unit_positions = self.current_unit_positions.copy()

        return "\n".join(report)

    def generate_game_id(self):
        """Generate unique game identifier based on server/port or lobby ID."""
        if self.server and self.port:
            # Direct IP connection: server_port
            self.current_game_id = f"{self.server}_{self.port}"
        elif self.server and self.server.startswith('lobby_id'):
            # Lobby connection: lobby_id_<id>
            self.current_game_id = self.server
        else:
            # Fallback to timestamp if no connection info
            from datetime import datetime
            self.current_game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"🎮 Game ID: {self.current_game_id}")

    def get_context_filename(self):
        """Get context filename specific to current game."""
        return f"ai_yapper_context_{self.current_game_id}.txt"

    def load_context(self):
        """Load saved context summary from game-specific file."""
        context_file = self.get_context_filename()
        try:
            if os.path.exists(context_file):
                with open(context_file, 'r', encoding='utf-8') as f:
                    self.context_summary = f.read().strip()
                print(f"📖 Loaded context summary from {context_file}")
            else:
                print(f"🆕 New game - no previous context found")
                self.context_summary = ""
        except Exception as e:
            print(f"Error loading context: {e}")
            self.context_summary = ""

    def save_context(self, context):
        """Save context summary to game-specific file."""
        context_file = self.get_context_filename()
        try:
            self.context_summary = context
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(context)
            print(f"💾 Saved context summary to {context_file}")
        except Exception as e:
            print(f"Error saving context: {e}")

    def reset_game_state(self):
        """Reset game state for new game session."""
        print(f"🔄 Resetting game state for new session: {self.current_game_id}")
        self.report_history = []
        self.context_summary = ""
        self.last_announcement = ""
        self.load_context()  # Load context specific to this game

    def generate_report_diff(self, new_report, old_report):
        """Generate a git-style unified diff between two reports."""
        if not old_report:
            return "First report - no comparison available"

        import difflib

        # Split reports into lines for comparison
        old_lines = old_report.splitlines(keepends=True)
        new_lines = new_report.splitlines(keepends=True)

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='previous_report',
            tofile='current_report',
            lineterm=''
        ))

        if not diff_lines:
            return "No changes detected"

        # Join the diff lines and return
        return '\n'.join(diff_lines)

    def send_to_gemini(self, prompt):
        """Send a prompt to Gemini API and return the response."""
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.gemini_api_key
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.gemini_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            # Extract text from the response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text']

            return None
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini API: {e}")
            return None

    def speak_announcement(self, text):
        """Use text-to-speech to announce the given text."""
        # Run TTS in separate process to avoid thread conflicts with game engine
        import subprocess
        import threading

        def run_tts_subprocess():
            """Run TTS in a completely separate process to avoid game thread issues."""

            # Try system TTS commands first (more reliable and thread-safe)
            tts_methods = [
                ["espeak", text],
                ["spd-say", text],
            ]

            for method in tts_methods:
                try:
                    subprocess.run(method, check=True, timeout=10,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"🔊 TTS Success with {method[0]}")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue

            # Try festival with echo pipe
            try:
                p1 = subprocess.Popen(["echo", text], stdout=subprocess.PIPE)
                p2 = subprocess.Popen(["festival", "--tts"], stdin=p1.stdout,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                p1.stdout.close()
                p2.wait(timeout=10)
                print("🔊 TTS Success with festival")
                return
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass

            # Try pyttsx3 in separate Python process to avoid threading issues
            if PYTTSX3_AVAILABLE:
                try:
                    # Create a simple TTS script and run it in separate process
                    tts_script = f'''
import pyttsx3
try:
    engine = pyttsx3.init()
    engine.say("{text.replace('"', '\\"')}")
    engine.runAndWait()
    print("TTS Success")
except Exception as e:
    print(f"TTS Error: {{e}}")
'''
                    result = subprocess.run([sys.executable, "-c", tts_script],
                                          capture_output=True, timeout=15, text=True)
                    if "TTS Success" in result.stdout:
                        print("🔊 TTS Success with pyttsx3 (subprocess)")
                        return
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    pass

            print("🔇 TTS not available, announcement:", text)

        # Run TTS in background thread to avoid blocking game
        try:
            tts_thread = threading.Thread(target=run_tts_subprocess, daemon=True)
            tts_thread.start()
            print(f"🎤 ANNOUNCEMENT: {text}")
        except Exception as e:
            print(f"🔇 TTS thread error: {e}")
            print("🎤 ANNOUNCEMENT:", text)

    def parse_gemini_response(self, response):
        """Parse Gemini response to extract announcement and context sections."""
        announcement = ""
        context = ""

        lines = response.split('\n')
        current_section = None

        for line in lines:
            lower_line = line.lower().strip()
            if 'announcement' in lower_line and ':' in line:
                current_section = 'announcement'
                # Try to get text after the colon on the same line
                parts = line.split(':', 1)
                if len(parts) > 1:
                    announcement = parts[1].strip()
            elif 'context' in lower_line and ':' in line:
                current_section = 'context'
                # Try to get text after the colon on the same line
                parts = line.split(':', 1)
                if len(parts) > 1:
                    context = parts[1].strip()
            elif current_section == 'announcement' and line.strip():
                if announcement:
                    announcement += " " + line.strip()
                else:
                    announcement = line.strip()
            elif current_section == 'context' and line.strip():
                if context:
                    context += " " + line.strip()
                else:
                    context = line.strip()

        return announcement, context

    def send_special_message(self, message_type, message_text):
        """Send special start/end game messages to TTS and news API."""
        print(f"\n🎉 {message_type.upper()}: {message_text}")
        self.speak_announcement(message_text)
        self.send_to_news_api(message_text)

    def check_game_state_changes(self):
        """Check for game start/end and send special messages."""
        current_game_state = uw_game.game_state()

        # Game start detection (transition to Game state)
        if (not self.game_start_announced and
            current_game_state == GameState.Game and
            self.previous_game_state != GameState.Game):

            # Get force information for start message
            all_entities = uw_world.entities()
            force_info = {}
            force_races = {}

            # Identify forces that have actual gameplay entities (not observers)
            forces_with_entities = set()
            for entity in all_entities.values():
                if entity.Owner and entity.Owner.force != 0:
                    # Only count forces that have units or buildings (not just observers)
                    if entity.type() in [PrototypeType.Unit, PrototypeType.Construction]:
                        forces_with_entities.add(entity.Owner.force)

            # First pass: collect player info (only for forces with gameplay entities)
            for entity in all_entities.values():
                if entity.Player:
                    player = entity.Player
                    force_id = player.force
                    # Include only forces that have actual gameplay entities
                    if force_id != 0 and force_id in forces_with_entities:
                        force_info[force_id] = {
                            'player_name': player.name,
                            'steam_id': player.steamUserId
                        }

            # Second pass: detect races from Force entities
            for entity in all_entities.values():
                if entity.Force:
                    force = entity.Force
                    # Try to match this force entity with existing force info
                    for fid in force_info.keys():
                        if fid not in force_races:
                            # Determine race from Force component
                            if hasattr(force, 'intendedRace') and force.intendedRace != 0:
                                try:
                                    race_proto = uw_prototypes.get(force.intendedRace)
                                    race_name = race_proto.name if race_proto else f"race_{force.intendedRace}"
                                    force_races[fid] = race_name
                                except:
                                    force_races[fid] = f"race_{force.intendedRace}"
                            break

                # Check for force detail entities for more race info
                if entity.ForceDetails:
                    force_details = entity.ForceDetails
                    for fid in force_info.keys():
                        if fid not in force_races and hasattr(force_details, 'race') and force_details.race != 0:
                            try:
                                race_proto = uw_prototypes.get(force_details.race)
                                race_name = race_proto.name if race_proto else f"race_{force_details.race}"
                                force_races[fid] = race_name
                            except:
                                force_races[fid] = f"race_{force_details.race}"
                            break

            # Create start message with proper race detection
            if len(force_info) >= 2:
                players = []
                for force_id, info in force_info.items():
                    race = force_races.get(force_id, "unknown")
                    # Map API race names to display names
                    if race == "biomass":
                        race = "fucking bugs"
                    players.append(f"{info['player_name']} as {race}")

                start_message = f"The battle begins! {' versus '.join(players)}. Let the carnage commence!"
            else:
                start_message = "The battlefield is set and the war machines are ready! Let the destruction begin!"

            # Record game start time
            import time
            self.game_start_time = time.time()

            # Only send the start message if we observed the actual transition from Session to Game
            # This prevents spam when joining an already-running game
            if self.previous_game_state == GameState.Session:
                self.send_special_message("GAME START", start_message)

            self.game_start_announced = True

        # Game end detection (transition to Finish state or all but one force eliminated)
        if (not self.game_end_announced and
            (current_game_state == GameState.Finish or
             self.check_victory_condition())):

            # Determine winner
            winner_message = self.get_victory_message()
            self.send_special_message("GAME END", winner_message)
            self.game_end_announced = True

        # Update previous state
        self.previous_game_state = current_game_state

    def check_victory_condition(self):
        """Check if victory condition is met (only one force remaining)."""
        all_entities = uw_world.entities()
        active_forces = set()
        observer_force_id = uw_world.my_force_id()

        for entity in all_entities.values():
            if entity.Owner and entity.Owner.force != 0 and entity.Owner.force != observer_force_id:
                if entity.Owner.force not in self.eliminated_forces:
                    active_forces.add(entity.Owner.force)

        return len(active_forces) <= 1

    def get_victory_message(self):
        """Generate victory message based on current game state."""
        all_entities = uw_world.entities()
        active_forces = set()
        observer_force_id = uw_world.my_force_id()

        # Find remaining active forces
        for entity in all_entities.values():
            if entity.Owner and entity.Owner.force != 0 and entity.Owner.force != observer_force_id:
                if entity.Owner.force not in self.eliminated_forces:
                    active_forces.add(entity.Owner.force)

        # Get force info for active forces
        force_info = {}
        for entity in all_entities.values():
            if entity.Player:
                player = entity.Player
                force_id = player.force
                if force_id in active_forces:
                    force_info[force_id] = {
                        'player_name': player.name,
                        'force_type': self.force_types.get(force_id, "unknown")
                    }

        if len(active_forces) == 1:
            # Single winner
            winner_force_id = next(iter(active_forces))
            if winner_force_id in force_info:
                winner_info = force_info[winner_force_id]
                race = "fucking bugs" if winner_info['force_type'] == "biomass" else winner_info['force_type']
                return f"Victory achieved! {winner_info['player_name']} and their {race} forces have conquered the battlefield! The war is over!"
            else:
                return "Victory achieved! One force stands triumphant over the ruins of their enemies!"
        elif len(active_forces) == 0:
            # No survivors
            return "Total annihilation! No forces remain standing on this devastated battlefield. The war has consumed all!"
        else:
            # Multiple forces still active (shouldn't happen in normal end conditions)
            return "The battle has ended with multiple forces still standing. What a strange conclusion to this war!"

    def process_with_ai_yapper(self, new_report):
        """Process the new report with AI yapper functionality."""
        # Add the new report to our storage
        self.report_history.append(new_report)

        # Keep only the last 10 reports to manage memory
        if len(self.report_history) > 10:
            self.report_history.pop(0)

        # Only process with AI if we have at least one report
        if len(self.report_history) < 1:
            return

        print("\n" + "="*60)
        print("PROCESSING WITH AI YAPPER...")
        print("="*60)

        # Prepare the current report and diffs
        current_report = self.report_history[-1]

        # Generate diff against previous report
        previous_diff = ""
        if len(self.report_history) >= 2:
            previous_report = self.report_history[-2]
            previous_diff = self.generate_report_diff(current_report, previous_report)
            print(f"\n🔍 DIFF FROM PREVIOUS REPORT:\n{previous_diff}")

        # Generate diff against 7 reports back
        seven_back_diff = ""
        if len(self.report_history) >= 8:
            seven_back_report = self.report_history[-8]
            seven_back_diff = self.generate_report_diff(current_report, seven_back_report)
            print(f"\n🔍 DIFF FROM 7 REPORTS AGO:\n{seven_back_diff}")

        # Combine all information for the prompt
        reports_text = f"""--- CURRENT REPORT ---
{current_report}

--- CHANGES FROM PREVIOUS REPORT ---
{previous_diff if previous_diff else "No previous report available"}

--- CHANGES FROM 7 REPORTS AGO ---
{seven_back_diff if seven_back_diff else "Not enough report history available"}

--- LAST ANNOUNCEMENT ---
{self.last_announcement if self.last_announcement else "No previous announcement"}"""

        # Build the prompt
        context_prefix = f"This is what happened in the game so far: {self.context_summary}\n\n" if self.context_summary else ""

        tag_info = """Game info:
- Technocracy / fucking bugs are race types. E.g. Technocracies are not allied with other technocracies.

Tags:
ambush - walks over additional terrain types.
artillery - longer range than most.
assault - good for front-line combat.
decoration - just a decoration.
deposit - contains ore; build a miner over this unit to gather resources.
harassment - good for hit-and-run attacks, especially targeting workers.
home - the center of your base. dont let it die.
miner - generates resources, usually from ore deposits.
navy - moves on water only.
noncombat - not intended for combat, even if it has an attack/explosion.
nonprogression - an alternative for another prototype (this tag is used to break cyclic dependencies).
production - produces more units.
research - produces upgrades.
scout - fast and cheap, good as a scout.
siege - designed for destroying buildings.
splash - area-of-effect attack/explosion.
suicidal - sacrifices itself when attacking.
tank - defensive unit with life above typical.
tower - stationary defensive structure.
volatile - may damage own/allied units.
wall - stationary path blocking structure.
worker - carries resources, automatic control by logistics planning.

"""

        prompt = f"""{context_prefix}{tag_info}You are an energetic RTS game announcer AI. You've received the latest game reports from an Unnatural Worlds observer bot:

{reports_text}

Based on this information, please provide:

1. **Announcement**: A brief (3-4 sentences) high-energy RTS-inspired announcement about the latest developments in the game. Make it exciting but be specific and accurate. Make sure to pick the right highlights, and avoid repeating information from previous announcements.

2. **Context**: A 1-paragraph summary of what has happened in the game so far that I can use for the next analysis. Add a small note about important reported events like eliminations to avoid repeating them.

Style instructions:
- Don't use "fucking bugs" in quotes
- Don't repeat who has been eliminated over and over
- DO NOT repeat themes, phrases, or specific information from the LAST ANNOUNCEMENT - focus on NEW developments and changes
- If there are no significant new developments, focus on tactical positioning or strategic trends rather than repeating old information

Format your response exactly as:
Announcement: [Your exciting announcement here]
Context: [Context summary for next time]"""

        # Send to Gemini
        response = self.send_to_gemini(prompt)

        if response:
            print(f"\nGemini Response:\n{response}")

            # Parse response
            announcement, context = self.parse_gemini_response(response)

            if announcement:
                print(f"\n🎤 ANNOUNCEMENT: {announcement}")
                self.last_announcement = announcement  # Store for next iteration to avoid repetition
                self.speak_announcement(announcement)
                self.send_to_news_api(announcement)
            else:
                print("❌ No announcement found in response")

            if context:
                print(f"\n📝 CONTEXT SUMMARY: {context}")
                self.save_context(context)
            else:
                print("❌ No context found in response")

        else:
            print("❌ Failed to get response from Gemini")

    def send_to_news_api(self, announcement):
        """Send announcement to news API."""
        try:
            headers = {
                'Authorization': 'Bearer admin',
                'Content-Type': 'application/json'
            }

            data = {
                'content': announcement
            }

            # Add dev flag when connecting to localhost
            if self.server == "127.0.0.1":
                data['dev'] = True

            response = requests.post(
                'https://sl.eu.ngrok.io/api/create_news',
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                print("✅ News API: Announcement sent successfully")
            else:
                print(f"⚠️ News API: HTTP {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ News API Error: {e}")

    def rgb_to_color_name(self, r, g, b):
        """Convert RGB values (0-255) to human-readable color names"""

        # Define color ranges for common colors
        colors = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'pink': (255, 192, 203),
            'brown': (165, 42, 42),
            'gray': (128, 128, 128),
            'white': (255, 255, 255),
            'black': (0, 0, 0)
        }

        # Calculate distance to each color
        min_distance = float('inf')
        closest_color = 'unknown'

        for color_name, (cr, cg, cb) in colors.items():
            # Euclidean distance in RGB space
            distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name

        # Add intensity modifiers
        brightness = (r + g + b) / 3
        saturation = max(r, g, b) - min(r, g, b)

        # Determine intensity modifiers
        intensity = ""
        if brightness < 85:
            intensity = "dark "
        elif brightness > 170:
            intensity = "light "

        # Check for low saturation (grayish colors)
        if saturation < 50 and closest_color not in ['gray', 'white', 'black']:
            if brightness < 85:
                return "dark gray"
            elif brightness > 170:
                return "light gray"
            else:
                return "gray"

        return intensity + closest_color

    def save_startup_data(self):
        """Save main base locations and oil deposits at game start"""
        if self.startup_data_saved:
            return

        all_entities = uw_world.entities()

        # Find main base positions for each force
        for entity in all_entities.values():
            if entity.Proto is None or entity.Owner is None:
                continue

            proto_name = entity.proto().name if entity.proto() else ""

            # Look for main base entities (control cores)
            if "core" in proto_name.lower() and "control" in proto_name.lower():
                force_id = entity.Owner.force
                if force_id != 0 and entity.Position:
                    self.main_base_positions[force_id] = entity.Position.position
                    print(f"Saved main base for Force {force_id} at position {entity.Position.position}")

        # Find oil deposit positions
        # Resource clusters contain: 2 metals, 1 oil, 1 aether per cluster
        for entity in all_entities.values():
            if entity.Proto is None or entity.Owner is not None:
                continue

            proto_name = entity.proto().name if entity.proto() else ""

            # Look for oil deposits
            if "oil" in proto_name.lower() and entity.Position:
                self.oil_deposit_positions.append(entity.Position.position)
                print(f"Saved oil deposit '{proto_name}' at position {entity.Position.position}")

        self.startup_data_saved = True
        print(f"Startup data saved: {len(self.main_base_positions)} main bases, {len(self.oil_deposit_positions)} oil deposits")
        # TODO: write to file here

    def get_brief_status(self):
        """Generate a brief status update"""
        current_tick = uw_game.game_tick()
        game_time_minutes = current_tick / 1200

        all_entities = uw_world.entities()

        # Count entities by force (observer perspective)
        force_counts = {}
        neutral_count = 0

        for entity in all_entities.values():
            if entity.Proto is None:
                continue

            if entity.Owner and entity.Owner.force != 0:
                force_id = entity.Owner.force
                if force_id not in force_counts:
                    force_counts[force_id] = 0
                force_counts[force_id] += 1
            else:
                neutral_count += 1

        # Format force counts
        force_summary = []
        for force_id, count in sorted(force_counts.items()):
            force_summary.append(f"Force{force_id}={count}")

        if neutral_count > 0:
            force_summary.append(f"Neutral={neutral_count}")

        entities_str = ", ".join(force_summary) if force_summary else "No entities"
        return f"[{game_time_minutes:.1f}min] Entities: {entities_str}"

    def on_update(self, stepping: bool):
        # Configure during session state
        if uw_game.game_state() == GameState.Session:
            self.configure()
            return

        if not stepping:
            return

        # Check for game state changes (start/end) on every update
        self.check_game_state_changes()

        # Only observe every 500 ticks to reduce frequency
        self.work_step += 1

        if self.work_step % 200 != 0:
            return

        current_tick = uw_game.game_tick()

        # Log setup info once when prototypes are loaded
        if not self.setup_done and len(uw_prototypes._all) > 0:
            self.setup_done = True
            print(f"Observer bot initialized - {len(uw_prototypes._all)} prototypes loaded")

            # Log map info
            if uw_game.map_state() == MapState.Loaded:
                print(f"Observing map: name='{uw_map._name}', path='{uw_map._path}'")
            else:
                print(f"Map not loaded yet, state: {uw_game.map_state()}")

            # Reset game state for new session (prevents mixing contexts between games)
            self.reset_game_state()

            # Save startup data (main bases and oil deposits)
            self.save_startup_data()

            # Force a full report on first observation
            self.last_full_report = current_tick - 2000



        # Full detailed report every 250 ticks (12.5 seconds)
        if self.work_step % 250 == 0:
            detailed_report = self.get_game_overview()
            print(detailed_report)

            # Process with AI Yapper for announcements
            self.process_with_ai_yapper(detailed_report)

    def run(self):
        uw_game.log_info("Observer bot start")

        if not uw_game.try_reconnect():
            # Check if we should connect via lobby_id or direct connection
            if self.server == "lobby_id":
                # Use port parameter as lobby_id
                lobby_id = int(self.port)
                uw_game.log_info(f"Connecting to lobby_id {lobby_id}")
                uw_game.connect_lobby_id(lobby_id)
            else:
                # Connect to specific server and port if provided
                uw_game.log_info(f"Connecting to server {self.server}:{self.port}")
                # Connect as observer to the specified server - using connect_direct
                uw_game.connect_direct(self.server, self.port)

        uw_game.log_info("Observer bot done")

    def on_force_eliminated(self, force_id: int):
        """Track when a force is eliminated"""
        self.eliminated_forces.add(force_id)
        print(f"[ELIMINATION] Force {force_id} has been eliminated!")