from triple_vision.networking.client import Client
from triple_vision.networking.objects import GameState
from triple_vision.networking.utils import get_status

client = Client()

__all__ = ('client', 'GameState', 'get_status')
