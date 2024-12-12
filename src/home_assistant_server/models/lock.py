from .entity import EntityDescription, EntityAttributes, EntityDomain
from enum import Enum

class LockState(str, Enum):
    """States specific to locks"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    LOCKING = "locking"
    UNLOCKING = "unlocking"

class LockAttributes(EntityAttributes):
    """Attributes for lock entities"""
    # brightness_pct: int | None = None
    # color_temp: int | None = None
    # rgb_color: tuple[int, int, int] | None = None
    # supported_color_modes: list[str] = []

class LockDescription(EntityDescription[LockState]):
    """lock-specific entity description"""
    domain: EntityDomain = EntityDomain.LOCK
    attributes: type[EntityAttributes] = LockAttributes
    supported_states: list[LockState]  # Type-safe states for locks