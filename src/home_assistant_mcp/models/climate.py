from .entity import EntityDescription, EntityAttributes, EntityDomain
from enum import Enum

class ClimateState(str, Enum):
    """States specific to climate entities"""
    OFF = "off"
    HEAT = "heat"
    COOL = "cool"
    HEAT_COOL = "heat_cool"
    DRY = "dry"
    FAN_ONLY = "fan_only"
    AUTO = "auto"

class ClimateAttributes(EntityAttributes):
    """Attributes for climate entities"""
    temperature: int | None = None
    current_temperature: int | None = None
    target_temperature: int | None = None
    target_temperature_high: int | None = None
    target_temperature_low: int | None = None
    current_humidity: int | None = None
    target_humidity: int | None = None
    supported_features: list[str] = []

class ClimateDescription(EntityDescription[ClimateState]):
    """Climate-specific entity description"""
    domain: EntityDomain = EntityDomain.CLIMATE
    attributes: type[EntityAttributes] = ClimateAttributes
    supported_states: list[ClimateState] 