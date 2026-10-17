"""Day 20.5: deliberately offline. No environment or secret access."""
from typing import Literal
Mode = Literal['mock']
DEFAULT_MODE: Mode = 'mock'
LIVE_API_ENABLED = False

def get_mode() -> Mode:
    return 'mock'
