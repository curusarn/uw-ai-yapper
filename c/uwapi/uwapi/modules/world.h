#ifndef unnatural_uwapi_worlds_h_dcfgh41dr5fsdtg
#define unnatural_uwapi_worlds_h_dcfgh41dr5fsdtg

#include "common.h"

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef UNNATURAL_BOTS
	typedef struct UwMyForceStatistics
	{
		uint32 logisticsUnitsIdle;
		uint32 logisticsUnitsTotal;
		uint32 militaryUnitsIdle;
		uint32 militaryUnitsTotal;
		uint32 closestDangerPosition;
		float closestDangerDistance;
	} UwMyForceStatistics;
	UNNATURAL_API void uwMyForceStatistics(UwMyForceStatistics *data);

	UNNATURAL_API UwPathStateEnum uwUnitPathState(uint32 unitId);
#endif

	typedef struct UwUnitUpgrades
	{
		float damage;
		float shootingRange;
		float splashRadius;
		float defense;
		float regenSpeed;
		float movementSpeed;
		float processingSpeed;
	} UwUnitUpgrades;
	UNNATURAL_API void uwUnitUpgrades(uint32 unit, UwUnitUpgrades *data);

	UNNATURAL_API bool uwTestShootingEntities(uint32 shooterId, uint32 targetId);

#ifdef UNNATURAL_BOTS
	UNNATURAL_API bool uwTestConstructionPlacement(uint32 constructionProto, uint32 position, uint32 recipeProto); // recipeProto may be 0
	UNNATURAL_API uint32 uwFindConstructionPlacement(uint32 constructionProto, uint32 position, uint32 recipeProto); // recipeProto may be 0
#endif

#ifdef UNNATURAL_SCRIPTS
	UNNATURAL_API bool uwTestPlacement(uint32 proto, uint32 position, uint32 owner);
	UNNATURAL_API uint32 uwFindPlacement(uint32 proto, uint32 position, uint32 owner);
	UNNATURAL_API bool uwTestConstructionPlacement(uint32 constructionProto, uint32 position, uint32 owner, uint32 recipeProto); // recipeProto may be 0
	UNNATURAL_API uint32 uwFindConstructionPlacement(uint32 constructionProto, uint32 position, uint32 owner, uint32 recipeProto); // recipeProto may be 0
#endif

#ifdef UNNATURAL_BOTS
	UNNATURAL_API void uwOfferForeignPolicy(uint32 forceId, UwForeignPolicyEnum policy);
#endif

	// overview

	typedef enum UwOverviewFlags
	{
		UwOverviewFlags_None = 0,
		UwOverviewFlags_Resource = 1 << 0,
		UwOverviewFlags_Construction = 1 << 1,
		UwOverviewFlags_MobileUnit = 1 << 2,
		UwOverviewFlags_StaticUnit = 1 << 3,
		UwOverviewFlags_Unit = UwOverviewFlags_MobileUnit | UwOverviewFlags_StaticUnit,
	} UwOverviewFlags;
	UNNATURAL_API UwOverviewFlags uwOverviewFlags(uint32 position);
	UNNATURAL_API void uwOverviewIds(uint32 position, UwIds *data);
	typedef struct UwOverviewExtract
	{
		UNNATURAL_POINTER(const UwOverviewFlags *) flags;
		uint32 count;
	} UwOverviewExtract;
	UNNATURAL_API void uwOverviewExtract(UwOverviewExtract *data);

	// unit pathfinding

	typedef struct UwUnitPathfindingQuery
	{
		uint64 taskUserData;
		uint32 startingPosition;
		uint32 goalPosition;
		uint32 unitPrototype;
		uint32 maxIterations;
		bool allowNearbyPosition;
	} UwUnitPathfindingQuery;
	typedef struct UwUnitPathfindingResult
	{
		UwIds path;
		UwPathStateEnum state;
	} UwUnitPathfindingResult;
	UNNATURAL_API void uwStartUnitPathfinding(const UwUnitPathfindingQuery *query);
	UNNATURAL_API void uwRetrieveUnitPathfinding(UwUnitPathfindingResult *data);

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_worlds_h_dcfgh41dr5fsdtg
