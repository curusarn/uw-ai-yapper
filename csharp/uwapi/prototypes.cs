using System.Runtime.InteropServices;
using System.Collections.Generic;
using System.Text.Json;

namespace Unnatural
{
    using MapStateEnum = Interop.UwMapStateEnum;
    using PrototypeTypeEnum = Interop.UwPrototypeTypeEnum;

    public class ProtoCommon
    {
        public uint id;
        public string name;
        public string json;
        public PrototypeTypeEnum type;
        public uint[] tags;
        public string[] tagsNames;

        public bool Tagged(uint tag)
        {
            foreach (var t in tags)
                if (t == tag)
                    return true;
            return false;
        }
    }

    public class ProtoResource : ProtoCommon
    {
        public uint maximumProcessingOutput; // recipe will stall if it was to produce a resource stack with more than this amount
    }

    public class ProtoRecipe : ProtoCommon
    {
        public Dictionary<uint, uint> inputs; // id -> count
        public Dictionary<uint, uint> outputs; // id -> count
        public uint duration; // ticks
        public uint placeOver; // id of unit
    }

    public class ProtoConstruction : ProtoCommon
    {
        public Dictionary<uint, uint> inputs; // id -> count
        public uint output; // id of unit
    }

    public class ProtoUnit : ProtoCommon
    {
        public List<uint> recipes; // ids of recipes available for processing by this unit
        public List<uint> upgrades; // ids of upgrades applicable to this unit
        public bool vital; // a force loses when it loses last vital unit
        public bool cargo; // the unit may carry resources
        public bool logistics; // vehicle that is automatically controlled by the logistics system
        public bool assembler; // the unit must have at least one valid recipe
        public bool emptyNeighbors; // the building requires empty space around
        public bool maximumDistance; // the unit moves to maximum distance when shooting
        public bool excludeFromMilitary; // the unit is excluded from all-army hotkey
        public bool neutralCategory; // the unit is put in neutral category in lexicon
        public bool explodesWhenAttacks; // suicidal unit
        public bool explodesWhenKilled;
        public bool explodesWhenSelfDestructed;
        public float processingSpeed;
        public float lifeRegen; // life per second
        public float manaRegen; // mana per second
        public uint maxLife;
        public uint maxMana;
        public uint startingMana;
        public uint regenDelay; // ticks
        public uint armorType;
        public string armorTypeName;

        // weapon
        public uint damageType;
        public string damageTypeName;
        public float dps;
        public float dpsAtLowLife;
        public float fireRange; // meters
        public float rateOfFire; // shots per second
        public float shooterElevation; // radians
        public float targetElevation; // radians
        public float splashRadius; // meters
        public float splashFractionAtEdge;
        public float splashFractionToFriendly;

        // explosion
        public uint explosionDamageType;
        public string explosionDamageTypeName;
        public float explosionDamage;
        public float explosionRadius; // meters
        public float explosionFractionAtEdge;
        public float explosionFractionToFriendly;

        // mobile only
        public Dictionary<uint, float> speeds; // terrain type -> speed (meters per second)

        // buildings only
        public float buildingRadius; // meters
    }

    public class ProtoUpgrade : ProtoCommon
    {
        public uint duration; // ticks
        public uint limit; // maximum stack size of the upgrade applied
        public float damage;
        public float shootingRange;
        public float splashRadius;
        public float defense;
        public float regenSpeed;
        public float movementSpeed;
        public float processingSpeed;
    }

    public class ProtoRace : ProtoCommon
    {
        public Dictionary<uint, uint> startingProvisions; // id -> count
        public List<uint> constructions;
    }

    public class Definitions
    {
        public List<string> tagsNames;
        public List<string> terrainNames;
        public List<string> armorNames;
        public List<string> damageNames;
        public List<List<float>> hitChancesTable; // damage type -> armor type -> damage chance
    }

    public static class Prototypes
    {
        public static IReadOnlyList<uint> All()
        {
            return all;
        }

        public static PrototypeTypeEnum Type(uint id)
        {
            ProtoCommon tmp;
            return commons.TryGetValue(id, out tmp) ? tmp.type : PrototypeTypeEnum.None;
        }

        public static string Name(uint id)
        {
            ProtoCommon tmp;
            return commons.TryGetValue(id, out tmp) ? tmp.name : "";
        }

        public static string Json(uint id)
        {
            ProtoCommon tmp;
            return commons.TryGetValue(id, out tmp) ? tmp.json : "";
        }

        public static ProtoCommon Common(uint id)
        {
            ProtoCommon tmp;
            if (commons.TryGetValue(id, out tmp))
                return tmp;
            return null;
        }

