from typing import TypeVar, Generic, Dict, Any
from ..models.entity import EntityDomain, EntityDescription, BaseEntityState

StateT = TypeVar('StateT', bound=BaseEntityState)
DescT = TypeVar('DescT', bound=EntityDescription)

class BaseService(Generic[StateT, DescT]):
    domain: EntityDomain
    tools: Dict[str, Dict[str, Any]]
    
    def __init__(self, call_service, get_state):
        self._call_service = call_service
        self._get_state = get_state
        
    async def call_domain_service(self, service: str, data: dict) -> dict:
        """Call a service within this domain"""
        return await self._call_service(self.domain, service, data)
        
    async def get_entity_state(self, entity_id: str) -> dict:
        """Get state for an entity in this domain"""
        return await self._get_state(f"{self.domain.value}.{entity_id}")
        
    @classmethod
    def get_available_entities(cls) -> Dict[str, DescT]:
        """Override to provide domain-specific entities"""
        raise NotImplementedError