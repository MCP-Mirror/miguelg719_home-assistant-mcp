#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime, timedelta
from collections.abc import Sequence
from functools import lru_cache
from typing import Any
from requests import post, get 
from mcp.server.models import InitializationOptions
import mcp
import httpx
import asyncio
from dotenv import load_dotenv
from mcp.server.stdio import stdio_server
from mcp.server import Server, NotificationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl, BaseModel, schema
from enum import Enum

import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Write to stderr so it doesn't interfere with stdio communication
)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("HOMEASSISTANT_TOKEN")

if not API_KEY:
    raise ValueError("HOMEASSISTANT_TOKEN is required. Please set it in the .env file.")

# HOMEASSISTANT_BASE_URL = os.getenv("HOMEASSISTANT_BASE_URL")
HOMEASSISTANT_BASE_URL = "http://localhost:8123"

if not HOMEASSISTANT_BASE_URL:
    raise ValueError("HOMEASSISTANT_BASE_URL is required. Please set it in the .env file.")


# TODO: ADD BETTER DESCRIPTION FOR THESE
# Define models for light control
class LightControl(BaseModel):
    entity_id: str
    brightness_pct: int = -1

class LightTools(str, Enum):
    TURN_ON = "light_turn_on"
    TURN_OFF = "light_turn_off"
    GET_STATE = "light_get_state"

# TODO: MIGRATE MORE FUNCTIONS

# Helper function for light control
async def turn_light_on(
    entity_id: str,
    brightness_pct: int = -1
):
    """
    A function that takes in a string and turns on a light

    Args:
        entity_id: The name of the light to be turned on. Options are ceiling_lights, bed_light.
        brightness_pct: The brightness level to turn the light on 

    Returns:
        A result string saying successful or unsuccesful command
    """
    logger.info(f"Turning on light {entity_id} with brightness {brightness_pct}")
    url = f"{HOMEASSISTANT_BASE_URL}/api/services/light/turn_on"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "content-type": "application/json",
    }

    # Initialize data with base configuration
    data = json.dumps({
        "entity_id": "light." + entity_id
    })

    # Add brightness only if valid value provided
    if brightness_pct >= 0 and brightness_pct <= 100:
        data = json.dumps({
            "entity_id": "light." + entity_id,
            "brightness_pct": brightness_pct
        })

    logger.info(f"Sending request to {url} with data: {data}")
    
    try:
        response = post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise exception for bad status codes
        
        if len(response.json()) > 0:
            state = response.json()[0]['state']
            logger.info(f"Light state: {state}")
            if state == "on":
                # Only include brightness in response if it exists in attributes
                if 'brightness' in response.json()[0]['attributes']:
                    logger.info(f"Brightness: {round(response.json()[0]['attributes']['brightness']/255*100)}")
                    return {
                        "state": state, 
                        "brightness": str(round(response.json()[0]['attributes']['brightness']/255 * 100))
                    }
                return {"state": state}
            else:
                return {"state": state}
        else:
            return {"state": "not updated"}
            
    except Exception as e:
        logger.error(f"Error turning on light: {str(e)}")
        return {"state": "error", "message": str(e)}


# @server.list_resources()
# async def handle_list_resources() -> list[Resource]:
#     """
#     List available light resources (eventually every other entity).
#     """
#     return [
#         Resource(
#             uri=AnyUrl(f"light://{name}/state"),
#             name=f"Light {name} state",
#             description=f"The state of the light",
#             mimeType="application/json",
#         )
#         for name in notes
#     ]

# @server.read_resource()
# async def handle_read_resource(uri: AnyUrl) -> str:
#     """
#     Read a specific note's content by its URI.
#     """
#     if uri.scheme != "note":
#         raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

#     name = uri.path
#     if name is not None:
#         name = name.lstrip("/")
#         return notes[name]
#     raise ValueError(f"Note not found: {name}")

async def serve():
    server = Server("home-assistant-server")
    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        """
        List available tools.
        Each tool specifies its arguments using JSON Schema validation.
        """
        return [
            Tool(
                name=LightTools.TURN_ON,
                description="Turn on a light with optional brightness",
                inputSchema=LightControl.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        """
        Handle tool execution requests.
        Tools can modify server state and notify clients of changes.
        """
        if name == LightTools.TURN_ON:
            result = await turn_light_on(
                arguments["entity_id"],
                arguments.get("brightness_pct", -1)
            )
            return [TextContent(
                type="text",
                text=f"Light control result: {result}"
            )]
        
        if name != LightTools.TURN_ON:
            raise ValueError(f"Unknown tool: {name}")

        if not arguments:
            raise ValueError("Missing arguments")


        # Update server state
        # notes[note_name] = content

        # # Notify clients that resources have changed
        # await server.request_context.session.send_resource_list_changed()
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
    print("Server running")


if __name__ == "__main__":
    asyncio.run(serve())