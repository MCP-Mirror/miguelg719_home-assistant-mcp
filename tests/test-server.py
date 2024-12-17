import pytest
from unittest.mock import patch, Mock
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from home_assistant_mcp.server import HomeAssistantServer

@pytest.mark.asyncio
async def test_turn_light_on_success():
    server = HomeAssistantServer()
    
    # Mock the httpx client call
    mock_response = Mock()
    mock_response.json.return_value = {'state': 'on', 'attributes': {'brightness': 100}}

    with patch('httpx.AsyncClient.post', return_value=mock_response):
        result = await server.turn_light_on('ceiling_lights', brightness_pct=100)
        assert result == {'state': 'on', 'attributes': {'brightness': 100}}

@pytest.mark.asyncio
async def test_turn_light_on_error():
    server = HomeAssistantServer()
    
    # Mock a failed request
    with patch('httpx.AsyncClient.post', side_effect=Exception('Connection error')):
        with pytest.raises(Exception, match='Connection error'):
            await server.turn_light_on('ceiling_lights')

@pytest.mark.asyncio
async def test_turn_light_on_no_brightness():
    server = HomeAssistantServer()
    
    mock_response = Mock()
    mock_response.json.return_value = {'state': 'on', 'attributes': {}}

    with patch('httpx.AsyncClient.post', return_value=mock_response):
        result = await server.turn_light_on('ceiling_lights')
        assert result == {'state': 'on', 'attributes': {}}