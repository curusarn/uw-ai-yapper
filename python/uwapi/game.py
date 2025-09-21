from .interop import *


class Game:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def log_info(self, msg: str):
        uw_interop.uwLog(UwSeverityEnum.Info, msg)

    def log_warning(self, msg: str):
        uw_interop.uwLog(UwSeverityEnum.Warning, msg)

    def log_error(self, msg: str):
        uw_interop.uwLog(UwSeverityEnum.Error, msg)

    def set_player_name(self, name: str) -> None:
        uw_interop.uwSetPlayerName(name)

    def player_join_force(self, force_id: int) -> None:
        uw_interop.uwPlayerJoinForce(force_id)

    def set_force_color(self, r: float, g: float, b: float) -> None:
        uw_interop.uwSetForceColor(r, g, b)

    def set_force_race(self, race_proto: int) -> None:
        uw_interop.uwSetForceRace(race_proto)

    def force_join_team(self, team: int) -> None:
        uw_interop.uwForceJoinTeam(team)

    def skip_cutscene(self) -> None:
        uw_interop.uwSkipCutscene()

    def set_connect_start_gui(
        self, start_gui: bool, extra_params: str = "--observer 1"
    ) -> None:
        uw_interop.uwSetConnectStartGui(start_gui, extra_params)

    def connect_find_lan(self, timeout_microseconds: int = 1000000) -> bool:
        return uw_interop.uwConnectFindLan(timeout_microseconds)

    def connect_direct(self, address: str, port: int) -> None:
        uw_interop.uwConnectDirect(address, port)

    def connect_lobby_id(self, lobby_id: int) -> None:
        uw_interop.uwConnectLobbyId(lobby_id)

    def connect_environment(self) -> bool:
        return uw_interop.uwConnectEnvironment()

    def connect_new_server(
        self, visibility: int = 0, name: str = "", extra_params: str = ""
    ) -> None:
        uw_interop.uwConnectNewServer(visibility, name, extra_params)

    def try_reconnect(self) -> bool:
        return uw_interop.uwTryReconnect()

    def disconnect(self) -> None:
        uw_interop.uwDisconnect()

    def connection_state(self) -> UwConnectionStateEnum:
        return uw_interop.uwConnectionState()

    def game_state(self) -> UwGameStateEnum:
        return uw_interop.uwGameState()

    def game_tick(self) -> int:
        return uw_interop.uwGameTick()

    def map_state(self) -> UwMapStateEnum:
        return uw_interop.uwMapState()

    def performance_statistics(self) -> UwPerformanceStatistics:
        return uw_interop.uwPerformanceStatistics()

    def performance_profiling(self, enable: bool) -> None:
        uw_interop.uwPerformanceProfiling(enable)

    def profiling_event_begin(self) -> int:
        return uw_interop.uwProfilingEventBegin()

    def profiling_event_end(self, name: str, event_start_time: int) -> None:
        uw_interop.uwProfilingEventEnd(name, event_start_time)


uw_game = Game()
