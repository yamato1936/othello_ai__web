import math
import random
import copy
from othello_ai import OthelloGame
# ▼▼▼ 新しい動的評価AIをインポート ▼▼▼
from teacher_ai import PhaseAwareAI

# UCTスコアの計算で使う探索のバランスを調整する定数
C_PARAM = 1.414 

class MCTSNode:
    """モンテカルロ木探索の各ノードを表すクラス"""
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game_state.get_valid_moves(game_state.current_player)

    def uct_select_child(self):
        """UCTスコアが最も高い子ノードを選択する"""
        for child in self.children:
            if child.visits == 0:
                return child
        log_total_visits = math.log(self.visits)
        s = sorted(
            self.children, 
            key=lambda c: (c.wins / c.visits) + C_PARAM * math.sqrt(log_total_visits / c.visits)
        )
        return s[-1]

    def add_child(self, move, state):
        child = MCTSNode(game_state=state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        self.wins += result

class MCTS_AI:
    """MCTSと動的評価関数を組み合わせたAI"""
    def __init__(self, iterations=100, simulation_depth=5):
        self.iterations = iterations
        self.simulation_depth = simulation_depth
        
        # ▼▼▼ AIの評価役を、新しいPhaseAwareAIに設定 ▼▼▼
        self.evaluator = PhaseAwareAI(color=1) 

    def get_move(self, game):
        if not game.get_valid_moves(game.current_player):
            return None

        root = MCTSNode(game_state=copy.deepcopy(game))

        for _ in range(self.iterations):
            node = root
            state = copy.deepcopy(game)

            # 1. 選択 (Selection)
            while not node.untried_moves and node.children:
                node = node.uct_select_child()
                state.make_move(*node.move, state.current_player)
                state.current_player *= -1

            # 2. 展開 (Expansion)
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                state.make_move(*move, state.current_player)
                state.current_player *= -1
                node = node.add_child(move, copy.deepcopy(state))

            # 3. シミュレーション (Simulation)
            for _ in range(self.simulation_depth):
                if state.is_game_over(): break
                moves = state.get_valid_moves(state.current_player)
                if not moves:
                    state.current_player *= -1
                    continue
                state.make_move(*random.choice(moves), state.current_player)
                state.current_player *= -1
            
            # 4. 更新 (Backpropagation)
            # ▼▼▼ 評価方法を新しいAIの評価関数に変更 ▼▼▼
            eval_score = self.evaluator.evaluate(state)
            # スコアのスケールが大きいので、正規化の分母を調整
            result = math.tanh(eval_score / 1000.0)

            while node is not None:
                result_for_node = result if node.game_state.current_player == root.game_state.current_player else -result
                node.update(result_for_node)
                node = node.parent

        best_child = sorted(root.children, key=lambda c: c.visits)[-1]
        return best_child.move