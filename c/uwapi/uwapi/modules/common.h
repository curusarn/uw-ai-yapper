#ifndef unnatural_uwapi_common_h_sdr8g4h1u
#define unnatural_uwapi_common_h_sdr8g4h1u

#if defined(UNNATURAL_SCRIPTS) == defined(UNNATURAL_BOTS)
	#error Exactly one of UNNATURAL_SCRIPTS or UNNATURAL_BOTS must be defined
#endif

#ifndef UNNATURAL_API
	#define UNNATURAL_API
#endif // !UNNATURAL_API

#ifndef UNNATURAL_ENTRY
	#define UNNATURAL_ENTRY
#endif

#ifndef UNNATURAL_POINTER
	#define UNNATURAL_POINTER(X) X
#endif // !UNNATURAL_POINTER

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C"
{
#endif

	typedef uint8_t uint8;
	typedef int8_t sint8;
	typedef uint16_t uint16;
	typedef int16_t sint16;
	typedef uint32_t uint32;
	typedef int32_t sint32;
	typedef uint64_t uint64;
	typedef int64_t sint64;

	static const uint32 UW_VERSION = 46;
	static const uint32 UW_GameTicksPerSecond = 20;

	typedef struct UwIds
	{
		UNNATURAL_POINTER(const uint32 *) ids;
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

	typedef enum UwChatTargetEnum
	{
		UwChatTargetEnum_None = 0,
		UwChatTargetEnum_Direct = 1,
		UwChatTargetEnum_Everyone = 2,
		UwChatTargetEnum_Allies = 3,
		UwChatTargetEnum_Enemies = 4,
		UwChatTargetEnum_Observers = 5,
	} UwChatTargetEnum;

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_common_h_sdr8g4h1u
