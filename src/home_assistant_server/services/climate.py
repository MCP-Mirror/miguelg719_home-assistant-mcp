from typing import Dict, Any, List
from pydantic import BaseModel
from ..models.climate import ClimateState, ClimateAttributes, ClimateDescription
from ..models.entity import EntityDomain
from ._base import BaseService

import logging
logger = logging.getLogger(__name__)

class ClimateControl(BaseModel):
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
                    "description": "The ID of the climate entity to control"
                }
            },
            "required": ["entity_id"]
        }
        
        # Feature-specific schema additions
        feature_schemas = {
            "temperature": {
                "temperature": {
                    "type": "integer",
                    "description": "The target temperature in degrees Fahrenheit",
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

class ClimateService(BaseService[ClimateState, ClimateDescription]):
  """Climate domain service handler"""
  domain = EntityDomain.CLIMATE

  tools = {
      "turn_off": {
          "name": "climate.turn_off",
          "description": "Turn off a climate entity",
          "schema": ClimateControl.get_llm_schema()
      }, 
      "set_temperature": {
          "name": "climate.set_temperature",
          "description": "Set the temperature of a climate entity",
          "schema": ClimateControl.get_llm_schema(["temperature"])
      },
      # "set_humidity": {
      #     "name": "climate_set_humidity",
      #     "description": "Set the humidity of a climate entity",
      #     "schema": ClimateControl.get_llm_schema(["target_humidity"])
      # },
      # "set_temperature_range": {
      #     "name": "climate_set_temperature_range",
      #     "description": "Set the temperature range of a climate entity",
      #     "schema": ClimateControl.get_llm_schema(["target_temperature_high", "target_temperature_low"])
      # },
      # "set_mode": {
      #     "name": "climate_set_mode",
      #     "description": "Set the mode of a climate entity",
      #     "schema": ClimateControl.get_llm_schema(["mode"])
      # }
  }

  async def turn_off(self, entity_id: str) -> dict:
      """Turn off a climate"""
      data = {"entity_id": f"climate.{entity_id}"}
      return await self.call_domain_service("turn_off", data)

  async def set_temperature(self, entity_id: str, temperature: int) -> dict:
      """Set the temperature of a climate entity"""
      data = {"entity_id": f"climate.{entity_id}", "temperature": temperature}
      return await self.call_domain_service("set_temperature", data)

  async def get_state(self, entity_id: str) -> dict:
      """Get the current state of a climate"""
      return await self.get_entity_state(entity_id)

  @classmethod
  def get_available_entities(cls) -> Dict[str, ClimateDescription]:
      """Get all available climate entities"""
      return {
          "climate": ClimateDescription(
              domain=cls.domain,
              name="hvac",
              description="Main climate hvac",
              supported_states=[ClimateState.OFF, ClimateState.AUTO],
              attributes=ClimateAttributes,
              available_tools=["turn_off", "get_state", "set_temperature"]
          ),
          # Add more climate entities here
      }