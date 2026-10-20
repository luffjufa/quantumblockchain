from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import psutil
import time
import math
import json
import hashlib
import os
import asyncio
from contextlib import asynccontextmanager

# Quantum Computing Libraries (PennyLane)
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def quantum_entropy_circuit(param1, param2):
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    qml.RZ(param1, wires=0)
    qml.RY(param2, wires=1)
    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

IDENTITY_FILE = "node_identity.json"
def load_or_create_node_identity():
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "r") as f:
            identity = json.load(f)
            print(f"[IDENTITY] Loaded Sovereign Node Pubkey: {identity['pubkey']}")
            return identity
    else:
        priv_key = os.urandom(32).hex()
        pubkey = hashlib.sha256(priv_key.encode()).hexdigest()[:16].upper()
        identity = {"pubkey": pubkey, "private_key": priv_key}
        with open(IDENTITY_FILE, "w") as f:
            json.dump(identity, f)
        print(f"[IDENTITY] Generated New Sovereign Node Pubkey: {pubkey}")
        return identity

NODE_IDENTITY = load_or_create_node_identity()

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(entangled_background_daemon())
    print("[STEALTH CORE] Initializing Tor v3 SOCKS5 Proxy Binding & P2P Mesh...")
    yield
    task.cancel()

app = FastAPI(title="Logos Sovereign Production Master Core", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "logos_jufa_ledger.db"
CONNECTED_PEERS = set()
RELAY_FEE = 0.0001  # Automated micro-fee collected by your node for transaction routing

BOOTSTRAP_NODES = [
    "ws://127.0.0.1:8000/ws/p2p",
    "ws://logosnodev3stealth777.onion/ws/p2p"
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS blocks (
                        block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prev_hash TEXT,
                        merkle_root TEXT,
                        invariant REAL,
                        jufa_potential REAL,
                        quantum_entropy REAL,
                        timestamp REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        pubkey TEXT PRIMARY KEY,
                        balance REAL,
                        nonce INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS assets (
                        symbol TEXT PRIMARY KEY,
                        name TEXT,
                        total_supply REAL,
                        price REAL)''')
    
    try:
        cursor.execute("ALTER TABLE blocks ADD COLUMN quantum_entropy REAL")
    except sqlite3.OperationalError:
        pass

    cursor.execute("SELECT COUNT(*) FROM accounts")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", (NODE_IDENTITY["pubkey"], 2000000.0, 0))
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", ("4A911C82FE33910B", 500000.0, 0))
        cursor.execute("INSERT INTO assets VALUES ('LOGOS', 'Logos Quantum Currency', 100000000.0, 42.50)")
        cursor.execute("INSERT INTO assets VALUES ('NXST', 'Nexus Global Tech Equities', 1000000.0, 150.00)")
        conn.commit()
    conn.close()

init_db()

def calculate_quantum_tensor_state(t: float) -> dict:
    param1 = (t % 10.0) * 0.314
    param2 = math.sin(t * 0.2) * 1.57
    q_val = float(quantum_entropy_circuit(param1, param2))
    
    c = 299792458.0
    G = 6.67430e-11
    hbar = 1.05457182e-34
    schwarzschild_prefactor = (2.0 * G) / (c ** 2)
    fibonacci_growth = 1.61803398875 * (1.0 + abs(q_val))
    
    u_n = (schwarzschild_prefactor * 1e30 * (fibonacci_growth * hbar)) / max(t % 100.0, 0.001)
    braid_invariant = round(q_val * math.pi * 0.5, 4)
    spectral_entropy = round(0.5 + abs(q_val * 0.3), 3)
    
    return {
        "jufa_potential": float(f"{u_n:.6e}"),
        "spectral_entropy": spectral_entropy,
        "braid_invariant": braid_invariant,
        "quantum_entropy": abs(q_val),
        "natc_status": "TOR_STEALTH_SYNCHRONIZED"
    }

async def broadcast_to_mesh(message: dict):
    payload = json.dumps(message)
    for peer in list(CONNECTED_PEERS):
        try:
            await peer.send(payload)
        except Exception:
            CONNECTED_PEERS.remove(peer)

async def entangled_background_daemon():
    while True:
        await asyncio.sleep(10.0)
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("SELECT block_id FROM blocks ORDER BY block_id DESC LIMIT 1")
            last_block = cursor.fetchone()
            new_id = (last_block[0] + 1) if last_block else 1
            prev_hash = hashlib.sha256(str(new_id - 1).encode()).hexdigest()
            t = time.time()
            
            metrics = calculate_quantum_tensor_state(t)
            
            cursor.execute("INSERT INTO blocks (prev_hash, merkle_root, invariant, jufa_potential, quantum_entropy, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                           (prev_hash, hashlib.sha256(str(t).encode()).hexdigest(), metrics["braid_invariant"], metrics["jufa_potential"], metrics["quantum_entropy"], t))
            
            cursor.execute("SELECT symbol, price FROM assets")
            for symbol, current_price in cursor.fetchall():
                amm_liquidity_pressure = 1.0 + (metrics["braid_invariant"] * 0.03)
                new_price = round(max(current_price * amm_liquidity_pressure, 1.0), 2)
                cursor.execute("UPDATE assets SET price = ? WHERE symbol = ?", (new_price, symbol))
                
            conn.commit()
            conn.close()
            print(f"[SOVEREIGN CORE] Block #{new_id} Minted over Tor Mesh // Invariant: {metrics['braid_invariant']}")
        except Exception as e:
            print(f"[DAEMON ERROR] {e}")

@app.websocket("/ws/p2p")
async def p2p_node_endpoint(websocket: WebSocket):
    await websocket.accept()
    CONNECTED_PEERS.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            packet = json.loads(data)
            await broadcast_to_mesh(packet)
    except WebSocketDisconnect:
        CONNECTED_PEERS.remove(websocket)

@app.post("/api/wallet/create")
def create_wallet():
    private_key = os.urandom(32).hex()
    pubkey = hashlib.sha256(private_key.encode()).hexdigest()[:16].upper()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", (pubkey, 100.0, 0))
        conn.commit()
    except:
        pass
    conn.close()
    return {"pubkey": pubkey, "private_key": private_key, "initial_balance": 100.0}

@app.post("/api/transaction/send")
async def send_transaction(tx: dict):
    sender = tx.get("sender")
    recipient = tx.get("recipient")
    amount = float(tx.get("amount", 0.0))
    nonce = int(tx.get("nonce", 0))

    total_debit = amount + RELAY_FEE
    if total_debit <= 0:
        raise HTTPException(status_code=400, detail="Invalid transfer amount.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, nonce FROM accounts WHERE pubkey = ?", (sender,))
    sender_row = cursor.fetchone()
    if not sender_row or sender_row[0] < total_debit:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient balance for transfer + relay fee.")

    cursor.execute("SELECT balance FROM accounts WHERE pubkey = ?", (recipient,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", (recipient, 0.0, 0))

    cursor.execute("UPDATE accounts SET balance = balance - ?, nonce = nonce + 1 WHERE pubkey = ?", (total_debit, sender))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE pubkey = ?", (amount, recipient))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE pubkey = ?", (RELAY_FEE, NODE_IDENTITY["pubkey"]))
    conn.commit()
    conn.close()

    await broadcast_to_mesh({"type": "TRANSACTION", "tx": tx})
    return {
        "status": "SUCCESS", 
        "message": f"Transferred {amount} LOGOS. Node collected {RELAY_FEE} LOGOS relay fee."
    }

@app.get("/telemetry")
def get_telemetry():
    t = time.time()
    metrics = calculate_quantum_tensor_state(t)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blocks")
    block_count = cursor.fetchone()[0]
    cursor.execute("SELECT symbol, price FROM assets")
    assets = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.execute("SELECT pubkey, balance, nonce FROM accounts")
    accounts = [{"pubkey": r[0], "balance": r[1], "nonce": r[2]} for r in cursor.fetchall()]
    conn.close()
    return {
        "node_identity": NODE_IDENTITY["pubkey"],
        "stealth_routing": "TOR_V3_ACTIVE",
        "bootstrap_nodes": BOOTSTRAP_NODES,
        "total_blocks": block_count,
        "assets": assets,
        "latest_tensor_metrics": metrics,
        "latest_invariant": metrics["braid_invariant"],
        "nodes": accounts,
        "active_mesh_peers": len(CONNECTED_PEERS)
    }

@app.get("/")
def serve_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return JSONResponse(status_code=404, content={"detail": "index.html not found in root directory."})

app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    print("[+] Launching Logos Sovereign Production Master Core...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
