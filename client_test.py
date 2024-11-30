from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import sys
import os
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

server_params = StdioServerParameters(
    command="python",
    args=["server_test.py"], # Optional command line arguments
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
                
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 