from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import sys
import os
import logging


# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

server_params = StdioServerParameters(
    command="python",
    args=["src/home_assistant_server/server.py"], # Optional command line arguments
    env=None # Optional environment variables
)

async def main():
    print("Starting client...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            print("Connected to server process...")
            async with ClientSession(read, write) as session:
                print("Created session, initializing...")
                await session.initialize()
                print("Session initialized!")

                # Test the connection by listing tools
                tools = await session.list_tools()
                print(f"Available tools: {tools}")

                # result = await session.call_tool("light.turn_on", arguments={"entity_id": "ceiling_lights", "brightness_pct": 25})
                # print(f"Tool result: {result}")

                # result = await session.call_tool("climate.turn_off", arguments={"entity_id": "hvac"})
                # print(f"Tool result: {result}")

                result = await session.call_tool("alarm_control_panel.disarm", arguments={"entity_id": "security", "code": "1234" })
                print(f"Tool result: {result}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 