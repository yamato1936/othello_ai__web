from celery import Celery
from othello_ai import OthelloGame
from mcts_ai import MCTS_AI 
import os

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

celery = Celery(
    __name__,
    broker=redis_url,
    backend=redis_url
)

# ▼▼▼ 軽量版AIをインスタンス化 ▼▼▼
# iterationsを調整して、速さと強さのバランスを取る
ai = MCTS_AI(iterations=100) 

@celery.task
def calculate_ai_move(board_state, current_player_state):
    temp_game = OthelloGame()
    temp_game.board = board_state
    temp_game.current_player = current_player_state
    
    move = ai.get_move(temp_game)
    return move
