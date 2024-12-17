from typing import Dict, Any, List
from pydantic import BaseModel
from ..models.lock import LockState, LockAttributes, LockDescription
from ..models.entity import EntityDomain
from ._base import BaseService

class LockControl(BaseModel):
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
                    "description": "The ID of the lock to control"
                }
            },
            "required": ["entity_id"]
        }
        
        # Feature-specific schema additions
        feature_schemas = {
        }
        
        # Add properties based on supported features
        if supported_features:
            for feature in supported_features:
                if feature in feature_schemas:
                    schema["parameters"].update(feature_schemas[feature])
        
        return schema

class LockService(BaseService[LockState, LockDescription]):
  """Lock domain service handler"""
  domain = EntityDomain.LOCK

  # Tool definitions for this domain
  tools = {
      "lock": {
          "name": "lock-lock",
          "description": "Lock (enable) a lock entity", 
          "schema": LockControl.get_llm_schema()
      },
      "unlock": {
          "name": "lock-unlock",
          "description": "Unlock (disable) a lock entity",
          "schema": LockControl.get_llm_schema()
      }
      # "set_brightness": {
      #     "name": "lock-set_brightness",
      #     "description": "Set lock brightness",
      #     "schema": LockControl.get_llm_schema(["brightness"])
      # },
      # "set_color": {
      #     "name": "lock-set_color",
      #     "description": "Set lock color",
      #     "schema": LockControl.get_llm_schema(["color"])
      # },
      # "get_state": {
      #     "name": "lock-get_state",
      #     "description": "Get the current state of a lock",
      #     "schema": LockControl.get_llm_schema()
      # }
  }

  async def lock(self, entity_id: str) -> dict:
      """Turn on a lock"""
      data = {"entity_id": f"lock.{entity_id}"}
      return await self.call_domain_service("lock", data)

  async def unlock(self, entity_id: str) -> dict:
      """Turn off"""
      data = {"entity_id": f"lock.{entity_id}"}
      return await self.call_domain_service("unlock", data)

  async def get_state(self, entity_id: str) -> dict:
      """Get the current state of a lock"""
      return await self.get_entity_state(entity_id)

  @classmethod
  def get_available_entities(cls) -> Dict[str, LockDescription]:
      """Get all available lock entities"""
      return {
          "front_door": LockDescription(
              domain=cls.domain,
              name="Front door lock",
              description="Main house lock",
              supported_states=[LockState.UNLOCKED, LockState.UNLOCKING, LockState.LOCKED, LockState.LOCKING],
              attributes=LockAttributes,
              available_tools=["unlock", "lock", "get_state"]
          ),
          # Add more lock entities here
      }