from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from game_state import GameState
from agent_logic import interpret_task

app = FastAPI()
game = GameState()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player_id = await game.connect_player(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            response = game.handle_input(player_id, data)
            await websocket.send_json(response)
    except:
        game.disconnect_player(player_id)
        
@app.get("/world")
def get_world():
    return JSONResponse([tile.model_dump() for tile in game.grid])

@app.get("/agents")
def get_agents():
    return [agent.model_dump() for agent in game.agents]

@app.on_event("startup")
async def start_agent_walking():
    async def loop():
        while True:
            game.step_agents()
            await asyncio.sleep(2)  # every 2 seconds
    asyncio.create_task(loop())

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
    # Note: In production, you might want to set `reload=False` and use a proper ASGI server
    # like Daphne or Uvicorn with Gunicorn for better performance.
    # Also, consider using environment variables for configuration settings like port number.  
    