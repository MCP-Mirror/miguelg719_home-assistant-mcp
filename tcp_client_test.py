import asyncio
import json

async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    try:
        print("Connected to server...")

        # List prompts
        list_request = {
            'command': 'list_prompts'
        }
        writer.write(json.dumps(list_request).encode() + b'\n')
        await writer.drain()

        data = await reader.read(1024)
        prompts_response = json.loads(data.decode())
        print(f"Available prompts: {prompts_response}")

        # Get specific prompt
        get_prompt_request = {
            'command': 'get_prompt',
            'name': 'example-prompt',
            'arguments': None
        }
        writer.write(json.dumps(get_prompt_request).encode() + b'\n')
        await writer.drain()

        data = await reader.read(1024)
        prompt_response = json.loads(data.decode())
        print(f"Prompt details: {prompt_response}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 