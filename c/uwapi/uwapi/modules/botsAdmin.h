#ifndef unnatural_uwapi_admin_h_kjh7r8se
#define unnatural_uwapi_admin_h_kjh7r8se

#include "common.h"

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef UNNATURAL_BOTS

	typedef struct UwGameConfig UwGameConfig;
	typedef struct UwPlayerAiConfigComponent UwPlayerAiConfigComponent;

	UNNATURAL_API uint64 uwGetLobbyId(void);
	UNNATURAL_API uint64 uwGetUserId(void);
	UNNATURAL_API uint16 uwGetServerPort(void);
	UNNATURAL_API void uwAdminSetMapSelection(const char *path);
	UNNATURAL_API void uwAdminSetGameConfig(const UwGameConfig *config);
	UNNATURAL_API void uwAdminStartGame(void);
	UNNATURAL_API void uwAdminTerminateGame(void);
	UNNATURAL_API void uwAdminPauseGame(bool pause);
	UNNATURAL_API void uwAdminSkipCutscene(void);
	UNNATURAL_API void uwAdminAddAi(uint32 intendedRace, float difficulty);
	UNNATURAL_API void uwAdminKickPlayer(uint32 playerId);
	UNNATURAL_API void uwAdminPlayerSetAdmin(uint32 playerId, bool admin);
	UNNATURAL_API void uwAdminPlayerSetName(uint32 playerId, const char *name);
	UNNATURAL_API void uwAdminPlayerAiConfig(uint32 playerId, const UwPlayerAiConfigComponent *config);
	UNNATURAL_API void uwAdminPlayerJoinForce(uint32 playerId, uint32 forceId);
	UNNATURAL_API void uwAdminForceJoinTeam(uint32 forceId, uint32 team);
	UNNATURAL_API void uwAdminForceSetColor(uint32 forceId, float r, float g, float b);
	UNNATURAL_API void uwAdminForceSetRace(uint32 forceId, uint32 raceProto);
	UNNATURAL_API void uwAdminSendSuggestedCameraFocus(uint32 position);
	UNNATURAL_API void uwAdminSetAutomaticSuggestedCameraFocus(bool enabled);
	UNNATURAL_API void uwAdminSendChatMessageToPlayer(const char *msg, uint32 playerId);
	UNNATURAL_API void uwAdminSendChatMessageToEveryone(const char *msg);
	UNNATURAL_API void uwAdminSendChatCommand(const char *msg);
	UNNATURAL_API void uwAdminSendPing(uint32 position, UwPingEnum ping, uint32 targetForce);

#endif

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_admin_h_kjh7r8se
