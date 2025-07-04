import copy
import math
import numpy as np

class AlphaBetaAI:
    def __init__(self, color, depth=4):
        self.color = color
        self.depth = depth

    WEIGHTS = np.array([
        [120, -20, 20, 5, 5, 20, -20, 120],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [20, -5, 15, 3, 3, 15, -5, 20],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [20, -5, 15, 3, 3, 15, -5, 20],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [120, -20, 20, 5, 5, 20, -20, 120]
    ]) 

    def evaluate(self, board, color):
        score = 0
        for x in range(8):
            for y in range(8):
                if board[x][y] == color:
                    score += self.WEIGHTS[x][y]
                elif board[x][y] == -color:
                    score -= self.WEIGHTS[x][y]
        return score

    def alphabeta(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.is_game_over():
            return self.evaluate(game.board, self.color)

        valid_moves = game.get_valid_moves(game.current_player)
        if not valid_moves:
            new_game = copy.deepcopy(game)
            new_game.current_player *= -1
            return self.alphabeta(new_game, depth - 1, alpha, beta, not maximizing_player)

        if maximizing_player:
            max_eval = -math.inf
            for move in valid_moves:
                new_game = copy.deepcopy(game)
                new_game.make_move(*move, new_game.current_player)
                new_game.current_player *= -1
                eval = self.alphabeta(new_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in valid_moves:
                new_game = copy.deepcopy(game)
                new_game.make_move(*move, new_game.current_player)
                new_game.current_player *= -1
                eval = self.alphabeta(new_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_move(self, game):
        best_score = -math.inf
        best_move = None
        
        valid_moves = game.get_valid_moves(self.color)
        if not valid_moves:
            return None # 打てる手がない場合はNoneを返す

        for move in valid_moves:
            new_game = copy.deepcopy(game)
            new_game.make_move(*move, self.color)
            new_game.current_player *= -1
            # ここで self.alphabeta に new_game を渡す
            score = self.alphabeta(new_game, self.depth - 1, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move