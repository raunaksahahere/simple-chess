"""
Main FastAPI application with Socket.IO server for multiplayer chess.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import socketio
from rooms import RoomManager
from chess_engine import ChessEngine
from socket_manager import SocketManager
import uvicorn
import os


# Initialize components
room_manager = RoomManager()
# Use path relative to backend directory for Render compatibility
BASE_DIR = os.path.dirname(__file__)
stockfish_path = os.path.join(BASE_DIR, "stockfish", "stockfish")
chess_engine = ChessEngine(stockfish_path=stockfish_path)

# Try to initialize engine (will fail gracefully if Stockfish not found)
try:
    chess_engine.initialize()
    print("✓ Stockfish engine initialized")
except Exception as e:
    print(f"⚠ Warning: {e}")
    print("  AI assistance will not work until Stockfish is installed")

# Create Socket.IO manager
socket_manager = SocketManager(room_manager, chess_engine)

# Create FastAPI app
app = FastAPI(title="Chess Game Server")

# Mount Socket.IO app
socket_app = socketio.ASGIApp(socket_manager.sio, app)

# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def read_root():
    """Serve the main HTML file."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Chess Game Server", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "engine_initialized": chess_engine.is_initialized(),
        "active_rooms": len(room_manager.rooms)
    }


@app.get("/api/rooms")
async def get_rooms():
    """Get list of available rooms (rooms with at least 1 player but not full)."""
    available_rooms = []
    for room_id, room in room_manager.rooms.items():
        player_count = len(room.players)
        if player_count > 0 and player_count < 2:
            available_rooms.append({
                "room_id": room_id,
                "players": list(room.players.keys()),
                "player_count": player_count
            })
    return {
        "rooms": available_rooms,
        "total": len(available_rooms)
    }


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🎮 Chess Game Server Starting...")
    print("="*50)
    print(f"  Engine Status: {'✓ Ready' if chess_engine.is_initialized() else '✗ Not Available'}")
    print(f"  Server: http://localhost:8000")
    print("="*50 + "\n")
    
    uvicorn.run(
        socket_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
