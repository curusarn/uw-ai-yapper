from dataclasses import dataclass
from typing import Optional
from .interop import *
from .prototypes import uw_prototypes, Prototype


def _make_empty_UwUnitUpgrades() -> UwUnitUpgrades:
    return UwUnitUpgrades(0, 0, 0, 0, 0, 0, 0)


@dataclass
class Entity:
    id: int
    fresh: bool = True
    destroyed: bool = False

    Proto: Optional[UwProtoComponent] = None
    Owner: Optional[UwOwnerComponent] = None
    Controller: Optional[UwControllerComponent] = None
    Position: Optional[UwPositionComponent] = None
    Unit: Optional[UwUnitComponent] = None
    Life: Optional[UwLifeComponent] = None
    Mana: Optional[UwManaComponent] = None
    Move: Optional[UwMoveComponent] = None
    Aim: Optional[UwAimComponent] = None
    Recipe: Optional[UwRecipeComponent] = None
    RecipeStatistics: Optional[UwRecipeStatisticsComponent] = None
    LogisticsTimestamp: Optional[UwLogisticsTimestampComponent] = None
    Priority: Optional[UwPriorityComponent] = None
    Amount: Optional[UwAmountComponent] = None
    Attachment: Optional[UwAttachmentComponent] = None
    Ping: Optional[UwPingComponent] = None
    Player: Optional[UwPlayerComponent] = None
    PlayerAiConfig: Optional[UwPlayerAiConfigComponent] = None
    Force: Optional[UwForceComponent] = None
    ForceDetails: Optional[UwForceDetailsComponent] = None
    ForeignPolicy: Optional[UwForeignPolicyComponent] = None
    DiplomacyProposal: Optional[UwDiplomacyProposalComponent] = None

    def pos(self) -> int:
        return self.Position.position if self.Position is not None else INVALID

    def policy(self) -> UwForeignPolicyEnum:
        from .world import uw_world

        return (
            uw_world.policy(self.Owner.force)
            if self.Owner is not None
            else UwForeignPolicyEnum.Nothing
        )

    def own(self) -> bool:
        from .world import uw_world

        return self.Owner is not None and self.Owner.force == uw_world.my_force_id()

    def ally(self) -> bool:
        return self.policy() == UwForeignPolicyEnum.Ally

    def enemy(self) -> bool:
        return self.policy() == UwForeignPolicyEnum.Enemy

    def type(self) -> UwPrototypeTypeEnum:
        return (
            uw_prototypes.type(self.Proto.proto)
            if self.Proto is not None
            else UwPrototypeTypeEnum.Nothing
        )

    def proto(self) -> Prototype:
        if self.Proto is not None:
            return uw_prototypes.get(self.Proto.proto)
        else:
            raise Exception("entity does not have a Proto")

    def unit_upgrades(self) -> UwUnitUpgrades:
        from .world import uw_world

        return (
            uw_world.unit_upgrades(self.id)
            if self.type() == UwPrototypeTypeEnum.Unit
            else _make_empty_UwUnitUpgrades()
        )

    def tagged(self, tag: int) -> bool:
        return self.proto().tagged(tag)
