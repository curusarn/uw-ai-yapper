import random
import sys
from uwapi import *


class ObserverBot:
    """Observer bot that connects as observer and reports game state without controlling units"""

    is_configured: bool = False
    work_step: int = 0

    # Track if we've done initial setup
    setup_done: bool = False

    # Track last report time to avoid spam
    last_full_report: int = 0

    def __init__(self, server=None, port=None):
        self.server = server
        self.port = port
        uw_events.on_update(self.on_update)

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

    def get_game_overview(self):
        """Generate a comprehensive game state report"""

        current_tick = uw_game.game_tick()
        game_time_minutes = current_tick / 1200  # 20 ticks per second, 60 seconds per minute

        report = []
        report.append("=" * 60)
        report.append(f"GAME STATE REPORT - Tick {current_tick} ({game_time_minutes:.1f} minutes)")
        report.append("=" * 60)

        # Basic game info
        report.append(f"Game State: {uw_game.game_state()}")
        report.append(f"Map State: {uw_game.map_state()}")
        if uw_game.map_state() == MapState.Loaded:
            report.append(f"Map: {uw_map._name} ({uw_map._path})")

        # Count entities by type and owner
        all_entities = uw_world.entities()
        report.append(f"Total Entities: {len(all_entities)}")

        # Categorize entities by force ID and player
        force_entities = {}  # force_id -> {type -> count}
        neutral_entities = {}  # type -> count
        resource_deposits = []
        force_info = {}  # force_id -> {player_name, steam_id, color}

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
                            'progress': player.progress
                        }

            # Check for force entities to get color
            if entity.Force:
                force = entity.Force
                # Force entities don't have a force ID directly, need to get it from the entity ID
                # For now, we'll update color info if we can match it
                if hasattr(entity, 'id'):
                    # Try to match this force entity with existing force info
                    for fid in force_info.keys():
                        if force_info[fid]['color'] is None:
                            force_info[fid]['color'] = force.color
                            break

        # Second pass: categorize other entities
        for entity in all_entities.values():
            if entity.Proto is None:
                continue

            proto_name = entity.proto().name if entity.proto() else "Unknown"

            # Get force/owner info - observer doesn't have "own" or "enemy" concept
            if entity.Owner and entity.Owner.force != 0:
                # Entity belongs to a force
                force_id = entity.Owner.force
                if force_id not in force_entities:
                    force_entities[force_id] = {}
                if proto_name not in force_entities[force_id]:
                    force_entities[force_id][proto_name] = 0
                force_entities[force_id][proto_name] += 1
            else:
                # Neutral entity (no owner)
                if proto_name not in neutral_entities:
                    neutral_entities[proto_name] = 0
                neutral_entities[proto_name] += 1

                # Check if it's a resource deposit
                if "deposit" in proto_name.lower() or "ore" in proto_name.lower() or "oil" in proto_name.lower() or "aether" in proto_name.lower():
                    resource_deposits.append({
                        'name': proto_name,
                        'id': entity.id,
                        'pos': entity.pos() if entity.Position else None
                    })

        # Report forces
        report.append("\nFORCES:")
        for force_key, entities in force_entities.items():
            # Add player information if available
            if force_key in force_info:
                info = force_info[force_key]
                player_name = info['player_name']
                steam_id = info['steam_id']
                color = info['color']
                progress = info['progress']

                color_str = ""
                if color:
                    # Convert color to RGB values (0-255)
                    r, g, b = [int(c * 255) for c in color]
                    color_name = self.rgb_to_color_name(r, g, b)
                    color_str = f" ({color_name})"

                report.append(f"  Force {force_key}: {player_name} (Steam: {steam_id}){color_str}")
            else:
                report.append(f"  Force {force_key}:")

            # Separate buildings and units
            buildings = {}
            units = {}
            resources = {}

            for proto_name, count in entities.items():
                proto_lower = proto_name.lower()
                if any(keyword in proto_lower for keyword in ['drill', 'factory', 'refinery', 'laboratory', 'core', 'fabricator']):
                    buildings[proto_name] = count
                elif any(keyword in proto_lower for keyword in ['metal', 'oil', 'fuel', 'aether', 'biomass']):
                    resources[proto_name] = count
                else:
                    units[proto_name] = count

            if buildings:
                report.append("    Buildings:")
                for name, count in sorted(buildings.items()):
                    report.append(f"      {name}: {count}")

            if units:
                report.append("    Units:")
                for name, count in sorted(units.items()):
                    report.append(f"      {name}: {count}")

            if resources:
                report.append("    Resources:")
                for name, count in sorted(resources.items()):
                    report.append(f"      {name}: {count}")

        # Report neutral entities (including deposits)
        if neutral_entities:
            report.append("\nNEUTRAL ENTITIES:")
            for proto_name, count in sorted(neutral_entities.items()):
                report.append(f"  {proto_name}: {count}")

        # Report resource deposits with positions
        if resource_deposits:
            report.append("\nRESOURCE DEPOSITS:")
            for deposit in resource_deposits:
                pos_str = f" at {deposit['pos']}" if deposit['pos'] is not None else ""
                report.append(f"  {deposit['name']} (ID: {deposit['id']}){pos_str}")

        # Observer doesn't have force statistics - skip this section

        report.append("=" * 60)

        return "\n".join(report)

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

        # Only observe every 100 ticks to reduce frequency
        self.work_step += 1

        if self.work_step % 100 != 0:
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

            # Force a full report on first observation
            self.last_full_report = current_tick - 2000

        # Full detailed report every 100 ticks (5 seconds)
        if self.work_step % 100 == 0:
            detailed_report = self.get_game_overview()
            print(detailed_report)

    def run(self):
        uw_game.log_info("Observer bot start")

        if not uw_game.try_reconnect():
            # Connect to specific server and port if provided
            uw_game.log_info(f"Connecting to server {self.server}:{self.port}")
            # Connect as observer to the specified server - using connect_direct
            uw_game.connect_direct(self.server, self.port)

        uw_game.log_info("Observer bot done")