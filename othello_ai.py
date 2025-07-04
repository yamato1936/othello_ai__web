import numpy as np 

EMPTY, BLACK, WHITE = 0, 1, -1
BOARD_SIZE = 8

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1), (1, 0), (1, 1)]

class OthelloGame:
    def __init__(self):
        self.board = self._create_board()
        self.current_player = BLACK

    def _create_board(self):
        board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        mid = BOARD_SIZE // 2
        board[mid - 1][mid - 1] = WHITE
        board[mid][mid] = WHITE
        board[mid - 1][mid] = BLACK
        board[mid][mid - 1] = BLACK
        return board

    def get_valid_moves(self, player):
        valid_moves = []
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.board[x][y] != EMPTY:
                    continue
                if any(self._can_flip(x, y, dx, dy, player) for dx, dy in DIRECTIONS):
                    valid_moves.append((x, y))
        return valid_moves

    def _can_flip(self, x, y, dx, dy, player):
        x += dx
        y += dy
        if not self._is_on_board(x, y) or self.board[x][y] != -player:
            return False
        x += dx
        y += dy
        while self._is_on_board(x, y):
            if self.board[x][y] == EMPTY:
                return False
            if self.board[x][y] == player:
                return True
            x += dx
            y += dy
        return False

    def _is_on_board(self, x, y):
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

    def make_move(self, x, y, player):
        self.board[x][y] = player
        for dx, dy in DIRECTIONS:
            if self._can_flip(x, y, dx, dy, player):
                self._flip_direction(x, y, dx, dy, player)

    def _flip_direction(self, x, y, dx, dy, player):
        x += dx
        y += dy
        while self._is_on_board(x, y) and self.board[x][y] == -player:
            self.board[x][y] = player
            x += dx
            y += dy

    def is_game_over(self):
        return not self.get_valid_moves(BLACK) and not self.get_valid_moves(WHITE)

    def count_pieces(self):
        black = sum(row.count(BLACK) for row in self.board)
        white = sum(row.count(WHITE) for row in self.board)
        return black, white

    def get_winner(self):
        black, white = self.count_pieces()
        if black > white:
            return BLACK
        elif white > black:
            return WHITE
        else:
            return 0