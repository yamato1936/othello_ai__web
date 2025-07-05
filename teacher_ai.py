import copy
import math
import numpy as np
from othello_ai import OthelloGame, EMPTY

class PhaseAwareAI:
    """
    序盤・中盤・終盤で思考モードを切り替える、より高度な評価AI。
    """

    # --- 評価テーブルをフェーズごとに定義 ---

    # 【序盤用】中央の価値を重視し、辺や隅の価値はまだ低く設定
    OPENING_WEIGHTS = np.array([
        [ 20,  -5, 10,  5,  5, 10,  -5,  20],
        [ -5, -25, -1, -1, -1, -1, -25,  -5],
        [ 10,  -1, 10,  2,  2, 10,  -1,  10],
        [  5,  -1,  2,  1,  1,  2,  -1,   5],
        [  5,  -1,  2,  1,  1,  2,  -1,   5],
        [ 10,  -1, 10,  2,  2, 10,  -1,  10],
        [ -5, -25, -1, -1, -1, -1, -25,  -5],
        [ 20,  -5, 10,  5,  5, 10,  -5,  20]
    ])

    # 【中盤用】隅の価値を最大化し、辺の確保も重視
    MIDGAME_WEIGHTS = np.array([
        [120, -20, 20,  5,  5, 20, -20, 120],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [ 20,  -5, 15,  3,  3, 15,  -5,  20],
        [  5,  -5,  3,  1,  1,  3,  -5,   5],
        [  5,  -5,  3,  1,  1,  3,  -5,   5],
        [ 20,  -5, 15,  3,  3, 15,  -5,  20],
        [-40, -40, -5, -5, -5, -5, -40, -40],
        [120, -20, 20,  5,  5, 20, -20, 120]
    ])

    def __init__(self, color, depth=4):
        self.color = color
        self.depth = depth

    def get_game_phase(self, board):
        """盤面の石の数から、ゲームのフェーズを判定する"""
        total_stones = 64 - sum(row.count(EMPTY) for row in board)
        # 終盤の開始を少し早める（残り20マスから）
        if total_stones > 44:
            return 'endgame'
        if total_stones > 20:
            return 'midgame'
        return 'opening'

    def evaluate(self, game):
        """
        ゲームフェーズに応じて、評価ロジックを完全に切り替える
        """
        board = game.board
        player = self.color
        opponent = -player
        phase = self.get_game_phase(board)

        # --- 評価軸を計算 ---
        my_moves = len(game.get_valid_moves(player))
        opp_moves = len(game.get_valid_moves(opponent))
        
        # --- フェーズごとに評価ロジックを分岐 ---
        if phase == 'opening':
            # 【序盤の思考】打てる手の多さ（選択肢）を最重視
            positional_score = 0
            for r in range(8):
                for c in range(8):
                    if board[r][c] == player:
                        positional_score += self.OPENING_WEIGHTS[r][c]
                    elif board[r][c] == opponent:
                        positional_score -= self.OPENING_WEIGHTS[r][c]
            
            mobility_score = 15 * (my_moves - opp_moves)
            return positional_score + mobility_score

        elif phase == 'midgame':
            # 【中盤の思考】隅と辺の価値を重視
            positional_score = 0
            for r in range(8):
                for c in range(8):
                    if board[r][c] == player:
                        positional_score += self.MIDGAME_WEIGHTS[r][c]
                    elif board[r][c] == opponent:
                        positional_score -= self.MIDGAME_WEIGHTS[r][c]

            mobility_score = 10 * (my_moves - opp_moves)
            return positional_score + mobility_score
        
        else: # endgame
            # 【終盤の思考】最終的な石の数を最重視（偶数理論の簡易版）
            # 相手の打てる手を無くす（手止まり）ことが非常に強力なため、
            # 打てる手の価値（重み）を最大化する
            my_stones = sum(row.count(player) for row in board)
            opp_stones = sum(row.count(opponent) for row in board)
            
            stone_diff_score = (my_stones - opp_stones)
            mobility_score = 50 * (my_moves - opp_moves)
            
            return stone_diff_score + mobility_score


    def alphabeta(self, game, depth, alpha, beta, maximizing_player):
        """アルファベータ法による探索"""
        if depth == 0 or game.is_game_over():
            return self.evaluate(game)

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
        """最善手を返す"""
        best_score = -math.inf
        best_move = None
        
        valid_moves = game.get_valid_moves(self.color)
        if not valid_moves:
            return None

        for move in valid_moves:
            new_game = copy.deepcopy(game)
            new_game.make_move(*move, self.color)
            new_game.current_player *= -1
            score = self.alphabeta(new_game, self.depth - 1, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move
