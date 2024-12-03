import os
import json
import logging
import sys
from collections.abc import Sequence
from typing import Dict, Any
import httpx
import asyncio
from dotenv import load_dotenv
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from home_assistant_server.models.entity import EntityDomain
from home_assistant_server.services.light import LightService
from home_assistant_server.services.climate import ClimateService
# Import other services as needed

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("HOMEASSISTANT_TOKEN")
HOMEASSISTANT_BASE_URL = os.getenv("HOMEASSISTANT_BASE_URL")

if not API_KEY:
    raise ValueError("HOMEASSISTANT_TOKEN is required. Please set it in the .env file.")
if not HOMEASSISTANT_BASE_URL:
    raise ValueError("HOMEASSISTANT_BASE_URL is required. Please set it in the .env file.")


class HomeAssistantServer:
    def __init__(self):
        self._services: Dict[EntityDomain, Any] = {}
        self._initialize_services()

    def _initialize_services(self):
        """Initialize service handlers"""
        self._services[EntityDomain.LIGHT] = LightService(
            call_service=self.call_service,
            get_state=self.get_entity_state
        )
        # Initialize other services here...
        self._services[EntityDomain.CLIMATE] = ClimateService(
            call_service=self.call_service,
            get_state=self.get_entity_state
        )

    async def get_entity_state(self, entity_id: str) -> dict:
        """Generic method to get any entity state"""
        url = f"{HOMEASSISTANT_BASE_URL}/api/states/{entity_id}"
        print(f"Getting state for {url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
            return response.json()

    async def call_service(
        self,
        domain: EntityDomain,
        service: str,
        data: dict
    ) -> dict:
        """Generic method to call any Home Assistant service"""
        url = f"{HOMEASSISTANT_BASE_URL}/api/services/{domain.value}/{service}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json=data
                )
                return response.json()
            except Exception as e:
                logger.error(f"Error calling service {service} for domain {domain}: {e}")
                raise e

    def get_all_tools(self) -> list[Tool]:
        """Collect all tools from registered services"""
        tools = []
        for service in self._services.values():
            for tool_id, tool_info in service.tools.items():
                tools.append(Tool(
                    name=tool_info["name"],
                    description=tool_info["description"],
                    inputSchema=tool_info["schema"]
                ))
            logger.info(tools)
        logger.info(f"Service tools: {service.tools}")
        return tools

    async def handle_tool_call(self, name: str, arguments: dict) -> dict:
        """Route tool calls to appropriate service handlers"""
        try:
            domain, service = name.split("_", 1)
            domain_enum = EntityDomain(domain)
            
            if domain_enum not in self._services:
                raise ValueError(f"Unsupported domain: {domain}")
                
            service_handler = self._services[domain_enum]
            method = getattr(service_handler, service, None)
            
            if not method:
                raise ValueError(f"Unsupported service {service} for domain {domain}")
                
            return await method(**arguments)
        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
            raise

async def serve() -> None:
    server = Server("home-assistant-server")
    ha_server = HomeAssistantServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available home assistant tools."""
        return ha_server.get_all_tools()

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for home assistant controls."""
        try:
            result = await ha_server.handle_tool_call(name, arguments)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            raise ValueError(f"Error processing home-assistant query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
    logger.info("Server running")

if __name__ == "__main__":
    asyncio.run(serve())