

typedef uint8_t uint8;
typedef int8_t sint8;
typedef uint16_t uint16;
typedef int16_t sint16;
typedef uint32_t uint32;
typedef int32_t sint32;
typedef uint64_t uint64;
typedef int64_t sint64;

static const uint32 UW_VERSION = 42;
static const uint32 UW_GameTicksPerSecond = 20;

typedef struct UwIds
{
	const uint32 *ids;
	uint32 count;
} UwIds;

typedef enum UwPriorityEnum
{
	UwPriorityEnum_Disabled = 0,
	UwPriorityEnum_Normal = 1,
	UwPriorityEnum_High = 2,
} UwPriorityEnum;

typedef enum UwPingEnum
{
	UwPingEnum_None = 0,
	UwPingEnum_Attention = 1,
	UwPingEnum_Attack = 2,
	UwPingEnum_Defend = 3,
	UwPingEnum_Rally = 4,
	UwPingEnum_Build = 5,
	UwPingEnum_Evacuate = 6,
} UwPingEnum;

typedef enum UwPathStateEnum
{
	UwPathStateEnum_None = 0,
	UwPathStateEnum_Searching = 1,
	UwPathStateEnum_Impossible = 2,
	UwPathStateEnum_NotFound = 3,
	UwPathStateEnum_Recompute = 4,
	UwPathStateEnum_Found = 5,
	UwPathStateEnum_Finished = 6,
} UwPathStateEnum;

typedef enum UwForeignPolicyEnum
{
	UwForeignPolicyEnum_None = 0,
	UwForeignPolicyEnum_Self = 1,
	UwForeignPolicyEnum_Ally = 2,
	UwForeignPolicyEnum_Neutral = 3,
	UwForeignPolicyEnum_Enemy = 4,
} UwForeignPolicyEnum;

typedef enum UwChatTargetFlags
{
	UwChatTargetFlags_None = 0,
	UwChatTargetFlags_Server = 1 << 0,
	UwChatTargetFlags_Direct = 1 << 1,
	UwChatTargetFlags_Self = 1 << 2,
	UwChatTargetFlags_Allies = 1 << 3,
	UwChatTargetFlags_Neutral = 1 << 4,
	UwChatTargetFlags_Enemy = 1 << 5,
	UwChatTargetFlags_Observer = 1 << 6,
	UwChatTargetFlags_Admin = 1 << 7,
	UwChatTargetFlags_Players = UwChatTargetFlags_Self | UwChatTargetFlags_Allies | UwChatTargetFlags_Neutral | UwChatTargetFlags_Enemy,
	UwChatTargetFlags_Everyone = UwChatTargetFlags_Players | UwChatTargetFlags_Observer | UwChatTargetFlags_Admin,
} UwChatTargetFlags;

typedef struct UwPlayerAiConfigComponent UwPlayerAiConfigComponent;

uint64 uwGetLobbyId(void);
uint64 uwGetUserId(void);
uint16 uwGetServerPort(void);
void uwAdminSetMapSelection(const char *path);
void uwAdminSetGameSpeed(float speed);
void uwAdminSetWeatherSpeed(float speed, float offset);
void uwAdminStartGame(void);
void uwAdminTerminateGame(void);
void uwAdminPauseGame(bool pause);
void uwAdminSkipCutscene(void);
void uwAdminAddAi(void);
void uwAdminKickPlayer(uint32 playerId);
void uwAdminPlayerSetAdmin(uint32 playerId, bool admin);
void uwAdminPlayerSetName(uint32 playerId, const char *name);
void uwAdminPlayerAiConfig(uint32 playerId, const UwPlayerAiConfigComponent *config);
void uwAdminPlayerJoinForce(uint32 playerId, uint32 forceId);
void uwAdminForceJoinTeam(uint32 forceId, uint32 team);
void uwAdminForceSetColor(uint32 forceId, float r, float g, float b);
void uwAdminForceSetRace(uint32 forceId, uint32 raceProto);
void uwAdminSendSuggestedCameraFocus(uint32 position);
void uwAdminSetAutomaticSuggestedCameraFocus(bool enabled);
void uwAdminSendChat(const char *msg, UwChatTargetFlags flags, uint32 targetId);
void uwAdminSendPing(uint32 position, UwPingEnum ping, uint32 targetForce);
void uwInitialize(uint32 version);
void uwDeinitialize(void);

typedef void (*UwExceptionCallbackType)(const char *message);
void uwSetExceptionCallback(UwExceptionCallbackType callback);

