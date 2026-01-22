# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Download Stockfish
- Go to https://stockfishchess.org/download/
- Download `stockfish.exe` (Windows) or appropriate binary for your OS
- Place it in the `stockfish/` folder

### 3. Run the Server
```bash
cd backend
python main.py
```

Then open `frontend/index.html` in your browser!

## 🎮 How to Test the AI Feature

1. Open the game in **two browser windows/tabs**
2. In **Window 1**: Join as username `Raunak` (or any username you configured)
3. In **Window 2**: Join as any other username (e.g., `Player2`)
4. Use the **same room ID** for both (e.g., `room1`)
5. When it's `Raunak`'s turn, the server will automatically play the best move!

## ⚠️ Important Notes

- **First 5 moves**: AI is disabled for the first 5 moves (Raunak plays manually)
- **After move 5**: AI takes over automatically
- **Randomness**: AI occasionally plays suboptimal moves to appear human
- **No authentication**: Just enter any username and start playing!

## 🔧 Troubleshooting

**Server won't start?**
- Make sure port 8000 is not in use
- Check that all dependencies are installed

**Stockfish error?**
- Verify `stockfish.exe` is in the `stockfish/` folder
- Check the path in `backend/chess_engine.py` matches your OS

**Moves not syncing?**
- Ensure both players are in the same room
- Check browser console for errors
- Verify server is running

---

**Ready to play?** Start the server and open the frontend! 🎯
