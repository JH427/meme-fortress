import uuid
import random 
from models import Agent, Player, Tile
from agent_logic import interpret_task

class GameState:
    def __init__(self):
        self.players = {}
        self.agents = [
            Agent(name="TestAgent", trait="literal", x=random.randint(0, 9), y=random.randint(0, 9)),
            Agent(name="DoomAgent", trait="doomer", x=random.randint(0, 9), y=random.randint(0, 9)),
            Agent(name="ChaosAgent", trait="chaotic", x=random.randint(0, 9), y=random.randint(0, 9)),
            Agent(name="CloutAgent", trait="clout chaser", x=random.randint(0, 9), y=random.randint(0, 9)),
        ]
        self.grid = [Tile(x=x, y=y, type="empty") for x in range(10) for y in range(10)]

    async def connect_player(self, websocket):
        pid = str(uuid.uuid4())
        self.players[pid] = Player(id=pid, websocket=websocket)
        return pid

    def disconnect_player(self, pid):
        if pid in self.players:
            del self.players[pid]

    def handle_input(self, pid, data):
        command = data.get("command")
        agent = random.choice(self.agents)
        result = interpret_task(command, agent.trait)

        import re
        match = re.search(r"build (\w+) at (\d+),\s*(\d+)", command)
        if match:
            tile_type, x, y = match.group(1), int(match.group(2)), int(match.group(3))
            for tile in self.grid:
                if tile.x == x and tile.y == y:
                    tile.type = tile_type
                    result += f" — {agent.name} built a {tile_type} at ({x}, {y})"
                    break

        return {"agent": agent.name, "response": result}
    
    def step_agents(self):
        for agent in self.agents:
            agent.prev_x = agent.x
            agent.prev_y = agent.y
            agent.copium_level -= random.randint(1, 5)

            moved = False

            if agent.trait == "clout chaser" and agent.copium_level < 70:
                # Seek nearest copium_field
                fields = [t for t in self.grid if t.type == "copium_field"]
                if fields:
                    target = min(fields, key=lambda t: abs(agent.x - t.x) + abs(agent.y - t.y))
                    dx = target.x - agent.x
                    dy = target.y - agent.y
                    move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                    move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                    new_x = max(0, min(9, agent.x + move_x))
                    new_y = max(0, min(9, agent.y + move_y))

                    if not any(a.x == new_x and a.y == new_y for a in self.agents if a.name != agent.name):
                        agent.x = new_x
                        agent.y = new_y
                        moved = True

            if not moved:
                # Random wander fallback
                dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                new_x = max(0, min(9, agent.x + dx))
                new_y = max(0, min(9, agent.y + dy))

                if not any(a.x == new_x and a.y == new_y for a in self.agents if a.name != agent.name):
                    agent.x = new_x
                    agent.y = new_y
                    
            # ✅ Resource gathering happens HERE (after position is updated)
            tile = next((t for t in self.grid if t.x == agent.x and t.y == agent.y), None)
            if tile:
                if tile.type == "cringe_mine":
                    agent.inventory["cringe"] = agent.inventory.get("cringe", 0) + 1
                elif tile.type == "copium_field":
                    agent.inventory["copium"] = agent.inventory.get("copium", 0) + 1
                    
    def get_resource_totals(self):
        totals = {"cringe": 0, "copium": 0}
        for agent in self.agents:
            for k in totals:
                totals[k] += agent.inventory.get(k, 0)
        return totals