typedef enum UwSeverityEnum
{
	UwSeverityEnum_Note = 0,
	UwSeverityEnum_Hint = 1,
	UwSeverityEnum_Warning = 2,
	UwSeverityEnum_Info = 3,
	UwSeverityEnum_Error = 4,
	UwSeverityEnum_Critical = 5,
} UwSeverityEnum;
typedef struct UwLogCallback
{
	const char *message;
	const char *component;
	UwSeverityEnum severity;
} UwLogCallback;
typedef void (*UwLogCallbackType)(const UwLogCallback *data);
void uwSetLogCallback(UwLogCallbackType callback);
void uwInitializeConsoleLogger(void);
void uwLog(UwSeverityEnum severity, const char *message);

typedef enum UwConnectionStateEnum
{
	UwConnectionStateEnum_None = 0,
	UwConnectionStateEnum_Connecting = 1,
	UwConnectionStateEnum_Connected = 2,
	UwConnectionStateEnum_Error = 3,
} UwConnectionStateEnum;
typedef void (*UwConnectionStateCallbackType)(UwConnectionStateEnum state);
void uwSetConnectionStateCallback(UwConnectionStateCallbackType callback);
UwConnectionStateEnum uwConnectionState(void);

void uwSetConnectStartGui(bool enabled, const char *extraCmdParams);
bool uwConnectFindLan(uint64 timeoutMicroseconds);
void uwConnectDirect(const char *address, uint16 port);
void uwConnectLobbyId(uint64 lobbyId);
bool uwConnectEnvironment();
void uwConnectNewServer(uint32 visibility, const char *name, const char *extraCmdParams);
bool uwTryReconnect(void);
void uwDisconnect(void);

void uwSetPlayerName(const char *name);
void uwPlayerJoinForce(uint32 force);
void uwSetForceColor(float r, float g, float b);
void uwSetForceRace(uint32 raceProto);
void uwForceJoinTeam(uint32 team);
void uwSkipCutscene(void);

typedef struct UwMyPlayer
{
	uint32 playerEntityId;
	uint32 forceEntityId;
	bool primaryController;
	bool admin;
} UwMyPlayer;
bool uwMyPlayer(UwMyPlayer *data);

typedef struct UwAssistConfig
{
	bool logistics;
	bool aiming;
	bool fighting;
} UwAssistConfig;
void uwSetAssistConfig(const UwAssistConfig *config);

typedef struct UwPerformanceStatistics
{
	float gameSpeed;
	float mainThreadUtilization;
	float ping;
	uint32 networkUp;
	uint32 networkDown;
} UwPerformanceStatistics;
void uwPerformanceStatistics(UwPerformanceStatistics *data);

void uwPerformanceProfiling(bool enable);
uint64 uwProfilingEventBegin(void);
void uwProfilingEventEnd(const char *name, uint64 eventStartTime);
typedef enum UwOrderTypeEnum
{
	UwOrderTypeEnum_None = 0,
	UwOrderTypeEnum_Stop = 1,
	UwOrderTypeEnum_Guard = 2,
	UwOrderTypeEnum_Run = 3,
	UwOrderTypeEnum_Fight = 4,
	UwOrderTypeEnum_Load = 5,
	UwOrderTypeEnum_Unload = 6,
	UwOrderTypeEnum_SelfDestruct = 7,
} UwOrderTypeEnum;
typedef enum UwOrderPriorityFlags
{
	UwOrderPriorityFlags_None = 0,
	UwOrderPriorityFlags_Assistant = 1 << 0,
	UwOrderPriorityFlags_User = 1 << 1,
	UwOrderPriorityFlags_Enqueue = 1 << 2,
	UwOrderPriorityFlags_Repeat = 1 << 3,
} UwOrderPriorityFlags;
typedef struct UwOrder
{
	uint32 entity;
	uint32 position;
	UwOrderTypeEnum order;
	UwOrderPriorityFlags priority;
} UwOrder;
void uwOrder(uint32 unit, const UwOrder *data);
typedef struct UwOrders
{
	const UwOrder *orders;
	uint32 count;
} UwOrders;
void uwOrders(uint32 unit, UwOrders *data);

void uwCommandPlaceConstruction(uint32 constructionProto, uint32 position, float yaw, uint32 recipeProto, UwPriorityEnum priority);
void uwCommandSetRecipe(uint32 unitOrConstructionId, uint32 recipeProto);
void uwCommandSetPriority(uint32 unitOrConstructionId, UwPriorityEnum priority);
void uwCommandLoad(uint32 unitId, uint32 resourceProto);
void uwCommandUnload(uint32 unitId);
void uwCommandMove(uint32 unitId, uint32 position, float yaw);
void uwCommandAim(uint32 unitId, uint32 targetId);
void uwCommandRenounceControl(uint32 entityId);
void uwCommandSelfDestruct(uint32 entityId);
typedef struct UwEntity UwEntity;
typedef UwEntity *UwEntityPtr;
UwEntityPtr uwEntityPointer(uint32 id);
uint32 uwEntityId(UwEntityPtr entity);
void uwModifiedEntities(UwIds *data);

