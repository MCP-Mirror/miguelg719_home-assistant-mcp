from typing import Dict, Any, List
from pydantic import BaseModel
from ..models.light import LightState, LightAttributes, LightDescription
from ..models.entity import EntityDomain
from ._base import BaseService

class LightControl(BaseModel):
    entity_id: str
    brightness_pct: int | None = None
    rgb_color: tuple[int, int, int] | None = None
    color_temp: int | None = None

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
            "brightness": {
                "brightness_pct": {
                    "type": "integer",
                    "description": "Brightness level (0-100)",
                    "minimum": 0,
                    "maximum": 100,
                    "optional": True
                }
            },
            "color": {
                "rgb_color": {
                    "type": "array",
                    "description": "RGB color values [red, green, blue]",
                    "items": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255
                    },
                    "minItems": 3,
                    "maxItems": 3,
                    "optional": True
                }
            },
            "color_temp": {
                "color_temp": {
                    "type": "integer",
                    "description": "Color temperature in Kelvin",
                    "minimum": 2000,
                    "maximum": 6500,
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

class LightService(BaseService[LightState, LightDescription]):
  """Light domain service handler"""
  domain = EntityDomain.LIGHT

  # Tool definitions for this domain
  tools = {
      "turn_on": {
          "name": "light_turn_on",
          "description": "Turn on a light with optional brightness and color settings",
          "schema": LightControl.get_llm_schema(["brightness", "color", "color_temp"])
      },
      "turn_off": {
          "name": "light_turn_off",
          "description": "Turn off a light",
          "schema": LightControl.get_llm_schema()
      }
      # "set_brightness": {
      #     "name": "light_set_brightness",
      #     "description": "Set light brightness",
      #     "schema": LightControl.get_llm_schema(["brightness"])
      # },
      # "set_color": {
      #     "name": "light_set_color",
      #     "description": "Set light color",
      #     "schema": LightControl.get_llm_schema(["color"])
      # },
      # "get_state": {
      #     "name": "light_get_state",
      #     "description": "Get the current state of a light",
      #     "schema": LightControl.get_llm_schema()
      # }
  }

  async def turn_on(self, entity_id: str, brightness_pct: int = -1) -> dict:
      """Turn on a light with optional brightness"""
      data = {"entity_id": f"light.{entity_id}"}
      if 0 <= brightness_pct <= 100:
          data["brightness_pct"] = brightness_pct
      return await self.call_domain_service("turn_on", data)

  async def turn_off(self, entity_id: str) -> dict:
      """Turn off a light"""
      data = {"entity_id": f"light.{entity_id}"}
      return await self.call_domain_service("turn_off", data)

  async def get_state(self, entity_id: str) -> dict:
      """Get the current state of a light"""
      return await self.get_entity_state(entity_id)

  @classmethod
  def get_available_entities(cls) -> Dict[str, LightDescription]:
      """Get all available light entities"""
      return {
          "ceiling_lights": LightDescription(
              domain=cls.domain,
              name="Ceiling Lights",
              description="Main Ceiling lights",
              supported_states=[LightState.ON, LightState.OFF],
              attributes=LightAttributes,
              available_tools=["turn_on", "turn_off", "get_state"]
          ),
          # Add more light entities here
      }