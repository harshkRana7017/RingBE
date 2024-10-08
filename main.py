import json
from typing import Dict
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware 
from Models import Users
from routers import calls, auth
from utils.get_user import get_current_user

app = FastAPI()

origins = [
    "http://localhost:5173",  # React app
    "http://localhost:8000",  # FastAPI app (if you ever need to call APIs from the same origin)
    # Add other origins as needed
]

app.add_middleware(CORSMiddleware, 
                   allow_origins=origins, 
                   allow_credentials=True, 
                   allow_methods=["*"],
                   allow_headers=["*"]
                   )

class ConnectionManger :
    def __init__(self):
        self.active_connections: Dict[str, WebSocket]={}

        async def connect(self, websocket:WebSocket, client_id:str):
            await websocket.accept()
            self.active_connections[client_id]=websocket

        async def disconnect(self,websocket:WebSocket, client_id:str):
            await websocket.close()
            self.active_connections[client_id].close()
            del self.active_connections[client_id]

        async def send_message(self,message: str, client_id:str):
            websocket: WebSocket= self.active_connections[client_id]
            if websocket:
                await websocket.send_text(message)

        async def broadcast(self, message:str):
            for websocket in self.active_connections.values():
                await websocket.send_text(message)

manager = ConnectionManger()



@app.websocket("/ws")
def websocket_endpoint(websocket:WebSocket,  user:Users= Depends(get_current_user)):
    client_id = user.id
    manager.connect(websocket, client_id)
    try:
        while True:
            data =  websocket.receive_text()
            message =json.loads(data)
            target_client_id = message.get("target_client_id")
            if target_client_id:
                manager.send_message(json.dump(message), target_client_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        


app.include_router(calls.router)
app.include_router(auth.router)

