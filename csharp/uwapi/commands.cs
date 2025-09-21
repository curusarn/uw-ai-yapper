using System.Runtime.InteropServices;

namespace Unnatural
{
    using Order = Interop.UwOrder;
    using Type = Interop.UwOrderTypeEnum;
    using Priority = Interop.UwOrderPriorityFlags;

    public static class Commands
    {
        public const uint Invalid = uint.MaxValue;

        public static Order[] Orders(uint unitId)
        {
            Interop.UwOrders os = new Interop.UwOrders();
            Interop.uwOrders(unitId, ref os);
            Order[] tmp = new Order[os.count];
            for (int i = 0; i < os.count; i++)
                tmp[i] = Marshal.PtrToStructure<Order>(os.orders + i * Marshal.SizeOf<Order>());
            return tmp;
        }

        public static void Order(uint unitId, Order order)
        {
            Interop.uwOrder(unitId, ref order);
        }

        public static Order Stop()
        {
            Order o = new Order();
            o.entity = Invalid;
            o.position = Invalid;
            o.order = Type.Stop;
            o.priority = Priority.User;
            return o;
        }

        public static Order Guard()
        {
            Order o = new Order();
            o.entity = Invalid;
            o.position = Invalid;
            o.order = Type.Guard;
            o.priority = Priority.User;
            return o;
        }

        public static Order RunToPosition(uint position)
        {
            Order o = new Order();
            o.entity = Invalid;
            o.position = position;
            o.order = Type.Run;
            o.priority = Priority.User;
            return o;
        }

        public static Order RunToEntity(uint entityId)
        {
            Order o = new Order();
            o.entity = entityId;
            o.position = Invalid;
            o.order = Type.Run;
            o.priority = Priority.User;
            return o;
        }

        public static Order FightToPosition(uint position)
        {
            Order o = new Order();
            o.entity = Invalid;
            o.position = position;
            o.order = Type.Fight;
            o.priority = Priority.User;
            return o;
        }

        public static Order FightToEntity(uint entityId)
        {
            Order o = new Order();
            o.entity = entityId;
            o.position = Invalid;
            o.order = Type.Fight;
            o.priority = Priority.User;
            return o;
        }

        public static void PlaceConstruction(uint constructionProto, uint position, float yaw = 0, uint recipeProto = 0, Interop.UwPriorityEnum priority = Interop.UwPriorityEnum.Normal)
        {
            Interop.uwCommandPlaceConstruction(constructionProto, position, yaw, recipeProto, priority);
        }

        public static void SetRecipe(uint unitId, uint recipeProto)
        {
            Interop.uwCommandSetRecipe(unitId, recipeProto);
        }

        public static void SetPriority(uint unitId, Interop.UwPriorityEnum priority)
        {
            Interop.uwCommandSetPriority(unitId, priority);
        }

        public static void Load(uint unitId, uint resourceProto)
        {
            Interop.uwCommandLoad(unitId, resourceProto);
        }

        public static void Unload(uint unitId)
        {
            Interop.uwCommandUnload(unitId);
        }

        public static void Move(uint unitId, uint position, float yaw = 0)
        {
            Interop.uwCommandMove(unitId, position, yaw);
        }

        public static void Aim(uint unitId, uint targetId)
        {
            Interop.uwCommandAim(unitId, targetId);
        }

        public static void RenounceControl(uint entityId)
        {
            Interop.uwCommandRenounceControl(entityId);
        }

        public static void SelfDestruct(uint entityId)
        {
            Interop.uwCommandSelfDestruct(entityId);
        }
    }
}
