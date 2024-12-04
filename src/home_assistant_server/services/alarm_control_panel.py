from typing import Dict, Any, List
from pydantic import BaseModel
from ..models.alarm_control_panel import AlarmControlPanelState, AlarmControlPanelAttributes, AlarmControlPanelMode, AlarmControlPanelDescription
from ..models.entity import EntityDomain
from ._base import BaseService

import logging
logger = logging.getLogger(__name__)

class AlarmControlPanelControl(BaseModel):
    entity_id: str

    @classmethod
    def get_llm_schema(cls, supported_features: List[str] = None) -> dict:
        """Generate schema based on supported features
        
        Args:
            supported_features: List of feature names to include in schema
        """
        # Base schema always includes entity_id
        schema = {
            "type": "object",
            "parameters": {
                "entity_id": {
                    "type": "string",
                    "description": "The ID of the light to control"
                }
            },
            "required": ["entity_id"]
        }
        
        # Feature-specific schema additions
        feature_schemas = {
            "alarm_mode": {
                "alarm_mode": {
                    "type": "string",
                    "description": "The mode of the alarm control panel",
                    "enum": [mode.value for mode in AlarmControlPanelMode],
                    "optional": False
                }
            },
            "code": {
                "code": {
                    "type": "string",
                    "description": "The code to arm the alarm control panel",
                    "optional": True
                }
            }
        }
    
        # Add properties based on supported features
        if supported_features:
            for feature in supported_features:
                if feature in feature_schemas:
                    schema["parameters"].update(feature_schemas[feature])
        
        return schema
    
class AlarmControlPanelService(BaseService[AlarmControlPanelState, AlarmControlPanelDescription]):
    """Service for controlling alarm control panel entities"""
    domain = EntityDomain.ALARM_CONTROL_PANEL
    
    tools = {
      "disarm": {
          "name": "alarm_control_panel.disarm",
          "description": "Disarm an alarm control panel entity",
          "schema": AlarmControlPanelControl.get_llm_schema(["code"])
      }, 
      "arm": {
          "name": "alarm_control_panel.arm",
          "description": "Arm the alarm control panel entity",
          "schema": AlarmControlPanelControl.get_llm_schema(["code", "alarm_mode"])
      }
    }

    async def disarm(self, entity_id: str, code: str = None) -> dict:
        """Disarm an alarm control panel entity"""
        data = {"entity_id": f"alarm_control_panel.{entity_id}", "code": code}
        return await self.call_domain_service("alarm_disarm", data)
  
    async def arm(self, entity_id: str, code: str = None, alarm_mode: AlarmControlPanelMode = None) -> dict:
        """Arm an alarm control panel entity"""
        data = {"entity_id": f"alarm_control_panel.{entity_id}", "code": code}
        return await self.call_domain_service(f"alarm_{alarm_mode}", data)
    
    @classmethod
    def get_available_entities(cls) -> Dict[str, AlarmControlPanelDescription]:
        """Get all available alarm control panel entities"""
        return {
            "alarm_control_panel": AlarmControlPanelDescription(
                domain=cls.domain,
                name="security",
                description="Main alarm control panel",
                supported_states=list(AlarmControlPanelState),
                attributes=AlarmControlPanelAttributes,
                available_tools=["disarm", "arm"]
            ),
            # Add more climate entities here
        }
