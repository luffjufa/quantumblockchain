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

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(entangled_background_daemon())
    yield
    task.cancel()

app = FastAPI(title="Logos JUFA V3 Sovereign Master Core", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "logos_jufa_ledger.db"
CONNECTED_PEERS = set()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS blocks (
                        block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prev_hash TEXT,
                        merkle_root TEXT,
                        invariant REAL,
                        jufa_potential REAL,
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
    cursor.execute("SELECT COUNT(*) FROM accounts")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", ("23799E75DDCB3260", 1000000.0, 0))
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", ("4A911C82FE33910B", 500000.0, 0))
        cursor.execute("INSERT INTO assets VALUES ('LOGOS', 'Logos Quantum Currency', 100000000.0, 42.50)")
        cursor.execute("INSERT INTO assets VALUES ('NXST', 'Nexus Global Tech Equities', 1000000.0, 150.00)")
        conn.commit()
    conn.close()

init_db()

def calculate_jufa_potential(memory_ratio: float, t: float) -> dict:
    c = 299792458.0
    G = 6.67430e-11
    hbar = 1.05457182e-34
    schwarzschild_prefactor = (2.0 * G) / (c ** 2)
    fibonacci_growth = 1.61803398875 * (1.0 + math.sin(t * 0.1))
    wqm = 0.5 + (memory_ratio * 0.5)
    time_denominator = max(t % 100.0, 0.001)
    information_entropy = max(memory_ratio * math.pi, 0.01)
    u_n = (schwarzschild_prefactor * 1e30 * (fibonacci_growth * hbar * wqm)) / (time_denominator * information_entropy)
    l_planck = 1.616255e-35
    s_entropy = memory_ratio * 138.0
    k_boltzmann = 1.380649e-23
    holographic_boundary = l_planck * math.sqrt(max(s_entropy / (math.pi * k_boltzmann), 0.0))
    braid_invariant = round(math.sin(t * 0.5) * memory_ratio * math.pi, 4)
    spectral_entropy = round(0.5 + (memory_ratio * 0.3), 3)
    return {
        "jufa_potential": float(f"{u_n:.6e}"),
        "holographic_boundary": float(f"{holographic_boundary:.6e}"),
        "spectral_entropy": spectral_entropy,
        "braid_invariant": braid_invariant,
        "natc_status": "STABLE_PHASE_BOUNCE" if abs(braid_invariant) > 0.0001 else "RE_PHASING"
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
            mem_ratio = psutil.virtual_memory().percent / 100.0
            metrics = calculate_jufa_potential(mem_ratio, t)
            
            cursor.execute("INSERT INTO blocks (prev_hash, merkle_root, invariant, jufa_potential, timestamp) VALUES (?, ?, ?, ?, ?)",
                           (prev_hash, hashlib.sha256(str(t).encode()).hexdigest(), metrics["braid_invariant"], str(metrics["jufa_potential"]), t))
            
            cursor.execute("SELECT symbol, price FROM assets")
            for symbol, current_price in cursor.fetchall():
                flux_factor = 1.0 + (metrics["braid_invariant"] * 0.02) + (math.sin(t * 0.5) * 0.005)
                new_price = round(max(current_price * flux_factor, 1.0), 2)
                cursor.execute("UPDATE assets SET price = ? WHERE symbol = ?", (new_price, symbol))
                
            conn.commit()
            conn.close()
            print(f"[SOVEREIGN MASTER] Block #{new_id} Minted // Invariant: {metrics['braid_invariant']}")
        except Exception as e:
            print(f"[MASTER ERROR] {e}")

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

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid transfer amount.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, nonce FROM accounts WHERE pubkey = ?", (sender,))
    sender_row = cursor.fetchone()
    if not sender_row or sender_row[0] < amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid balance or account.")

    cursor.execute("SELECT balance FROM accounts WHERE pubkey = ?", (recipient,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", (recipient, 0.0, 0))

    cursor.execute("UPDATE accounts SET balance = balance - ?, nonce = nonce + 1 WHERE pubkey = ?", (amount, sender))
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE pubkey = ?", (amount, recipient))
    conn.commit()
    conn.close()

    await broadcast_to_mesh({"type": "TRANSACTION", "tx": tx})
    return {"status": "SUCCESS", "message": f"Transfer of {amount} LOGOS executed."}

@app.get("/telemetry")
def get_telemetry():
    mem = psutil.virtual_memory()
    mem_usage_ratio = mem.percent / 100.0
    t = time.time()
    jufa_metrics = calculate_jufa_potential(mem_usage_ratio, t)
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
        "total_blocks": block_count,
        "assets": assets,
        "latest_tensor_metrics": jufa_metrics,
        "latest_invariant": jufa_metrics["braid_invariant"],
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
    print("[+] Launching Logos Sovereign Master Core...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
