using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace Unnatural
{
    using MyForceStatistics = Interop.UwMyForceStatistics;
    using ForeignPolicy = Interop.UwForeignPolicyComponent;
    using PolicyEnum = Interop.UwForeignPolicyEnum;
    using UnitUpgrades = Interop.UwUnitUpgrades;
    using PathStateEnum = Interop.UwPathStateEnum;
    using OverviewFlags = Interop.UwOverviewFlags;

    public static class World
    {
        public static uint MyPlayerId()
        {
            return myPlayer.playerEntityId;
        }

        public static uint MyForceId()
        {
            return myPlayer.forceEntityId;
        }

        public static bool IsPrimaryController()
        {
            return myPlayer.primaryController;
        }

        public static bool IsAdmin()
        {
            return myPlayer.admin;
        }

        public static MyForceStatistics MyForceStatistics()
        {
            return myForceStatistics;
        }

        public static PathStateEnum UnitPathState(uint unitId)
        {
            return Interop.uwUnitPathState(unitId);
        }

        public static UnitUpgrades UnitUpgrades(uint unitId)
        {
            UnitUpgrades data = new UnitUpgrades();
            Interop.uwUnitUpgrades(unitId, ref data);
            return data;
        }

        public static bool TestShooting(uint shooterId, uint targetId)
        {
            return Interop.uwTestShootingEntities(shooterId, targetId);
        }

        public static bool TestConstructionPlacement(uint constructionProto, uint position, uint recipeProto = 0)
        {
            return Interop.uwTestConstructionPlacement(constructionProto, position, recipeProto);
        }

        public static uint FindConstructionPlacement(uint constructionProto, uint position, uint recipeProto = 0)
        {
            return Interop.uwFindConstructionPlacement(constructionProto, position, recipeProto);
        }

        public static IReadOnlyList<OverviewFlags> OverviewFlags()
        {
            return overview;
        }

        public static OverviewFlags OverviewFlags(uint position)
        {
            return overview[(int)position];
        }

        public static uint[] OverviewEntities(uint position)
        {
            Interop.UwIds ns = new Interop.UwIds();
            Interop.uwOverviewIds(position, ref ns);
            return InteropHelpers.Ids(ns);
        }

        public static void UnitPathfinding(Action<UnitPathfindingResult> callback, uint startingPosition, uint goalPosition, uint unitPrototype, bool allowNearbyPosition = false, uint maxIterations = 0)
        {
            Action fin = () =>
            {
                Interop.UwUnitPathfindingResult tmp = new Interop.UwUnitPathfindingResult();
                Interop.uwRetrieveUnitPathfinding(ref tmp);
                UnitPathfindingResult res = new UnitPathfindingResult();
                res.path = InteropHelpers.Ids(tmp.path);
                res.state = tmp.state;
                callback(res);
            };
            Interop.UwUnitPathfindingQuery q = new Interop.UwUnitPathfindingQuery();
            q.startingPosition = startingPosition;
            q.goalPosition = goalPosition;
            q.unitPrototype = unitPrototype;
            q.allowNearbyPosition = allowNearbyPosition;
            q.maxIterations = maxIterations;
            q.taskUserData = UwapiTasks.InsertTask(fin);
            Interop.uwStartUnitPathfinding(ref q);
        }

        public static IReadOnlyDictionary<uint, Entity> Entities()
        {
            return entities;
        }

        public static Entity Entity(uint id)
        {
            return entities[id];
        }

        public static PolicyEnum Policy(uint force)
        {
            PolicyEnum val;
            return policies.TryGetValue(force, out val) ? val : PolicyEnum.None;
        }

        static Interop.UwMyPlayer myPlayer;
        static MyForceStatistics myForceStatistics = new MyForceStatistics();
        static readonly Dictionary<uint, Entity> entities = new Dictionary<uint, Entity>();
        static readonly Dictionary<uint, PolicyEnum> policies = new Dictionary<uint, PolicyEnum>();
        static OverviewFlags[] overview = new OverviewFlags[0];

        static uint[] AllIds()
        {
            Interop.UwIds ids = new Interop.UwIds();
            Interop.uwAllEntities(ref ids);
            return InteropHelpers.Ids(ids);
        }

        static uint[] ModifiedIds()
        {
            Interop.UwIds ids = new Interop.UwIds();
            Interop.uwModifiedEntities(ref ids);
            return InteropHelpers.Ids(ids);
        }

        static void UpdateRemoved()
        {
            var allIds = new HashSet<uint>(AllIds());
            var removed = new List<uint>();
            foreach (uint id in entities.Keys)
                if (!allIds.Contains(id))
                    removed.Add(id);
            foreach (uint id in removed)
            {
                entities[id].Destroyed = true;
                entities.Remove(id);
            }
        }

        static void UpdateFresh()
        {
            foreach (Entity e in entities.Values)
                e.Fresh = false;
        }

        static void UpdateModified()
        {
            foreach (uint id in ModifiedIds())
            {
                if (entities.ContainsKey(id))
                {
                    entities[id].FetchComponents();
                }
                else
                {
                    Entity o = new Entity(id);
                    o.FetchComponents();
                    entities[id] = o;
                }
            }
        }

        static void UpdatePolicies()
        {
            policies.Clear();
            foreach (Entity e in entities.Values)
            {
                if (!e.ForeignPolicy.HasValue)
                    continue;
                ForeignPolicy fp = e.ForeignPolicy.Value;
                if (fp.forces[0] == myPlayer.forceEntityId)
                    policies[fp.forces[1]] = fp.policy;
                if (fp.forces[1] == myPlayer.forceEntityId)
                    policies[fp.forces[0]] = fp.policy;
            }
        }

        static void UpdateOverview(bool stepping)
        {
            if (stepping)
            {
                Interop.UwOverviewExtract ex = new Interop.UwOverviewExtract();
                Interop.uwOverviewExtract(ref ex);
                if (overview.Length != ex.count)
                    overview = new OverviewFlags[ex.count];
                if (ex.count > 0)
                    Marshal.Copy(ex.flags, (int[])(object)overview, 0, (int)ex.count);
            }
            else
                overview = new OverviewFlags[0];
        }

        static void Updating(object sender, bool stepping)
        {
            Interop.uwMyPlayer(ref myPlayer);
            Interop.uwMyForceStatistics(ref myForceStatistics);
            UpdateRemoved();
            UpdateFresh();
            UpdateModified();
            UpdatePolicies();
            UpdateOverview(stepping);
        }

        static World()
        {
            Events.Updating += Updating;
        }
    }

    public struct UnitPathfindingResult
    {
        public uint[] path;
        public PathStateEnum state;
    }
}
