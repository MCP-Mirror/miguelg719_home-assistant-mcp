from .entity import EntityDescription, EntityAttributes, EntityDomain
from enum import Enum

class LightState(str, Enum):
    """States specific to lights"""
    ON = "on"
    OFF = "off"

class LightAttributes(EntityAttributes):
    """Attributes for light entities"""
    brightness_pct: int | None = None
    color_temp: int | None = None
    rgb_color: tuple[int, int, int] | None = None
    supported_color_modes: list[str] = []

class LightDescription(EntityDescription[LightState]):
    """Light-specific entity description"""
    domain: EntityDomain = EntityDomain.LIGHT
    attributes: type[EntityAttributes] = LightAttributes
    supported_states: list[LightState]  # Type-safe states for lights