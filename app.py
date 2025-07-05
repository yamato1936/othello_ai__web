from flask import Flask, render_template, request, jsonify, session
import json
import os

from othello_ai import OthelloGame
from tasks import calculate_ai_move # Celeryタスクをインポート

# --- Flaskアプリケーションの初期化 ---
app = Flask(__name__, template_folder='templates', static_folder='static')
# セッションを暗号化するための秘密鍵
app.secret_key = os.environ.get('SECRET_KEY', 'a-very-secret-key-for-local-dev')

# --- ヘルパー関数 ---
def get_game_from_session():
    """セッションからゲーム状態を復元、なければ新規作成"""
    game = OthelloGame()
    if 'board' in session:
        game.board = json.loads(session['board'])
        game.current_player = session['current_player']
    else:
        save_game_to_session(game)
    return game

def save_game_to_session(game):
    """ゲーム状態をセッションに保存"""
    session['board'] = json.dumps(game.board)
    session['current_player'] = game.current_player

# --- ルート定義 ---
@app.route('/')
def index():
    return render_template('index.html')

# --- ゲームAPI ---
@app.route('/board', methods=['GET'])
def get_board_state():
    game = get_game_from_session()
    black, white = game.count_pieces()
    return jsonify({
        "board": game.board,
        "current_player": game.current_player,
        "black": black,
        "white": white,
        "game_over": game.is_game_over()
    })

@app.route('/legal_moves', methods=['GET'])
def get_legal_moves():
    game = get_game_from_session()
    if not game.is_game_over():
        moves = game.get_valid_moves(game.current_player)
        return jsonify({"moves": moves})
    return jsonify({"moves": []})

@app.route('/make_move', methods=['POST'])
def make_move():
    game = get_game_from_session()
    data = request.get_json()
    x, y = data.get("x"), data.get("y")

    if (x, y) in game.get_valid_moves(game.current_player):
        game.make_move(x, y, game.current_player)
        game.current_player *= -1
        save_game_to_session(game)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Invalid move"})

@app.route('/start_ai_move', methods=['POST'])
def start_ai_move():
    game = get_game_from_session()
    if not game.get_valid_moves(game.current_player):
        game.current_player *= -1
        save_game_to_session(game)
        return jsonify({"pass": True})
    task = calculate_ai_move.delay(game.board, game.current_player)
    return jsonify({"task_id": task.id})

@app.route('/get_ai_result/<task_id>', methods=['GET'])
def get_ai_result(task_id):
    task = calculate_ai_move.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        move = task.get()
        game = get_game_from_session()
        game.make_move(move[0], move[1], game.current_player)
        game.current_player *= -1
        # プレイヤーがパスしなければならないかチェック
        if not game.is_game_over() and not game.get_valid_moves(game.current_player):
            # パスの場合、再度ターンをAIに戻す
            game.current_player *= -1
            save_game_to_session(game)
            # フロントエンドに「プレイヤーがパスした」ことを伝える
            return jsonify({"state": task.state, "player_must_pass": True})
        save_game_to_session(game)
        return jsonify({"state": task.state})
    else:
        return jsonify({"state": task.state})

@app.route('/reset', methods=['POST'])
def reset_game():
    session.pop('board', None)
    session.pop('current_player', None)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)