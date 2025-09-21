import math
from dataclasses import dataclass
from .interop import *
from .events import uw_events


@dataclass
class Vector3:
    x: float = 0
    y: float = 0
    z: float = 0


class Map:
    _instance = None
    _name: str = ""
    _guid: str = ""
    _path: str = ""
    _max_players: int = 0
    _starting_positions: List[UwMapStartingPosition] = []
    _positions: List[Vector3] = []
    _ups: List[Vector3] = []
    _neighbors: List[List[int]] = []
    _terrains: List[int] = []
    _map_tile_to_cluster: List[int] = []
    _map_cluster_to_tile: List[int] = []
    _clusters_neighbors: List[List[int]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            uw_events.on_map_state(cls._instance._map_state)
        return cls._instance

    def name(self) -> str:
        return self._name

    def guid(self) -> str:
        return self._guid

    def path(self) -> str:
        return self._path

    def max_players(self) -> int:
        return self._max_players

    def starting_positions(self) -> List[UwMapStartingPosition]:
        return self._starting_positions

    def positions(self) -> List[Vector3]:
        return self._positions

    def position(self, position: int) -> Vector3:
        return self._positions[position]

    def ups(self) -> List[Vector3]:
        return self._ups

    def up(self, position: int) -> Vector3:
        return self._ups[position]

    def neighbors_all(self) -> List[List[int]]:
        return self._neighbors

    def neighbors(self, position: int) -> List[int]:
        return self._neighbors[position]

    def terrains(self) -> List[int]:
        return self._terrains

    def terrain(self, position: int) -> int:
        return self._terrains[position]

    def area_range(self, point: Vector3, radius: float) -> List[int]:
        return uw_interop.uwAreaRange(point.x, point.y, point.z, radius).ids

    def area_connected(self, position: int, radius: float) -> List[int]:
        return uw_interop.uwAreaConnected(position, radius).ids

    def area_neighborhood(self, position: int, radius: float) -> List[int]:
        return uw_interop.uwAreaNeighborhood(position, radius).ids

    def area_extended(self, position: int, radius: float) -> List[int]:
        return uw_interop.uwAreaExtended(position, radius).ids

    def test_visible(self, a: Vector3, b: Vector3) -> bool:
        return uw_interop.uwTestVisible(a.x, a.y, a.z, b.x, b.y, b.z)

    def test_shooting(
        self,
        shooter_position: int,
        shooter_proto: int,
        shooting_range_upgrade: float,
        target_position: int,
        target_proto: int,
    ) -> bool:
        return uw_interop.uwTestShooting(
            shooter_position,
            shooter_proto,
            shooting_range_upgrade,
            target_position,
            target_proto,
        )

    def distance_line(self, a: int, b: int) -> float:
        a3 = self._positions[a]
        b3 = self._positions[b]
        dx = a3.x - b3.x
        dy = a3.y - b3.y
        dz = a3.z - b3.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def distance_estimate(self, position_a: int, position_b: int) -> float:
        return uw_interop.uwDistanceEstimate(position_a, position_b)

    def yaw(self, start_position: int, goal_position: int) -> float:
        return uw_interop.uwYaw(start_position, goal_position)

    def tile_to_cluster_map(self) -> List[int]:
        return self._map_tile_to_cluster

    def cluster_to_tile_map(self) -> List[int]:
        return self._map_cluster_to_tile

    def tile_to_cluster(self, tile: int) -> int:
        return self._map_tile_to_cluster[tile]

    def cluster_to_tile(self, cluster: int) -> int:
        return self._map_cluster_to_tile[cluster]

    def clusters_neighbors_all(self) -> List[List[int]]:
        return self._clusters_neighbors

    def clusters_neighbors(self, cluster: int) -> List[int]:
        return self._clusters_neighbors[cluster]

    def clusters_distances(
        self,
        callback: Callable,
        starting_cluster: int,
        unit_prototype: int,
        allow_impassable_terrain: bool = False,
    ) -> None:
        def fin():
            callback(uw_interop.uwRetrieveClustersDistances())

        q = UwClustersDistancesQuery(
            uw_events._insert_task(fin),
            starting_cluster,
            unit_prototype,
            allow_impassable_terrain,
        )
        uw_interop.uwStartClustersDistances(q)

    def _reset(self) -> None:
        self._name: str = ""
        self._guid: str = ""
        self._path: str = ""
        self._max_players: int = 0
        self._starting_positions: List[UwMapStartingPosition] = []
        self._positions: List[Vector3] = []
        self._ups: List[Vector3] = []
        self._neighbors: List[List[int]] = []
        self._terrains: List[int] = []
        self._map_tile_to_cluster: List[int] = []
        self._map_cluster_to_tile: List[int] = []
        self._clusters_neighbors: List[List[int]] = []

    def _load_info(self) -> None:
        info = uw_interop.uwMapInfo()
        if info[0]:
            self._name = info[1].name
            self._guid = info[1].guid
            self._path = info[1].path
            self._max_players = info[1].maxPlayers

    def _load_tiles(self) -> None:
        count = uw_interop.uwTilesCount()
        for i in range(count):
            tile = uw_interop.uwTile(i)
            self._positions.append(
                Vector3(tile.position[0], tile.position[1], tile.position[2])
            )
            self._ups.append(Vector3(tile.up[0], tile.up[1], tile.up[2]))
            self._neighbors.append(tile.neighborsIndices)
            self._terrains.append(tile.terrain)
            self._map_tile_to_cluster.append(tile.clusterIndex)

    def _load_clusters(self) -> None:
        count = uw_interop.uwClustersCount()
        for i in range(count):
            cluster = uw_interop.uwCluster(i)
            self._clusters_neighbors.append(cluster.neighborsIndices)
            self._map_cluster_to_tile.append(cluster.centerTileIndex)

    def _load(self) -> None:
        uw_interop.uwLog(UwSeverityEnum.Info, "loading map")
        self._reset()
        self._load_info()
        self._starting_positions = uw_interop.uwMapStartingPositions().data
        self._load_tiles()
        self._load_clusters()
        uw_interop.uwLog(UwSeverityEnum.Info, "map loaded")

    def _map_state(self, state: UwMapStateEnum) -> None:
        if state == UwMapStateEnum.Loaded:
            self._load()


uw_map = Map()
