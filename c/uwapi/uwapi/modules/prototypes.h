#ifndef unnatural_uwapi_prototypes_h_c5s4zgkisdf
#define unnatural_uwapi_prototypes_h_c5s4zgkisdf

#include "common.h"

#ifdef __cplusplus
extern "C"
{
#endif

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
	UNNATURAL_API void uwAllPrototypes(UwIds *data);
	UNNATURAL_API UwPrototypeTypeEnum uwPrototypeType(uint32 prototypeId);
	UNNATURAL_API const char *uwPrototypeJson(uint32 prototypeId);
	UNNATURAL_API const char *uwDefinitionsJson(void);

	UNNATURAL_API uint32 uwHashString(const char *str);

#ifdef __cplusplus
} // extern C
#endif

#endif // unnatural_uwapi_prototypes_h_c5s4zgkisdf
