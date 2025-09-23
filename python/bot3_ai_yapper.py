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

        uw_game.set_player_name("observer-bot")
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

        # Categorize entities
        force_entities = {}  # force_id -> {type -> count}
        neutral_entities = {}  # type -> count
        resource_deposits = []

        for entity in all_entities.values():
            if entity.Proto is None:
                continue

            proto_name = entity.proto().name if entity.proto() else "Unknown"

            # Track by ownership
            if entity.own():
                force_id = uw_world.my_force_id()
                if force_id not in force_entities:
                    force_entities[force_id] = {}
                if proto_name not in force_entities[force_id]:
                    force_entities[force_id][proto_name] = 0
                force_entities[force_id][proto_name] += 1
            elif entity.enemy():
                # Get enemy force ID if possible
                # For simplicity, group all enemies under "Enemy"
                enemy_key = "Enemy"
                if enemy_key not in force_entities:
                    force_entities[enemy_key] = {}
                if proto_name not in force_entities[enemy_key]:
                    force_entities[enemy_key][proto_name] = 0
                force_entities[enemy_key][proto_name] += 1
            else:
                # Neutral entity
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
            report.append(f"  {force_key}:")

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

        # Report force statistics if available
        try:
            if uw_world.my_force_id() != 0:  # We have a force
                stats = uw_world.my_force_statistics()
                if stats:
                    report.append("\nMY FORCE STATISTICS:")
                    report.append(f"  Combat Units: {stats.combatUnitsTotal} (Idle: {stats.combatUnitsIdle})")
                    report.append(f"  Logistics Units: {stats.logisticsUnitsTotal} (Idle: {stats.logisticsUnitsIdle})")
                    report.append(f"  Worker Units: {stats.workerUnitsTotal} (Idle: {stats.workerUnitsIdle})")
        except:
            # Observer might not have force statistics
            pass

        report.append("=" * 60)

        return "\n".join(report)

    def get_brief_status(self):
        """Generate a brief status update"""
        current_tick = uw_game.game_tick()
        game_time_minutes = current_tick / 1200

        all_entities = uw_world.entities()

        # Count forces
        my_units = 0
        enemy_units = 0
        neutral_units = 0

        for entity in all_entities.values():
            if entity.Proto is None:
                continue

            if entity.own():
                my_units += 1
            elif entity.enemy():
                enemy_units += 1
            else:
                neutral_units += 1

        return f"[{game_time_minutes:.1f}min] Entities: My={my_units}, Enemy={enemy_units}, Neutral={neutral_units}"

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
            uw_game.log_info(f"Observer bot initialized - {len(uw_prototypes._all)} prototypes loaded")

            # Log map info
            if uw_game.map_state() == MapState.Loaded:
                uw_game.log_info(f"Observing map: name='{uw_map._name}', path='{uw_map._path}'")
            else:
                uw_game.log_info(f"Map not loaded yet, state: {uw_game.map_state()}")

            # Force a full report on first observation
            self.last_full_report = current_tick - 2000

        # Brief status every 100 ticks (5 seconds)
        if self.work_step % 100 == 0:
            brief_status = self.get_brief_status()
            uw_game.log_info(brief_status)

        # Full detailed report every 2000 ticks (100 seconds / ~1.7 minutes)
        if current_tick - self.last_full_report >= 2000:
            self.last_full_report = current_tick

            detailed_report = self.get_game_overview()
            uw_game.log_info(detailed_report)

    def run(self):
        uw_game.log_info("Observer bot starting")

        # Connect to specific server and port if provided
        if self.server and self.port:
            uw_game.log_info(f"Connecting to server {self.server}:{self.port}")
            # Connect as observer to the specified server
            uw_game.set_connect_start_gui(True, "--observer 2")
            if not uw_game.connect_server(self.server, self.port):
                uw_game.log_error(f"Failed to connect to server {self.server}:{self.port}")
                return False
        else:
            # Try to reconnect first, then fallback to environment
            if not uw_game.try_reconnect():
                # Enable observer mode
                uw_game.set_connect_start_gui(True, "--observer 2")
                if not uw_game.connect_environment():
                    uw_game.log_error("Failed to connect to any server")
                    return False

        uw_game.log_info("Observer bot connected successfully")
        return True


def main():
    """Main entry point that can accept server and port arguments"""
    server = None
    port = None

    # Parse command line arguments
    if len(sys.argv) >= 3:
        server = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            uw_game.log_error(f"Invalid port number: {sys.argv[2]}")
            return
    elif len(sys.argv) >= 2:
        uw_game.log_error("Usage: python bot3_ai_yapper.py [server] [port]")
        return

    # Create and run the observer bot
    bot = ObserverBot(server, port)
    success = bot.run()

    if success:
        uw_game.log_info("Observer bot finished")
    else:
        uw_game.log_error("Observer bot failed to start")


if __name__ == "__main__":
    main()