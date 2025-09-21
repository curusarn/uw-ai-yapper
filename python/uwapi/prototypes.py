import json
from dataclasses import dataclass, field
from typing import Dict, Any
from .interop import *
from .events import uw_events


@dataclass
class Prototype:
    id: int = 0
    type: UwPrototypeTypeEnum = UwPrototypeTypeEnum.Nothing
    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    tags: List[int] = field(default_factory=list)
    tagsNames: List[str] = field(default_factory=list)
    json: str = ""

    def tagged(self, tag: int) -> bool:
        return tag in self.tags

    def _load(self) -> None:
        self.type = uw_interop.uwPrototypeType(self.id)
        self.json = uw_interop.uwPrototypeJson(self.id)
        self.data = json.loads(self.json)
        self.name = self.data.get("name", "")
        self.tags = self.data.get("tags", [])
        self.tagsNames = self.data.get("tagsNames", [])


class Prototypes:
    _instance = None
    _all: Dict[int, Prototype] = {}
    _definitions: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            uw_events.on_map_state(cls._instance._map_state)
        return cls._instance

    def get(self, id: int) -> Prototype:
        return self._all[id]

    def type(self, id: int) -> UwPrototypeTypeEnum:
        p = self._all.get(id, None)
        if p is not None:
            return p.type
        return UwPrototypeTypeEnum.Nothing

    def name(self, id: int) -> str:
        p = self._all.get(id, None)
        return p.name if p is not None else ""

    def json(self, id: int) -> str:
        p = self._all.get(id, None)
        return p.json if p is not None else ""

    def definitions(self) -> Dict[str, Any]:
        return self._definitions

    def hashString(self, name: str) -> int:
        return uw_interop.uwHashString(name)

    def tagId(self, name: str) -> int:
        try:
            return self._definitions["tagsNames"].index(name)
        except ValueError:
            raise KeyError(f"tag name '{name}' not found")

    def _load(self) -> None:
        uw_interop.uwLog(UwSeverityEnum.Info, "loading prototypes")
        self._all.clear()
        self._definitions.clear()
        for id in uw_interop.uwAllPrototypes().ids:
            p = Prototype(id)
            p._load()
            self._all[id] = p
        self._definitions = json.loads(uw_interop.uwDefinitionsJson())
        uw_interop.uwLog(UwSeverityEnum.Info, "prototypes loaded")

    def _map_state(self, state: UwMapStateEnum) -> None:
        if state == UwMapStateEnum.Loaded:
            self._load()


uw_prototypes = Prototypes()
