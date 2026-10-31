"""
QUANT.FLOW // Institutional Crypto Sector Taxonomy & Rotation Dashboard Launcher
Starts the FastAPI server with live CoinGecko and DefiLlama feeds.
"""

import sys
import os
import uvicorn

# Ensure project path is loaded
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from backend.server import app

def find_available_port(start_port: int = 8088, max_attempts: int = 10) -> int:
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

if __name__ == "__main__":
    port = find_available_port(8088)
    print("=" * 70)
    print(">> QUANT.FLOW // INSTITUTIONAL SECTOR TAXONOMY & ROTATION SERVER <<")
    print(f">> UI Dashboard URL: http://localhost:{port}")
    print(f">> REST API Docs:    http://localhost:{port}/docs")
    print(f">> API Health Check: http://localhost:{port}/api/health")
    print("=" * 70)
    uvicorn.run("backend.server:app", host="127.0.0.1", port=port, reload=False, log_level="info")
