document.addEventListener('DOMContentLoaded', () => {

    const boardEl = document.getElementById("board");
    const blackCountEl = document.getElementById("black-count");
    const whiteCountEl = document.getElementById("white-count");
    const messageEl = document.getElementById("message");
    const thinkingOverlay = document.getElementById("thinking-overlay");
    const resetButton = document.getElementById("reset-button");

    let boardData = [];
    let currentPlayer = 1;
    let gameOver = false;

    async function fetchBoard() {
        try {
            const res = await fetch("/board");
            const data = await res.json();
            boardData = data.board;
            currentPlayer = data.current_player;
            gameOver = data.game_over;
            renderBoard(data.black, data.white);
        } catch (error) {
            console.error("Failed to fetch board:", error);
        }
    }

    function renderBoard(black, white) {
        boardEl.innerHTML = "";
        boardEl.appendChild(thinkingOverlay);

        for (let x = 0; x < 8; x++) {
            for (let y = 0; y < 8; y++) {
                const cell = document.createElement("div");
                cell.className = "cell";
                cell.dataset.x = x;
                cell.dataset.y = y;

                const val = boardData[x][y];
                if (val === 1 || val === -1) {
                    const stone = document.createElement("div");
                    stone.className = "stone " + (val === 1 ? "black" : "white");
                    cell.appendChild(stone);
                }
                cell.addEventListener("click", () => handleCellClick(x, y));
                boardEl.appendChild(cell);
            }
        }
        
        blackCountEl.textContent = black;
        whiteCountEl.textContent = white;
        updateMessage(black, white);
        
        if (!gameOver && currentPlayer === 1) {
            showLegalMoves();
        }
    }
    
    function updateMessage(black, white) {
        if (gameOver) {
            if (black > white) messageEl.textContent = "You Win!";
            else if (white > black) messageEl.textContent = "You Lose.";
            else messageEl.textContent = "Draw!";
        } else {
            messageEl.textContent = currentPlayer === 1 ? "Your Turn" : "AI's Turn";
        }
    }

    async function showLegalMoves() {
        try {
            const res = await fetch('/legal_moves');
            const data = await res.json();
            data.moves.forEach(([x, y]) => {
                const cell = boardEl.querySelector(`[data-x='${x}'][data-y='${y}']`);
                if (cell && cell.children.length === 0) {
                    const indicator = document.createElement('div');
                    indicator.className = 'legal-move-indicator';
                    cell.appendChild(indicator);
                }
            });
        } catch (error) {
            console.error("Failed to fetch legal moves:", error);
        }
    }

    function handleCellClick(x, y) {
        if (gameOver || currentPlayer !== 1) return;
        
        const cell = boardEl.querySelector(`[data-x='${x}'][data-y='${y}']`);
        if (!cell || !cell.querySelector('.legal-move-indicator')) return;

        makeMove(x, y);
    }

    async function makeMove(x, y) {
        try {
            const res = await fetch("/make_move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ x, y })
            });
            const data = await res.json();
            if (!data.success) {
                alert("Invalid move.");
                return;
            }
            await fetchBoard(); // 自分の手を反映
            setTimeout(startAiTask, 100);
        } catch (error) {
            console.error("Failed to make move:", error);
        }
    }

    async function startAiTask() {
        thinkingOverlay.style.display = 'flex';
        try {
            const res = await fetch("/start_ai_move", { method: "POST" });
            const data = await res.json();
            if (data.pass) {
                alert("AI passed. It's your turn.");
                hideOverlay();
                await fetchBoard();
                return;
            }
            pollTaskStatus(data.task_id);
        } catch(error) {
            console.error("Failed to start AI task:", error);
            hideOverlay();
        }
    }

    function pollTaskStatus(taskId) {
        const intervalId = setInterval(async () => {
            try {
                const res = await fetch(`/get_ai_result/${taskId}`);
                const data = await res.json();

                if (data.state === 'SUCCESS') {
                    clearInterval(intervalId);
                    if (data.player_must_pass) {
                    // プレイヤーがパスした場合
                        alert("No moves available. Passing turn.");
                    // 盤面を更新し、即座に次のAIの思考を開始
                        await fetchBoard();
                        setTimeout(startAiTask, 100);
                    } else {
                    // 通常通り、UIのロックを解除して盤面を更新
                        hideOverlay();
                        await fetchBoard();
                }
                } else if (data.state === 'FAILURE') {
                    clearInterval(intervalId);
                    alert("An error occurred during the AI's turn.");
                    hideOverlay();
                }
            } catch (error) {
                clearInterval(intervalId);
                console.error("Polling error:", error);
                hideOverlay();
            }
        }, 2000);
    }
    
    function hideOverlay() {
        thinkingOverlay.style.display = 'none';
    }

    async function resetGame() {
        await fetch("/reset", { method: "POST" });
        await fetchBoard();
    }

    resetButton.addEventListener('click', resetGame);
    fetchBoard();
});
