#ifndef unnatural_uwapi_game_h_we56rs4dcjq
#define unnatural_uwapi_game_h_we56rs4dcjq

#include "common.h"

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef UNNATURAL_BOTS

#endif

	// game config

	typedef struct UwGameConfig
	{
		bool ranked;
		bool diplomacy;
		bool lockedSpeed;
		bool cheats;
	} UwGameConfig;

	UNNATURAL_API void uwGameConfig(UwGameConfig *config);

	UNNATURAL_API void uwSetGameSpeed(float speed);
	UNNATURAL_API void uwSetWeatherSpeed(float speed, float offset);

	// game state

	typedef enum UwGameStateEnum
	{
		UwGameStateEnum_None = 0,
		UwGameStateEnum_Session = 1,
		UwGameStateEnum_Preparation = 2,
		UwGameStateEnum_Starting = 3,
		UwGameStateEnum_Game = 4,
		UwGameStateEnum_Pause = 5,
		UwGameStateEnum_CutscenePaused = 6,
		UwGameStateEnum_CutsceneRunning = 7,
		UwGameStateEnum_Finish = 8,
	} UwGameStateEnum;
#ifdef UNNATURAL_BOTS
	typedef void (*UwGameStateCallbackType)(UwGameStateEnum state);
	UNNATURAL_API void uwSetGameStateCallback(UwGameStateCallbackType callback);
#endif
#ifdef UNNATURAL_SCRIPTS
	UNNATURAL_ENTRY void uwGameStateCallback(UwGameStateEnum state);
#endif
	UNNATURAL_API UwGameStateEnum uwGameState(void);

	UNNATURAL_API uint32 uwGameTick(void);

	// update callback

#ifdef UNNATURAL_BOTS
	typedef void (*UwUpdateCallbackType)(bool stepping);
	UNNATURAL_API void uwSetUpdateCallback(UwUpdateCallbackType callback);
#endif
#ifdef UNNATURAL_SCRIPTS
	UNNATURAL_ENTRY void uwUpdateCallback(bool stepping);
#endif

	// shootings callback

	typedef enum UwShootingEventEnum
	{
		UwShootingEventEnum_None = 0,
		UwShootingEventEnum_Shooting = 1,
		UwShootingEventEnum_Death = 2,
		UwShootingEventEnum_Explosion = 3,
	} UwShootingEventEnum;
	typedef struct UwShootingsArray
	{
		UNNATURAL_POINTER(const uint32 *) data;
		uint32 count;
	} UwShootingsArray;
#ifdef UNNATURAL_BOTS
	typedef void (*UwShootingsCallbackType)(const UwShootingsArray *data);
	UNNATURAL_API void uwSetShootingsCallback(UwShootingsCallbackType callback);
#endif
#ifdef UNNATURAL_SCRIPTS
	UNNATURAL_ENTRY void uwShootingsCallback(const UwShootingsArray *data);
#endif

	// force eliminated callback

#ifdef UNNATURAL_BOTS
	typedef void (*UwForceEliminatedCallbackType)(uint32 id);
	UNNATURAL_API void uwSetForceEliminatedCallback(UwForceEliminatedCallbackType callback);
#endif
#ifdef UNNATURAL_SCRIPTS
	UNNATURAL_ENTRY void uwForceEliminatedCallback(uint32 id);
#endif

	// chat

#ifdef UNNATURAL_BOTS
	typedef void (*UwChatCallbackType)(uint32 sender, const char *message, UwChatTargetEnum target);
	UNNATURAL_API void uwSetChatCallback(UwChatCallbackType callback);
#endif
#ifdef UNNATURAL_SCRIPTS
	UNNATURAL_ENTRY void uwChatCallback(uint32 sender, const char *message, UwChatTargetEnum target);
#endif

	// tasks callback

	typedef enum UwTaskTypeEnum
	{
		UwTaskTypeEnum_None = 0,
		UwTaskTypeEnum_UnitPathfinding = 1,
		UwTaskTypeEnum_ClustersDistances = 2,
	} UwTaskTypeEnum;

#ifdef UNNATURAL_BOTS
	typedef void (*UwTaskCompletedCallbackType)(uint64 taskUserData, UwTaskTypeEnum type);
	UNNATURAL_API void uwSetTaskCompletedCallback(UwTaskCompletedCallbackType callback);
#endif
#ifdef UNNATURAL_SCRIPTS
	UNNATURAL_ENTRY void uwTaskCompletedCallback(uint64 taskUserData, UwTaskTypeEnum type);
#endif

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_game_h_we56rs4dcjq
