import asyncio
import json

class LogosP2PNode:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.peers = set()

    async def register_peer(self, peer_uri):
        self.peers.add(peer_uri)

    async def broadcast_block(self, block_data):
        payload = json.dumps({"type": "NEW_BLOCK", "data": block_data})
        for peer in self.peers:
            try:
                reader, writer = await asyncio.open_connection(*peer.split(":"))
                writer.write(payload.encode("utf-8"))
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def handle_connection(self, reader, writer):
        data = await reader.read(65536)
        if data:
            try:
                json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                pass
        writer.close()

    async def start_server(self):
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        async with server:
            await server.serve_forever()