void uwAllEntities(UwIds *data);
bool uwEntityExists(uint32 id);

typedef struct UwProtoComponent
{
	uint32 proto;
} UwProtoComponent;
bool uwFetchProtoComponent(UwEntityPtr entity, UwProtoComponent *data);

typedef struct UwOwnerComponent
{
	uint32 force;
} UwOwnerComponent;
bool uwFetchOwnerComponent(UwEntityPtr entity, UwOwnerComponent *data);

typedef struct UwControllerComponent
{
	uint32 player;
	uint32 timestamp;
} UwControllerComponent;
bool uwFetchControllerComponent(UwEntityPtr entity, UwControllerComponent *data);

typedef struct UwPositionComponent
{
	uint32 position;
	float yaw;
} UwPositionComponent;
bool uwFetchPositionComponent(UwEntityPtr entity, UwPositionComponent *data);

typedef enum UwUnitStateFlags
{
	UwUnitStateFlags_None = 0,
	UwUnitStateFlags_Shooting = 1 << 0,
	UwUnitStateFlags_Processing = 1 << 1,
	UwUnitStateFlags_Rebuilding = 1 << 2,
	UwUnitStateFlags_Stalling = 1 << 3,
	UwUnitStateFlags_Damaged = 1 << 4,
} UwUnitStateFlags;
typedef struct UwUnitComponent
{
	UwUnitStateFlags state;
	uint32 killCount;
} UwUnitComponent;
bool uwFetchUnitComponent(UwEntityPtr entity, UwUnitComponent *data);

typedef struct UwLifeComponent
{
	sint32 life;
} UwLifeComponent;
bool uwFetchLifeComponent(UwEntityPtr entity, UwLifeComponent *data);

typedef struct UwManaComponent
{
	sint32 mana;
} UwManaComponent;
bool uwFetchManaComponent(UwEntityPtr entity, UwManaComponent *data);

typedef struct UwMoveComponent
{
	uint32 timestamp;
} UwMoveComponent;
bool uwFetchMoveComponent(UwEntityPtr entity, UwMoveComponent *data);

typedef struct UwAimComponent
{
	uint32 target;
} UwAimComponent;
bool uwFetchAimComponent(UwEntityPtr entity, UwAimComponent *data);

typedef struct UwRecipeComponent
{
	uint32 recipe;
} UwRecipeComponent;
bool uwFetchRecipeComponent(UwEntityPtr entity, UwRecipeComponent *data);

typedef struct UwRecipeStatisticsComponent
{
	uint32 timestamps[3];
	uint32 completed;
} UwRecipeStatisticsComponent;
bool uwFetchRecipeStatisticsComponent(UwEntityPtr entity, UwRecipeStatisticsComponent *data);

typedef struct UwLogisticsTimestampComponent
{
	uint32 timestamp;
} UwLogisticsTimestampComponent;
bool uwFetchLogisticsTimestampComponent(UwEntityPtr entity, UwLogisticsTimestampComponent *data);

typedef struct UwPriorityComponent
{
	UwPriorityEnum priority;
} UwPriorityComponent;
bool uwFetchPriorityComponent(UwEntityPtr entity, UwPriorityComponent *data);

typedef struct UwAmountComponent
{
	uint32 amount;
} UwAmountComponent;
bool uwFetchAmountComponent(UwEntityPtr entity, UwAmountComponent *data);

typedef struct UwAttachmentComponent
{
	uint32 target;
} UwAttachmentComponent;
bool uwFetchAttachmentComponent(UwEntityPtr entity, UwAttachmentComponent *data);

typedef struct UwPingComponent
{
	UwPingEnum ping;
} UwPingComponent;
bool uwFetchPingComponent(UwEntityPtr entity, UwPingComponent *data);

