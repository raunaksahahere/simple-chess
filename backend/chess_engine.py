"""
Stockfish chess engine integration with strength limits.
Handles AI move generation for the special username.
Always returns the best move with no randomness.
"""

import chess
import chess.engine
from typing import Optional
import os
import stat


class ChessEngine:
    """Wrapper for Stockfish engine with configurable strength."""
    
    def __init__(self, stockfish_path: str = None):
        # Resolve path relative to this file's directory if relative path provided
        if stockfish_path is None:
            BASE_DIR = os.path.dirname(__file__)
            stockfish_path = os.path.join(BASE_DIR, "stockfish", "stockfish")
        elif not os.path.isabs(stockfish_path):
            # Relative path - resolve from this file's directory
            BASE_DIR = os.path.dirname(__file__)
            stockfish_path = os.path.join(BASE_DIR, stockfish_path)
        
        self.stockfish_path = stockfish_path
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.initialized = False
        
    def initialize(self):
        """Initialize the Stockfish engine."""
        if self.initialized:
            return
        
        # Check if file exists
        if not os.path.exists(self.stockfish_path):
            raise FileNotFoundError(
                f"Stockfish not found at {self.stockfish_path}. "
                "Please download Stockfish and place it in backend/stockfish/ directory."
            )
        
        # Check if file is executable (Unix systems)
        if os.name != 'nt':  # Not Windows
            if not os.access(self.stockfish_path, os.X_OK):
                raise PermissionError(
                    f"Stockfish at {self.stockfish_path} is not executable. "
                    "Run: chmod +x backend/stockfish/stockfish"
                )
        
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            self.initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Stockfish: {e}")
    
    def close(self):
        """Close the engine connection."""
        if self.engine:
            self.engine.quit()
            self.engine = None
        self.initialized = False
    
    def get_best_move(self, board: chess.Board, move_count: int = 0) -> Optional[chess.Move]:
        """
        Get the best move from Stockfish with strength limits.
        Always returns the best move with no randomness.
        
        Args:
            board: Current chess board position
            move_count: Number of moves made so far (unused, kept for compatibility)
        
        Returns:
            Best move or None if error occurs
        """
        if not self.initialized:
            self.initialize()
        
        if not self.engine:
            return None
        
        try:
            # Limit engine strength: depth ≤ 10 or time ≤ 0.1s
            limit = chess.engine.Limit(depth=10, time=0.1)
            
            # Get best move - always return the optimal move
            result = self.engine.play(board, limit)
            return result.move if result.move else None
                
        except Exception as e:
            print(f"Error getting move from Stockfish: {e}")
            # Fallback: return first legal move if engine fails
            legal_moves = list(board.legal_moves)
            if legal_moves:
                return legal_moves[0]
            return None
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self.initialized
