#ifndef unnatural_uwapi_botsConnection_h_d5fgh4df5dfgh
#define unnatural_uwapi_botsConnection_h_d5fgh4df5dfgh

#include "common.h"

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef UNNATURAL_BOTS

	// initialization

	UNNATURAL_API void uwInitialize(uint32 version);
	UNNATURAL_API void uwDeinitialize(void);

	typedef void (*UwExceptionCallbackType)(const char *message);
	UNNATURAL_API void uwSetExceptionCallback(UwExceptionCallbackType callback);

	// logging

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
	UNNATURAL_API void uwSetLogCallback(UwLogCallbackType callback);
	UNNATURAL_API void uwInitializeConsoleLogger(void);
	UNNATURAL_API void uwLog(UwSeverityEnum severity, const char *message);

	// connection state

	typedef enum UwConnectionStateEnum
	{
		UwConnectionStateEnum_None = 0,
		UwConnectionStateEnum_Connecting = 1,
		UwConnectionStateEnum_Connected = 2,
		UwConnectionStateEnum_Error = 3,
	} UwConnectionStateEnum;
	typedef void (*UwConnectionStateCallbackType)(UwConnectionStateEnum state);
	UNNATURAL_API void uwSetConnectionStateCallback(UwConnectionStateCallbackType callback);
	UNNATURAL_API UwConnectionStateEnum uwConnectionState(void);

	// connect

	UNNATURAL_API void uwSetConnectStartGui(bool enabled, const char *extraCmdParams);
	UNNATURAL_API bool uwConnectFindLan(uint64 timeoutMicroseconds);
	UNNATURAL_API void uwConnectDirect(const char *address, uint16 port);
	UNNATURAL_API void uwConnectLobbyId(uint64 lobbyId);
	UNNATURAL_API bool uwConnectEnvironment();
	UNNATURAL_API void uwConnectNewServer(uint32 visibility, const char *name, const char *extraCmdParams);
	UNNATURAL_API bool uwTryReconnect(void);
	UNNATURAL_API void uwDisconnect(void);

	// my player

	UNNATURAL_API void uwSetPlayerName(const char *name);
	UNNATURAL_API void uwPlayerJoinForce(uint32 force);
	UNNATURAL_API void uwSetForceColor(float r, float g, float b); // [0 .. 1]
	UNNATURAL_API void uwSetForceRace(uint32 raceProto);
	UNNATURAL_API void uwForceJoinTeam(uint32 team);
	UNNATURAL_API void uwSkipCutscene(void);

	typedef struct UwMyPlayer
	{
		uint32 playerEntityId;
		uint32 forceEntityId;
		bool primaryController;
		bool admin;
	} UwMyPlayer;
	UNNATURAL_API bool uwMyPlayer(UwMyPlayer *data);

	typedef struct UwAssistConfig
	{
		bool logistics;
		bool aiming;
		bool fighting;
	} UwAssistConfig;
	UNNATURAL_API void uwSetAssistConfig(const UwAssistConfig *config);

	// performance

	typedef struct UwPerformanceStatistics
	{
		float gameSpeed;
		float mainThreadUtilization;
		float ping; // ms
		uint32 networkUp; // kb/s
		uint32 networkDown; // kb/s
	} UwPerformanceStatistics;
	UNNATURAL_API void uwPerformanceStatistics(UwPerformanceStatistics *data);

	UNNATURAL_API void uwPerformanceProfiling(bool enable);
	UNNATURAL_API uint64 uwProfilingEventBegin(void);
	UNNATURAL_API void uwProfilingEventEnd(const char *name, uint64 eventStartTime);

#endif

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_botsConnection_h_d5fgh4df5dfgh