typedef enum UwPlayerStateFlags
{
	UwPlayerStateFlags_None = 0,
	UwPlayerStateFlags_Disconnected = 1 << 0,
	UwPlayerStateFlags_Admin = 1 << 1,
	UwPlayerStateFlags_Loaded = 1 << 2,
	UwPlayerStateFlags_Pause = 1 << 3,
	UwPlayerStateFlags_SkipCutscene = 1 << 4,
} UwPlayerStateFlags;
typedef enum UwPlayerConnectionClassEnum
{
	UwPlayerConnectionClassEnum_None = 0,
	UwPlayerConnectionClassEnum_Computer = 1,
	UwPlayerConnectionClassEnum_VirtualReality = 2,
	UwPlayerConnectionClassEnum_Robot = 3,
	UwPlayerConnectionClassEnum_UwApi = 4,
} UwPlayerConnectionClassEnum;
typedef struct UwPlayerComponent
{
	char name[28];
	uint32 nameLength;
	uint64 steamUserId;
	uint32 force;
	float progress;
	uint32 ping;
	UwPlayerStateFlags state;
	UwPlayerConnectionClassEnum playerConnectionClass;
} UwPlayerComponent;
bool uwFetchPlayerComponent(UwEntityPtr entity, UwPlayerComponent *data);

typedef struct UwPlayerAiConfigComponent
{
	float difficulty;
	float aggressive;
	float stretching;
	float expansive;
} UwPlayerAiConfigComponent;
bool uwFetchPlayerAiConfigComponent(UwEntityPtr entity, UwPlayerAiConfigComponent *data);

typedef enum UwForceStateFlags
{
	UwForceStateFlags_None = 0,
	UwForceStateFlags_Disconnected = 1 << 0,
	UwForceStateFlags_Winner = 1 << 1,
	UwForceStateFlags_Defeated = 1 << 2,
} UwForceStateFlags;
typedef struct UwForceComponent
{
	float color[3];
	uint64 score;
	uint32 killCount;
	uint32 lossCount;
	uint32 finishTimestamp;
	uint32 intendedTeam;
	uint32 intendedRace;
	UwForceStateFlags state;
} UwForceComponent;
bool uwFetchForceComponent(UwEntityPtr entity, UwForceComponent *data);

typedef struct UwForceDetailsComponent
{
	uint64 killValue;
	uint64 lossValue;
	uint32 startingPosition;
	uint32 race;
} UwForceDetailsComponent;
bool uwFetchForceDetailsComponent(UwEntityPtr entity, UwForceDetailsComponent *data);

typedef struct UwForeignPolicyComponent
{
	uint32 forces[2];
	UwForeignPolicyEnum policy;
} UwForeignPolicyComponent;
bool uwFetchForeignPolicyComponent(UwEntityPtr entity, UwForeignPolicyComponent *data);

typedef struct UwDiplomacyProposalComponent
{
	uint32 offeror;
	uint32 offeree;
	UwForeignPolicyEnum proposal;
} UwDiplomacyProposalComponent;
bool uwFetchDiplomacyProposalComponent(UwEntityPtr entity, UwDiplomacyProposalComponent *data);
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

typedef void (*UwGameStateCallbackType)(UwGameStateEnum state);
void uwSetGameStateCallback(UwGameStateCallbackType callback);

UwGameStateEnum uwGameState(void);

uint32 uwGameTick(void);

typedef void (*UwUpdateCallbackType)(bool stepping);
void uwSetUpdateCallback(UwUpdateCallbackType callback);

typedef enum UwShootingEventEnum
{
	UwShootingEventEnum_None = 0,
	UwShootingEventEnum_Shooting = 1,
	UwShootingEventEnum_Death = 2,
	UwShootingEventEnum_Explosion = 3,
} UwShootingEventEnum;
typedef struct UwShootingsArray
{
	const uint32 *data;
	uint32 count;
} UwShootingsArray;

typedef void (*UwShootingsCallbackType)(const UwShootingsArray *data);
void uwSetShootingsCallback(UwShootingsCallbackType callback);
typedef void (*UwForceEliminatedCallbackType)(uint32 id);
void uwSetForceEliminatedCallback(UwForceEliminatedCallbackType callback);
typedef void (*UwChatCallbackType)(const char *msg, uint32 sender, UwChatTargetFlags flags);
void uwSetChatCallback(UwChatCallbackType callback);

typedef enum UwTaskTypeEnum
{
	UwTaskTypeEnum_None = 0,
	UwTaskTypeEnum_UnitPathfinding = 1,
	UwTaskTypeEnum_ClustersDistances = 2,
} UwTaskTypeEnum;

typedef void (*UwTaskCompletedCallbackType)(uint64 taskUserData, UwTaskTypeEnum type);
void uwSetTaskCompletedCallback(UwTaskCompletedCallbackType callback);
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
void uwSetMapStateCallback(UwMapStateCallbackType callback);
UwMapStateEnum uwMapState(void);

