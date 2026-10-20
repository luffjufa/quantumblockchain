import asyncio
import json
import os
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

    def get_ledger_metrics(self):
        """Retrieves live local wallet and ledger statistics securely."""
        balance = 1000.0 # Default baseline sovereign reserve
        wallet_file = "wallet_keystore.json"
        if os.path.exists(wallet_file):
            try:
                with open(wallet_file, "r") as f:
                    data = json.load(f)
                    balance = data.get("balance", 1000.0)
            except Exception:
                pass
        return {
            "balance": balance,
            "active_peers_count": len(self.connected_peers)
        }

    async def broadcast_telemetry(self, websocket, path):
        await self.register(websocket)
        try:
            while True:
                telemetry = {
                    "node": "The Architect - Sovereign Master Core",
                    "status": "ONLINE",
                    "manifold_state": self.physics.compute_commutator_field(),
                    "ledger_state": self.get_ledger_metrics()
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
