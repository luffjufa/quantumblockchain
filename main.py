from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import psutil
import time
import math

app = FastAPI(title="Logos Sovereign Network Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated Node Registry & Mempool state
REGISTERED_NODES = [
    {"pubkey": "23799E75DDCB3260", "ip": "127.0.0.1", "status": "ACTIVE", "nonce": 12},
    {"pubkey": "4A911C82FE33910B", "ip": "192.168.1.104", "status": "SYNCED", "nonce": 8},
    {"pubkey": "7B388F110AAC442E", "ip": "192.168.1.112", "status": "SYNCED", "nonce": 15}
]

MEMPOOL_TXS = [
    {"txid": "tx_99a8f2", "sender": "23799E75DDCB3260", "amount": 5.0}
]

@app.get("/telemetry")
def get_telemetry():
    # Capture system memory state for holographic braid equations
    mem = psutil.virtual_memory()
    mem_usage_ratio = mem.percent / 100.0
    
    # Calculate Holographic Braid Invariant (Artin braid group mapping over system memory & time)
    t = time.time()
    braid_invariant = round(math.sin(t * 0.5) * mem_usage_ratio * 3.14159, 4)
    spectral_entropy = round(0.5 + (mem_usage_ratio * 0.3), 3)
    shear_factor = round(math.cos(t * 0.2) * 0.15, 3)

    return {
        "total_blocks": 2,
        "mempool_tx_count": len(MEMPOOL_TXS),
        "pending_ai_tasks": 0,
        "latest_tensor_metrics": {
            "spectral_entropy": spectral_entropy,
            "shear_factor": shear_factor,
            "memory_pressure": mem_usage_ratio
        },
        "latest_invariant": braid_invariant,
        "nodes": REGISTERED_NODES
    }

app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
