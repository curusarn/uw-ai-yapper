#ifndef unnatural_uwapi_scriptsServer_h_w4e5rhbsds
#define unnatural_uwapi_scriptsServer_h_w4e5rhbsds

#include "common.h"

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef UNNATURAL_SCRIPTS

	UNNATURAL_API uint32 uwCreateEntity(uint32 proto, uint32 position, uint32 owner);
	UNNATURAL_API void uwDestroyEntity(uint32 entity);

	UNNATURAL_API uint32 uwChangeOwner(uint32 entity, uint32 owner);

	UNNATURAL_API void uwSetPositionYaw(uint32 entity, uint32 position, float yaw);
	UNNATURAL_API void uwSetPosition(uint32 entity, uint32 position);
	UNNATURAL_API void uwSetYaw(uint32 entity, float yaw);
	UNNATURAL_API void uwMove(uint32 entity, uint32 position); // neighbor only
	UNNATURAL_API void uwMoveYaw(uint32 entity, uint32 position, float yaw); // neighbor only
	UNNATURAL_API void uwMoveTowards(uint32 entity, uint32 position); // performs serves-side pathfinding - use with care

	UNNATURAL_API void uwSetLife(uint32 entity, uint32 life);
	UNNATURAL_API void uwSetMana(uint32 entity, uint32 mana);
	UNNATURAL_API void uwSetAim(uint32 entity, uint32 target); // target = 0 to remove
	UNNATURAL_API void uwSetRecipe(uint32 entity, uint32 recipe); // recipe = 0 to remove
	UNNATURAL_API void uwSetPriority(uint32 entity, UwPriorityEnum priority);
	UNNATURAL_API void uwSetShootingCooldown(uint32 entity, uint32 ticks); // ticks = 0 to remove cooldown
	UNNATURAL_API void uwSetRegenCooldown(uint32 entity, uint32 ticks); // ticks = 0 to remove cooldown
	UNNATURAL_API void uwSetProcessingCooldown(uint32 entity, uint32 ticks); // ticks = 0 to remove cooldown
	UNNATURAL_API void uwSetDecay(uint32 entity, uint32 ticks); // ticks = -1 to remove decay

	UNNATURAL_API void uwSetAmount(uint32 entity, uint32 amount);
	UNNATURAL_API void uwSetAttached(uint32 entity, uint32 target); // target = 0 to detach

	UNNATURAL_API uint32 uwCreateForce(void);
	UNNATURAL_API void uwDestroyForce(uint32 force);
	UNNATURAL_API void uwSetForceColor(uint32 force, float r, float g, float b);
	UNNATURAL_API void uwSetForceFinish(uint32 force, bool winner, bool defeated);
	UNNATURAL_API void uwSetForceStartingTeam(uint32 force, uint32 team);
	UNNATURAL_API void uwSetForceStartingPosition(uint32 force, uint32 position);
	UNNATURAL_API void uwSetForeignPolicy(uint32 force1, uint32 force2, UwForeignPolicyEnum policy);

	UNNATURAL_API uint32 uwCreateAiPlayer(void);
	UNNATURAL_API void uwSetPlayerAiConfig(uint32 player, const UwPlayerAiConfigComponent *config);
	UNNATURAL_API void uwSetPlayerForce(uint32 player, uint32 force);
	UNNATURAL_API void uwPlayerCamera(uint32 player, uint32 tileIndex, bool resetToDefaultZoomAndOrientation, float duration, float smooth); // use -1 to send to all players, use NaN for default values
	UNNATURAL_API void uwPlayerCameraPosition(uint32 player, uint32 tileIndex, float yaw, float pitch, float eyeDistance, float duration, float smooth); // use -1 to send to all players, use NaN for default values
	UNNATURAL_API void uwPlayerCameraTransform(uint32 player, const float targetPosition[3], const float eyePosition[3], const float eyeUp[3], float duration, float smooth); // use -1 to send to all players, use NaN for default values
	UNNATURAL_API void uwPlayerDialogue(uint32 player, uint32 avatarId, uint32 voicelineId, uint32 translatedTextId); // use -1 to send to all players, use 0 for no avatar/voice/text

	UNNATURAL_API void uwCutsceneBegin(void);
	UNNATURAL_API void uwCutsceneEnd(void);
	UNNATURAL_API void uwCutsceneGameSimulation(bool runGameSimulation);
	UNNATURAL_API float uwCutsceneTime(void); // seconds since start of the cutscene
	UNNATURAL_ENTRY void uwCutsceneSkipCallback(void);

	UNNATURAL_API void uwStandardVictoryConditions(bool enable);
	UNNATURAL_API void uwSendChat(const char *msg, UwChatTargetFlags flags, uint32 targetId);
	UNNATURAL_API void uwSendPing(uint32 position, UwPingEnum ping, uint32 targetForce);

	UNNATURAL_API void uwPrint(const char *msg);
	UNNATURAL_API uint32 uwRand(void);

#endif

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_scriptsServer_h_w4e5rhbsds
