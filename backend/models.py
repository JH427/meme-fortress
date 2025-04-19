from fastapi import WebSocket
from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass

class Agent(BaseModel):
    name: str
    trait: str
    task: Optional[str] = None
    mood: int = 100
    copium_level: int = 100
    x: int = 0
    y: int = 0
    prev_x: int = 0
    prev_y: int = 0

class Tile(BaseModel):
    x: int
    y: int
    type: str  # "empty", "mine", "structure", etc.

@dataclass
class Player:
    id: str
    websocket: WebSocket
