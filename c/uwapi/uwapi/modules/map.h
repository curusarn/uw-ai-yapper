#ifndef unnatural_uwapi_map_h_mnawtg145ft
#define unnatural_uwapi_map_h_mnawtg145ft

#include "common.h"

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef UNNATURAL_BOTS

	typedef enum UwMapStateEnum
	{
		UwMapStateEnum_None = 0,
		UwMapStateEnum_Downloading = 1,
		UwMapStateEnum_Loading = 2,
		UwMapStateEnum_Loaded = 3,
		UwMapStateEnum_Unloading = 4,
		UwMapStateEnum_Error = 5,
	} UwMapStateEnum;
	typedef void (*UwMapStateCallbackType)(UwMapStateEnum state);
	UNNATURAL_API void uwSetMapStateCallback(UwMapStateCallbackType callback);
	UNNATURAL_API UwMapStateEnum uwMapState(void);

#endif

	// map

	typedef struct UwMapInfo
	{
		UNNATURAL_POINTER(const char *) name;
		UNNATURAL_POINTER(const char *) guid;
		UNNATURAL_POINTER(const char *) path;
		uint32 maxPlayers;
	} UwMapInfo;
	UNNATURAL_API bool uwMapInfo(UwMapInfo *data);

	typedef struct UwMapStartingPosition
	{
		uint32 position;
		uint32 minForces;
		uint32 maxForces;
	} UwMapStartingPosition;
	typedef struct UwMapStartingPositionsArray
	{
		UNNATURAL_POINTER(const UwMapStartingPosition *) data;
		uint32 count;
	} UwMapStartingPositionsArray;
	UNNATURAL_API void uwMapStartingPositions(UwMapStartingPositionsArray *data);

	// tiles

	UNNATURAL_API uint32 uwTilesCount(void);
	typedef struct UwTile
	{
		float position[3];
		float up[3];
		UNNATURAL_POINTER(const uint32 *) neighborsIndices;
		uint32 neighborsCount;
		uint32 clusterIndex;
		uint8 terrain;
		bool border;
	} UwTile;
	UNNATURAL_API void uwTile(uint32 index, UwTile *data);

	// clusters

	UNNATURAL_API uint32 uwClustersCount(void);
	typedef struct UwCluster
	{
		UNNATURAL_POINTER(const uint32 *) neighborsIndices;
		uint32 neighborsCount;
		uint32 centerTileIndex;
	} UwCluster;
	UNNATURAL_API void uwCluster(uint32 index, UwCluster *data);

	// map miscellaneous

	UNNATURAL_API void uwAreaRange(float x, float y, float z, float radius, UwIds *data);
	UNNATURAL_API void uwAreaConnected(uint32 position, float radius, UwIds *data);
	UNNATURAL_API void uwAreaNeighborhood(uint32 position, float radius, UwIds *data);
	UNNATURAL_API void uwAreaExtended(uint32 position, float radius, UwIds *data);

	UNNATURAL_API bool uwTestVisible(float x1, float y1, float z1, float x2, float y2, float z2);
	UNNATURAL_API bool uwTestShooting(uint32 shooterPosition, uint32 shooterProto, float shootingRangeUpgrade, uint32 targetPosition, uint32 targetProto);
	UNNATURAL_API float uwDistanceLine(float x1, float y1, float z1, float x2, float y2, float z2);
	UNNATURAL_API float uwDistanceEstimate(uint32 positionA, uint32 positionB);
	UNNATURAL_API float uwYaw(uint32 startPosition, uint32 goalPosition);

	// clusters distances

	typedef struct UwClustersDistancesQuery
	{
		uint64 taskUserData;
		uint32 startingCluster;
		uint32 unitPrototype;
		bool allowImpassableTerrain;
	} UwClustersDistancesQuery;
	typedef struct UwClustersDistancesResult
	{
		UwIds distances;
	} UwClustersDistancesResult;
	UNNATURAL_API void uwStartClustersDistances(const UwClustersDistancesQuery *query);
	UNNATURAL_API void uwRetrieveClustersDistances(UwClustersDistancesResult *data);

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_map_h_mnawtg145ft
