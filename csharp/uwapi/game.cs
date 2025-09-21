namespace Unnatural
{
    using ConnectionStateEnum = Interop.UwConnectionStateEnum;
    using GameStateEnum = Interop.UwGameStateEnum;
    using MapStateEnum = Interop.UwMapStateEnum;

    public static class Game
    {
        public static void LogInfo(string msg)
        {
            Interop.uwLog(Interop.UwSeverityEnum.Info, msg);
        }

        public static void LogWarning(string msg)
        {
            Interop.uwLog(Interop.UwSeverityEnum.Warning, msg);
        }

        public static void LogError(string msg)
        {
            Interop.uwLog(Interop.UwSeverityEnum.Error, msg);
        }

        public static void SetPlayerName(string name)
        {
            Interop.uwSetPlayerName(name);
        }

        public static void PlayerJoinForce(uint forceId)
        {
            Interop.uwPlayerJoinForce(forceId);
        }

        public static void SetForceColor(float r, float g, float b) // [0 .. 1]
        {
            Interop.uwSetForceColor(r, g, b);
        }

        public static void SetForceRace(uint raceProto)
        {
            Interop.uwSetForceRace(raceProto);
        }

        public static void ForceJoinTeam(uint team)
        {
            Interop.uwForceJoinTeam(team);
        }

        public static void SkipCutscene()
        {
            Interop.uwSkipCutscene();
        }

        public static void SetConnectStartGui(bool startGui, string extraParams = "--observer 1")
        {
            Interop.uwSetConnectStartGui(startGui, extraParams);
        }

        public static bool ConnectFindLan(ulong timeoutMicroseconds = 1000000)
        {
            return Interop.uwConnectFindLan(timeoutMicroseconds);
        }

        public static void ConnectDirect(string address, ushort port)
        {
            Interop.uwConnectDirect(address, port);
        }

        public static void ConnectLobbyId(ulong lobbyId)
        {
            Interop.uwConnectLobbyId(lobbyId);
        }

        public static bool ConnectEnvironment()
        {
            return Interop.uwConnectEnvironment();
        }

        public static void ConnectNewServer(uint visibility = 0, string name = "", string extraParams = "")
        {
            Interop.uwConnectNewServer(visibility, name, extraParams);
        }

        // returns false if no data for reconnect are available
        // returns true after a reconnect was attempted (irrespective of whether actual connection has succeded)
        public static bool TryReconnect()
        {
            return Interop.uwTryReconnect();
        }

        public static void Disconnect()
        {
            Interop.uwDisconnect();
        }

        public static ConnectionStateEnum ConnectionState()
        {
            return Interop.uwConnectionState();
        }

        public static GameStateEnum GameState()
        {
            return Interop.uwGameState();
        }

        public static uint GameTick()
        {
            return Interop.uwGameTick();
        }

        public static MapStateEnum MapState()
        {
            return Interop.uwMapState();
        }

        public static Interop.UwPerformanceStatistics PerformanceStatistics()
        {
            Interop.UwPerformanceStatistics data = new Interop.UwPerformanceStatistics();
            Interop.uwPerformanceStatistics(ref data);
            return data;
        }

        public static void PerformanceProfiling(bool enable)
        {
            Interop.uwPerformanceProfiling(enable);
        }

        public static ulong ProfilingEventBegin()
        {
            return Interop.uwProfilingEventBegin();
        }

        public static void ProfilingEventEnd(string name, ulong eventStartTime)
        {
            Interop.uwProfilingEventEnd(name, eventStartTime);
        }
    }
}
