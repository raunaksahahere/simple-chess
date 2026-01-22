# 🎮 Multiplayer Chess Game

A private online multiplayer chess game built with Python (FastAPI + Socket.IO) and vanilla JavaScript. Features real-time gameplay and secret AI assistance for a specific username.

## ✨ Features

- **Real-time Multiplayer Chess**: Two players can join a room and play chess in real-time
- **Socket.IO Communication**: Instant move synchronization between players
- **Server-side Validation**: All moves are validated on the server using `python-chess`
- **Secret AI Assistance**: Username "Raunak" automatically gets Stockfish-powered moves from the very first move
- **Automatic AI Play**: AI plays automatically for "Raunak" - no manual input required
- **Random Room Finder**: Quick join button to find and join available rooms
- **Loading Screen**: Smooth loading experience when joining rooms
- **Beautiful UI**: Modern, responsive chess interface with animated loading states

## 🏗️ Project Structure

```
Simple Chess/
├── backend/
│   ├── main.py              # FastAPI server entry point
│   ├── chess_engine.py       # Stockfish integration
│   ├── socket_manager.py     # Socket.IO event handlers
│   ├── rooms.py              # Room and game state management
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Main HTML file
│   ├── style.css             # Styling
│   └── script.js             # Client-side logic
├── stockfish/                # Stockfish engine directory
│   └── stockfish.exe         # Stockfish executable (download separately)
└── README.md                 # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Stockfish chess engine executable

### Step 1: Install Python Dependencies

Navigate to the `backend` directory and install the required packages:

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Download Stockfish

1. Download Stockfish from [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
2. For Windows: Download the Windows executable
3. Place the `stockfish.exe` file in the `stockfish/` directory at the project root

**Alternative**: If you're on Linux/Mac, download the appropriate binary and update the path in `backend/chess_engine.py`:
```python
ChessEngine(stockfish_path="stockfish/stockfish")  # Linux/Mac
```

### Step 3: Run the Server

From the `backend` directory:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:socket_app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### Step 4: Open the Frontend

1. Open `frontend/index.html` in your web browser
2. Or serve it using a simple HTTP server:

```bash
# Using Python
cd frontend
python -m http.server 8080

# Then open http://localhost:8080/index.html
```

**Note**: For Socket.IO to work properly, you may need to serve the frontend through the FastAPI server. The server is configured to serve static files from the `frontend/` directory at `/static`.

## 🎯 How to Play

1. **Join a Room**:
   - Enter your username (no authentication required)
   - **Option A**: Enter a room ID manually (e.g., "room1", "default")
   - **Option B**: Click the "🎲 Random" button to automatically find and join an available room
   - Click "Join Room"
   - A loading screen will appear while connecting

2. **Wait for Opponent**:
   - The first player to join becomes White
   - The second player becomes Black
   - Game starts automatically when both players are in
   - Loading screen disappears when the game is ready

3. **Make Moves**:
   - Click on a piece to select it
   - Click on a valid destination square to move
   - Moves are validated and synced in real-time

4. **Special AI Feature**:
   - If your username is "Raunak" (case-insensitive), the server will automatically calculate and play the best move using Stockfish
   - **AI works from the very first move** - no waiting period
   - **No randomness** - always plays the optimal move
   - **Fully automatic** - no manual input needed or allowed for "Raunak"
   - The frontend will show "AI is calculating your move..." when it's your turn

## 🔧 Configuration

### Stockfish Engine Settings

The engine is configured with the following limits (in `backend/chess_engine.py`):
- **Depth**: ≤ 10
- **Time**: ≤ 0.1 seconds
- **No randomness**: Always plays the best move
- **Works from move 1**: No waiting period, AI active immediately

### Server Settings

Default server configuration:
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8000`
- **CORS**: Enabled for all origins (development only)

## 📡 API Endpoints

### REST API

- `GET /api/rooms` - Get list of available rooms (rooms with 1 player waiting)
  - Returns: `{ "rooms": [...], "total": number }`
  - Each room object contains: `room_id`, `players`, `player_count`

### Socket.IO Events

#### Client → Server

- `join_room`: `{ username, room_id }` - Join a game room
- `player_move`: `{ username, room_id, fen, move_uci }` - Send a move

#### Server → Client

- `game_state`: `{ fen, turn, status, players, room_id }` - Current game state
- `move_update`: `{ fen, move_uci, username }` - Move update broadcast
- `player_joined`: `{ username, players }` - Another player joined
- `opponent_disconnected`: `{}` - Opponent left the game
- `error`: `{ message }` - Error message

## 🐛 Troubleshooting

### Stockfish Not Found

If you see: `Stockfish not found at stockfish/stockfish.exe`

1. Make sure you've downloaded Stockfish
2. Place `stockfish.exe` in the `stockfish/` directory
3. Check the file path in `backend/chess_engine.py` matches your OS

### Socket.IO Connection Failed

1. Make sure the backend server is running
2. Check that the frontend is connecting to the correct URL (default: `http://localhost:8000`)
3. Ensure no firewall is blocking the connection

### Moves Not Syncing

1. Check browser console for errors
2. Verify both players are in the same room
3. Ensure it's the correct player's turn

## 🎨 Customization

### Change AI Username

Edit `backend/socket_manager.py`, line 145:
```python
if username.lower() == "raunak":  # Change "raunak" to your desired username
```

### Adjust AI Strength

Edit `backend/chess_engine.py`, line 70:
```python
limit = chess.engine.Limit(depth=10, time=0.1)  # Adjust depth/time
```

### Change Server Port

Edit `backend/main.py`, line 70:
```python
port=8000  # Change to your desired port
```

### Random Room Feature

The random room button (`🎲 Random`) will:
1. Fetch available rooms from `/api/rooms` endpoint
2. If rooms exist, randomly select one to join
3. If no rooms are available, generate a random room ID (e.g., "room1234")
4. Automatically fill the room ID field and join

## 📝 License

This is a private demo/educational project. Use at your own discretion.

## 🙏 Credits

- **python-chess**: Chess library for Python
- **Stockfish**: Open-source chess engine
- **Socket.IO**: Real-time communication
- **FastAPI**: Modern Python web framework

---

**Enjoy your chess games!** ♟️
