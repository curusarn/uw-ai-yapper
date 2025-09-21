from .interop import *


class Commands:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def orders(self, unit_id: int) -> list[UwOrder]:
        return uw_interop.uwOrders(unit_id).orders

    def order(self, unit_id: int, order: UwOrder) -> None:
        uw_interop.uwOrder(unit_id, order)

    def stop(self) -> UwOrder:
        o = self._default_order()
        o.order = UwOrderTypeEnum.Stop
        return o

    def guard(self) -> UwOrder:
        o = self._default_order()
        o.order = UwOrderTypeEnum.Guard
        return o

    def run_to_position(self, position: int) -> UwOrder:
        o = self._default_order()
        o.position = position
        o.order = UwOrderTypeEnum.Run
        return o

    def run_to_entity(self, entity_id: int) -> UwOrder:
        o = self._default_order()
        o.entity = entity_id
        o.order = UwOrderTypeEnum.Run
        return o

    def fight_to_position(self, position: int) -> UwOrder:
        o = self._default_order()
        o.position = position
        o.order = UwOrderTypeEnum.Fight
        return o

    def fight_to_entity(self, entity_id: int) -> UwOrder:
        o = self._default_order()
        o.entity = entity_id
        o.order = UwOrderTypeEnum.Fight
        return o

    def place_construction(
        self,
        construction_proto: int,
        position: int,
        yaw: float = 0,
        recipe_proto: int = 0,
        priority: UwPriorityEnum = UwPriorityEnum.Normal,
    ) -> None:
        uw_interop.uwCommandPlaceConstruction(
            construction_proto, position, yaw, recipe_proto, priority
        )

    def set_recipe(self, unit_id: int, recipe_proto: int) -> None:
        uw_interop.uwCommandSetRecipe(unit_id, recipe_proto)

    def set_priority(self, unit_id: int, priority: UwPriorityEnum) -> None:
        uw_interop.uwCommandSetPriority(unit_id, priority)

    def load(self, unit_id: int, resource_proto: int) -> None:
        uw_interop.uwCommandLoad(unit_id, resource_proto)

    def unload(self, unit_id: int) -> None:
        uw_interop.uwCommandUnload(unit_id)

    def move(self, unit_id: int, position: int, yaw: float = 0) -> None:
        uw_interop.uwCommandMove(unit_id, position, yaw)

    def aim(self, unit_id: int, target_id: int) -> None:
        uw_interop.uwCommandAim(unit_id, target_id)

    def renounce_control(self, entity_id: int) -> None:
        uw_interop.uwCommandRenounceControl(entity_id)

    def self_destruct(self, entity_id: int) -> None:
        uw_interop.uwCommandSelfDestruct(entity_id)

    def _default_order(self) -> UwOrder:
        return UwOrder(
            INVALID, INVALID, UwOrderTypeEnum.Nothing, UwOrderPriorityFlags.User
        )


uw_commands = Commands()
