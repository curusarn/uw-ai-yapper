from .interop import *


class Admin:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_lobby_id(self) -> int:
        return uw_interop.uwGetLobbyId()

    def get_user_id(self) -> int:
        return uw_interop.uwGetUserId()

    def get_server_port(self) -> int:
        return uw_interop.uwGetServerPort()

    def set_map_selection(self, path: str) -> None:
        uw_interop.uwAdminSetMapSelection(path)

    def start_game(self) -> None:
        uw_interop.uwAdminStartGame()

    def terminate_game(self) -> None:
        uw_interop.uwAdminTerminateGame()

    def add_ai(self, intendedRace: int = 0, difficulty: float = 0) -> None:
        uw_interop.uwAdminAddAi(intendedRace, difficulty)

    def kick_player(self, player_id: int) -> None:
        uw_interop.uwAdminKickPlayer(player_id)

    def player_set_admin(self, player_id: int, admin: bool) -> None:
        uw_interop.uwAdminPlayerSetAdmin(player_id, admin)

    def player_set_name(self, player_id: int, name: str) -> None:
        uw_interop.uwAdminPlayerSetName(player_id, name)

    def player_join_force(self, player_id: int, force_id: int) -> None:
        uw_interop.uwAdminPlayerJoinForce(player_id, force_id)

    def force_join_team(self, force_id: int, team: int) -> None:
        uw_interop.uwAdminForceJoinTeam(force_id, team)

    def force_set_color(self, force_id: int, r: float, g: float, b: float) -> None:
        uw_interop.uwAdminForceSetColor(force_id, r, g, b)

    def force_set_race(self, force_id: int, race_proto: int) -> None:
        uw_interop.uwAdminForceSetRace(force_id, race_proto)

    def send_suggested_camera_focus(self, position: int) -> None:
        uw_interop.uwAdminSendSuggestedCameraFocus(position)

    def set_automatic_suggested_camera_focus(self, enabled: bool) -> None:
        uw_interop.uwAdminSetAutomaticSuggestedCameraFocus(enabled)

    def send_chat_message_to_player(self, msg: str, id: int) -> None:
        uw_interop.uwAdminSendChatMessageToPlayer(msg, id)

    def send_chat_message_to_everyone(self, msg: str) -> None:
        uw_interop.uwAdminSendChatMessageToEveryone(msg)

    def send_chat_command(self, msg: str) -> None:
        uw_interop.uwAdminSendChatCommand(msg)

    def send_ping(self, position: int, ping, id: int) -> None:
        uw_interop.uwAdminSendPing(position, ping, id)


uw_admin = Admin()
