import copy
from typing import List, Optional, Tuple

# Representation des pieces :
# 0 = vide
# 1 = pion blanc, 2 = dame blanche
# -1 = pion noir, -2 = dame noire


Position = Tuple[int, int]
CaptureMove = Tuple[int, int, int, int]


def color(piece: int) -> int:
    """Retourne 1 pour blanc, -1 pour noir, 0 pour vide."""
    if piece > 0:
        return 1
    if piece < 0:
        return -1
    return 0


def is_king(piece: int) -> bool:
    return abs(piece) == 2


class Board:
    def __init__(self) -> None:
        self.grid: List[List[int]] = [[0 for _ in range(8)] for _ in range(8)]
        self.reset()

    def reset(self) -> None:
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    self.grid[r][c] = 0
                elif r < 3:
                    self.grid[r][c] = -1
                elif r > 4:
                    self.grid[r][c] = 1
                else:
                    self.grid[r][c] = 0

    def clone(self) -> "Board":
        new_board = Board()
        new_board.grid = copy.deepcopy(self.grid)
        return new_board


# Directions pour les pions et les dames
WHITE_DIRS = [(-1, -1), (-1, 1)]
BLACK_DIRS = [(1, -1), (1, 1)]
KING_DIRS = WHITE_DIRS + BLACK_DIRS


def inside(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8


def get_captures(board: Board, r: int, c: int) -> List[CaptureMove]:
    moves: List[CaptureMove] = []
    piece = board.grid[r][c]
    col = color(piece)
    if col == 0:
        return moves

    directions = KING_DIRS if is_king(piece) else (WHITE_DIRS if col == 1 else BLACK_DIRS)

    for dr, dc in directions:
        mid_r, mid_c = r + dr, c + dc
        end_r, end_c = r + 2 * dr, c + 2 * dc
        if inside(end_r, end_c) and inside(mid_r, mid_c):
            middle_piece = board.grid[mid_r][mid_c]
            landing_piece = board.grid[end_r][end_c]
            if color(middle_piece) == -col and landing_piece == 0:
                moves.append((end_r, end_c, mid_r, mid_c))
    return moves


def get_simple_moves(board: Board, r: int, c: int) -> List[Position]:
    moves: List[Position] = []
    piece = board.grid[r][c]
    col = color(piece)
    if col == 0:
        return moves

    directions = KING_DIRS if is_king(piece) else (WHITE_DIRS if col == 1 else BLACK_DIRS)

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if inside(nr, nc) and board.grid[nr][nc] == 0:
            moves.append((nr, nc))
    return moves


class Engine:
    def __init__(self) -> None:
        self.board = Board()
        self.turn: int = 1  # 1 = blanc, -1 = noir

    def reset(self) -> None:
        self.board.reset()
        self.turn = 1

    def _any_capture_available(self) -> bool:
        for r in range(8):
            for c in range(8):
                if color(self.board.grid[r][c]) == self.turn:
                    if get_captures(self.board, r, c):
                        return True
        return False

    def get_legal_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        piece = self.board.grid[r][c]
        if color(piece) != self.turn:
            return []
        captures = get_captures(self.board, r, c)
        if self._any_capture_available():
            return [(r2, c2) for r2, c2, _, _ in captures]
        return get_simple_moves(self.board, r, c)

    def move_piece(self, r: int, c: int, r2: int, c2: int) -> bool:
        piece = self.board.grid[r][c]
        if color(piece) != self.turn:
            return False

        captures = get_captures(self.board, r, c)
        must_capture = self._any_capture_available()
        target_capture = None
        if captures:
            for move in captures:
                if (move[0], move[1]) == (r2, c2):
                    target_capture = move
                    break

        if must_capture and target_capture is None:
            return False

        if target_capture:
            r_cap, c_cap = target_capture[2], target_capture[3]
            self.board.grid[r_cap][c_cap] = 0
        elif must_capture:
            return False
        elif (r2, c2) not in get_simple_moves(self.board, r, c):
            return False

        self.board.grid[r][c] = 0
        self.board.grid[r2][c2] = piece

        if r2 == 0 and piece == 1:
            self.board.grid[r2][c2] = 2
        elif r2 == 7 and piece == -1:
            self.board.grid[r2][c2] = -2

        self.turn *= -1
        return True

    def get_hint(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Retourne un hint sous la forme (r, c, r2, c2)
        ou None si aucun coup.
        """
        b = self.board

        # 1. rechercher captures
        for r in range(8):
            for c in range(8):
                p = b.grid[r][c]
                if color(p) == self.turn:
                    caps = get_captures(b, r, c)
                    if caps:
                        r2, c2, _, _ = caps[0]
                        return (r, c, r2, c2)

        # 2. rechercher mouvements simples
        for r in range(8):
            for c in range(8):
                p = b.grid[r][c]
                if color(p) == self.turn:
                    moves = get_simple_moves(b, r, c)
                    if moves:
                        r2, c2 = moves[0]
                        return (r, c, r2, c2)

        return None
