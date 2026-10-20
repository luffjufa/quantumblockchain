import time
import hashlib
import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BLOCKCHAIN = []
MEMPOOL = []
CONNECTED_PEERS = []

@app.get("/telemetry")
def get_telemetry():
    latest_metrics = {"spectral_entropy": 0.65, "shear_factor": 0.04}
    latest_invariant = 8.5
    jufa_potential = "2.06e-23"
    holographic_boundary = "ACTIVE"
    
    if BLOCKCHAIN:
        latest_metrics = BLOCKCHAIN[-1].get("tensor_metrics", latest_metrics)
        latest_invariant = BLOCKCHAIN[-1].get("invariant", 8.5)
        
    return {
        "status": "online",
        "total_blocks": len(BLOCKCHAIN),
        "mempool_tx_count": len(MEMPOOL),
        "pending_ai_tasks": 0,
        "latest_tensor_metrics": latest_metrics,
        "latest_invariant": latest_invariant,
        "jufa_potential": jufa_potential,
        "holographic_boundary": holographic_boundary,
        "active_mesh_peers": len(CONNECTED_PEERS)
    }

app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("logos_core_daemon:app", host="127.0.0.1", port=8000, reload=True)
