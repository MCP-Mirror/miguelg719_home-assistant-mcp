from enum import Enum
from pydantic import BaseModel
from typing import TypeVar, Generic

class BaseEntityState(str, Enum):
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"

class EntityDomain(str, Enum):
    LIGHT = "light"
    CLIMATE = "climate"
    SWITCH = "switch"
    SENSOR = "sensor"
    SECURITY = "security"

class EntityAttributes(BaseModel):
    """Base model for entity attributes"""
    friendly_name: str
    supported_features: list[str] = []
    device_class: str | None = None

StateT = TypeVar('StateT', bound=BaseEntityState)

class EntityDescription(BaseModel, Generic[StateT]):
    """Base description for all entities"""
    domain: EntityDomain
    name: str
    description: str
    supported_states: list[StateT]
    attributes: type[EntityAttributes]
    available_tools: list[str]