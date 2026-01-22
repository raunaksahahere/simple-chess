"""
Socket.IO event handlers for real-time chess game communication.
"""

import socketio
from typing import Dict
from rooms import RoomManager, Room
from chess_engine import ChessEngine


class SocketManager:
    """Manages Socket.IO connections and game events."""
    
    def __init__(self, room_manager: RoomManager, chess_engine: ChessEngine):
        self.sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode='asgi')
        self.room_manager = room_manager
        self.chess_engine = chess_engine
        self.username_to_socket: Dict[str, str] = {}  # {username: socket_id}
        self.socket_to_username: Dict[str, str] = {}  # {socket_id: username}
        
        # Register event handlers
        self.sio.on('connect')(self.on_connect)
        self.sio.on('disconnect')(self.on_disconnect)
        self.sio.on('join_room')(self.on_join_room)
        self.sio.on('player_move')(self.on_player_move)
    
    async def on_connect(self, sid, environ):
        """Handle client connection."""
        print(f"Client connected: {sid}")
    
    async def on_disconnect(self, sid):
        """Handle client disconnection."""
        username = self.socket_to_username.get(sid)
        if username:
            # Find and remove player from their room
            for room_id, room in self.room_manager.rooms.items():
                if username in room.players:
                    room.remove_player(username)
                    other_player = room.get_other_player(username)
                    if other_player:
                        # Notify other player
                        other_sid = room.players.get(other_player)
                        if other_sid:
                            await self.sio.emit('opponent_disconnected', 
                                              to=other_sid)
                    # Clean up empty rooms
                    if len(room.players) == 0:
                        self.room_manager.remove_room(room_id)
                    break
            
            del self.username_to_socket[username]
            del self.socket_to_username[sid]
        
        print(f"Client disconnected: {sid}")
    
    async def on_join_room(self, sid, data):
        """Handle player joining a room."""
        username = data.get('username', '').strip()
        room_id = data.get('room_id', 'default').strip()
        
        if not username:
            await self.sio.emit('error', {'message': 'Username is required'}, to=sid)
            return
        
        # Store username-socket mapping
        self.username_to_socket[username] = sid
        self.socket_to_username[sid] = username
        
        # Get or create room
        room = self.room_manager.get_or_create_room(room_id)
        
        # Check if room is full
        if room.is_full() and username not in room.players:
            await self.sio.emit('error', {'message': 'Room is full'}, to=sid)
            return
        
        # Add player to room
        if username not in room.players:
            success = room.add_player(username, sid)
            if not success:
                await self.sio.emit('error', {'message': 'Failed to join room'}, to=sid)
                return
        
        # Join Socket.IO room
        await self.sio.enter_room(sid, room_id)
        
        # Send current game state
        await self.sio.emit('game_state', {
            'fen': room.get_fen(),
            'turn': room.get_turn(),
            'status': room.get_status(),
            'players': list(room.players.keys()),
            'room_id': room_id
        }, to=sid)
        
        # Notify other player if room is full
        if room.is_full():
            other_player = room.get_other_player(username)
            if other_player:
                other_sid = room.players.get(other_player)
                if other_sid:
                    await self.sio.emit('player_joined', {
                        'username': username,
                        'players': list(room.players.keys())
                    }, to=other_sid)
            
            # When room becomes full, auto-play for Raunak if it's their turn
            await self.auto_play_for_raunak(room_id, room)
        
        print(f"Player {username} joined room {room_id}")
    
    async def auto_play_for_raunak(self, room_id: str, room):
        """Automatically generate and play a move for Raunak if it's their turn."""
        if not room.is_full():
            return
        
        players_list = list(room.players.keys())
        if len(players_list) < 2:
            return
        
        # Check if it's Raunak's turn
        is_white_turn = room.board.turn
        raunak_username = None
        
        for player in players_list:
            if player.lower() == "raunak":
                raunak_username = player
                break
        
        if not raunak_username:
            return
        
        # Check if it's Raunak's turn
        player_index = players_list.index(raunak_username)
        is_raunak_white = (player_index == 0)
        
        if is_raunak_white == is_white_turn:
            # It's Raunak's turn - generate AI move automatically
            ai_move = self.chess_engine.get_best_move(room.board, room.move_count)
            
            if ai_move:
                move_uci = ai_move.uci()
                if room.make_move(move_uci):
                    # Broadcast to both players
                    await self.sio.emit('move_update', {
                        'fen': room.get_fen(),
                        'move_uci': move_uci,
                        'username': raunak_username
                    }, room=room_id)
                    
                    # Send game state update
                    await self.sio.emit('game_state', {
                        'fen': room.get_fen(),
                        'turn': room.get_turn(),
                        'status': room.get_status()
                    }, room=room_id)
                    
                    print(f"Auto AI move for {raunak_username}: {move_uci}")
                    
                    # Recursively check if it's still Raunak's turn (shouldn't happen, but just in case)
                    await self.auto_play_for_raunak(room_id, room)
    
    async def on_player_move(self, sid, data):
        """Handle player move."""
        username = self.socket_to_username.get(sid)
        if not username:
            await self.sio.emit('error', {'message': 'Not authenticated'}, to=sid)
            return
        
        room_id = data.get('room_id', 'default')
        room = self.room_manager.get_room(room_id)
        
        if not room:
            await self.sio.emit('error', {'message': 'Room not found'}, to=sid)
            return
        
        if username not in room.players:
            await self.sio.emit('error', {'message': 'Not in this room'}, to=sid)
            return
        
        # Check if it's the player's turn
        current_turn = room.get_turn()
        is_white_turn = room.board.turn
        # Determine if this player is white or black
        players_list = list(room.players.keys())
        if len(players_list) < 2:
            await self.sio.emit('error', {'message': 'Waiting for opponent'}, to=sid)
            return
        
        # Simple turn check: first player is white, second is black
        player_index = players_list.index(username)
        is_player_white = (player_index == 0)
        
        if is_player_white != is_white_turn:
            await self.sio.emit('error', {'message': 'Not your turn'}, to=sid)
            return
        
        # Special handling for "Raunak" username
        if username.lower() == "raunak":
            # Ignore client move completely, always generate AI move
            ai_move = self.chess_engine.get_best_move(room.board, room.move_count)
            
            if ai_move:
                move_uci = ai_move.uci()
                if room.make_move(move_uci):
                    # Broadcast to both players
                    await self.sio.emit('move_update', {
                        'fen': room.get_fen(),
                        'move_uci': move_uci,
                        'username': username
                    }, room=room_id)
                    
                    # Send game state update
                    await self.sio.emit('game_state', {
                        'fen': room.get_fen(),
                        'turn': room.get_turn(),
                        'status': room.get_status()
                    }, room=room_id)
                    
                    print(f"AI move for {username}: {move_uci}")
                else:
                    await self.sio.emit('error', {'message': 'Invalid AI move'}, to=sid)
            else:
                # If AI can't generate move, return error (should not happen)
                await self.sio.emit('error', {'message': 'AI could not generate move'}, to=sid)
        else:
            # Normal player move - validate and apply using UCI
            move_uci = data.get('move_uci', '')
            
            # If no UCI provided, try to extract from FEN difference
            if not move_uci:
                client_fen = data.get('fen', '')
                if client_fen:
                    try:
                        import chess
                        temp_board = chess.Board(client_fen)
                        current_board = room.board.copy()
                        
                        # Find the move by comparing board states
                        for move in current_board.legal_moves:
                            test_board = current_board.copy()
                            test_board.push(move)
                            if test_board.fen() == temp_board.fen():
                                move_uci = move.uci()
                                break
                    except:
                        pass
            
            if not move_uci:
                await self.sio.emit('error', {'message': 'Move required'}, to=sid)
                return
            
            # Validate and apply move
            if room.make_move(move_uci):
                # Broadcast to both players
                await self.sio.emit('move_update', {
                    'fen': room.get_fen(),
                    'move_uci': move_uci,
                    'username': username
                }, room=room_id)
                
                # Send game state update
                await self.sio.emit('game_state', {
                    'fen': room.get_fen(),
                    'turn': room.get_turn(),
                    'status': room.get_status()
                }, room=room_id)
                
                print(f"Move by {username}: {move_uci}")
                
                # Auto-play for Raunak if it's now their turn
                await self.auto_play_for_raunak(room_id, room)
            else:
                await self.sio.emit('error', {'message': 'Invalid move'}, to=sid)
