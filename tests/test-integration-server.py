import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from home_assistant_mcp.server import turn_light_on

@pytest.mark.asyncio
@pytest.mark.integration  # Mark these tests as integration tests
async def test_real_light_on_success():
    # Test with brightness
    result = await turn_light_on('ceiling_lights', brightness_pct=50)
    assert 'state' in result
    print(result)
    
    # Test without brightness
    result = await turn_light_on('ceiling_lights')
    assert 'state' in result 