import asyncio
import logging
import json
from typing import Any
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types

logger = logging.getLogger(__name__)

class TCPServer(Server):
    def __init__(self, name: str, host: str = '127.0.0.1', port: int = 8888):
        super().__init__(name)
        self.host = host
        self.port = port

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                try:
                    request = json.loads(data.decode())
                    command = request.get('command')
                    logger.info(f"Received command: {command}")

                    response: dict[str, Any] = {}
                    
                    # Handle different request types
                    if command == 'list_prompts':
                        if types.ListPromptsRequest in self.request_handlers:
                            handler = self.request_handlers[types.ListPromptsRequest]
                            result = await handler(None)
                            # The prompts are directly in the result
                            prompts = result.prompts
                            # Convert prompts to dict
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
                        if types.GetPromptRequest in self.request_handlers:
                            handler = self.request_handlers[types.GetPromptRequest]
                            name = request.get('name')
                            arguments = request.get('arguments')
                            
                            # Create a GetPromptRequest object
                            req = types.GetPromptRequest(
                                params=types.GetPromptParams(
                                    name=name,
                                    arguments=arguments
                                )
                            )
                            
                            result = await handler(req)
                            # The prompt result is directly in the result
                            prompt_result = result
                            
                            # Convert result to dict
                            result_dict = {
                                'description': prompt_result.description,
                                'messages': [
                                    {
                                        'role': msg.role,
                                        'content': {
                                            'type': msg.content.type,
                                            'text': msg.content.text
                                        }
                                    }
                                    for msg in prompt_result.messages
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

                    # Send response
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
            logger.error(f"Error handling client: {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

    async def run_tcp(self):
        """Run the server using TCP instead of stdio"""
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        addr = server.sockets[0].getsockname()
        logger.info(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

# Example usage:
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create server instance
    server = TCPServer("example-server")

    # Add prompt capabilities (same as before)
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

    # Run the TCP server
    asyncio.run(server.run_tcp()) 