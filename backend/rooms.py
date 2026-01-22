"""
Room management for multiplayer chess games.
Each room maintains game state for two players.
"""

from typing import Dict, Optional
import chess
import chess.pgn


class Room:
    """Represents a chess game room with two players."""
    
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.board = chess.Board()
        self.players: Dict[str, str] = {}  # {username: socket_id}
        self.game_log: list = []  # Store moves for PGN export
        self.move_count = 0
        
    def add_player(self, username: str, socket_id: str) -> bool:
        """Add a player to the room. Returns True if successful, False if room is full."""
        if len(self.players) >= 2:
            return False
        self.players[username] = socket_id
        return True
    
    def remove_player(self, username: str):
        """Remove a player from the room."""
        if username in self.players:
            del self.players[username]
    
    def is_full(self) -> bool:
        """Check if room has 2 players."""
        return len(self.players) >= 2
    
    def get_other_player(self, username: str) -> Optional[str]:
        """Get the username of the other player in the room."""
        for player in self.players:
            if player != username:
                return player
        return None
    
    def make_move(self, move_uci: str) -> bool:
        """Make a move on the board. Returns True if valid, False otherwise."""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_count += 1
                self.game_log.append(move_uci)
                return True
        except (ValueError, chess.InvalidMoveError):
            pass
        return False
    
    def get_fen(self) -> str:
        """Get current board position in FEN notation."""
        return self.board.fen()
    
    def get_turn(self) -> str:
        """Get whose turn it is ('white' or 'black')."""
        return 'white' if self.board.turn else 'black'
    
    def get_status(self) -> str:
        """Get game status: 'ongoing', 'checkmate', 'stalemate', 'draw', etc."""
        if self.board.is_checkmate():
            return 'checkmate'
        elif self.board.is_stalemate():
            return 'stalemate'
        elif self.board.is_insufficient_material():
            return 'insufficient_material'
        elif self.board.is_seventyfive_moves():
            return 'seventyfive_moves'
        elif self.board.is_fivefold_repetition():
            return 'fivefold_repetition'
        elif self.board.is_variant_draw():
            return 'variant_draw'
        return 'ongoing'
    
    def export_pgn(self) -> str:
        """Export game to PGN format."""
        game = chess.pgn.Game()
        game.headers["Event"] = f"Room {self.room_id}"
        game.headers["Site"] = "Local"
        
        node = game
        temp_board = chess.Board()
        for move_uci in self.game_log:
            move = chess.Move.from_uci(move_uci)
            if move in temp_board.legal_moves:
                node = node.add_variation(move)
                temp_board.push(move)
        
        return str(game)


class RoomManager:
    """Manages all game rooms."""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
    
    def get_or_create_room(self, room_id: str) -> Room:
        """Get existing room or create a new one."""
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id)
        return self.rooms[room_id]
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get room by ID, or None if it doesn't exist."""
        return self.rooms.get(room_id)
    
    def remove_room(self, room_id: str):
        """Remove a room when game ends."""
        if room_id in self.rooms:
            del self.rooms[room_id]