typedef struct UwMapInfo
{
	const char *name;
	const char *guid;
	const char *path;
	uint32 maxPlayers;
} UwMapInfo;
bool uwMapInfo(UwMapInfo *data);

typedef struct UwMapStartingPosition
{
	uint32 position;
	uint32 minForces;
	uint32 maxForces;
} UwMapStartingPosition;
typedef struct UwMapStartingPositionsArray
{
	const UwMapStartingPosition *data;
	uint32 count;
} UwMapStartingPositionsArray;
void uwMapStartingPositions(UwMapStartingPositionsArray *data);

uint32 uwTilesCount(void);
typedef struct UwTile
{
	float position[3];
	float up[3];
	const uint32 *neighborsIndices;
	uint32 neighborsCount;
	uint32 clusterIndex;
	uint8 terrain;
	bool border;
} UwTile;
void uwTile(uint32 index, UwTile *data);

uint32 uwClustersCount(void);
typedef struct UwCluster
{
	const uint32 *neighborsIndices;
	uint32 neighborsCount;
	uint32 centerTileIndex;
} UwCluster;
void uwCluster(uint32 index, UwCluster *data);

void uwAreaRange(float x, float y, float z, float radius, UwIds *data);
void uwAreaConnected(uint32 position, float radius, UwIds *data);
void uwAreaNeighborhood(uint32 position, float radius, UwIds *data);
void uwAreaExtended(uint32 position, float radius, UwIds *data);

bool uwTestVisible(float x1, float y1, float z1, float x2, float y2, float z2);
bool uwTestShooting(uint32 shooterPosition, uint32 shooterProto, float shootingRangeUpgrade, uint32 targetPosition, uint32 targetProto);
float uwDistanceLine(float x1, float y1, float z1, float x2, float y2, float z2);
float uwDistanceEstimate(uint32 positionA, uint32 positionB);
float uwYaw(uint32 startPosition, uint32 goalPosition);

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
void uwStartClustersDistances(const UwClustersDistancesQuery *query);
void uwRetrieveClustersDistances(UwClustersDistancesResult *data);
typedef enum UwPrototypeTypeEnum
{
	UwPrototypeTypeEnum_None = 0,
	UwPrototypeTypeEnum_Resource = 1,
	UwPrototypeTypeEnum_Recipe = 2,
	UwPrototypeTypeEnum_Construction = 3,
	UwPrototypeTypeEnum_Unit = 4,
	UwPrototypeTypeEnum_Upgrade = 5,
	UwPrototypeTypeEnum_Race = 6,
} UwPrototypeTypeEnum;
void uwAllPrototypes(UwIds *data);
UwPrototypeTypeEnum uwPrototypeType(uint32 prototypeId);
const char *uwPrototypeJson(uint32 prototypeId);
const char *uwDefinitionsJson(void);

uint32 uwHashString(const char *str);
typedef struct UwMyForceStatistics
{
	uint32 logisticsUnitsIdle;
	uint32 logisticsUnitsTotal;
	uint32 militaryUnitsIdle;
	uint32 militaryUnitsTotal;
	uint32 closestDangerPosition;
	float closestDangerDistance;
} UwMyForceStatistics;
void uwMyForceStatistics(UwMyForceStatistics *data);

UwPathStateEnum uwUnitPathState(uint32 unitId);

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
void uwUnitUpgrades(uint32 unit, UwUnitUpgrades *data);

bool uwTestShootingEntities(uint32 shooterId, uint32 targetId);

bool uwTestConstructionPlacement(uint32 constructionProto, uint32 position, uint32 recipeProto);
uint32 uwFindConstructionPlacement(uint32 constructionProto, uint32 position, uint32 recipeProto);
typedef enum UwOverviewFlags
{
	UwOverviewFlags_None = 0,
	UwOverviewFlags_Resource = 1 << 0,
	UwOverviewFlags_Construction = 1 << 1,
	UwOverviewFlags_MobileUnit = 1 << 2,
	UwOverviewFlags_StaticUnit = 1 << 3,
	UwOverviewFlags_Unit = UwOverviewFlags_MobileUnit | UwOverviewFlags_StaticUnit,
} UwOverviewFlags;
UwOverviewFlags uwOverviewFlags(uint32 position);
void uwOverviewIds(uint32 position, UwIds *data);
typedef struct UwOverviewExtract
{
	const UwOverviewFlags *flags;
	uint32 count;
} UwOverviewExtract;
void uwOverviewExtract(UwOverviewExtract *data);

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
void uwStartUnitPathfinding(const UwUnitPathfindingQuery *query);
void uwRetrieveUnitPathfinding(UwUnitPathfindingResult *data);
