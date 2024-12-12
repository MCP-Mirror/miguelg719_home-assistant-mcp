from typing import Dict, Any, List
from pydantic import BaseModel
from ..models.humidifier import HumidifierState, HumidifierAttributes, HumidifierDescription
from ..models.entity import EntityDomain
from ._base import BaseService

import logging
logger = logging.getLogger(__name__)

class HumidifierControl(BaseModel):
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
                    "description": "The ID of the humidifier entity to control"
                }
            },
            "required": ["entity_id"]
        }
        
        # Feature-specific schema additions
        feature_schemas = {
            "humidity": {
                "humidity": {
                    "type": "int",
                    "description": "The target percentage humidity",
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

class HumidifierService(BaseService[HumidifierState, HumidifierDescription]):
  """Humidifier domain service handler"""
  domain = EntityDomain.HUMIDIFIER

  tools = {
      "turn_on": {
          "name": "humidifier-turn_on",
          "description": "Turn on a humidifier entity",
          "schema": HumidifierControl.get_llm_schema()
      },
      "turn_off": {
          "name": "humidifier-turn_off",
          "description": "Turn off a humidifier entity",
          "schema": HumidifierControl.get_llm_schema()
      }, 
      "set_humidity": {
          "name": "humidifier-set_temperature",
          "description": "Set the temperature of a humidifier entity",
          "schema": HumidifierControl.get_llm_schema(["humidity"])
      },
      # "set_mode": {
      #     "name": "humidifier-sset_mode",
      #     "description": "Set the mode of a humidifiere entity",
      #     "schema": ClimateControl.get_llm_schema(["mode"])
      # }
  }

  async def turn_on(self, entity_id: str) -> dict:
      """Turn on a humdifier"""
      data = {"entity_id": f"humdifier.{entity_id}"}
      return await self.call_domain_service("turn_on", data)

  async def turn_off(self, entity_id: str) -> dict:
      """Turn off a humdifier"""
      data = {"entity_id": f"humdifier.{entity_id}"}
      return await self.call_domain_service("turn_off", data)

  async def set_humidity(self, entity_id: str, humidity: int) -> dict:
      """Set the temperature of a humidifier entity"""
      data = {"entity_id": f"humdifier.{entity_id}", "humidity": humidity}
      logger.info(data)
      return await self.call_domain_service("set_humidity", data)

  async def get_state(self, entity_id: str) -> dict:
      """Get the current state of a humidifier"""
      return await self.get_entity_state(entity_id)

  @classmethod
  def get_available_entities(cls) -> Dict[str, HumidifierDescription]:
      """Get all available humidifier entities"""
      return {
          "humidifier": HumidifierDescription(
              domain=cls.domain,
              name="dehumidifier",
              description="Main dehumidifier entity",
              supported_states=[HumidifierState.OFF, HumidifierState.ON],
              attributes=HumidifierAttributes,
              available_tools=["turn_on", "turn_off", "get_state", "set_humidity"]
          ),
          # Add more humidifier entities here
      }