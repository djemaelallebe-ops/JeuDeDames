import random
from typing import List, Optional, Tuple

from engine import Board, color, get_captures, get_simple_moves, is_king

Move = Tuple[int, int, int, int]


class AI:
    def __init__(self, engine, level: int = 1):
        self.engine = engine
        self.level = level
        self.ai_color = 1

    def choose_move(self) -> Optional[Move]:
        self.ai_color = self.engine.turn
        if self.level == 1:
            return self.random_move()
        elif self.level == 2:
            return self.greedy_move()
        else:
            return self.minimax_move()

    # --- Public strategies ---
    def random_move(self) -> Optional[Move]:
        moves = self.all_legal_moves(self.engine.board, self.engine.turn)
        if not moves:
            return None
        return random.choice(moves)

    def greedy_move(self) -> Optional[Move]:
        captures = self.all_captures(self.engine.board, self.engine.turn)
        if captures:
            return random.choice(captures)

        moves = self.all_simple_moves(self.engine.board, self.engine.turn)
        if not moves:
            return None

        direction = -1 if self.engine.turn == 1 else 1
        forward_moves = [m for m in moves if (m[2] - m[0]) == direction]
        if forward_moves:
            return forward_moves[0]
        return moves[0]

    def minimax_move(self) -> Optional[Move]:
        best_score = float("-inf")
        best_move: Optional[Move] = None
        legal_moves = self.all_legal_moves(self.engine.board, self.engine.turn)
        for move in legal_moves:
            board_copy = self.apply_move_sim(self.engine.board, move)
            score = self.minimax(board_copy, 2, False)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    # --- Utilities ---
    def all_captures(self, board: Board, player: int) -> List[Move]:
        captures: List[Move] = []
        for r in range(8):
            for c in range(8):
                if color(board.grid[r][c]) == player:
                    for r2, c2, mr, mc in get_captures(board, r, c):
                        captures.append((r, c, r2, c2))
        return captures

    def all_simple_moves(self, board: Board, player: int) -> List[Move]:
        moves: List[Move] = []
        for r in range(8):
            for c in range(8):
                if color(board.grid[r][c]) == player:
                    for r2, c2 in get_simple_moves(board, r, c):
                        moves.append((r, c, r2, c2))
        return moves

    def all_legal_moves(self, board: Board, player: int) -> List[Move]:
        captures = self.all_captures(board, player)
        if captures:
            return captures
        return self.all_simple_moves(board, player)

    def apply_move_sim(self, board: Board, move: Move) -> Board:
        r, c, r2, c2 = move
        piece = board.grid[r][c]
        new_board = board.clone()

        # handle capture removal
        caps = get_captures(board, r, c)
        captured = next(((mr, mc) for (er, ec, mr, mc) in caps if (er, ec) == (r2, c2)), None)
        if captured:
            mr, mc = captured
            new_board.grid[mr][mc] = 0

        new_board.grid[r][c] = 0
        new_board.grid[r2][c2] = piece

        if r2 == 0 and piece == 1:
            new_board.grid[r2][c2] = 2
        elif r2 == 7 and piece == -1:
            new_board.grid[r2][c2] = -2

        return new_board

    def evaluate(self, board: Board) -> int:
        score = 0
        for r in range(8):
            for c in range(8):
                piece = board.grid[r][c]
                if piece == 0:
                    continue
                value = 3 if is_king(piece) else 1
                score += value if color(piece) == self.ai_color else -value
        return score

    def minimax(self, board: Board, depth: int, maximizing: bool) -> int:
        player = self.ai_color if maximizing else -self.ai_color
        legal_moves = self.all_legal_moves(board, player)

        if depth == 0 or not legal_moves:
            return self.evaluate(board)

        if maximizing:
            value = float("-inf")
            for move in legal_moves:
                next_board = self.apply_move_sim(board, move)
                value = max(value, self.minimax(next_board, depth - 1, False))
            return value
        else:
            value = float("inf")
            for move in legal_moves:
                next_board = self.apply_move_sim(board, move)
                value = min(value, self.minimax(next_board, depth - 1, True))
            return value
