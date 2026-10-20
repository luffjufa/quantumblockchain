import asyncio
import json
import websockets
from logos_physics_validator import LogosPhysicsEngine

class SovereignNodeNetwork:
    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        self.connected_peers = set()
        self.physics = LogosPhysicsEngine()

    async def register(self, websocket):
        self.connected_peers.add(websocket)
        print(f"[+] Peer connected. Total active peers: {len(self.connected_peers)}")

    async def unregister(self, websocket):
        self.connected_peers.remove(websocket)
        print(f"[-] Peer disconnected. Total active peers: {len(self.connected_peers)}")

    async def broadcast_telemetry(self, websocket, path):
        await self.register(websocket)
        try:
            while True:
                telemetry = {
                    "node": "The Architect - Sovereign Master Core",
                    "status": "ONLINE",
                    "manifold_state": self.physics.compute_commutator_field()
                }
                await websocket.send(json.dumps(telemetry))
                await asyncio.sleep(2.0)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def start_server(self):
        print(f"[*] Starting Sovereign P2P WebSocket Node on ws://{self.host}:{self.port}")
        async with websockets.serve(self.broadcast_telemetry, self.host, self.port):
            await asyncio.Future()

if __name__ == "__main__":
    node = SovereignNodeNetwork()
    try:
        asyncio.run(node.start_server())
    except KeyboardInterrupt:
        print("[!] Sovereign Node shut down gracefully by The Architect.")