        public static ProtoResource Resource(uint id)
        {
            ProtoCommon tmp;
            if (commons.TryGetValue(id, out tmp))
                if (tmp.type == PrototypeTypeEnum.Resource)
                    return (ProtoResource)tmp;
            return null;
        }

        public static ProtoRecipe Recipe(uint id)
        {
            ProtoCommon tmp;
            if (commons.TryGetValue(id, out tmp))
                if (tmp.type == PrototypeTypeEnum.Recipe)
                    return (ProtoRecipe)tmp;
            return null;
        }

        public static ProtoConstruction Construction(uint id)
        {
            ProtoCommon tmp;
            if (commons.TryGetValue(id, out tmp))
                if (tmp.type == PrototypeTypeEnum.Construction)
                    return (ProtoConstruction)tmp;
            return null;
        }

        public static ProtoUnit Unit(uint id)
        {
            ProtoCommon tmp;
            if (commons.TryGetValue(id, out tmp))
                if (tmp.type == PrototypeTypeEnum.Unit)
                    return (ProtoUnit)tmp;
            return null;
        }

        public static ProtoUpgrade Upgrade(uint id)
        {
            ProtoCommon tmp;
            if (commons.TryGetValue(id, out tmp))
                if (tmp.type == PrototypeTypeEnum.Upgrade)
                    return (ProtoUpgrade)tmp;
            return null;
        }

        public static ProtoRace Race(uint id)
        {
            ProtoCommon tmp;
            if (commons.TryGetValue(id, out tmp))
                if (tmp.type == PrototypeTypeEnum.Race)
                    return (ProtoRace)tmp;
            return null;
        }

        public static Definitions Definitions()
        {
            return definitions;
        }

        public static uint HashString(string str)
        {
            return Interop.uwHashString(str);
        }

        public static uint TagId(string tag)
        {
            int i = definitions.tagsNames.IndexOf(tag);
            if (i < 0)
                throw new KeyNotFoundException("tag name not found");
            return (uint)i;
        }

        static readonly List<uint> all = new List<uint>();
        static readonly Dictionary<uint, ProtoCommon> commons = new Dictionary<uint, ProtoCommon>();
        static string definitionsJson;
        static Definitions definitions;

        static uint[] AllIds()
        {
            Interop.UwIds ids = new Interop.UwIds();
            Interop.uwAllPrototypes(ref ids);
            return InteropHelpers.Ids(ids);
        }

        static void LoadPrototypes()
        {
            Game.LogInfo("loading prototypes");

            all.Clear();
            commons.Clear();

            var options = new JsonSerializerOptions
            {
                IncludeFields = true,
            };

            foreach (uint id in AllIds())
            {
                PrototypeTypeEnum type = Interop.uwPrototypeType(id);
                string json = Marshal.PtrToStringAnsi(Interop.uwPrototypeJson(id));
                ProtoCommon pc;
                switch (type)
                {
                    case PrototypeTypeEnum.Resource:
                        pc = JsonSerializer.Deserialize<ProtoResource>(json, options);
                        break;
                    case PrototypeTypeEnum.Recipe:
                        pc = JsonSerializer.Deserialize<ProtoRecipe>(json, options);
                        break;
                    case PrototypeTypeEnum.Construction:
                        pc = JsonSerializer.Deserialize<ProtoConstruction>(json, options);
                        break;
                    case PrototypeTypeEnum.Unit:
                        pc = JsonSerializer.Deserialize<ProtoUnit>(json, options);
                        break;
                    case PrototypeTypeEnum.Upgrade:
                        pc = JsonSerializer.Deserialize<ProtoUpgrade>(json, options);
                        break;
                    case PrototypeTypeEnum.Race:
                        pc = JsonSerializer.Deserialize<ProtoRace>(json, options);
                        break;
                    default:
                        throw new System.Exception("unknown prototype type enum");
                }
                pc.json = json;
                commons[id] = pc;
                all.Add(id);
            }

            Game.LogInfo("prototypes loaded");
        }

        static void LoadDefinitions()
        {
            Game.LogInfo("loading definitions");

            var options = new JsonSerializerOptions
            {
                IncludeFields = true,
            };

            definitionsJson = Marshal.PtrToStringAnsi(Interop.uwDefinitionsJson());
            definitions = JsonSerializer.Deserialize<Definitions>(definitionsJson, options);

            Game.LogInfo("definitions loaded");
        }

        static void MapStateChanged(object sender, MapStateEnum state)
        {
            if (state == MapStateEnum.Loaded)
            {
                LoadPrototypes();
                LoadDefinitions();
            }
        }

        static Prototypes()
        {
            Events.MapStateChanged += MapStateChanged;
        }
    }
}
