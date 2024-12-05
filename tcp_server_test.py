# /// script
# dependencies = [
#   "mcp"
# ]
# ///
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import asyncio
import json
from dataclasses import asdict
from typing import Any

# Create a server instance
server = Server("example-server")

# Add prompt capabilities
@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="example-prompt",
            description="An example prompt template",
            arguments=[
                types.PromptArgument(
                    name="arg1",
                    description="Example argument",
                    required=True
                )
            ]
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str,
    arguments: dict[str, str] | None
) -> types.GetPromptResult:
    if name != "example-prompt":
        raise ValueError(f"Unknown prompt: {name}")

    return types.GetPromptResult(
        description="Example prompt",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="Example prompt text"
                )
            )
        ]
    )

async def handle_client(reader, writer):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
                
            try:
                request = json.loads(data.decode())
                command = request.get('command')
                
                response: dict[str, Any] = {}
                if command == 'list_prompts':
                    prompts = await handle_list_prompts()
                    # Convert each prompt object to a dict manually
                    prompt_list = []
                    for prompt in prompts:
                        prompt_dict = {
                            'name': prompt.name,
                            'description': prompt.description,
                            'arguments': [
                                {
                                    'name': arg.name,
                                    'description': arg.description,
                                    'required': arg.required
                                }
                                for arg in prompt.arguments
                            ]
                        }
                        prompt_list.append(prompt_dict)
                    
                    response = {
                        'status': 'success',
                        'prompts': prompt_list
                    }
                
                elif command == 'get_prompt':
                    name = request.get('name')
                    arguments = request.get('arguments')
                    result = await handle_get_prompt(name, arguments)
                    # Convert GetPromptResult to dict manually
                    result_dict = {
                        'description': result.description,
                        'messages': [
                            {
                                'role': msg.role,
                                'content': {
                                    'type': msg.content.type,
                                    'text': msg.content.text
                                }
                            }
                            for msg in result.messages
                        ]
                    }
                    response = {
                        'status': 'success',
                        'prompt': result_dict
                    }
                
                else:
                    response = {
                        'status': 'error',
                        'message': f'Unknown command: {command}'
                    }
                
                writer.write(json.dumps(response).encode() + b'\n')
                await writer.drain()
                
            except json.JSONDecodeError:
                error_response = {
                    'status': 'error',
                    'message': 'Invalid JSON format'
                }
                writer.write(json.dumps(error_response).encode() + b'\n')
                await writer.drain()
                
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception as e:
            print(f"Error closing connection: {e}")

async def run():
    server_socket = await asyncio.start_server(
        handle_client, '127.0.0.1', 8888
    )
    
    addr = server_socket.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server_socket:
        await server_socket.serve_forever()

if __name__ == "__main__":
    asyncio.run(run())