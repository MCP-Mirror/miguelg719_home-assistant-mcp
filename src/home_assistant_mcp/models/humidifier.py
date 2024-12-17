from .entity import EntityDescription, EntityAttributes, EntityDomain
from enum import Enum

class HumidifierState(str, Enum):
    """States specific to humidifiers"""
    ON = "on"
    OFF = "off"

class HumidifierAttributes(EntityAttributes):
    """Attributes for humidifier entities"""
    humidity: int | None = None
    current_humidity: int | None = None
    # target_temperature: int | None = None
    # target_temperature_high: int | None = None
    # target_temperature_low: int | None = None
    # current_humidity: int | None = None
    target_humidity: int | None = None
    supported_features: list[str] = []

class HumidifierDescription(EntityDescription[HumidifierState]):
    """Humidifier-specific entity description"""
    domain: EntityDomain = EntityDomain.HUMIDIFIER
    attributes: type[EntityAttributes] = HumidifierAttributes
    supported_states: list[HumidifierState] 