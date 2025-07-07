# Othello AI Web Application

## Overview
This is a web-based Othello application featuring an AI opponent powered by the Monte Carlo Tree Search (MCTS) algorithm.

This project was not just about implementing an Othello AI, but also about tackling the real-world performance challenges that arise when deploying such applications. I addressed these issues by implementing modern web technologies, including asynchronous task processing with Celery and containerization with Docker.

Play the live demo here!
https://othello-web-iiy2.onrender.com/


## Key Features
AI Opponent: Play against an MCTS-powered AI that utilizes a dynamic evaluation function, changing its strategy based on the game phase (opening, mid-game, endgame).

Asynchronous AI: The UI remains responsive and never freezes, even while the AI is thinking, thanks to background task processing.

Legal Move Highlighting: The board displays indicators for all possible moves for the current player.

Session Management: Multiple users can play simultaneously, with each game state managed independently through server-side sessions.

## Tech Stack
・Backend: Python, Flask
・Asynchronous Task Queue: Celery, Redis
・Frontend: HTML, CSS, JavaScript
・AI Algorithm: Monte Carlo Tree Search (MCTS) with a Dynamic Evaluation Function
・Infrastructure & Deployment: Docker, Gunicorn, Render

## About the AI Logic
The AI in this application is based on the Monte Carlo Tree Search (MCTS) algorithm. MCTS determines the most promising move by repeating the following four steps:

### Selection: 
Starting from the current game state (the root), traverse the tree by selecting the most promising child nodes (based on UCT score) until a leaf node is reached.

### Expansion: 
If the leaf node is not a terminal state, expand the tree by creating a new child node for one of the untried, valid moves.

### Simulation: 
From the new node, simulate a random game (playout) to its conclusion to determine the winner.

【Optimization Strategy】: 
Instead of running a full playout, this AI runs a limited-depth simulation and then uses a dynamic evaluation function (teacher_ai.py) to score the resulting board state. This function changes its weighting based on the game phase (opening, mid-game, or endgame), allowing for fast yet highly accurate evaluations.

### Backpropagation:
Update the visit counts and win scores of the nodes from the new node back up to the root, based on the simulation result.

By iterating through this cycle hundreds of times (iterations), the AI statistically determines the move with the highest probability of winning.






# File Structure
```
/othello_ai_web
|
|-- app.py             # Flask main app: API endpoints and session management
|-- tasks.py           # Celery task definition for asynchronous AI thinking
|-- othello_ai.py      # Othello game rules and board management class
|-- mcts_ai.py         # MCTS algorithm implementation
|-- teacher_ai.py      # Dynamic evaluation function used by MCTS
|-- requirements.txt   # Required Python libraries
|-- Dockerfile         # Blueprint for containerizing the application
|-- render.yaml        # Infrastructure-as-Code for deployment on Render
|-- .gitignore         # Specifies files to be ignored by Git
|
|-- templates/
|   |-- index.html     # HTML template for the game board
|
|-- static/
    |-- css/
    |   |-- style.css  # Custom styles for the application
    |-- js/
        |-- main.js    # Frontend logic for game interaction
```

## How to Run Locally

1,Clone the repository:
```
git clone [https://github.com/yamato1936/othello_ai__web.git](https://github.com/yamato1936/othello_ai__web.git)
cd othello_ai__web
```

2,Install the required libraries:
```
pip install -r requirements.txt
```

3,Start the Redis server using Docker:
```
docker run -d -p 6379:6379 redis
```

4,In a new terminal, start the Celery worker:
```
celery -A tasks.celery worker --loglevel=info
```

5,In yet another terminal, start the Flask application:
```
flask run
```

6,Open your browser and navigate to http://127.0.0.1:5000.
