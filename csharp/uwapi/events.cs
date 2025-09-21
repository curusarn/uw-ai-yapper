using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace Unnatural
{
    using ConnectionStateEnum = Interop.UwConnectionStateEnum;
    using GameStateEnum = Interop.UwGameStateEnum;
    using MapStateEnum = Interop.UwMapStateEnum;
    using ShootingsArray = Interop.UwShootingsArray;
    using ChatTargetFLags = Interop.UwChatTargetFlags;

    public class ChatMessage
    {
        public string Message;
        public uint Sender;
        public ChatTargetFLags Flags;
    }

    public struct ShootingControlData
    {
        public Interop.UwShootingEventEnum type;
        public ushort count;
    }

    public static class Events
    {
        public static event EventHandler<ConnectionStateEnum> ConnectionStateChanged;
        public static event EventHandler<GameStateEnum> GameStateChanged;
        public static event EventHandler<MapStateEnum> MapStateChanged;
        public static event EventHandler<bool> Updating;
        public static event EventHandler<IReadOnlyList<uint>> Shootings;
        public static event EventHandler<uint> ForceEliminated;
        public static event EventHandler<ChatMessage> ChatReceived;

        static readonly Interop.UwExceptionCallbackType ExceptionDelegate = new Interop.UwExceptionCallbackType(ExceptionCallback);
        static readonly Interop.UwConnectionStateCallbackType ConnectionStateDelegate = new Interop.UwConnectionStateCallbackType(ConnectionStateCallback);
        static readonly Interop.UwGameStateCallbackType GameStateDelegate = new Interop.UwGameStateCallbackType(GameStateCallback);
        static readonly Interop.UwMapStateCallbackType MapStateDelegate = new Interop.UwMapStateCallbackType(MapStateCallback);
        static readonly Interop.UwUpdateCallbackType UpdateDelegate = new Interop.UwUpdateCallbackType(UpdateCallback);
        static readonly Interop.UwShootingsCallbackType ShootingsDelegate = new Interop.UwShootingsCallbackType(ShootingsCallback);
        static readonly Interop.UwForceEliminatedCallbackType ForceEliminatedDelegate = new Interop.UwForceEliminatedCallbackType(ForceEliminatedCallback);
        static readonly Interop.UwChatCallbackType ChatDelegate = new Interop.UwChatCallbackType(ChatCallback);

        static void ExceptionCallback([MarshalAs(UnmanagedType.LPStr)] string message)
        {
            Console.WriteLine("exception: " + message);
            if (System.Diagnostics.Debugger.IsAttached)
                System.Diagnostics.Debugger.Break();
        }

        static void ConnectionStateCallback(ConnectionStateEnum state)
        {
            if (ConnectionStateChanged == null)
                return;
            ConnectionStateChanged(null, state);
        }

        static void GameStateCallback(GameStateEnum state)
        {
            if (GameStateChanged == null)
                return;
            GameStateChanged(null, state);
        }

        static void MapStateCallback(MapStateEnum state)
        {
            if (MapStateChanged == null)
                return;
            MapStateChanged(null, state);
        }

        static void UpdateCallback(bool stepping)
        {
            if (Updating == null)
                return;
            Updating(null, stepping);
        }

        static void ShootingsCallback(ref ShootingsArray data)
        {
            if (Shootings == null)
                return;
            uint[] tmp = new uint[data.count];
            if (data.count > 0)
                Marshal.Copy(data.data, (int[])(object)tmp, 0, (int)data.count);
            Shootings(null, tmp);
        }

        public static ShootingControlData ShootingControlData(uint id)
        {
            ushort low = (ushort)(id & 0xFFFF);
            ushort high = (ushort)(id >> 16);
            return new ShootingControlData
            {
                type = (Interop.UwShootingEventEnum)low,
                count = high
            };
        }

        static void ForceEliminatedCallback(uint force)
        {
            if (ForceEliminated == null)
                return;
            ForceEliminated(null, force);
        }

        static void ChatCallback(string msg, uint sender, ChatTargetFLags flags)
        {
            if (ChatReceived == null)
                return;
            ChatMessage c = new ChatMessage();
            c.Message = msg;
            c.Sender = sender;
            c.Flags = flags;
            ChatReceived(null, c);
        }

        static Events()
        {
            AppDomain.CurrentDomain.ProcessExit += Destructor;
            Interop.uwInitialize(Interop.UW_VERSION);
            Interop.uwInitializeConsoleLogger();

            Interop.uwSetExceptionCallback(ExceptionDelegate);
            Interop.uwSetConnectionStateCallback(ConnectionStateDelegate);
            Interop.uwSetGameStateCallback(GameStateDelegate);
            Interop.uwSetMapStateCallback(MapStateDelegate);
            Interop.uwSetUpdateCallback(UpdateDelegate);
            Interop.uwSetShootingsCallback(ShootingsDelegate);
            Interop.uwSetForceEliminatedCallback(ForceEliminatedDelegate);
            Interop.uwSetChatCallback(ChatDelegate);

            // make sure that others register their callbacks too (call any method)
            Prototypes.All();
            Map.Positions();
            World.Entities();
            UwapiTasks.Init();
        }

        static void Destructor(object sender, EventArgs e)
        {
            Interop.uwDeinitialize();
        }
    }

    public static class UwapiTasks
    {
        public static ulong InsertTask(Action a)
        {
            ulong i = index++;
            actions.Add(i, a);
            return i;
        }

        static ulong index = 1;
        static Dictionary<ulong, Action> actions = new Dictionary<ulong, Action>();
        static readonly Interop.UwTaskCompletedCallbackType TaskCompletedDelegate = new Interop.UwTaskCompletedCallbackType(TaskCompleted);

        static void TaskCompleted(ulong taskUserData, Interop.UwTaskTypeEnum type)
        {
            if (type != Interop.UwTaskTypeEnum.None)
            {
                Action a;
                if (actions.TryGetValue(taskUserData, out a))
                    a();
            }
            actions.Remove(taskUserData);
        }

        static UwapiTasks()
        {
            Interop.uwSetTaskCompletedCallback(TaskCompletedDelegate);
        }

        public static void Init()
        { }
    }
}
