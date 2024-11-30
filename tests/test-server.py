import pytest
from unittest.mock import patch, Mock
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from home_assistant_server.server import turn_light_on

@pytest.mark.asyncio
async def test_turn_light_on_success():
    # Mock the post request
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        'state': 'on',
        'attributes': {'brightness': 255}  # Full brightness
    }]

    with patch('home_assistant_server.server.post', return_value=mock_response):
        result = await turn_light_on('ceiling_lights', brightness_pct=100)
        
        assert result == {'state': 'on', 'brightness': '100'}

@pytest.mark.asyncio
async def test_turn_light_on_error():
    # Mock a failed request
    with patch('home_assistant_server.server.post', side_effect=Exception('Connection error')):
        result = await turn_light_on('ceiling_lights')
        
        assert result == {'state': 'error', 'message': 'Connection error'}

@pytest.mark.asyncio
async def test_turn_light_on_no_brightness():
    # Mock the post request without brightness
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        'state': 'on',
        'attributes': {}  # Add empty attributes dictionary
    }]

    with patch('home_assistant_server.server.post', return_value=mock_response):
        result = await turn_light_on('ceiling_lights')
        
        assert result == {'state': 'on'}