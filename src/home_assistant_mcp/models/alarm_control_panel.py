from .entity import EntityDescription, EntityAttributes, EntityDomain
from enum import Enum

class AlarmControlPanelState(str, Enum):
    """States specific to alarm control panel entities"""
    DISARMED = "disarmed"
    ARMED_HOME = "armed_home"
    ARMED_AWAY = "armed_away"
    ARMED_NIGHT = "armed_night"
    ARMED_VACATION = "armed_vacation"
    ARMED_CUSTOM_BYPASS = "armed_custom_bypass"
    PENDING = "pending"
    ARMING = "arming"
    DISARMING = "disarming"
    TRIGGERED = "triggered"


class AlarmControlPanelMode(str, Enum):
    """Modes for alarm control panel entities"""
    ARM_AWAY = "arm_away"
    ARM_HOME = "arm_home"
    ARM_NIGHT = "arm_night"
    ARM_VACATION = "arm_vacation"
    ARM_CUSTOM_BYPASS = "arm_custom_bypass"
    TRIGGER = "trigger"
    DISARM = "disarm"

class AlarmControlPanelCodeFormat(str, Enum):
    """Code formats for alarm control panel entities"""
    NONE = None
    NUMBER = "number"
    TEXT = "text"

class AlarmControlPanelAttributes(EntityAttributes):
    """Attributes for alarm control panel entities"""
    alarm_state: AlarmControlPanelState
    code_arm_required: bool = False
    code_format: AlarmControlPanelCodeFormat | None = None
    supported_features: list[str] = []

class AlarmControlPanelDescription(EntityDescription[AlarmControlPanelState]):
    """Alarm control panel-specific entity description"""
    domain: EntityDomain = EntityDomain.ALARM_CONTROL_PANEL
    attributes: type[EntityAttributes] = AlarmControlPanelAttributes
    supported_states: list[AlarmControlPanelState] 
